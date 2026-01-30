from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import pandas as pd

from .jira_client import JiraClient
from .jira_config import (
    JiraConfig,
    ENV_LABEL_BY_ENV,
    FIELD_ASSIGNMENT_GROUP,
    FIELD_ENVIRONMENT,
    get_assignment_group_name,
    ENV_ID_BY_ENV
)
from .jira_service import (
    get_template_fields,
    normalize_impacted_ci_field_from_template,
    create_issue_from_template,
    attach_files,
)
from .recon_rules import should_create_jira
from .recon_text import build_summary, build_description


def create_recon_event_and_attach(
        jira: JiraClient,
        cfg: JiraConfig,
        *,
        env: str,
        df_last4: pd.DataFrame,
        operating_date_ddmmyyyy: str,
        files: List[Path],
        labels: Optional[List[str]] = None,
) -> Optional[str]:
    if not should_create_jira(df_last4):
        return None

    # 1) pega somente required fields do template
    template_fields = get_template_fields(jira, cfg.template_issue_key)

    # 2) override assignment group
    template_fields[FIELD_ASSIGNMENT_GROUP] = {"name": get_assignment_group_name()}

    # 3) override environment (RESOLVE ID via createmeta e envia {"id": ...})
    env_label = ENV_LABEL_BY_ENV.get(env, env)  # só para summary/description
    env_id = ENV_ID_BY_ENV.get(env)

    if not env_id:
        raise RuntimeError(f"Missing ENV option id mapping for env={env}")

    template_fields[FIELD_ENVIRONMENT] = {"id": str(env_id)}

    if not env_label:
        raise RuntimeError(f"Missing ENV label mapping for env={env}")

    # 4) impacted CI no formato certo (array de objects com key CI-xxxx)
    template_fields.update(normalize_impacted_ci_field_from_template(jira, cfg.template_issue_key))

    summary = build_summary(env_label)
    description = build_description(df_last4, operating_date_ddmmyyyy)

    issue_key = create_issue_from_template(
        jira,
        project_key=cfg.project_key,
        issue_type_name=cfg.issue_type_name,
        summary=summary,
        description=description,
        template_fields=template_fields,
        labels=labels or ["CPH_Reconciliation"],
    )

    attach_files(jira, issue_key, files)
    return issue_key
