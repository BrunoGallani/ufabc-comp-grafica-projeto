"""
Flores da primavera, na grama e na copa da árvore. Todas são a mesma malha (a flor
de cinco pétalas), com o círculo compartilhado de miolo.
"""
import moderngl
import numpy as np

from config import Y_CHAO, Estacao
from geometria import curva_flor
from objetos.objeto_cena import ObjetoCena

TAMANHO_FLOR = 0.026    # raio até a ponta das pétalas
ESCALA_MIOLO = 0.35     # proporcional ao tamanho da flor
COR_MIOLO = (1.00, 0.80, 0.15, 1.0)

CORES_GRAMA = [
    (0.96, 0.42, 0.62, 1.0),   # rosa
    (1.00, 1.00, 1.00, 1.0),   # branca
    (0.72, 0.52, 0.92, 1.0),   # lilás
    (0.92, 0.20, 0.22, 1.0),   # vermelha
]
N_FLORES_GRAMA = 14

# (dx, dy) a partir do topo do tronco, dentro da copa (ver COPA em arvore.py)
COR_FLOR_COPA = (1.00, 0.80, 0.88, 1.0)   # rosa-claro, tipo cerejeira
FLORES_COPA = [(-0.12, 0.03), (-0.05, -0.06), (0.03, 0.02), (0.11, -0.03),
               (0.13, 0.06), (-0.06, 0.12), (0.04, 0.17), (-0.01, 0.07)]


class Flores(ObjetoCena):
    """Na grama, sorteadas com semente fixa; na copa da `arvore`, em lugares fixos."""

    def __init__(self, r, arvore, semente=3):
        self.flor = r.criar_malha(curva_flor(), moderngl.TRIANGLE_FAN)
        self.circulo = r.circulo
        self.flores = []   # (x, y, cor)

        # Uma flor sorteada em cada faixa da largura, pra elas não se amontoarem.
        gerador = np.random.default_rng(semente)
        largura_faixa = 1.9 / N_FLORES_GRAMA
        for i in range(N_FLORES_GRAMA):
            x = -0.95 + (i + float(gerador.uniform(0.2, 0.8))) * largura_faixa
            y = float(gerador.uniform(-0.95, Y_CHAO - 0.05))
            self.flores.append((x, y, CORES_GRAMA[i % len(CORES_GRAMA)]))

        for dx, dy in FLORES_COPA:
            self.flores.append((arvore.x + dx, arvore.topo + dy, COR_FLOR_COPA))

    def desenhar(self, r, estado):
        if estado.estacao != Estacao.PRIMAVERA:
            return
        for x, y, cor in self.flores:
            r.desenhar(self.flor, TAMANHO_FLOR, (x, y), cor)
            r.desenhar(self.circulo, TAMANHO_FLOR * ESCALA_MIOLO, (x, y), COR_MIOLO)
