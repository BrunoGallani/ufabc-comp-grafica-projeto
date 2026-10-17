"""
Flores da primavera, espalhadas pela grama e pela copa da árvore.

Todas as flores são cópias de uma única malha, a flor de cinco pétalas
(`TRIANGLE_FAN`), como as gotas da :class:`Chuva`: a malha vai para a VRAM uma
única vez, e cada flor é só uma posição e uma cor. O miolo é o círculo
compartilhado. Fora da primavera, nada é desenhado.
"""
import moderngl
import numpy as np

from config import Y_CHAO, Estacao
from geometria import curva_flor
from objetos.objeto_cena import ObjetoCena

TAMANHO_FLOR = 0.026    # raio da flor, até a ponta das pétalas
ESCALA_MIOLO = 0.35     # raio do miolo, em proporção ao tamanho da flor
COR_MIOLO = (1.00, 0.80, 0.15, 1.0)

# Cores das flores da grama, usadas em sequência.
CORES_GRAMA = [
    (0.96, 0.42, 0.62, 1.0),   # rosa
    (1.00, 1.00, 1.00, 1.0),   # branca (margarida)
    (0.72, 0.52, 0.92, 1.0),   # lilás
    (0.92, 0.20, 0.22, 1.0),   # vermelha
]
N_FLORES_GRAMA = 14

# Flores da copa: (deslocamento x, deslocamento y) a partir do topo do tronco,
# todas dentro dos círculos da copa (veja COPA em arvore.py).
COR_FLOR_COPA = (1.00, 0.80, 0.88, 1.0)   # rosa-claro, como flor de cerejeira
FLORES_COPA = [(-0.12, 0.03), (-0.05, -0.06), (0.03, 0.02), (0.11, -0.03),
               (0.13, 0.06), (-0.06, 0.12), (0.04, 0.17), (-0.01, 0.07)]


class Flores(ObjetoCena):
    """
    Flores na grama, em posições sorteadas uma única vez a partir de uma
    `semente` fixa, e na copa da `arvore`, em posições fixas.
    """

    def __init__(self, r, arvore, semente=3):
        self.flor = r.criar_malha(curva_flor(), moderngl.TRIANGLE_FAN)
        self.circulo = r.circulo
        self.flores = []   # cada flor: (x, y, cor)

        # Na grama: a largura da tela é dividida em faixas iguais, com uma flor
        # sorteada dentro de cada faixa. Assim elas não se amontoam num canto.
        gerador = np.random.default_rng(semente)
        largura_faixa = 1.9 / N_FLORES_GRAMA
        for i in range(N_FLORES_GRAMA):
            x = -0.95 + (i + float(gerador.uniform(0.2, 0.8))) * largura_faixa
            y = float(gerador.uniform(-0.95, Y_CHAO - 0.05))
            self.flores.append((x, y, CORES_GRAMA[i % len(CORES_GRAMA)]))

        # Na copa: as posições acompanham o lugar da árvore.
        for dx, dy in FLORES_COPA:
            self.flores.append((arvore.x + dx, arvore.topo + dy, COR_FLOR_COPA))

    def desenhar(self, r, estado):
        """
        Desenha as pétalas e, por cima, o miolo de cada flor. Fora da
        primavera, não desenha nada.
        """
        if estado.estacao != Estacao.PRIMAVERA:
            return
        for x, y, cor in self.flores:
            r.desenhar(self.flor, TAMANHO_FLOR, (x, y), cor)
            r.desenhar(self.circulo, TAMANHO_FLOR * ESCALA_MIOLO, (x, y), COR_MIOLO)
