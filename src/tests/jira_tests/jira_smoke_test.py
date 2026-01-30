from jira_api import JiraClient, JiraConfig
from config import (
    JIRA_BASE_URL, JIRA_USERNAME, JIRA_PASSWORD,
    JIRA_PROJECT_KEY, JIRA_ISSUE_TYPE, JIRA_VERIFY_SSL
)


def main():
    jira = JiraClient(JiraConfig(
        base_url=JIRA_BASE_URL,
        username=JIRA_USERNAME,
        password=JIRA_PASSWORD,
        project_key=JIRA_PROJECT_KEY,
        issue_type_name=JIRA_ISSUE_TYPE,
        verify=JIRA_VERIFY_SSL,  # por agora: False
    ))

    r = jira.get("/rest/api/2/myself")
    print("Status:", r.status_code)
    print("Content-Type:", r.headers.get("Content-Type"))
    print("Body head:", r.text[:200])

    r.raise_for_status()
    data = r.json()
    print("User:", data.get("displayName"))
    print("Email:", data.get("emailAddress"))


if __name__ == "__main__":
    main()
