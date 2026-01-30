import re
from datetime import datetime, time, timezone
import pandas as pd

CUTOFF_TIME = time(6, 0)  # 06:00 GMT


def get_env_config(env: str, envs: dict):
    if not isinstance(envs, dict):
        raise TypeError(f"ENV must be a dictionary ")

    if env not in envs:
        raise ValueError(f"Invalid environment: {env} ")

    return envs[env]


def validate_jira(jira: str) -> str | None:
    jira = jira.strip().lower()
    return jira if re.fullmatch(r"evt-\d{6}", jira) else None


def validate_date(date_str: str) -> str | None:
    try:
        return datetime.strptime(date_str.strip(), "%d-%m-%Y").strftime("%d-%m-%Y")
    except ValueError:
        return None


def decide_email_type(job_snapshot, override_s1=False, now_utc=None):
    """
    Decide FULL / PARTIAL / FLOW_STOPPED / WAIT
    """
    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    after_cutoff = now_utc.time() >= CUTOFF_TIME
    statuses = [job["status"] for job in job_snapshot]

    all_ok = all(s == "OK" for s in statuses)
    none_ok = all(s != "OK" for s in statuses)

    if all_ok:
        return "FULL"
    if not after_cutoff and not override_s1:
        return "WAIT"
    if none_ok:
        return "FLOW_STOPPED"
    return "PARTIAL"


def format_excel_column(col) -> str:
    """
    Formata nomes de colunas do Excel para exibição humana.
    Converte datas para dd-mm-yyyy, remove sufixos .1, .2 etc de strings.
    """

    # Tenta converter para datetime
    try:
        dt = pd.to_datetime(col, dayfirst=True, errors="coerce")
        if not pd.isna(dt):
            return dt.strftime("%d-%m-%Y")
    except Exception:
        pass

    # Se não for datetime, trata como string
    col_str = str(col)
    # Remove sufixo tipo .1, .2
    if "." in col_str:
        parts = col_str.split(".")
        # se a parte antes do ponto for numérica grande ou data, pode manter apenas antes do ponto
        col_str = parts[0]

    return col_str


def show_dataframe_in_treeview(treeview, df):
    treeview.delete(*treeview.get_children())

    cols = ["Metric"] + list(df.columns.astype(str))
    treeview["columns"] = cols

    for col in cols:
        treeview.heading(col, text=col)
        treeview.column(col, anchor="center", width=120)

    for idx, row in df.iterrows():
        treeview.insert(
            "",
            "end",
            values=[idx] + list(row.values)
        )


def dataframe_to_html(df):
    return df.to_html(
        border=1,
        index=True,
        justify="center"
    )


def get_operating_date_from_df(df: pd.DataFrame) -> str:
    """
    Retorna dd-mm-yyyy baseado na última coluna do DF.
    Aceita colunas tipo '17-11-2025' ou '17-11-2025.1'.
    """
    last_col = str(df.columns[-1]).split(".")[0]
    dt = pd.to_datetime(last_col, dayfirst=True, errors="coerce")
    if pd.isna(dt):
        raise ValueError(f"Cannot determine operating date from last column: {df.columns[-1]}")
    return dt.strftime("%d-%m-%Y")


def operating_key_yyyy_mm_dd(date_dd_mm_yyyy: str) -> str:
    """
    Converte dd-mm-yyyy -> yyyy-mm-dd (boa para chave do JSON).
    """
    dt = pd.to_datetime(date_dd_mm_yyyy, dayfirst=True, errors="raise")
    return dt.strftime("%Y-%m-%d")
