"""
Chuva: muitas cópias de UMA única malha, a gota.

É o reaproveitamento de geometria levado ao extremo. A gota (uma elipse alta
e fina) vai para a VRAM uma única vez e é desenhada N_GOTAS vezes por quadro,
cada vez com um u_deslocamento diferente. Cada gota é só um par [x, y]
guardado na CPU, numa lista.

Tecla R: liga/desliga a chuva (o estado.chovendo, controlado pela Cena).
"""
import random

import moderngl

from config import Y_CHAO
from geometria import curva_elipse
from objetos.objeto_cena import ObjetoCena

N_GOTAS = 80
ESCALA_GOTA = 0.02            # tamanho de cada gota na tela
VELOCIDADE_QUEDA = 1.3        # em NDC por SEGUNDO (como no 07_triangulo_animado.py)
COR_GOTA = (0.35, 0.55, 1.00, 1.0)
TOPO = 1.0                    # y da borda de cima da janela


class Chuva(ObjetoCena):
    def __init__(self, r):
        # Elipse 0.35 x 1.0: bem mais alta do que larga. Como u_escala é igual
        # nos dois eixos, essa proporção precisa estar nos próprios vértices.
        self.gota = r.criar_malha(curva_elipse(0.35, 1.0), moderngl.TRIANGLE_FAN)
        # Cada gota começa num ponto aleatório entre o chão e o topo: [x, y].
        self.gotas = [[random.uniform(-1.0, 1.0), random.uniform(Y_CHAO, TOPO)]
                      for _ in range(N_GOTAS)]

    def atualizar(self, dt, estado):
        """Faz a chuva cair. A Cena chama este método uma vez por quadro."""
        if not estado.chovendo:
            return
        # TODO(human): faça cada gota de self.gotas descer VELOCIDADE_QUEDA * dt
        # e, quando ela passar do chão (Y_CHAO), mande-a de volta para o alto.

    def desenhar(self, r, estado):
        if not estado.chovendo:
            return
        for x, y in self.gotas:
            r.desenhar(self.gota, ESCALA_GOTA, (x, y), COR_GOTA)
