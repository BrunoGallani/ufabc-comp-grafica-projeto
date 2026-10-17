"""Chão: uma faixa de grama de y = -1 até Y_CHAO, na largura toda. No inverno, neve."""
import moderngl

from config import COR_NEVE, Y_CHAO, Estacao
from geometria import retangulo
from objetos.objeto_cena import ObjetoCena

COR_GRAMA = (0.30, 0.66, 0.26, 1.0)


class Chao(ObjetoCena):
    def __init__(self, r):
        altura = Y_CHAO - (-1.0)
        vertices, indices = retangulo(2.0, altura)
        self.grama = r.criar_malha(vertices, moderngl.TRIANGLES, indices=indices)
        self.centro = (0.0, (-1.0 + Y_CHAO) / 2.0)   # meio da faixa

    def desenhar(self, r, estado):
        cor = COR_NEVE if estado.estacao == Estacao.INVERNO else COR_GRAMA
        r.desenhar(self.grama, 1.0, self.centro, cor)
