from __future__ import annotations

import pandas as pd

# Ordem + nomes exatamente como no Jira (print)
ROW_LABELS = [
    ("Settled", "Settled Events"),
    ("Pending", "Pending Events"),
    ("Participants", "Participants"),
    ("ISIN", "ISINS"),
    ("Holdings", "Holdings"),
    ("Accounts", "Accounts"),
]


def build_summary(env_label: str) -> str:
    return f"{env_label} | CSD | ES-CPH | Reconciliation | Detected errors on Reconciliation at 08:00 CET"


def build_description(df_last4: pd.DataFrame, operating_date_ddmmyyyy: str) -> str:
    """
    Gera Description em Jira Wiki Markup (table).
    O Jira vai renderizar igual ao screenshot.
    """
    df = df_last4.copy()
    df.index = df.index.astype(str)

    # garante últimas 4 colunas (datas)
    df = df.iloc[:, -4:].copy()

    # garante colunas como dd-mm-yyyy
    cols = [str(c) for c in df.columns.tolist()]

    # header de tabela (primeira coluna vazia)
    # Ex: || ||04-11-2025||05-11-2025||06-11-2025||07-11-2025||
    header = "|| ||" + "||".join(cols) + "||"

    lines = []
    lines.append("Hello everyone,")
    lines.append("")
    lines.append(
        f"In attachment is the excel with the report for the reconciliation CPH for {operating_date_ddmmyyyy} and the raw files."
    )
    lines.append("")
    lines.append("*Grand Totals*")
    lines.append("")
    lines.append(header)

    # linhas
    for src_metric, jira_label in ROW_LABELS:
        if src_metric in df.index:
            vals = pd.to_numeric(df.loc[src_metric], errors="coerce").fillna(0).astype(int).tolist()
        else:
            # se faltar métrica, preenche 0 (ou você pode preferir blank)
            vals = [0] * len(cols)

        # Ex: |Settled Events|0|0|0|0|
        row = "|" + jira_label + "|" + "|".join(str(v) for v in vals) + "|"
        lines.append(row)

    lines.append("")  # newline final
    return "\n".join(lines)
