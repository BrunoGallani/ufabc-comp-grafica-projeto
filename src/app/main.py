from utils.date_utils import get_date_prefix
from utils.naming_utils import get_app_window_title
from utils.hardware_utils import get_hardware_properties
from config import LARGURA_JANELA, ALTURA_JANELA
from cena import Cena, AJUDA_TECLAS
import sys
import glfw
import moderngl

def glfw_error(error_code: int, error_message: str) -> None:
    """
    Substitui o aviso padrão do `pyGLFW`: imprime código 
    e descrição de qualquer erro do `GLFW` em `stderr`.
    """
    print(f"{get_date_prefix()} GLFW [{error_code}]: {error_message}", file=sys.stderr)

def init_glfw() -> tuple:
    """
    Inicializa o GLFW, define o callback de erro, cria a janela e
    retorna o par (contexto moderngl, janela).
    """
    
    glfw.set_error_callback(glfw_error) 

    if not glfw.init():
        sys.exit(f"{get_date_prefix()} ERRO: glfw não inicializou!")

    # Restrições
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    # Para funcionar em MacOS, é necessário habilitar o forward compatibility
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    # Antialiasing (MSAA): 4 amostras por pixel, como no 06_senhor_coracao.py
    glfw.window_hint(glfw.SAMPLES, 4)
    # Janela quadrada e de tamanho fixo: o NDC vai de -1 a 1 nos dois eixos,
    # e só numa janela quadrada os círculos continuam redondos (ver config.py)
    glfw.window_hint(glfw.RESIZABLE, False)

    window = glfw.create_window(LARGURA_JANELA, ALTURA_JANELA, get_app_window_title(), None, None)
    if not window:
        glfw.terminate()
        sys.exit(f"{get_date_prefix()} ERRO: não foi possível criar a janela")

    # A ordem importa: o moderngl não cria contexto, ele adota o que estiver
    # ativo na thread (slides04, p.26)
    glfw.make_context_current(window)
    # Vsync: a troca de buffers acompanha a taxa de atualização do monitor
    glfw.swap_interval(1)
    ctx = moderngl.create_context()
    
    return ctx, window

def run_app(window, ctx):
    """
    Cria a cena e roda o laço principal até a janela ser fechada.
    """
    cena = Cena(ctx)
    # As teclas chegam por callback: o GLFW chama cena.tecla a cada evento
    # (inclusive o ESC, que agora é tratado lá)
    glfw.set_key_callback(window, cena.tecla)

    instante_anterior = glfw.get_time()
    while not glfw.window_should_close(window):
        # dt: segundos desde o quadro anterior (como no 07_triangulo_animado.py).
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

def main():
    """
    Função principal do programa.
    """
    ctx, window = init_glfw()
    
    print(f"{get_date_prefix()} Propriedades do driver/hardware:\n{get_hardware_properties(ctx)}")
    print(AJUDA_TECLAS)

    run_app(window, ctx)
    
    print("Execucao finalizada.")
    
if __name__ == "__main__":
    main()