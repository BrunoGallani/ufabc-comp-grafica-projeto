"""Classe base de tudo que aparece na cena."""


class ObjetoCena:
    """
    A Cena chama atualizar() e desenhar() de todo objeto a cada quadro, sem saber o
    tipo de cada um (polimorfismo). Cada objeto olha o estado e decide como aparecer.
    """

    def atualizar(self, dt, estado):
        """Anima o objeto; `dt` é o tempo desde o último quadro. Por padrão, fica parado."""

    def desenhar(self, r, estado):
        raise NotImplementedError("cada objeto precisa implementar desenhar()")
