import sys

import glfw
import moderngl

from cena import Cena
from config import ALTURA_JANELA, LARGURA_JANELA, TITULO_JANELA
from utils.log_utils import Log

def glfw_error(error_code: int, error_message: str) -> None:
    """Manda os erros do GLFW pro stderr."""
    Log.e(f"GLFW [{error_code}]: {error_message}")

def setup_glfw() -> tuple[moderngl.Context, 'glfw._GLFWwindowPointerT']:
    """Abre a janela com OpenGL 4.0 Core e devolve (contexto, janela). Se falhar, encerra."""
    glfw.set_error_callback(glfw_error)

    if not glfw.init():
        Log.e("o GLFW não inicializou.")
        sys.exit(1)

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE) # sem isso não roda no macOS
    glfw.window_hint(glfw.SAMPLES, 4)                       # antialiasing
    glfw.window_hint(glfw.AUTO_ICONIFY, False)              # tela cheia não minimiza sem foco

    window = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, TITULO_JANELA, None, None)
    if not window:
        Log.e("não foi possível criar a janela (o driver suporta OpenGL 4.0 Core?).")
        glfw.terminate()
        sys.exit(1)

    glfw.make_context_current(window)
    glfw.swap_interval(1)
    ctx = moderngl.create_context()

    return ctx, window

def run_app(ctx: moderngl.Context, window: 'glfw._GLFWwindowPointerT') -> None:
    """Laço principal: atualiza, desenha e mostra cada quadro até fecharem a janela."""
    cena = Cena(ctx, window)

    glfw.set_key_callback(window, cena.tecla)
    glfw.set_framebuffer_size_callback(window, cena.redimensionar)
    # O callback só roda quando o tamanho muda, então o primeiro viewport vai na mão.
    cena.redimensionar(window, *glfw.get_framebuffer_size(window))

    instante_anterior = glfw.get_time()
    while not glfw.window_should_close(window):
        # Limitar o dt evita que a animação dê um salto se a janela travar.
        agora = glfw.get_time()
        dt = min(agora - instante_anterior, 0.1)
        instante_anterior = agora

        cena.atualizar(dt)
        cena.desenhar()
        glfw.swap_buffers(window)
        glfw.poll_events()   # é aqui que o GLFW chama cena.tecla

    cena.liberar()
    glfw.terminate()
    Log.d("Execução finalizada")

def main() -> None:
    Log.d("Cena interativa iniciada")
    Log.d("Aperte a tecla 'K' para visualizar o tutorial no terminal")
    run_app(*setup_glfw())

if __name__ == "__main__":
    main()
