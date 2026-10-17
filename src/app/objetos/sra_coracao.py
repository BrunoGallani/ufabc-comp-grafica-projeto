"""
Sra. Coração: herda tudo do Sr. Coração e só muda três coisas: a cor, o olhar
(sempre pra ele) e um laço por cima. O senhor_coracao.py não precisou mudar nada.
"""
import math

import moderngl

from geometria import laco
from objetos.senhor_coracao import LIMITE_OLHAR, SenhorCoracao

VERMELHO = (0.90, 0.15, 0.25, 1.0)
COR_LACO = (1.00, 0.82, 0.25, 1.0)
COR_NO_LACO = (0.85, 0.65, 0.15, 1.0)   # o nó, um pouco mais escuro

ESCALA_LACO = 0.13           # meia largura do laço (a malha vai de -1 a 1)
ESCALA_NO_LACO = 0.04
CENTRO_LACO = (-0.27, 0.50)  # em cima do lóbulo esquerdo, longe dos olhos


class SraCoracao(SenhorCoracao):
    COR_CORPO = VERMELHO

    def __init__(self, r, alvo, posicao=(0.0, 0.0), tamanho=1.0):
        super().__init__(r, posicao, tamanho)
        self.alvo = alvo
        vertices, indices = laco()
        self.laco = r.criar_malha(vertices, moderngl.TRIANGLES, indices=indices)

    def atualizar(self, dt, estado):
        dx = self.alvo.posicao[0] - self.posicao[0]
        dy = self.alvo.posicao[1] - self.posicao[1]
        distancia = math.hypot(dx, dy)
        if distancia > 0.0:
            # vetor unitário até o alvo, esticado até a borda do olho
            self.olhar_x = dx / distancia * LIMITE_OLHAR
            self.olhar_y = dy / distancia * LIMITE_OLHAR

    def desenhar(self, r, estado):
        super().desenhar(r, estado)

        k = self.tamanho
        centro = self.na_tela(*CENTRO_LACO)
        r.desenhar(self.laco, ESCALA_LACO * k, centro, COR_LACO)
        r.desenhar(self.circulo, ESCALA_NO_LACO * k, centro, COR_NO_LACO)
