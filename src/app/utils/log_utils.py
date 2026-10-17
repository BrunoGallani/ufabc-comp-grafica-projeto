import sys
from datetime import datetime, timedelta, timezone

# Horário de Brasília fixo em UTC-3 (sem horário de verão desde 2019). Com ZoneInfo
# precisaria do banco de fusos do sistema, que o Windows não tem.
BRT = timezone(timedelta(hours=-3), "BRT")

def get_date_prefix() -> str:
    """Prefixo dos logs: [AAAA-MM-DD hh:mm:ss.mmm BRT]."""
    agora = datetime.now(BRT)
    return f"[{agora:%Y-%m-%d %H:%M:%S}.{agora.microsecond // 1000:03d} BRT]"

class Log:
    """
    Logs com data e hora: `d` pra eventos (stdout) e `e` pra erros (stderr). O flush
    faz a mensagem sair na hora, mesmo com a saída redirecionada.
    """

    @staticmethod
    def d(msg: str) -> None:
        print(f"{get_date_prefix()} {msg}", flush=True)

    @staticmethod
    def e(msg: str) -> None:
        print(f"{get_date_prefix()} ERRO: {msg}", file=sys.stderr, flush=True)
