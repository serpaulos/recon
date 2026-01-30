import os
from dataclasses import dataclass


@dataclass(frozen=True)
class JiraConfig:
    base_url: str
    username: str
    password: str
    verify_ssl: bool
    project_key: str
    issue_type_name: str
    template_issue_key: str
    timeout: tuple[int, int] = (10, 60)


# -------------------------
# Field IDs (Jira custom fields)
# -------------------------
FIELD_ENVIRONMENT = "customfield_10225"
FIELD_ASSIGNMENT_GROUP = "customfield_10218"
FIELD_CATEGORY_SUBCATEGORY = "customfield_10219"
FIELD_IMPACTED_CI = "customfield_10333"

REQUIRED_FIELDS = [
    FIELD_ENVIRONMENT,
    FIELD_ASSIGNMENT_GROUP,
    FIELD_CATEGORY_SUBCATEGORY,
    FIELD_IMPACTED_CI,
]


# -------------------------
# Jira mode / assignment group
# -------------------------
def get_jira_mode() -> str:
    return os.getenv("JIRA_MODE", "QA").upper()  # QA | PROD


JIRA_ASSIGNMENT_GROUP_QA = os.getenv("JIRA_ASSIGNMENT_GROUP_QA", "CSD Operations")
JIRA_ASSIGNMENT_GROUP_PROD = os.getenv("JIRA_ASSIGNMENT_GROUP_PROD", "CA4U 2nd Level Support")


def get_assignment_group_name() -> str:
    mode = get_jira_mode()
    return JIRA_ASSIGNMENT_GROUP_PROD if mode == "PROD" else JIRA_ASSIGNMENT_GROUP_QA


# -------------------------
# Environment mapping (Recon env -> Jira Environment field label)
# Ajuste os valores para o label EXATO que o Jira aceita
# -------------------------
ENV_LABEL_BY_ENV = {
    "DEMO": os.getenv("JIRA_ENV_LABEL_DEMO", "pEUA"),
    "PROD": os.getenv("JIRA_ENV_LABEL_PROD", "PROD"),
    "FUNK": os.getenv("JIRA_ENV_LABEL_FUNK", "pEUA"),
}

# Environment option IDs (customfield_10225)
ENV_ID_BY_ENV = {
    "DEMO": "14313",  # pEUA
    "FUNK": "14313",  # usa o mesmo de pEUA
    "PROD": "10258",  # Production
}
