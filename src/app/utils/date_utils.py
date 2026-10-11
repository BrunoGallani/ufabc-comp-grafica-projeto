from datetime import datetime

def get_date_prefix() -> str:
    """
    Retorna um prefixo de data no formato `[%Y-%m-%d %H:%M:%S]`
    """
    return f'{datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")}'