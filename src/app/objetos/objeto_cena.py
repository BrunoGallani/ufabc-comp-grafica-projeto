"""
Classe base de tudo o que aparece na cena.

Todo objeto da cena sabe fazer duas coisas, e a Cena chama as duas a cada quadro:

- atualizar(dt, estado): muda o próprio objeto com o passar do tempo (animação).
  dt é o tempo, em segundos, desde o quadro anterior.
- desenhar(r, estado): pede ao Renderizador r que desenhe as suas partes.

estado é o EstadoCena (cena.py): é noite? está chovendo? quanto tempo passou?
qual é a cor do céu? Assim cada objeto decide sozinho como aparecer em cada
situação, e a Cena não precisa conhecer os detalhes de nenhum deles: ela só
chama atualizar() e desenhar() de todos, do mesmo jeito (polimorfismo).
"""


class ObjetoCena:
    def atualizar(self, dt, estado):
        """Por padrão, nada muda com o tempo (objeto parado).
        Objetos animados (nuvem, chuva...) sobrescrevem este método."""

    def desenhar(self, r, estado):
        """Cada objeto TEM de dizer como se desenha."""
        raise NotImplementedError("cada objeto precisa implementar desenhar()")
