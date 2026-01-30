from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Union
import requests

VerifyType = Union[bool, str]

REQUIRED_FIELDS = [
    "customfield_10225",  # Environment
    "customfield_10218",  # Assignment group
    "customfield_10219",  # Category - Subcategory
    "customfield_10333",  # Impacted CI
]


@dataclass
class JiraConfig:
    base_url: str
    username: str
    password: str
    project_key: str
    issue_type_name: str
    verify: VerifyType = False
    timeout: tuple[int, int] = (10, 60)


class JiraClient:
    def __init__(self, cfg: JiraConfig):
        self.cfg = cfg
        self.session = requests.Session()
        self.session.auth = (cfg.username, cfg.password)

        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Recon-Automation/1.0",
        })

        # cookie session (evita XSRF no POST em alguns Jira Server/DC)
        self.login_session()

    def _url(self, path: str) -> str:
        return self.cfg.base_url.rstrip("/") + path

    def login_session(self) -> None:
        r = self.session.post(
            self._url("/rest/auth/1/session"),
            json={"username": self.cfg.username, "password": self.cfg.password},
            verify=self.cfg.verify,
            timeout=self.cfg.timeout,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "X-Atlassian-Token": "no-check",
            },
        )

        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"Jira session login failed: {r.status_code}\n"
                f"Content-Type: {r.headers.get('Content-Type')}\n"
                f"Body head: {(r.text or '')[:400]}"
            )

    def get(self, path: str, params=None) -> requests.Response:
        return self.session.get(
            self._url(path),
            params=params,
            verify=self.cfg.verify,
            timeout=self.cfg.timeout,
        )

    def post(self, path: str, *, json=None, headers=None, files=None) -> requests.Response:
        h = {}
        if headers:
            h.update(headers)

        # XSRF
        h.setdefault("X-Atlassian-Token", "no-check")

        if json is not None:
            h.setdefault("Content-Type", "application/json")
            h.setdefault("Accept", "application/json")

        return self.session.post(
            self._url(path),
            json=json,
            headers=h,
            files=files,
            verify=self.cfg.verify,
            timeout=self.cfg.timeout,
        )


def get_template_fields(jira: JiraClient, template_issue_key: str) -> Dict:
    r = jira.get(
        f"/rest/api/2/issue/{template_issue_key}",
        params={"fields": ",".join(REQUIRED_FIELDS)}
    )
    if r.status_code != 200:
        raise RuntimeError(f"Read template failed: {r.status_code} {r.text[:300]}")

    data = r.json()
    fields = data.get("fields", {})
    out = {}

    missing = []
    for f in REQUIRED_FIELDS:
        if f not in fields or fields[f] in (None, "", [], {}):
            missing.append(f)
        else:
            for f in REQUIRED_FIELDS:
                if f not in fields or fields[f] in (None, "", [], {}):
                    missing.append(f)
                    continue

                v = fields[f]

                # customfield_10333 (Impacted CI) precisa ser OBJETO no create
                # Se veio como list de string, tenta converter pelo customFieldOption id
                if f == "customfield_10333":
                    # casos comuns: já vem como dict ou list de dict
                    if isinstance(v, dict):
                        out[f] = v
                    elif isinstance(v, list):
                        # se for lista de dicts -> provavelmente multi, mas seu erro pede objeto
                        if v and isinstance(v[0], dict):
                            out[f] = v[0]  # pega o primeiro como objeto
                        elif v and isinstance(v[0], str):
                            # pega o option id a partir do endpoint de option (você tem 13613)
                            # melhor: manter isso configurável — por enquanto hardcode via config
                            out[f] = v
                        else:
                            raise RuntimeError(f"Unsupported value for {f}: {v}")
                    else:
                        # string ou outro tipo
                        raise RuntimeError(f"Unsupported value for {f}: {v}")
                else:
                    out[f] = v

    if missing:
        raise RuntimeError(f"Template issue missing required fields: {missing}")

    return out


def create_issue_from_template(
        jira: JiraClient,
        *,
        summary: str,
        description: str,
        template_fields: Dict,
        labels: Optional[List[str]] = None,
) -> str:
    payload = {
        "fields": {
            "project": {"key": jira.cfg.project_key},
            "issuetype": {"name": jira.cfg.issue_type_name},
            "summary": summary,
            "description": description,
            **template_fields,
        }
    }

    if labels:
        payload["fields"]["labels"] = labels

    r = jira.post("/rest/api/2/issue", json=payload)

    if r.status_code not in (200, 201):
        raise RuntimeError(
            f"Create issue failed: {r.status_code}\n"
            f"Content-Type: {r.headers.get('Content-Type')}\n"
            f"Body head: {(r.text or '')[:500]}"
        )

    issue_key = None
    try:
        if r.text and r.text.strip():
            issue_key = r.json().get("key")
    except Exception:
        issue_key = None

    if not issue_key:
        loc = r.headers.get("Location") or r.headers.get("location")
        if loc and "/issue/" in loc:
            issue_key = loc.rsplit("/issue/", 1)[-1].strip("/")

    if not issue_key:
        raise RuntimeError(
            "Create issue succeeded but could not extract issue key.\n"
            f"Status: {r.status_code}\n"
            f"Location: {r.headers.get('Location')}\n"
            f"Body head: {(r.text or '')[:300]}"
        )

    return issue_key


def get_createmeta_fields(jira, project_key: str, issue_type_name: str) -> dict:
    """
    Busca os fields disponíveis para criação (Create Meta) e retorna o dict de fields.
    """
    r = jira.get(
        "/rest/api/2/issue/createmeta",
        params={
            "projectKeys": project_key,
            "issuetypeNames": issue_type_name,
            "expand": "projects.issuetypes.fields",
        },
    )
    if r.status_code != 200:
        raise RuntimeError(f"createmeta failed: {r.status_code} {r.text[:400]}")

    data = r.json()
    projects = data.get("projects", [])
    if not projects:
        raise RuntimeError("createmeta: no projects returned (check project key / permissions)")

    issuetypes = projects[0].get("issuetypes", [])
    if not issuetypes:
        raise RuntimeError("createmeta: no issuetypes returned (check issue type name)")

    fields = issuetypes[0].get("fields", {})
    return fields


def read_issue_field_raw(jira, issue_key: str, field_id: str):
    r = jira.get(
        f"/rest/api/2/issue/{issue_key}",
        params={"fields": field_id}
    )
    if r.status_code != 200:
        raise RuntimeError(f"read_issue_field_raw failed: {r.status_code} {r.text[:300]}")
    return r.json().get("fields", {}).get(field_id)


def resolve_allowed_value_id(fields_meta: dict, field_id: str, wanted_label: str) -> str:
    """
    Para fields do tipo select/multi-select: encontra o ID dentro de allowedValues
    comparando pelo 'value' ou 'name' (case-insensitive).
    """
    field_meta = fields_meta.get(field_id)
    if not field_meta:
        raise RuntimeError(f"{field_id} not found in createmeta fields")

    allowed = field_meta.get("allowedValues") or []
    if not allowed:
        schema = field_meta.get("schema")
        raise RuntimeError(
            f"{field_id} has no allowedValues. Schema={schema}. "
            f"This may be Assets/Insight or a special picker; needs different payload."
        )

    wanted_norm = wanted_label.strip().lower()
    for opt in allowed:
        label = (opt.get("value") or opt.get("name") or "").strip().lower()
        if label == wanted_norm:
            opt_id = opt.get("id")
            if not opt_id:
                raise RuntimeError(f"Matched '{wanted_label}' but option has no id: {opt}")
            return str(opt_id)

    # Debug útil
    sample = [opt.get("value") or opt.get("name") for opt in allowed[:10]]
    raise RuntimeError(
        f"Could not find '{wanted_label}' in allowedValues for {field_id}. "
        f"First values: {sample}"
    )


def attach_files(jira: JiraClient, issue_key: str, files: List[Path]) -> List[str]:
    attached = []

    for p in files:
        if not p.exists() or not p.is_file():
            continue

        with p.open("rb") as f:
            r = jira.post(
                f"/rest/api/2/issue/{issue_key}/attachments",
                files={"file": (p.name, f)},
                headers={"X-Atlassian-Token": "no-check"},
            )

        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"Attach failed for {p.name}: {r.status_code}\n"
                f"Content-Type: {r.headers.get('Content-Type')}\n"
                f"Body head: {(r.text or '')[:300]}"
            )

        attached.append(p.name)

    return attached
