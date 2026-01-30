import subprocess
import os
import xlwings as xw
from pathlib import Path
import pandas as pd

# ====== CONFIG =======
user_home = os.path.expanduser("~")

bat_file = f"{user_home}\\Euronext\\ES Operations - General\\16. Files\\CPH_Reconciliation\\main.bat"
excel_base_dir = f"{user_home}\\Euronext\\ES Operations - General\\16. Files\\CPH_Reconciliation"


envs = {
    "PROD": {
        "folder": "PROD",
        "file": "Reconciliation automation - v2.0.xlsm",
        "macro": "MainReconExecution"
    },
    "DEMO": {
        "folder": "EUA",
        "file": "Reconciliation automation - UAT - v2.0.xlsm",
        "macro": "MainReconExecution"
    },
    "FUNK": {
        "folder": "FUNK",
        "file": "Reconciliation automation - FUNK - v2.0 - test.xlsm",
        "macro": "MainReconExecution"
    }
}


env_config = envs["FUNK"]
base_dir = Path(excel_base_dir)

filename = base_dir / env_config['folder'] / env_config['file']

data = pd.read_excel(filename, sheet_name="Overview", header=2, index_col=0)


