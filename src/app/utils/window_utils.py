import glfw

from config import ALTURA_JANELA, LARGURA_JANELA

def toggle_fullscreen(window: 'glfw._GLFWwindowPointerT') -> bool:
    """
    Alterna a janela entre o modo janela e a tela cheia, no monitor principal.

    Retorna `True` se a janela ficou em tela cheia. Ao voltar ao modo janela, ela
    recupera o tamanho original e fica centralizada no monitor.

    Quem ajusta o desenho ao novo tamanho é o callback de framebuffer
    (:meth:`Cena.redimensionar`), chamado pelo GLFW logo depois da troca.
    """
    monitor = glfw.get_primary_monitor()
    modo = glfw.get_video_mode(monitor)
    largura_monitor, altura_monitor = modo.size

    if glfw.get_window_monitor(window):   # já está em tela cheia: volta à janela
        x = (largura_monitor - LARGURA_JANELA) // 2
        y = (altura_monitor - ALTURA_JANELA) // 2
        glfw.set_window_monitor(window, None, x, y, LARGURA_JANELA, ALTURA_JANELA, 0)
        return False

    # Com a resolução e a taxa de atualização atuais do monitor, o GLFW não
    # precisa trocar o modo de vídeo, e a tela não "pisca" ao entrar.
    glfw.set_window_monitor(window, monitor, 0, 0, largura_monitor, altura_monitor,
                            modo.refresh_rate)
    return True
