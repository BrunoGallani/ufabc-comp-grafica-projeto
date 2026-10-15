"""
Raios de calor do verão: retângulos finos que saem do sol.

Cada raio nasce a uma certa distância do sol, anda um pouco para fora, na sua
direção, e some; logo em seguida, um novo raio surge na posição original.
"""
import math

import moderngl
import numpy as np

from config import Estacao
from geometria import retangulo_girado
from objetos.astros import CENTRO_ASTRO
from objetos.objeto_cena import ObjetoCena

N_RAIOS = 12
COMPRIMENTO = 0.07          # comprimento de cada raio
ESPESSURA = 0.012           # espessura de cada raio
DISTANCIA_INICIAL = 0.24    # do centro do sol até onde o raio nasce, além das pontas do Sol
PERCURSO = 0.12             # quanto o raio anda antes de sumir
VELOCIDADE = 0.10           # em NDC por segundo
SURGIR = 0.2                # fração inicial do percurso em que o raio cresce
SUMIR = 0.4                 # fração final do percurso em que o raio encolhe e desbota
COR_RAIO = (1.00, 0.72, 0.25, 1.0)


class RaiosVerao(ObjetoCena):
    """
    Raios que partem do sol nos vãos entre os seus triângulos. Cada raio
    começa num ponto do percurso sorteado a partir de uma `semente` fixa, para
    que não nasçam e sumam todos juntos.
    """

    def __init__(self, r, semente=5):
        gerador = np.random.default_rng(semente)
        self.raios = []   # cada raio: [malha, direção (cos, sen), distância já percorrida]
        for k in range(N_RAIOS):
            # Meio passo a mais que os triângulos do Sol: o raio fica no vão entre dois deles.
            angulo = 2.0 * math.pi * (k + 0.5) / N_RAIOS
            v, i = retangulo_girado(COMPRIMENTO, ESPESSURA, angulo)
            malha = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
            direcao = (math.cos(angulo), math.sin(angulo))
            self.raios.append([malha, direcao, float(gerador.uniform(0.0, PERCURSO))])

    @staticmethod
    def visivel(estado):
        """
        Os raios só aparecem no verão, de dia e sem chuva.
        """
        return estado.estacao == Estacao.VERAO and not estado.noite and not estado.chovendo

    def atualizar(self, dt, estado):
        """
        Faz cada raio andar `VELOCIDADE * dt` para fora; o raio que completa o
        `PERCURSO` volta à posição original, como um raio novo.
        """
        if not self.visivel(estado):
            return
        for raio in self.raios:
            raio[2] = (raio[2] + VELOCIDADE * dt) % PERCURSO

    def desenhar(self, r, estado):
        """
        Desenha cada raio na sua distância do sol. Ao nascer, o raio cresce; ao
        fim do percurso, encolhe e vai tomando a cor do céu até sumir.
        """
        if not self.visivel(estado):
            return
        cx, cy = CENTRO_ASTRO
        for malha, (dx, dy), percorrido in self.raios:
            fracao = percorrido / PERCURSO
            # Sobe de 0 a 1 no começo, fica em 1 e desce a 0 no fim do percurso.
            intensidade = min(1.0, fracao / SURGIR, (1.0 - fracao) / SUMIR)
            # Mistura linear com a cor do céu: com intensidade 0, o raio some no
            # fundo. Funciona porque, de dia e sem chuva, u_atenuacao vale 1.0.
            cor = tuple(c_ceu + (c_raio - c_ceu) * intensidade
                        for c_raio, c_ceu in zip(COR_RAIO, estado.cor_do_ceu))
            distancia = DISTANCIA_INICIAL + percorrido
            r.desenhar(malha, intensidade, (cx + distancia * dx, cy + distancia * dy), cor)
