import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from jira_api import JiraClient, JiraConfig, get_template_fields, REQUIRED_FIELDS
from config import (
    JIRA_BASE_URL, JIRA_USERNAME, JIRA_PASSWORD,
    JIRA_PROJECT_KEY, JIRA_ISSUE_TYPE, JIRA_VERIFY_SSL,
    JIRA_TEMPLATE_ISSUE
)


def main():
    jira = JiraClient(JiraConfig(
        base_url=JIRA_BASE_URL,
        username=JIRA_USERNAME,
        password=JIRA_PASSWORD,
        project_key=JIRA_PROJECT_KEY,
        issue_type_name=JIRA_ISSUE_TYPE,
        verify=JIRA_VERIFY_SSL,  # False por enquanto
    ))

    fields = get_template_fields(jira, JIRA_TEMPLATE_ISSUE)
    print("✅ Template OK:", JIRA_TEMPLATE_ISSUE)
    for f in REQUIRED_FIELDS:
        v = fields.get(f)
        print(f"- {f}: type={type(v).__name__}, value_preview={str(v)[:80]}")


if __name__ == "__main__":
    main()
