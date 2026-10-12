"""
Chuva: muitas cópias de uma única malha, a gota.

É o reaproveitamento de geometria levado ao extremo. A gota (uma elipse alta
e fina) vai para a VRAM uma única vez e é desenhada `N_GOTAS` vezes por quadro,
cada vez com um `u_deslocamento` diferente. Cada gota é só um par `[x, y]`
guardado na CPU, numa lista.

Tecla R: liga/desliga a chuva (o `estado.chovendo`, controlado pela :class:`Cena`).
"""
import random

import moderngl

from config import Y_CHAO
from geometria import curva_elipse
from objetos.objeto_cena import ObjetoCena

N_GOTAS = 80
ESCALA_GOTA = 0.02            # tamanho de cada gota na tela
VELOCIDADE_QUEDA = 0.8        # em NDC por segundo
COR_GOTA = (0.35, 0.55, 1.00, 1.0)
TOPO = 1.0                    # y da borda de cima da janela


class Chuva(ObjetoCena):
    """
    Gotas que caem com velocidade constante e voltam ao topo ao atingir o chão.
    """

    def __init__(self, r):
        # Elipse 0.35 x 1.0: bem mais alta do que larga. Como u_escala é igual
        # nos dois eixos, essa proporção precisa estar nos próprios vértices.
        self.gota = r.criar_malha(curva_elipse(0.35, 1.0), moderngl.TRIANGLE_FAN)
        # Cada gota começa num ponto aleatório entre o chão e o topo: [x, y].
        self.gotas = [[random.uniform(-1.0, 1.0), random.uniform(Y_CHAO, TOPO)]
                      for _ in range(N_GOTAS)]

    def atualizar(self, dt, estado):
        """
        Faz cada gota descer `VELOCIDADE_QUEDA * dt`; a gota que passa do chão
        volta ao topo, numa posição horizontal sorteada.
        """
        if not estado.chovendo:
            return
        self.gotas = [
                    [x, y - (VELOCIDADE_QUEDA * dt)] if y > Y_CHAO else
                    [random.uniform(-1.0, 1.0), TOPO]
                    for x, y in self.gotas]

    def desenhar(self, r, estado):
        """
        Desenha todas as gotas com a mesma malha, só mudando o deslocamento.
        """
        if not estado.chovendo:
            return
        for x, y in self.gotas:
            r.desenhar(self.gota, ESCALA_GOTA, (x, y), COR_GOTA)
