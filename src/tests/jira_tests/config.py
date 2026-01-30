# =====================
# JIRA
# =====================
JIRA_BASE_URL = "https://jiraqa.srv.euronext.com/"
JIRA_USERNAME = "pagerduty.svc@euronext.com"
JIRA_PASSWORD = "GRlBjkcNpjq0Y01UbiOs8nBNHMmQsyVp0lKN8N"

JIRA_PROJECT_KEY = "EVT"
JIRA_ISSUE_TYPE = "Event"

# Jira – Assignment Group
JIRA_ASSIGNMENT_GROUP = "CSD Operations"  # QA / testes
# JIRA_ASSIGNMENT_GROUP = "CA4U 2nd Level Support"  # PROD


# EVT modelo criado manualmente (template)
JIRA_TEMPLATE_ISSUE = "EVT-110422"

# SSL
# TEMPORÁRIO: False (self-signed)
# IDEAL: caminho para CA corporativo .pem
JIRA_VERIFY_SSL = False
# JIRA_VERIFY_SSL = r"C:\certs\euronext_ca_bundle.pem"
