"""
Casa: paredes, porta e janelas são retângulos com EBO; o telhado é uma malha só
desenhada duas vezes (TRIANGLES e depois LINE_LOOP pro contorno); o arco da porta
e a maçaneta são o círculo compartilhado; e o caixilho é uma cruz em LINES.
"""
import itertools

import moderngl

from config import Y_CHAO
from geometria import cruz, retangulo, triangulo
from objetos.objeto_cena import ObjetoCena

# (nome, cor), na ordem da tecla C
PALETA_PAREDE = [
    ("creme", (0.93, 0.87, 0.70, 1.0)),
    ("azul-claro", (0.55, 0.75, 0.95, 1.0)),
    ("verde-menta", (0.62, 0.85, 0.66, 1.0)),
    ("salmão", (0.96, 0.66, 0.56, 1.0)),
    ("lilás", (0.78, 0.68, 0.92, 1.0)),
]
COR_TELHADO = (0.80, 0.22, 0.18, 1.0)
COR_CONTORNO_TELHADO = (0.22, 0.04, 0.03, 1.0)
COR_PORTA = (0.45, 0.26, 0.12, 1.0)
COR_MACANETA = (0.95, 0.80, 0.25, 1.0)
COR_VIDRO_DIA = (0.72, 0.87, 0.97, 1.0)
COR_VIDRO_NOITE = (1.00, 0.88, 0.45, 1.0)
COR_CAIXILHO = (0.30, 0.18, 0.10, 1.0)

LARGURA_PAREDE, ALTURA_PAREDE = 0.50, 0.40
BASE_TELHADO, ALTURA_TELHADO = 0.62, 0.28
LARGURA_PORTA, ALTURA_PORTA = 0.12, 0.18
RAIO_MACANETA = 0.012
AFASTAMENTO_MACANETA = 0.035   # distância horizontal da maçaneta ao centro da porta
LADO_JANELA = 0.11
AFASTAMENTO_JANELA = 0.15      # do centro da casa até cada janela
ALTURA_CENTRO_JANELA = 0.27    # do chão até o centro das janelas


class Casa(ObjetoCena):
    """Casa apoiada no chão, centrada em `x`."""

    def __init__(self, r, x=-0.58):
        self.x = x
        self.paleta = itertools.cycle(PALETA_PAREDE)   # depois da última cor, volta pra primeira
        self.nome_cor, self.cor_parede = next(self.paleta)
        self.circulo = r.circulo

        # Cada proporção precisa da sua malha, já que a escala é uma só pros dois eixos.
        v, i = retangulo(LARGURA_PAREDE, ALTURA_PAREDE)
        self.parede = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
        v, i = retangulo(LARGURA_PORTA, ALTURA_PORTA)
        self.porta = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
        v, i = retangulo(LADO_JANELA, LADO_JANELA)
        self.janela = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
        self.telhado = r.criar_malha(triangulo(BASE_TELHADO, ALTURA_TELHADO),
                                     moderngl.TRIANGLES)
        self.caixilho = r.criar_malha(cruz(), moderngl.LINES)

    def proxima_cor(self):
        self.nome_cor, self.cor_parede = next(self.paleta)

    def desenhar(self, r, estado):
        x = self.x

        # Tudo nasce centrado na origem; pra apoiar no chão, sobe meia altura.
        r.desenhar(self.parede, 1.0, (x, Y_CHAO + ALTURA_PAREDE / 2), self.cor_parede)

        centro_telhado = (x, Y_CHAO + ALTURA_PAREDE + ALTURA_TELHADO / 2)
        r.desenhar(self.telhado, 1.0, centro_telhado, COR_TELHADO)
        r.desenhar(self.telhado, 1.0, centro_telhado, COR_CONTORNO_TELHADO,
                   primitiva=moderngl.LINE_LOOP)

        # Porta com um círculo em cima: a metade de baixo some na porta, que é da mesma cor.
        r.desenhar(self.porta, 1.0, (x, Y_CHAO + ALTURA_PORTA / 2), COR_PORTA)
        r.desenhar(self.circulo, LARGURA_PORTA / 2, (x, Y_CHAO + ALTURA_PORTA), COR_PORTA)
        macaneta = (x + AFASTAMENTO_MACANETA, Y_CHAO + ALTURA_PORTA / 2)
        r.desenhar(self.circulo, RAIO_MACANETA, macaneta, COR_MACANETA)

        for lado in (-1.0, 1.0):
            centro = (x + lado * AFASTAMENTO_JANELA, Y_CHAO + ALTURA_CENTRO_JANELA)
            if estado.noite:   # luz acesa: a noite não escurece a janela
                r.desenhar_emissivo(self.janela, 1.0, centro, COR_VIDRO_NOITE)
            else:
                r.desenhar(self.janela, 1.0, centro, COR_VIDRO_DIA)
            # a cruz vai de -1 a 1, então escala = meia janela
            r.desenhar(self.caixilho, LADO_JANELA / 2, centro, COR_CAIXILHO)
