import xlwings as xw
from src.config.app_config import EXCEL_BASE_DIR, ENVS
from src.utils import get_env_config


def run_excel_macro(env: str):
    """
    Abre o Excel invisível, roda a macro do environment escolhido,
    salva e fecha o arquivo e o Excel.
    """

    env_config = get_env_config(env, ENVS)
    filename = EXCEL_BASE_DIR / env_config['folder'] / env_config['file']

    app = xw.App(visible=False)  # Excel invisível
    try:
        wb = app.books.open(filename)
        # Executa a macro
        wb.macro(env_config['macro'])()
        wb.save()
        print(f"Macro '{env_config['macro']}' executada com sucesso!")
    except Exception as e:
        print(f"[ERROR] Falha ao executar macro: {e}")
        raise
    finally:
        # Fecha o workbook e o Excel de forma segura
        try:
            wb.close()
        except:
            pass
        app.quit()
