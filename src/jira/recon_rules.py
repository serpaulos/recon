import pandas as pd

RECON_METRICS = [
    "Settled",
    "Pending",
    "Participants",
    "ISIN",
    "Holdings",
    "Accounts",
]


def should_create_jira(df_last4: pd.DataFrame) -> bool:
    """
    Retorna True  -> criar Jira
    Retorna False -> NÃO criar Jira (cenário ideal)


    Regra:
    - Olha SOMENTE a última coluna
    - Se as 6 métricas forem 0 -> mundo ideal -> False
    - Qualquer outro caso -> True
    """
    if df_last4 is None or df_last4.empty:
        # Sem dados = risco -> cria Jira
        return True

    df = df_last4.copy()
    df.index = df.index.astype(str)

    # Garante que todas as métricas existem
    missing = set(RECON_METRICS) - set(df.index)
    if missing:
        # Métrica faltando = não confiável -> cria Jira
        return True

    last_col = df.columns[-1]

    # Converte para número
    last_vals = pd.to_numeric(
        df.loc[RECON_METRICS, last_col],
        errors="coerce"
    )

    # Se tiver NaN, já não é mundo ideal
    if last_vals.isna().any():
        return True

    # Mundo ideal: tudo exatamente zero
    return not (last_vals == 0).all()
