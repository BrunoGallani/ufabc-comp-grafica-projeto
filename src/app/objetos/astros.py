"""
Sol de dia; lua e estrelas à noite. Todos usam o círculo compartilhado e decidem
sozinhos se aparecem (a Cena desenha todos, sempre).
"""
import math

import moderngl
import numpy as np

from geometria import raios_do_sol
from objetos.objeto_cena import ObjetoCena

CENTRO_ASTRO = (0.62, 0.66)   # o sol e a lua ficam no mesmo lugar


class Sol(ObjetoCena):
    """Disco com raios que "respiram"."""
    RAIO = 0.11
    COR_DISCO = (1.00, 0.84, 0.20, 1.0)
    COR_RAIOS = (1.00, 0.55, 0.10, 1.0)

    def __init__(self, r):
        self.disco = r.circulo
        self.raios = r.criar_malha(raios_do_sol(), moderngl.TRIANGLES)

    def desenhar(self, r, estado):
        if estado.noite:
            return
        # A escala dos raios oscila 6% num seno (meio ciclo por segundo).
        pulso = 1.0 + 0.06 * math.sin(2.0 * math.pi * 0.5 * estado.tempo)
        r.desenhar(self.raios, self.RAIO * pulso, CENTRO_ASTRO, self.COR_RAIOS)
        r.desenhar(self.disco, self.RAIO, CENTRO_ASTRO, self.COR_DISCO)


class Lua(ObjetoCena):
    """
    Lua crescente pelo algoritmo do pintor: a lua cheia e, por cima, um círculo da
    cor do céu meio deslocado "mordendo" ela.
    """
    RAIO = 0.10
    COR = (0.96, 0.95, 0.82, 1.0)
    CENTRO_SOMBRA = (CENTRO_ASTRO[0] - 0.045, CENTRO_ASTRO[1] + 0.030)

    def __init__(self, r):
        self.disco = r.circulo

    def desenhar(self, r, estado):
        if not estado.noite:
            return
        # Os dois são emissivos: a sombra tem que ter exatamente a cor do céu.
        # Atenuada, ela ficaria mais escura e apareceria como uma mancha.
        r.desenhar_emissivo(self.disco, self.RAIO, CENTRO_ASTRO, self.COR)
        r.desenhar_emissivo(self.disco, self.RAIO * 0.92, self.CENTRO_SOMBRA, estado.cor_do_ceu)


class Estrelas(ObjetoCena):
    """Sorteadas com semente fixa, então o céu é sempre o mesmo."""
    QUANTIDADE = 22
    COR = (1.00, 1.00, 0.92, 1.0)

    def __init__(self, r, semente=7):
        self.disco = r.circulo
        gerador = np.random.default_rng(semente)
        self.estrelas = []   # (x, y, raio, fase)
        while len(self.estrelas) < self.QUANTIDADE:
            x = float(gerador.uniform(-0.95, 0.95))
            y = float(gerador.uniform(0.05, 0.95))
            if math.dist((x, y), CENTRO_ASTRO) < 0.22:
                continue   # nada de estrela atrás da lua
            raio = float(gerador.uniform(0.005, 0.010))
            fase = float(gerador.uniform(0.0, 2.0 * math.pi))
            self.estrelas.append((x, y, raio, fase))

    def desenhar(self, r, estado):
        if not estado.noite:
            return
        for x, y, raio, fase in self.estrelas:
            # Pisca: o tamanho segue um seno, com uma fase diferente pra cada estrela.
            brilho = 0.75 + 0.25 * math.sin(3.0 * estado.tempo + fase)
            r.desenhar_emissivo(self.disco, raio * brilho, (x, y), self.COR)
