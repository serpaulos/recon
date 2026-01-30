from src.config.secrets import (
    JIRA_BASE_URL,
    JIRA_USERNAME,
    JIRA_PASSWORD,
    JIRA_VERIFY_SSL,
)
from src.jira.jira_client import JiraClient
from src.jira.jira_config import JiraConfig, FIELD_ENVIRONMENT

ISSUE_KEY = "EVT-71315"  # 👈 troca por um EVT real (QA ou PROD)


def main():
    jira = JiraClient(JiraConfig(
        base_url=JIRA_BASE_URL,
        username=JIRA_USERNAME,
        password=JIRA_PASSWORD,
        verify_ssl=JIRA_VERIFY_SSL,
        project_key="EVT",
        issue_type_name="Event",
        template_issue_key="DUMMY",  # não usado aqui
    ))

    r = jira.get(
        f"/rest/api/2/issue/{ISSUE_KEY}",
        params={"fields": FIELD_ENVIRONMENT}
    )

    if r.status_code != 200:
        print("ERROR:", r.status_code, r.text)
        return

    field = r.json()["fields"][FIELD_ENVIRONMENT]

    print("Raw Environment field:")
    print(field)


if __name__ == "__main__":
    main()
