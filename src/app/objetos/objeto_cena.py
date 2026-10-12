"""
Classe base de tudo o que aparece na cena.
"""


class ObjetoCena:
    """
    Interface comum dos objetos da cena.

    A :class:`Cena` chama dois métodos de cada objeto, a cada quadro:

    - :meth:`atualizar`: muda o objeto com o passar do tempo (animação);
    - :meth:`desenhar`: pede ao :class:`Renderizador` que desenhe as partes do objeto.

    Ambos recebem o :class:`EstadoCena` (é noite? está chovendo? quanto tempo
    passou? qual é a cor do céu?). Assim, cada objeto decide sozinho como aparecer,
    e a cena trata todos do mesmo jeito (polimorfismo).
    """

    def atualizar(self, dt, estado):
        """
        Atualiza o objeto, sendo `dt` o tempo, em segundos, desde o quadro anterior.

        Por padrão, nada muda (objeto parado). Objetos animados sobrescrevem este método.
        """

    def desenhar(self, r, estado):
        """
        Desenha o objeto usando o renderizador `r`. Todo objeto deve implementar este método.
        """
        raise NotImplementedError("cada objeto precisa implementar desenhar()")
