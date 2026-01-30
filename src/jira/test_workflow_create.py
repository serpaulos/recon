from pathlib import Path

import pandas as pd

from jira_client import JiraClient, JiraHttpConfig
from jira_config import JiraConfig
from jira_workflow import create_recon_event_and_attach

# Ajuste para seu ambiente (ou importe de um config local)
JIRA_BASE_URL = "https://jiraqa.srv.euronext.com"
JIRA_USERNAME = "pagerduty.svc@euronext.com"
JIRA_PASSWORD = "GRlBjkcNpjq0Y01UbiOs8nBNHMmQsyVp0lKN8N"
JIRA_VERIFY_SSL = False


def main():
    http = JiraHttpConfig(
        base_url=JIRA_BASE_URL,
        username=JIRA_USERNAME,
        password=JIRA_PASSWORD,
        verify_ssl=JIRA_VERIFY_SSL,
        timeout=(10, 60),
    )
    jira = JiraClient(http)

    cfg = JiraConfig(
        base_url=JIRA_BASE_URL,
        username=JIRA_USERNAME,
        password=JIRA_PASSWORD,
        verify_ssl=JIRA_VERIFY_SSL,
        project_key="EVT",
        issue_type_name="Event",
        template_issue_key="EVT-110442",  # seu template
    )

    # exemplo df_last4 (substitua pelo seu)
    df_last4 = pd.DataFrame(
        {
            "01-01-2026": [0, 0, 0, 0, 0, 0],
            "02-01-2026": [0, 0, 0, 0, 0, 0],
            "03-01-2026": [0, 0, 0, 0, 0, 0],
            "04-01-2026": [1, 0, 0, 0, 0, 0],
        },
        index=["Settled", "Pending", "Participants", "ISIN", "Holdings", "Accounts"]
    )

    files = [Path(r"C:\Dev\recon\src\tests\jira_tests\PENDERR_X201770A.CSV")]

    issue_key = create_recon_event_and_attach(
        jira,
        cfg,
        env="DEMO",
        df_last4=df_last4,
        operating_date_ddmmyyyy="04-01-2026",
        files=files,
        labels=["CPH_Reconciliation"],
    )

    print("Created:", issue_key)


if __name__ == "__main__":
    main()
