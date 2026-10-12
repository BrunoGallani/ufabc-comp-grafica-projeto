"""
Árvore: tronco (retângulo, TRIANGLES + EBO) e copa (três círculos sobrepostos,
o círculo compartilhado em TRIANGLE_FAN).

Tecla A: troca a estação do ano, ou seja, a cor da copa.
"""
import moderngl

from config import Y_CHAO
from geometria import retangulo
from objetos.objeto_cena import ObjetoCena

# (nome, cor da copa) para cada estação, na ordem em que a tecla A as percorre.
ESTACOES = [
    ("verão", (0.16, 0.55, 0.20, 1.0)),
    ("outono", (0.88, 0.47, 0.12, 1.0)),
    ("inverno", (0.90, 0.94, 0.97, 1.0)),     # copa coberta de neve
    ("primavera", (0.96, 0.62, 0.78, 1.0)),   # flores de cerejeira
]
COR_TRONCO = (0.42, 0.26, 0.13, 1.0)
LARGURA_TRONCO, ALTURA_TRONCO = 0.08, 0.30

# Círculos da copa: (deslocamento x, deslocamento y, raio), medidos a partir do
# topo do tronco. Três círculos sobrepostos formam uma copa "fofinha".
COPA = [(-0.07, 0.00, 0.12), (0.07, 0.00, 0.12), (0.00, 0.10, 0.13)]


class Arvore(ObjetoCena):
    def __init__(self, r, x=0.78):
        self.x = x
        self.indice_estacao = 0
        self.circulo = r.circulo
        v, i = retangulo(LARGURA_TRONCO, ALTURA_TRONCO)
        self.tronco = r.criar_malha(v, moderngl.TRIANGLES, indices=i)

    def proxima_estacao(self):
        """Tecla A: avança para a próxima estação e devolve o nome dela."""
        self.indice_estacao = (self.indice_estacao + 1) % len(ESTACOES)
        return ESTACOES[self.indice_estacao][0]

    def desenhar(self, r, estado):
        r.desenhar(self.tronco, 1.0, (self.x, Y_CHAO + ALTURA_TRONCO / 2), COR_TRONCO)

        topo = Y_CHAO + ALTURA_TRONCO
        cor_copa = ESTACOES[self.indice_estacao][1]
        for dx, dy, raio in COPA:
            # O círculo tem raio 1; com u_escala = raio, ele fica do tamanho certo.
            r.desenhar(self.circulo, raio, (self.x + dx, topo + dy), cor_copa)
