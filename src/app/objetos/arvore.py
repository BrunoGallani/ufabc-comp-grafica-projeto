"""
Árvore: tronco, copa de três círculos e, no outono, só os galhos. No inverno a
copa fica branca; na primavera as flores vêm por cima (classe Flores).
"""
import moderngl

from config import COR_NEVE, Y_CHAO, Estacao
from geometria import galhos, retangulo
from objetos.objeto_cena import ObjetoCena

COR_COPA = (0.16, 0.55, 0.20, 1.0)
COR_TRONCO = (0.42, 0.26, 0.13, 1.0)
LARGURA_TRONCO, ALTURA_TRONCO = 0.08, 0.30

# (dx, dy, raio) a partir do topo do tronco
COPA = [(-0.07, 0.00, 0.12), (0.07, 0.00, 0.12), (0.00, 0.10, 0.13)]

# (base, ponta, meia largura na base) a partir do topo do tronco
GALHOS = [
    ((0.00, 0.00), (0.00, 0.24), 0.040),
    ((0.00, -0.02), (-0.17, 0.14), 0.024),
    ((0.00, 0.03), (0.16, 0.18), 0.022),
    ((-0.09, 0.06), (-0.10, 0.21), 0.010),
    ((0.08, 0.10), (0.20, 0.08), 0.010),
    ((0.00, 0.12), (0.07, 0.25), 0.010),
    ((0.00, 0.10), (-0.06, 0.22), 0.009),
]


class Arvore(ObjetoCena):
    def __init__(self, r, x=0.78):
        self.x = x
        self.topo = Y_CHAO + ALTURA_TRONCO   # de onde saem a copa e os galhos
        self.circulo = r.circulo
        v, i = retangulo(LARGURA_TRONCO, ALTURA_TRONCO)
        self.tronco = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
        self.galhos = r.criar_malha(galhos(GALHOS), moderngl.TRIANGLES)

    def desenhar(self, r, estado):
        r.desenhar(self.tronco, 1.0, (self.x, Y_CHAO + ALTURA_TRONCO / 2), COR_TRONCO)

        if estado.estacao == Estacao.OUTONO:
            r.desenhar(self.galhos, 1.0, (self.x, self.topo), COR_TRONCO)
            return

        cor_copa = COR_NEVE if estado.estacao == Estacao.INVERNO else COR_COPA
        for dx, dy, raio in COPA:
            # o círculo tem raio 1, então a escala já é o raio
            r.desenhar(self.circulo, raio, (self.x + dx, self.topo + dy), cor_copa)
