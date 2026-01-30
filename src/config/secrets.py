# src/config/secrets.py
import os

from dotenv import load_dotenv

load_dotenv()  # lê .env


def env_bool(name: str, default=False) -> bool:
    return os.getenv(name, str(default)).lower() in ("1", "true", "yes", "on")


def require_env(name: str) -> str:
    v = (os.getenv(name) or "").strip()
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v


# -------------------------
# Jira base credentials
# -------------------------
JIRA_BASE_URL = (os.getenv("JIRA_BASE_URL") or "").strip()
JIRA_USERNAME = (os.getenv("JIRA_USERNAME") or "").strip()
JIRA_PASSWORD = (os.getenv("JIRA_PASSWORD") or "").strip()
JIRA_VERIFY_SSL = env_bool("JIRA_VERIFY_SSL", False)

JIRA_PROJECT_KEY = (os.getenv("JIRA_PROJECT_KEY") or "EVT").strip()
JIRA_ISSUE_TYPE = (os.getenv("JIRA_ISSUE_TYPE") or "Event").strip()
JIRA_TEMPLATE_ISSUE = (os.getenv("JIRA_TEMPLATE_ISSUE") or "").strip()

# QA | PROD (por enquanto). Se no futuro ficar só PROD, deixa "PROD" fixo no .env.
JIRA_MODE = (os.getenv("JIRA_MODE") or "QA").strip().upper()

JIRA_ASSIGNMENT_GROUP_QA = (os.getenv("JIRA_ASSIGNMENT_GROUP_QA") or "CSD Operations").strip()
JIRA_ASSIGNMENT_GROUP_PROD = (os.getenv("JIRA_ASSIGNMENT_GROUP_PROD") or "CA4U 2nd Level Support").strip()

JIRA_IMPACTED_CI_KEY = (os.getenv("JIRA_IMPACTED_CI_KEY") or "").strip()


def jira_creds() -> tuple[str, str, str]:
    """
    Retorna credenciais básicas do Jira (base_url, username, password).
    Lança erro se estiver faltando algo.
    """
    base_url = require_env("JIRA_BASE_URL").rstrip("/")  # evita //browse
    username = require_env("JIRA_USERNAME")
    password = require_env("JIRA_PASSWORD")
    return base_url, username, password


def assignment_group() -> str:
    """
    Retorna o nome do grupo para customfield_10218 baseado no modo.
    """
    if JIRA_MODE == "PROD":
        return JIRA_ASSIGNMENT_GROUP_PROD
    return JIRA_ASSIGNMENT_GROUP_QA
