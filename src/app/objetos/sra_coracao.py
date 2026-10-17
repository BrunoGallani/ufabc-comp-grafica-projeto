"""
Sra. Coração: um exemplo de herança.

A :class:`SraCoracao` "é um" :class:`SenhorCoracao`: herda a geometria, os olhos,
o desenho e o `andar()`. Só três coisas mudam:

- **Cor do corpo:** o atributo de classe `COR_CORPO` é sobrescrito;
- **Olhar:** em vez de obedecer às setas, ela sempre olha para o Sr. Coração.
  Para isso, guarda uma referência a ele (o alvo) e, a cada quadro, calcula a
  direção até ele;
- **Laço:** um acessório que o Sr. não tem. O `__init__` cria a malha do laço, e
  o `desenhar()` faz o desenho herdado (`super().desenhar`) e, por cima, o laço.

Nada no `senhor_coracao.py` precisou mudar para esta classe existir.
"""
import math

import moderngl

from geometria import laco
from objetos.senhor_coracao import LIMITE_OLHAR, SenhorCoracao

VERMELHO = (0.90, 0.15, 0.25, 1.0)
COR_LACO = (1.00, 0.82, 0.25, 1.0)
COR_NO_LACO = (0.85, 0.65, 0.15, 1.0)   # o nó, um pouco mais escuro que as asas

ESCALA_LACO = 0.13           # meia largura do laço (a malha vai de -1 a 1)
ESCALA_NO_LACO = 0.04        # raio do nó (o círculo compartilhado)
CENTRO_LACO = (-0.27, 0.50)  # em cima do lóbulo esquerdo, longe dos olhos


class SraCoracao(SenhorCoracao):
    """
    A Sra. Coração, que acompanha com o olhar o objeto `alvo` e usa um laço.
    """
    COR_CORPO = VERMELHO   # sobrescreve a cor herdada (MAGENTA)

    def __init__(self, r, alvo, posicao=(0.0, 0.0), tamanho=1.0):
        super().__init__(r, posicao, tamanho)   # monta tudo como um Sr. Coração
        self.alvo = alvo                        # o objeto para o qual ela olha
        # As asas do laço: TRIANGLES com EBO (o nó usa o círculo compartilhado).
        vertices, indices = laco()
        self.laco = r.criar_malha(vertices, moderngl.TRIANGLES, indices=indices)

    def atualizar(self, dt, estado):
        """
        Aponta as pupilas para o centro do alvo, até onde o olho permite.
        """
        dx = self.alvo.posicao[0] - self.posicao[0]
        dy = self.alvo.posicao[1] - self.posicao[1]
        distancia = math.hypot(dx, dy)
        if distancia > 0.0:
            # (dx, dy) / distancia é um vetor de comprimento 1 que aponta para
            # o alvo. Multiplicado por LIMITE_OLHAR, leva a pupila até a borda
            # do olho, naquela direção (o mesmo limite usado pelas setas).
            self.olhar_x = dx / distancia * LIMITE_OLHAR
            self.olhar_y = dy / distancia * LIMITE_OLHAR

    def desenhar(self, r, estado):
        """
        Desenha tudo como um Sr. Coração e, por cima, o laço: as asas e o nó.
        """
        super().desenhar(r, estado)

        k = self.tamanho
        centro = self.na_tela(*CENTRO_LACO)
        r.desenhar(self.laco, ESCALA_LACO * k, centro, COR_LACO)
        r.desenhar(self.circulo, ESCALA_NO_LACO * k, centro, COR_NO_LACO)
