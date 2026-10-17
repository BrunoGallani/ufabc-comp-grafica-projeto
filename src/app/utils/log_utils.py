import sys
from datetime import datetime, timedelta, timezone

# Horário de Brasília: UTC-3, sem horário de verão desde 2019. O fuso fixo não
# depende do banco de fusos horários do sistema, que o Windows não tem.
BRT = timezone(timedelta(hours=-3), "BRT")

def get_date_prefix() -> str:
    """
    Retorna um prefixo de data no formato `[AAAA-MM-DD hh:mm:ss.mmm BRT]`,
    usando o fuso horário de Brasília. Este prefixo é utilizado nos logs do programa.
    """
    agora = datetime.now(BRT)
    return f"[{agora:%Y-%m-%d %H:%M:%S}.{agora.microsecond // 1000:03d} BRT]"

class Log:
    """
    Registro de mensagens no terminal, sempre com data e hora.

    - :meth:`d`: eventos do programa, em `stdout`;
    - :meth:`e`: erros, em `stderr`.

    As mensagens são enviadas imediatamente (`flush`), mesmo quando a saída é
    redirecionada para um arquivo ou para outro programa.
    """

    @staticmethod
    def d(msg: str) -> None:
        """
        Registra no terminal o que aconteceu, com data e hora.
        """
        print(f"{get_date_prefix()} {msg}", flush=True)

    @staticmethod
    def e(msg: str) -> None:
        """
        Registra um erro no terminal (`stderr`), com data e hora.
        """
        print(f"{get_date_prefix()} ERRO: {msg}", file=sys.stderr, flush=True)
