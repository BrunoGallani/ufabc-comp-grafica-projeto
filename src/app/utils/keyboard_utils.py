from enum import IntEnum
import glfw

AJUDA_TECLAS = """Teclas disponíveis:
Setas ............ o Sr. Coração olha
Shift + setas .... o Sr. Coração anda
K ................ exibe no terminal o tutorial com as teclas de controle
H ................ exibe informações do hardware
I ................ mostra / esconde o painel com o estado da cena
D ................ dia / noite
R ................ liga / desliga a chuva
C ................ troca a cor da casa
E ................ troca a estação do ano (verão, outono, inverno, primavera)
F ................ liga / desliga a tela cheia
P ................ salva uma captura de tela em capturas/
ESC .............. encerra o programa"""

class Key(IntEnum):
    """
    Mapeia as teclas para constantes.
    """
    SETA_CIMA = glfw.KEY_UP
    SETA_BAIXO = glfw.KEY_DOWN
    SETA_DIREITA = glfw.KEY_RIGHT
    SETA_ESQUERDA = glfw.KEY_LEFT
    K = glfw.KEY_K
    H = glfw.KEY_H
    I = glfw.KEY_I
    D = glfw.KEY_D
    R = glfw.KEY_R
    C = glfw.KEY_C
    E = glfw.KEY_E
    F = glfw.KEY_F
    P = glfw.KEY_P
    ESC = glfw.KEY_ESCAPE

# Direção (dx, dy) de cada seta: para onde o Sr. Coração olha ou anda.
SETAS = {
    Key.SETA_CIMA: (0.0, 1.0),
    Key.SETA_BAIXO: (0.0, -1.0),
    Key.SETA_DIREITA: (1.0, 0.0),
    Key.SETA_ESQUERDA: (-1.0, 0.0),
}
