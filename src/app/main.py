import sys

import glfw
import moderngl

from cena import Cena
from config import ALTURA_JANELA, LARGURA_JANELA, TITULO_JANELA
from utils.log_utils import Log

def glfw_error(error_code: int, error_message: str) -> None:
    """
    Callback para erros do GLFW.

    Substitui o aviso padrão do `pyGLFW`: imprime código
    e descrição de qualquer erro do `GLFW` em `stderr`.
    """
    Log.e(f"GLFW [{error_code}]: {error_message}")

def setup_glfw() -> tuple[moderngl.Context, 'glfw._GLFWwindowPointerT']:
    """
    Inicializa o GLFW, cria a janela com contexto OpenGL 4.0 Core e retorna o
    par (contexto `moderngl`, janela).

    Se o GLFW ou a janela falharem, o erro é registrado e o programa é encerrado.
    """
    glfw.set_error_callback(glfw_error)

    if not glfw.init():
        Log.e("o GLFW não inicializou.")
        sys.exit(1)

    # Restrições
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE) # requisito para funcionamento no MacOS
    glfw.window_hint(glfw.SAMPLES, 4)                       # antialiasing (MSAA, 4 amostras)
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
    """
    Cria a cena e roda o laço principal até a janela ser fechada.

    A cada quadro, a cena é atualizada pelo tempo transcorrido desde o quadro
    anterior (`dt`) e desenhada no *backbuffer*, que então é exibido.
    Ao final, libera a VRAM e encerra o GLFW.
    """
    cena = Cena(ctx, window)

    glfw.set_key_callback(window, cena.tecla)
    glfw.set_framebuffer_size_callback(window, cena.redimensionar)
    # Viewport inicial: o callback só é chamado quando o tamanho muda.
    cena.redimensionar(window, *glfw.get_framebuffer_size(window))

    instante_anterior = glfw.get_time()
    while not glfw.window_should_close(window):
        # O limite de 0.1 s evita um "salto" na animação se a janela travar
        agora = glfw.get_time()
        dt = min(agora - instante_anterior, 0.1)
        instante_anterior = agora

        cena.atualizar(dt)          # 1. move o que se move (nuvens, chuva...)
        cena.desenhar()             # 2. desenha o quadro inteiro no backbuffer
        glfw.swap_buffers(window)   # 3. mostra o quadro pronto
        glfw.poll_events()          # 4. processa os eventos (chama cena.tecla)

    cena.liberar()  # libera VBOs, VAOs e o programa de shaders da VRAM
    glfw.terminate()
    Log.d("Execução finalizada.")

def main() -> None:
    """
    Função principal do programa.
    """
    Log.d("Esta cena é interativa!"
          "\nAperte a tecla 'K' para visualizar o tutorial no terminal.")
    run_app(*setup_glfw())

if __name__ == "__main__":
    main()