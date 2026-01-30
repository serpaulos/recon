import requests
from requests.auth import HTTPBasicAuth

JIRA_URL = "https://jiraqa.srv.euronext.com/"
USERNAME = "pagerduty.svc@euronext.com"
PASSWORD = "GRlBjkcNpjq0Y01UbiOs8nBNHMmQsyVp0lKN8N"

url = f"{JIRA_URL}/rest/api/2/myself"

response = requests.get(
    url,
    auth=HTTPBasicAuth(USERNAME, PASSWORD),
    headers={"Accept": "application/json"},
    timeout=10
)

print("Status Code:", response.status_code)

if response.status_code == 200:
    data = response.json()
    print("Usuário:", data.get("displayName"))
    print("Email:", data.get("emailAddress"))
else:
    print("Erro:", response.text)
