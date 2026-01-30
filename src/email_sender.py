import win32com.client as win32
from src.config.app_config import TO_LIST, CC_LIST, ENVS
from src.utils import get_env_config


def format_missing_jobs(job_snapshot):
    """
    Gera uma lista HTML com os jobs que NÃO estão OK,
    garantindo que o RC nunca fique vazio.
    """
    if not job_snapshot:
        return ""

    rows = []
    for j in job_snapshot:
        if j.get("status") != "OK":
            rc = j.get("rc")
            if not rc:
                rc = "Not Run"

            rows.append(
                f"<li>{j['job']} ({j['job_id']}) – RC: {rc}</li>"
            )

    if not rows:
        return ""

    return "<ul>" + "".join(rows) + "</ul>"


def send_recon_email(env: str, df, jira_event: str, date_for_email: str,
                     email_type: str, job_snapshot: list, draft_only: bool = True):
    env_config = get_env_config(env, ENVS)
    jira_url = f"https://jira.euronext.com/browse/{jira_event}"

    outlook = win32.Dispatch("Outlook.Application")
    mail = outlook.CreateItem(0)

    # Recipients
    if env.upper() == "FUNK":
        to_list = ["fwieland@euronext.com", "amet@euronext.com"]
        cc_list = ["es-it-operations@euronext.com"]
    else:
        to_list = TO_LIST
        cc_list = CC_LIST

    mail.To = "; ".join(to_list)
    mail.CC = "; ".join(cc_list)

    subject_map = {
        "FULL": "Reconciliation",
        "PARTIAL": "Reconciliation (Partial)",
        "FLOW_STOPPED": "Reconciliation NOT Executed"
    }
    mail.Subject = f"[ES Operations] {subject_map.get(email_type, 'Reconciliation')} {env_config['folder']} CPH Report - {date_for_email}"

    # Prepare intro
    intro = ""
    if email_type == "FULL":
        intro = f"""
        <p>All legacy jobs executed successfully.</p>
        <p>Please find in <a href="{jira_url}">{jira_event}</a> the report for the reconciliation CPH for {date_for_email} and the raw files.</p>"
        """
    elif email_type == "PARTIAL":
        intro = f"""
        <p>Some legacy jobs did not run before 06:00 GMT.</p>
        <p>The reconciliation was executed with partial data.</p>
        <p>Missing jobs:</p>
        {format_missing_jobs(job_snapshot)}
        <p>An update will be sent as soon as the flow is completed.</p>
        <p>Please find in <a href="{jira_url}">{jira_event}</a> the report for the reconciliation CPH for {date_for_email} and the raw files.</p>"
        """
    elif email_type == "FLOW_STOPPED":
        intro = f"""
        <p>The reconciliation could not be executed as the legacy flow is stopped.</p>
        <p>Jobs not executed:</p>
        {format_missing_jobs(job_snapshot)}
        <p>An update will be sent as soon as the flow is restored.</p>
        """

    # Convert df safely
    if df is not None:
        df_html = df.copy().astype(str)
        df_html_str = df_html.to_html(border=1, index=True)
    else:
        df_html_str = ""

    # CSS inline para tabelas
    css = """
    <style>
    table {border-collapse: collapse;}
    table th, table td {border: 1px solid #555; padding: 4px 8px; text-align: center;}
    </style>
    """

    mail.HTMLBody = f"""
    {css}
    <p>Hello everyone,</p>
    {intro}
    {df_html_str}
    <p>Kind regards,<br>ES Operations</p>
    <p>EURONEXT SECURITIES<br>
    Rua de Anibal Cunha, 164 | 4050-047 Porto | Portugal<br> 
    Office: +351 220 600 102 | +45 43 588 877<br>
    Email: <a href="mailto:es-it-operations@euronext.com">es-it-operations@euronext.com</a><br>
    """

    mail.SentOnBehalfOfName = "es-it-operations@euronext.com"

    if draft_only:
        mail.Display()
    else:
        mail.Send()
