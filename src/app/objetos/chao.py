"""
Chão: a faixa de grama na parte de baixo da tela.

É um único retângulo (`TRIANGLES` + EBO) que vai da borda de baixo da janela
(`y = -1`) até `Y_CHAO`, ocupando toda a largura (`x` de -1 a 1).
"""
import moderngl

from config import Y_CHAO
from geometria import retangulo
from objetos.objeto_cena import ObjetoCena

COR_GRAMA = (0.30, 0.66, 0.26, 1.0)


class Chao(ObjetoCena):
    """
    Faixa de grama, com as medidas já no tamanho final (escala 1.0).
    """

    def __init__(self, r):
        altura = Y_CHAO - (-1.0)               # da base da janela até o topo da grama
        vertices, indices = retangulo(2.0, altura)
        self.grama = r.criar_malha(vertices, moderngl.TRIANGLES, indices=indices)
        # O retângulo nasce centrado na origem; seu centro na tela fica no meio
        # da faixa entre y = -1 e y = Y_CHAO.
        self.centro = (0.0, (-1.0 + Y_CHAO) / 2.0)

    def desenhar(self, r, estado):
        """
        Desenha a faixa de grama.
        """
        r.desenhar(self.grama, 1.0, self.centro, COR_GRAMA)
