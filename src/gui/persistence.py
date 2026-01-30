from datetime import date, timedelta


def prune_job_state(job_state_by_date: dict, keep_days: int = 90) -> bool:
    """
    Remove dias antigos do jobs_state.json.
    Mantém apenas os últimos `keep_days`.
    Retorna True se algo foi removido.
    """
    if not isinstance(job_state_by_date, dict):
        return False

    cutoff = date.today() - timedelta(days=keep_days)
    removed = False

    for key in list(job_state_by_date.keys()):
        try:
            y, m, d = map(int, key.split("-"))
            key_date = date(y, m, d)
        except Exception:
            # chave fora do padrão YYYY-MM-DD → ignora
            continue

        if key_date < cutoff:
            job_state_by_date.pop(key, None)
            removed = True

    return removed
