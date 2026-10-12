"""
Sra. Coração: um exemplo de herança.

A :class:`SraCoracao` "é um" :class:`SenhorCoracao`: herda a geometria, os olhos,
o desenho e o `andar()`. Só duas coisas mudam:

- **Cor do corpo:** o atributo de classe `COR_CORPO` é sobrescrito;
- **Olhar:** em vez de obedecer às setas, ela sempre olha para o Sr. Coração.
  Para isso, guarda uma referência a ele (o alvo) e, a cada quadro, calcula a
  direção até ele.

Nada no `senhor_coracao.py` precisou mudar para esta classe existir.
"""
from objetos.senhor_coracao import LIMITE_OLHAR, SenhorCoracao

VERMELHO = (0.90, 0.15, 0.25, 1.0)


class SraCoracao(SenhorCoracao):
    """
    A Sra. Coração, que acompanha com o olhar o objeto `alvo`.
    """
    COR_CORPO = VERMELHO   # sobrescreve a cor herdada (MAGENTA)

    def __init__(self, r, alvo, posicao=(0.0, 0.0), tamanho=1.0):
        super().__init__(r, posicao, tamanho)   # monta tudo como um Sr. Coração
        self.alvo = alvo                        # o objeto para o qual ela olha

    def atualizar(self, dt, estado):
        """
        Aponta as pupilas para o centro do alvo, até onde o olho permite.
        """
        dx = self.alvo.posicao[0] - self.posicao[0]
        dy = self.alvo.posicao[1] - self.posicao[1]
        distancia = (dx ** 2 + dy ** 2) ** 0.5
        if distancia > 0.0:
            # (dx, dy) / distancia é um vetor de comprimento 1 que aponta para
            # o alvo. Multiplicado por LIMITE_OLHAR, leva a pupila até a borda
            # do olho, naquela direção (o mesmo limite usado pelas setas).
            self.olhar_x = dx / distancia * LIMITE_OLHAR
            self.olhar_y = dy / distancia * LIMITE_OLHAR
