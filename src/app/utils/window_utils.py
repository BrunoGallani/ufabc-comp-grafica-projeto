"""
Tela cheia (tecla F).
"""
import glfw

from config import ALTURA_JANELA, LARGURA_JANELA

def toggle_fullscreen(window: 'glfw._GLFWwindowPointerT') -> bool:
    """
    Alterna entre janela e tela cheia (no monitor principal) e diz se ficou em tela
    cheia. Quem ajusta o desenho ao novo tamanho é o callback Cena.redimensionar.
    """
    monitor = glfw.get_primary_monitor()
    modo = glfw.get_video_mode(monitor)
    largura_monitor, altura_monitor = modo.size

    if glfw.get_window_monitor(window):   # já está em tela cheia: volta pra janela, centralizada
        x = (largura_monitor - LARGURA_JANELA) // 2
        y = (altura_monitor - ALTURA_JANELA) // 2
        glfw.set_window_monitor(window, None, x, y, LARGURA_JANELA, ALTURA_JANELA, 0)
        return False

    # Usando a resolução e a taxa do monitor, o GLFW não troca o modo de vídeo e a
    # tela não pisca ao entrar.
    glfw.set_window_monitor(window, monitor, 0, 0, largura_monitor, altura_monitor,
                            modo.refresh_rate)
    return True
