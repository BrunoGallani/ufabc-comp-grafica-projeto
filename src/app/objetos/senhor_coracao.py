"""
Sr. Coração: o corpo e dois olhos (branco + pupila). As setas mexem o olhar e
Shift + setas fazem ele andar. `posicao` e `tamanho` valem pro personagem inteiro.
"""
import math

import moderngl

from objetos.objeto_cena import ObjetoCena
from geometria import curva_coracao

MAGENTA = (0.85, 0.10, 0.45, 1.0)
BRANCO_OLHO = (1.0, 1.0, 1.0, 1.0)
PRETO = (0.05, 0.05, 0.05, 1.0)

# Medidas com tamanho 1.0
ESCALA_CORPO = 0.62
ESCALA_OLHO, ESCALA_PUPILA = 0.085, 0.040
CENTRO_OLHO = (0.17, 0.20)   # distância do meio e altura de cada olho

# Até onde a pupila sai do centro sem escapar do olho.
LIMITE_OLHAR = ESCALA_OLHO - ESCALA_PUPILA
PASSO_OLHAR = LIMITE_OLHAR / 2.0

PASSO_ANDAR = 0.03   # NDC por toque de Shift + seta


class SenhorCoracao(ObjetoCena):
    COR_CORPO = MAGENTA   # a Sra. Coração troca só isso

    def __init__(self, r, posicao=(0.0, 0.0), tamanho=1.0):
        self.coracao = r.criar_malha(curva_coracao(), moderngl.TRIANGLE_FAN)
        self.circulo = r.circulo

        self.posicao = list(posicao)   # centro do corpo na tela
        self.tamanho = tamanho

        self.olhar_x, self.olhar_y = 0.0, 0.0   # quanto as pupilas saem do centro dos olhos

    def olhar(self, dx, dy):
        self.olhar_x += dx * PASSO_OLHAR
        self.olhar_y += dy * PASSO_OLHAR
        # O olho é redondo, então o limite vale pro vetor, não pra cada eixo
        # (senão a pupila escapa na diagonal).
        distancia = math.hypot(self.olhar_x, self.olhar_y)
        if distancia > LIMITE_OLHAR:
            self.olhar_x *= LIMITE_OLHAR / distancia
            self.olhar_y *= LIMITE_OLHAR / distancia

    def andar(self, dx, dy):
        # A curva do coração cabe em [-1, 1], então na tela ela vai até
        # ESCALA_CORPO * tamanho do centro. Segurando o centro a essa distância da
        # borda, o corpo não sai da janela.
        limite = 1.0 - ESCALA_CORPO * self.tamanho
        self.posicao[0] = min(max(self.posicao[0] + dx * PASSO_ANDAR, -limite), limite)
        self.posicao[1] = min(max(self.posicao[1] + dy * PASSO_ANDAR, -limite), limite)

    def na_tela(self, x, y):
        """Leva um ponto do desenho base (centro em (0, 0), tamanho 1) pra tela."""
        return (self.posicao[0] + x * self.tamanho,
                self.posicao[1] + y * self.tamanho)

    def desenhar(self, r, estado):
        k = self.tamanho

        r.desenhar(self.coracao, ESCALA_CORPO * k, self.na_tela(0.0, 0.0), self.COR_CORPO)

        # Olhos e pupilas: o mesmo círculo quatro vezes, só mudando os uniforms.
        for lado in (-1.0, 1.0):
            centro = (lado * CENTRO_OLHO[0], CENTRO_OLHO[1])
            r.desenhar(self.circulo, ESCALA_OLHO * k, self.na_tela(*centro), BRANCO_OLHO)
            r.desenhar(self.circulo, ESCALA_PUPILA * k,
                       self.na_tela(centro[0] + self.olhar_x, centro[1] + self.olhar_y),
                       PRETO)
