"""
Astros do céu. Possui as seguintes classes:

- :class:`Sol`: visível de dia;
- :class:`Lua`: visível à noite, em fase crescente;
- :class:`Estrelas`: visíveis à noite, cintilando.

Os três usam o círculo compartilhado e decidem sozinhos, olhando o estado da
cena, se devem aparecer ou não: a :class:`Cena` desenha todos, sempre.
"""
import math

import moderngl
import numpy as np

from geometria import raios_do_sol
from objetos.objeto_cena import ObjetoCena

# O sol e a lua ocupam o mesmo lugar do céu (canto superior direito).
CENTRO_ASTRO = (0.62, 0.66)


class Sol(ObjetoCena):
    """
    Sol com disco e raios; os raios "respiram" com o passar do tempo.
    """
    RAIO = 0.11
    COR_DISCO = (1.00, 0.84, 0.20, 1.0)
    COR_RAIOS = (1.00, 0.55, 0.10, 1.0)

    def __init__(self, r):
        self.disco = r.circulo
        # Os 12 raios num único VBO, desenhados com uma só chamada TRIANGLES.
        self.raios = r.criar_malha(raios_do_sol(), moderngl.TRIANGLES)

    def desenhar(self, r, estado):
        """
        Desenha os raios e, por cima, o disco. À noite, não desenha nada.
        """
        if estado.noite:
            return
        # A escala dos raios oscila 6% para cima e para baixo, seguindo um seno
        # do tempo (meio ciclo por segundo). Só um uniform muda.
        pulso = 1.0 + 0.06 * math.sin(2.0 * math.pi * 0.5 * estado.tempo)
        r.desenhar(self.raios, self.RAIO * pulso, CENTRO_ASTRO, self.COR_RAIOS)
        r.desenhar(self.disco, self.RAIO, CENTRO_ASTRO, self.COR_DISCO)   # por cima


class Lua(ObjetoCena):
    """
    Lua crescente, feita com dois círculos pelo algoritmo do pintor.
    """
    RAIO = 0.10
    COR = (0.96, 0.95, 0.82, 1.0)
    DESLOCAMENTO_SOMBRA = (-0.045, 0.030)   # onde fica o círculo que "morde" a lua

    def __init__(self, r):
        self.disco = r.circulo

    def desenhar(self, r, estado):
        """
        Desenha a lua cheia e, por cima, um círculo da cor do céu um pouco
        deslocado: o que sobra visível é a "fatia" iluminada. De dia, não
        desenha nada.
        """
        if not estado.noite:
            return
        # Os dois desenhos são emissivos: a lua tem luz própria, e a "sombra"
        # precisa ter exatamente a cor do fundo. Se fosse atenuada, ficaria mais
        # escura que o céu e apareceria como uma mancha.
        r.desenhar_emissivo(self.disco, self.RAIO, CENTRO_ASTRO, self.COR)
        centro_sombra = (CENTRO_ASTRO[0] + self.DESLOCAMENTO_SOMBRA[0],
                         CENTRO_ASTRO[1] + self.DESLOCAMENTO_SOMBRA[1])
        r.desenhar_emissivo(self.disco, self.RAIO * 0.92, centro_sombra, estado.cor_do_ceu)


class Estrelas(ObjetoCena):
    """
    Estrelas em posições sorteadas uma única vez, a partir de uma `semente` fixa:
    o céu fica igual toda vez que o programa abre.
    """
    QUANTIDADE = 22
    COR = (1.00, 1.00, 0.92, 1.0)

    def __init__(self, r, semente=7):
        self.disco = r.circulo
        gerador = np.random.default_rng(semente)
        self.estrelas = []   # cada estrela: (x, y, raio, fase do brilho)
        while len(self.estrelas) < self.QUANTIDADE:
            x = float(gerador.uniform(-0.95, 0.95))
            y = float(gerador.uniform(0.05, 0.95))
            if math.dist((x, y), CENTRO_ASTRO) < 0.22:
                continue   # nenhuma estrela "atrás" da lua
            raio = float(gerador.uniform(0.005, 0.010))
            fase = float(gerador.uniform(0.0, 2.0 * math.pi))
            self.estrelas.append((x, y, raio, fase))

    def desenhar(self, r, estado):
        """
        Desenha as estrelas à noite, como objetos emissivos. De dia, não desenha nada.
        """
        if not estado.noite:
            return
        for x, y, raio, fase in self.estrelas:
            # Cintilar: o tamanho varia com um seno do tempo. A fase sorteada
            # faz cada estrela piscar num momento diferente.
            brilho = 0.75 + 0.25 * math.sin(3.0 * estado.tempo + fase)
            r.desenhar_emissivo(self.disco, raio * brilho, (x, y), self.COR)
