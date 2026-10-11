"""
Janela, contexto OpenGL e limpeza do buffer de cor.
MCCC007-23 - Computação Gráfica - UFABC
Prof. João Paulo Gois

Executar: python 01_janela.py      Sair: ESC ou fechar a janela
"""
from utils.date_utils import get_date_prefix
from utils.naming_utils import get_app_window_title
from utils.hardware_utils import get_hardware_properties
import sys
import glfw
import moderngl

def glfw_error(error_code: int, error_message: str) -> None:
    """
    Substitui o aviso padrão do `pyGLFW`: imprime código 
    e descrição de qualquer erro do `GLFW` em `stderr`.
    """
    print(f"{get_date_prefix()} GLFW [{error_code}]: {error_message}", file=sys.stderr)

glfw.set_error_callback(glfw_error) 

if not glfw.init():
    sys.exit(f"{get_date_prefix()} ERRO: glfw não inicializou!")

# Restrições
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
# Para funcionar em MacOS, é necessário habilitar o forward compatibility
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)

window = glfw.create_window(800, 600, f"{get_app_window_title()}", None, None)
if not window:
    glfw.terminate()
    sys.exit(f"{get_date_prefix()} ERRO: não foi possível criar a janela")

glfw.make_context_current(window)
ctx = moderngl.create_context()

print(f"{get_date_prefix()} Propriedades do driver/hardware:\n{get_hardware_properties(ctx)}")
print(f"{get_date_prefix()} ESC ou feche a janela para sair.")

while not glfw.window_should_close(window):
    if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    ctx.clear(1.0, 1.0, 1.0, 1.0)
    glfw.swap_buffers(window)
    glfw.poll_events()

glfw.terminate()
print("Execucao finalizada.")
