from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, Optional, Any

ENVS = ("PROD", "DEMO", "FUNK")


@dataclass
class AppState:
    # controle diário de execução (reset automático quando muda o dia)
    run_date_key: Optional[str] = None  # YYYY-MM-DD (dia em que a GUI está rodando)

    bat_done: bool = False
    bat_last_run: Optional[str] = None

    excel_done: Dict[str, bool] = field(default_factory=lambda: {e: False for e in ENVS})
    validate_done: Dict[str, bool] = field(default_factory=lambda: {e: False for e in ENVS})

    # último Jira criado por env
    last_jira_key: Dict[str, Optional[str]] = field(default_factory=lambda: {e: None for e in ENVS})

    # operating date (setado após Validate Excel)
    operating_date_ddmmyyyy: Optional[str] = None
    operating_date_key: Optional[str] = None

    # guarda estado temporário antes do operating_date existir
    draft_jobs_by_env: Dict[str, Dict[str, Dict[str, Any]]] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "AppState":
        st = cls()
        if not isinstance(data, dict):
            return st

        # campos simples
        st.run_date_key = data.get("run_date_key")
        st.bat_done = bool(data.get("bat_done", False))
        st.bat_last_run = data.get("bat_last_run")

        st.operating_date_ddmmyyyy = data.get("operating_date_ddmmyyyy")
        st.operating_date_key = data.get("operating_date_key")

        # dicts por env (merge com defaults)
        excel_done = data.get("excel_done", {})
        validate_done = data.get("validate_done", {})
        last_jira_key = data.get("last_jira_key", {})

        for e in ENVS:
            st.excel_done[e] = bool(excel_done.get(e, st.excel_done[e]))
            st.validate_done[e] = bool(validate_done.get(e, st.validate_done[e]))
            st.last_jira_key[e] = last_jira_key.get(e, st.last_jira_key[e])

        # draft (pode ser grande)
        draft = data.get("draft_jobs_by_env", {})
        if isinstance(draft, dict):
            st.draft_jobs_by_env = draft
        else:
            st.draft_jobs_by_env = {}

        return st
