"""
Lê um campo específico de um ticket Jira e imprime o valor bruto.
Útil para descobrir o formato correto do customfield (objeto vs lista).
"""

from jira_api import JiraClient, JiraConfig
from config import (
    JIRA_BASE_URL,
    JIRA_USERNAME,
    JIRA_PASSWORD,
    JIRA_VERIFY_SSL,
)

# 🔧 AJUSTE AQUI
ISSUE_KEY = "EVT-110422"
FIELD_ID = "customfield_10218"  # Assignment group


def main():
    jira = JiraClient(
        JiraConfig(
            base_url=JIRA_BASE_URL,
            username=JIRA_USERNAME,
            password=JIRA_PASSWORD,
            # ✅ estes 2 são obrigatórios no seu JiraConfig atual
            project_key="EVT",
            issue_type_name="Event",
            verify=JIRA_VERIFY_SSL,  # provavelmente False em QA
        )
    )

    print(f"🔎 Inspecting field '{FIELD_ID}' from issue {ISSUE_KEY}...\n")

    r = jira.get(
        f"/rest/api/2/issue/{ISSUE_KEY}",
        params={"fields": FIELD_ID},
    )

    if r.status_code != 200:
        raise RuntimeError(
            f"Failed to read issue {ISSUE_KEY}: {r.status_code}\n{r.text[:500]}"
        )

    value = r.json().get("fields", {}).get(FIELD_ID)

    print("✅ Raw value returned by Jira:\n")
    print(value)
    print("\n📌 Copie esse formato exatamente para usar no create issue.")


if __name__ == "__main__":
    main()
