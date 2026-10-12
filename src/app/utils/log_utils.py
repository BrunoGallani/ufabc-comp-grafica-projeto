import sys

from moderngl import Context

from utils.date_utils import get_date_prefix

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

def log_hardware_properties(ctx: Context) -> str:
    """
    Retorna as propriedades do driver e da placa de vídeo do contexto, uma por linha.
    """
    return (f"GL_VERSION  : {ctx.info['GL_VERSION']}\n"
            f"GL_RENDERER : {ctx.info['GL_RENDERER']}\n"
            f"GL_VENDOR   : {ctx.info['GL_VENDOR']}\n"
            f"GL (código de versão) : {ctx.version_code}")
