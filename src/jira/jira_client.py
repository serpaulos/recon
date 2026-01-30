# src/jira/jira_client.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Union

import requests

VerifyType = Union[bool, str]


@dataclass(frozen=True)
class JiraHttpConfig:
    base_url: str
    username: str
    password: str
    verify_ssl: VerifyType = True
    timeout: tuple[int, int] = (10, 60)  # (connect, read)


class JiraClient:
    def __init__(self, cfg: JiraHttpConfig):
        self.cfg = cfg
        self.base_url = cfg.base_url.rstrip("/")
        self.session = requests.Session()
        self.session.verify = cfg.verify_ssl
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "Recon-Automation/1.0",
        })

        # cookie session (evita XSRF/401 em POST em alguns Jira Server/DC)
        self.login_session()

    def _url(self, path: str) -> str:
        if not path.startswith("/"):
            path = "/" + path
        return f"{self.base_url}{path}"

    def login_session(self) -> None:
        r = self.session.post(
            self._url("/rest/auth/1/session"),
            json={"username": self.cfg.username, "password": self.cfg.password},
            timeout=self.cfg.timeout,
            verify=self.cfg.verify_ssl,
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

    def get(self, path: str, **kwargs) -> requests.Response:
        return self.session.get(self._url(path), verify=self.cfg.verify_ssl, timeout=self.cfg.timeout, **kwargs)

    def post(self, path: str, **kwargs) -> requests.Response:
        headers = kwargs.pop("headers", {}) or {}
        headers.setdefault("X-Atlassian-Token", "no-check")
        headers.setdefault("Accept", "application/json")

        # ⚠️ só setar Content-Type JSON se for json=
        if "json" in kwargs and kwargs["json"] is not None:
            headers.setdefault("Content-Type", "application/json")

        return self.session.post(self._url(path), headers=headers, timeout=self.cfg.timeout, **kwargs)
