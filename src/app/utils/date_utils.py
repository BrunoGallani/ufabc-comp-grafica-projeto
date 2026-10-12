from datetime import datetime
from zoneinfo import ZoneInfo

def get_date_prefix() -> str:
    """
    Retorna um prefixo de data no formato `[AAAA-MM-DD hh:mm:ss.mmm BRT]`,
    usando o fuso horário de Brasília. Este prefixo é utilizado nos logs do programa.
    """

    fuso_br = ZoneInfo("America/Sao_Paulo")
    agora = datetime.now(fuso_br)

    return f"[{agora:%Y-%m-%d %H:%M:%S}.{agora.microsecond // 1000:03d} BRT]"