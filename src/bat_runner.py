import subprocess

from src.config.app_config import BAT_FILE

def run_bat():
    result = subprocess.run(
        ['cmd', '/c', 'start', '', '/wait', BAT_FILE]
    )
    if result.returncode != 0:
        raise RuntimeError(f"BAT failed with code {result.returncode}")

    print("BAT executed with success")