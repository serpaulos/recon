import pandas as pd
import warnings


def normalizar_colunas_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converte TODAS as colunas que parecem datas para DD-MM-YYYY (string),
    mantendo duplicatas como .1, .2 etc.
    """
    novas_colunas = []
    contagem = {}

    for col in df.columns:
        col_str = str(col).strip()

        # tenta converter para datetime
        dt = pd.to_datetime(col_str, errors="coerce", dayfirst=True)

        if pd.notna(dt):
            base = dt.strftime("%d-%m-%Y")
        else:
            base = col_str

        # mantém unicidade
        if base not in contagem:
            contagem[base] = 0
            novas_colunas.append(base)
        else:
            contagem[base] += 1
            novas_colunas.append(f"{base}.{contagem[base]}")

    df = df.copy()
    df.columns = novas_colunas
    return df


def validar_snapshots(df, limite_percentual=80):
    """
    Valida as duas últimas colunas de um DataFrame e normaliza nomes das colunas.

    Passos:
        1. Valida duplicação ou quase duplicação
        2. Emite warning se necessário
        3. Remove hora das colunas
        4. Mantém unicidade das colunas
        5. Retorna DataFrame pronto para extrair últimos movimentos

    Parâmetros:
        df : pd.DataFrame
            DataFrame limpo de NaNs
        limite_percentual : int
            Percentual de igualdade que dispara warning de quase duplicado

    Retorna:
        df_formatado : pd.DataFrame
            DataFrame com colunas normalizadas
        status : str
            "duplicado", "quase_duplicado", "ok"
    """

    # --- Validação das duas últimas colunas ---
    col_penult = df.iloc[:, -2]
    col_ult = df.iloc[:, -1]
    nome_penult = df.columns[-2]
    nome_ult = df.columns[-1]

    # Converte para numérico para comparação segura
    col_penult_num = pd.to_numeric(col_penult, errors="coerce")
    col_ult_num = pd.to_numeric(col_ult, errors="coerce")

    # Verifica igualdade linha a linha
    iguais = col_penult_num == col_ult_num
    percentual_iguais = iguais.mean() * 100

    # Detecta diferenças
    diferencas = df.loc[~iguais, [nome_penult, nome_ult]]

    # --- Decisão por níveis ---
    if percentual_iguais == 100:
        warnings.warn(
            f"⚠️ Snapshots '{nome_penult}' e '{nome_ult}' são 100% idênticos (duplicação clara).",
            UserWarning
        )
        status = "duplicado"


    elif percentual_iguais >= limite_percentual:
        warnings.warn(
            f"⚠️ Snapshots '{nome_penult}' e '{nome_ult}' são quase idênticos "
            f"({percentual_iguais:.1f}% iguais). Possível falha de extração.",
            UserWarning
        )
        status = "quase_duplicado"


    else:
        print(
            f"✅ Snapshots '{nome_penult}' e '{nome_ult}' têm diferenças relevantes ({percentual_iguais:.1f}% iguais).")
        status = "ok"

    # Mostra diferenças para análise rápida
    if not diferencas.empty:
        print("\n🔍 Diferenças detectadas:")
        print(diferencas)

    # --- Normalização de colunas ---
    df_formatado = df.copy()
    colunas_str = df_formatado.columns.astype(str)

    # Remove hora (mantém apenas a parte da data)
    colunas_formatadas = [c.split()[0] for c in colunas_str]

    # Função para manter unicidade
    def tornar_unicas(colunas):
        novas = []
        contagem = {}
        for c in colunas:
            if c not in contagem:
                contagem[c] = 0
                novas.append(c)
            else:
                contagem[c] += 1
                novas.append(f"{c}.{contagem[c]}")
        return novas

    df_formatado.columns = tornar_unicas(colunas_formatadas)

    return df_formatado, status
