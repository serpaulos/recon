# src/config/env_resolver.py
from __future__ import annotations
from pathlib import Path
from src.config.app_config import ENVS

# Jira mapping (o seu real)
ENV_LABEL_BY_ENV = {
    "DEMO": "pEUA",
    "PROD": "PROD",
    "FUNK": "pEUA",
}

def env_fs_folder(env: str) -> str:
    """Converte env lógico (PROD/DEMO/FUNK) para folder real do SharePoint/local."""
    return ENVS[env]["folder"]

def env_jira_label(env: str) -> str:
    """Converte env lógico para o label do campo Environment no Jira."""
    return ENV_LABEL_BY_ENV[env]

def env_send_dir(env: str, send_base_dir: Path) -> Path:
    """Pasta padrão onde ficam os anexos CSV."""
    return send_base_dir / env_fs_folder(env) / "Send”"


teste = env_fs_folder("FUNK")
print(teste)