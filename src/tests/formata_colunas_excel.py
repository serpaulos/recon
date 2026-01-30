import pandas as pd
import warnings


def validar_e_normalizar_snapshots(df, limite_percentual=80, mostrar_diferencas=False):
    """
    Valida as duas últimas colunas de um DataFrame e normaliza os nomes das colunas.

    Parâmetros:
        df : pd.DataFrame
            DataFrame limpo de colunas NaN
        limite_percentual : int
            Percentual de igualdade que dispara warning de quase duplicado
        mostrar_diferencas : bool
            Se True, imprime as linhas que diferem

    Retorna:
        df_formatado : pd.DataFrame
            DataFrame com colunas normalizadas (sem hora, duplicadas com .1, .2)
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

    # Mostra diferenças se solicitado
    if mostrar_diferencas and not diferencas.empty:
        print("\n🔍 Diferenças detectadas:")
        print(diferencas.to_string())

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



import pandas as pd


# Leitura do Excel
nome_arquivo = "./Reconciliation automation - UAT - v2.0.xlsm"
data = pd.read_excel(nome_arquivo, sheet_name="Overview", header=2, index_col=0)


# Remove colunas totalmente NaN
df_limpo = data.dropna(axis=1, how='all')


# Valida e normaliza
df_formatado, status = validar_e_normalizar_snapshots(df_limpo, limite_percentual=80, mostrar_diferencas=True)


print("Status da validação:", status)



