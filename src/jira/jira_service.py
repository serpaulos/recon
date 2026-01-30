from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .jira_client import JiraClient
from .jira_config import (
    REQUIRED_FIELDS,
    FIELD_IMPACTED_CI,
)


def _raise_http(r: requests.Response, prefix: str):
    ct = r.headers.get("Content-Type", "")
    body_head = (r.text or "")[:500]
    raise RuntimeError(
        f"{prefix}: {r.status_code}\n"
        f"URL: {r.url}\n"
        f"Content-Type: {ct}\n"
        f"Body head: {body_head}"
    )


def read_issue_field_raw(jira: JiraClient, issue_key: str, field_id: str):
    r = jira.get(f"/rest/api/2/issue/{issue_key}", params={"fields": field_id})
    if r.status_code != 200:
        _raise_http(r, "read_issue_field_raw failed")
    return r.json().get("fields", {}).get(field_id)


def get_template_fields(jira: JiraClient, template_issue_key: str) -> Dict[str, Any]:
    r = jira.get(
        f"/rest/api/2/issue/{template_issue_key}",
        params={"fields": ",".join(REQUIRED_FIELDS)}
    )
    if r.status_code != 200:
        _raise_http(r, "Read template failed")

    fields = r.json().get("fields", {})
    missing = [f for f in REQUIRED_FIELDS if f not in fields or fields[f] in (None, "", [], {})]
    if missing:
        raise RuntimeError(f"Template issue missing required fields: {missing}")

    return {f: fields[f] for f in REQUIRED_FIELDS}


def normalize_impacted_ci_field_from_template(jira: JiraClient, template_issue_key: str) -> Dict[str, Any]:
    """
    Lê o RAW de Impacted CI do template e devolve o valor no formato aceito:
      customfield_10333: [{"key":"CI-7685538"}]
    """
    raw = read_issue_field_raw(jira, template_issue_key, FIELD_IMPACTED_CI)
    if not raw:
        raise RuntimeError("Template issue has empty customfield_10333. Fill Impacted CI on template first.")

    raw_list = raw if isinstance(raw, list) else [str(raw)]
    raw_text = str(raw_list[0]) if raw_list else ""

    m = re.search(r"(CI-\d+)", raw_text)
    if not m:
        raise RuntimeError(f"Could not extract CI key from: {raw_text}")

    ci_key = m.group(1)
    return {FIELD_IMPACTED_CI: [{"key": ci_key}]}


def create_issue_from_template(
        jira: JiraClient,
        *,
        project_key: str,
        issue_type_name: str,
        summary: str,
        description: str,
        template_fields: Dict[str, Any],
        labels: Optional[List[str]] = None,
) -> str:
    payload = {
        "fields": {
            "project": {"key": project_key},
            "issuetype": {"name": issue_type_name},
            "summary": summary,
            "description": description,
            **template_fields,
        }
    }
    if labels:
        payload["fields"]["labels"] = labels

    r = jira.post("/rest/api/2/issue", json=payload, headers={"Content-Type": "application/json"})
    if r.status_code not in (200, 201):
        _raise_http(r, "Create issue failed")

    data = r.json()
    issue_key = data.get("key")
    if not issue_key:
        raise RuntimeError("Create issue succeeded but response has no 'key'")
    return issue_key


def attach_files(jira: JiraClient, issue_key: str, files: List[Path]) -> List[str]:
    attached = []
    for p in files:
        if not p.exists() or not p.is_file():
            print(f"[JIRA] SKIP attach (not found): {p}")
            continue

        with p.open("rb") as f:
            r = jira.post(
                f"/rest/api/2/issue/{issue_key}/attachments",
                files={"file": (p.name, f)},
                headers={"X-Atlassian-Token": "no-check"},
            )

        print(f"[JIRA] attach {p.name} -> {r.status_code} {r.headers.get('Content-Type')}")
        if r.status_code not in (200, 201):
            print("[JIRA] attach body head:", (r.text or "")[:400])
            raise RuntimeError(f"Attach failed for {p.name}: {r.status_code}")

        attached.append(p.name)

    print("[JIRA] Attached:", attached)
    return attached


def get_createmeta_fields(jira, project_key: str, issue_type_name: str) -> dict:
    r = jira.get(
        "/rest/api/2/issue/createmeta",
        params={
            "projectKeys": project_key,
            "issuetypeNames": issue_type_name,
            "expand": "projects.issuetypes.fields",
        },
    )
    if r.status_code != 200:
        _raise_http(r, "createmeta failed")

    data = r.json()
    projects = data.get("projects", [])
    issuetypes = projects[0].get("issuetypes", []) if projects else []
    fields = issuetypes[0].get("fields", {}) if issuetypes else {}
    return fields


def resolve_allowed_value_id(fields_meta: dict, field_id: str, wanted_label: str) -> str:
    field_meta = fields_meta.get(field_id) or {}
    allowed = field_meta.get("allowedValues") or []
    wanted = wanted_label.strip().lower()

    for opt in allowed:
        label = (opt.get("value") or opt.get("name") or "").strip().lower()
        if label == wanted:
            return str(opt["id"])
    raise RuntimeError(f"Could not resolve id for {field_id} label='{wanted_label}'")
