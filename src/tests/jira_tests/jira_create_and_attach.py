from pathlib import Path
from datetime import datetime

from jira_api import (
    JiraClient, JiraConfig,
    get_template_fields, create_issue_from_template, attach_files,
    read_issue_field_raw,
)
from config import (
    JIRA_BASE_URL, JIRA_USERNAME, JIRA_PASSWORD,
    JIRA_PROJECT_KEY, JIRA_ISSUE_TYPE, JIRA_VERIFY_SSL,
    JIRA_TEMPLATE_ISSUE, JIRA_ASSIGNMENT_GROUP
)

FIELD_IMPACTED_CI = "customfield_10333"


def main():
    jira = JiraClient(JiraConfig(
        base_url=JIRA_BASE_URL,
        username=JIRA_USERNAME,
        password=JIRA_PASSWORD,
        project_key=JIRA_PROJECT_KEY,
        issue_type_name=JIRA_ISSUE_TYPE,
        verify=JIRA_VERIFY_SSL,  # por agora: False
    ))

    # 1) Campos required vindos do template (env, assignment group, category, etc.)
    template_fields = get_template_fields(jira, JIRA_TEMPLATE_ISSUE)

    # --- OVERRIDE: Assignment group (customfield_10218) ---
    # Em QA/testes: CSD Operations
    template_fields["customfield_10218"] = {
        "name": "CSD Operations"
    }
    # Em PROD futuramente (troca para):
    # template_fields["customfield_10218"] = {"name": "CA4U 2nd Level Support"}

    # --- OVERRIDE: Impacted CI (customfield_10333) ---
    # Esse campo precisa ser array de objects (pelo seu erro anterior).
    # Usa o CI key que já funcionou no seu create.
    template_fields["customfield_10333"] = [
        {"key": "CI-7685538"}
    ]

    print("Template fields loaded OK:", list(template_fields.keys()))
    print("customfield_10218:", template_fields["customfield_10218"])
    print("customfield_10333:", template_fields["customfield_10333"])

    # 2) Lê o RAW do Impacted CI diretamente do template issue
    impacted_ci_raw = read_issue_field_raw(jira, JIRA_TEMPLATE_ISSUE, FIELD_IMPACTED_CI)
    print("RAW customfield_10333 from template:", impacted_ci_raw)

    if not impacted_ci_raw:
        raise RuntimeError(
            "Template issue has empty customfield_10333. "
            "Open the template issue and fill Impacted CI there first."
        )

    # 3) Copia exatamente o RAW para o create
    # 3) Converte RAW do template para o formato aceito no CREATE
    # RAW veio como list[str] tipo: ['Euronext Securities Copenhagen Office (CI-7685538)']
    raw_list = impacted_ci_raw if isinstance(impacted_ci_raw, list) else [str(impacted_ci_raw)]
    raw_text = raw_list[0] if raw_list else ""

    # Extrai o CI-xxxxxx de "(CI-7685538)"
    import re
    m = re.search(r"\((CI-\d+)\)", raw_text)
    if not m:
        raise RuntimeError(f"Could not extract CI key from: {raw_text}")

    ci_key = m.group(1)

    # Tentativa 1: campo espera objeto único
    template_fields[FIELD_IMPACTED_CI] = [{"key": ci_key}]
    print("Using customfield_10333 as object:", template_fields[FIELD_IMPACTED_CI])

    # 4) Criar issue
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    summary = f"[TEST] CPH Recon API – {now}"
    description = "Created automatically via Python requests.\n\n(Testing template-fields create + attachments.)"

    issue_key = create_issue_from_template(
        jira,
        summary=summary,
        description=description,
        template_fields=template_fields,
        labels=["CPH_Reconciliation"],
    )

    print("✅ Created issue:", issue_key)
    print("URL:", f"{JIRA_BASE_URL}/browse/{issue_key}")

    # 5) Anexar arquivos
    files = [
        Path(r"C:\Dev\recon\src\tests\jira_tests\PENDERR_X201770A.CSV"),
    ]
    attached = attach_files(jira, issue_key, files)
    print("✅ Attached:", attached)


if __name__ == "__main__":
    main()
