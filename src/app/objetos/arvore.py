"""
Árvore da cena, formada por três partes:

- **Tronco:** retângulo desenhado com `TRIANGLES` + EBO;
- **Copa:** três círculos sobrepostos (a malha compartilhada, em `TRIANGLE_FAN`);
- **Galhos:** triângulos finos num único VBO (`TRIANGLES`), visíveis só no outono.

A aparência segue a estação da cena (tecla E):

- **Verão:** copa verde (o padrão);
- **Outono:** a árvore perde as folhas: no lugar da copa, aparecem os galhos;
- **Inverno:** a copa fica branca de neve;
- **Primavera:** copa verde, com as flores desenhadas por cima pela :class:`Flores`.
"""
import moderngl

from config import COR_NEVE, Y_CHAO, Estacao
from geometria import galhos, retangulo
from objetos.objeto_cena import ObjetoCena

COR_COPA = (0.16, 0.55, 0.20, 1.0)
COR_TRONCO = (0.42, 0.26, 0.13, 1.0)
LARGURA_TRONCO, ALTURA_TRONCO = 0.08, 0.30

# Círculos da copa: (deslocamento x, deslocamento y, raio), medidos a partir do
# topo do tronco. Três círculos sobrepostos formam uma copa "fofinha".
COPA = [(-0.07, 0.00, 0.12), (0.07, 0.00, 0.12), (0.00, 0.10, 0.13)]

# Galhos do outono: (base, ponta, meia largura na base), medidos a partir do
# topo do tronco. Os raminhos nascem no meio dos galhos principais.
GALHOS = [
    ((0.00, 0.00), (0.00, 0.24), 0.040),      # continuação do tronco (mesma largura)
    ((0.00, -0.02), (-0.17, 0.14), 0.024),    # galho esquerdo
    ((0.00, 0.03), (0.16, 0.18), 0.022),      # galho direito
    ((-0.09, 0.06), (-0.10, 0.21), 0.010),    # raminho do galho esquerdo
    ((0.08, 0.10), (0.20, 0.08), 0.010),      # raminho do galho direito
    ((0.00, 0.12), (0.07, 0.25), 0.010),      # raminho do topo
    ((0.00, 0.10), (-0.06, 0.22), 0.009),     # outro raminho do topo
]


class Arvore(ObjetoCena):
    """
    Árvore apoiada no chão, na posição horizontal `x`.
    """

    def __init__(self, r, x=0.78):
        self.x = x
        self.topo = Y_CHAO + ALTURA_TRONCO   # topo do tronco: onde nascem a copa e os galhos
        self.circulo = r.circulo
        v, i = retangulo(LARGURA_TRONCO, ALTURA_TRONCO)
        self.tronco = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
        self.galhos = r.criar_malha(galhos(GALHOS), moderngl.TRIANGLES)

    def desenhar(self, r, estado):
        """
        Desenha o tronco e, por cima, a copa (ou, no outono, só os galhos).
        """
        r.desenhar(self.tronco, 1.0, (self.x, Y_CHAO + ALTURA_TRONCO / 2), COR_TRONCO)

        if estado.estacao == Estacao.OUTONO:
            # Sem folhas: os galhos, da cor do tronco, numa única chamada.
            r.desenhar(self.galhos, 1.0, (self.x, self.topo), COR_TRONCO)
            return

        cor_copa = COR_NEVE if estado.estacao == Estacao.INVERNO else COR_COPA
        for dx, dy, raio in COPA:
            # O círculo tem raio 1; com u_escala = raio, ele fica do tamanho certo.
            r.desenhar(self.circulo, raio, (self.x + dx, self.topo + dy), cor_copa)
