"""
Raios de calor do verão: retângulos finos que nascem perto do sol, andam pra fora
e somem; logo depois nasce outro no lugar.
"""
import math

import moderngl
import numpy as np

from config import Estacao
from geometria import retangulo_girado
from objetos.astros import CENTRO_ASTRO
from objetos.objeto_cena import ObjetoCena

N_RAIOS = 12
COMPRIMENTO = 0.07
ESPESSURA = 0.012
DISTANCIA_INICIAL = 0.24    # do centro do sol até onde o raio nasce (depois das pontas)
PERCURSO = 0.12             # quanto ele anda antes de sumir
VELOCIDADE = 0.10           # NDC por segundo
FRACAO_SURGIR = 0.2         # pedaço do começo do percurso em que o raio cresce
FRACAO_SUMIR = 0.4          # pedaço do fim em que ele encolhe e desbota
COR_RAIO = (1.00, 0.72, 0.25, 1.0)


class RaiosVerao(ObjetoCena):
    """
    Raios nos vãos entre os triângulos do sol. Cada um parte de um ponto sorteado
    (semente fixa), pra não nascerem e sumirem todos juntos.
    """

    def __init__(self, r, semente=5):
        gerador = np.random.default_rng(semente)
        self.raios = []   # (malha, direção (cos, sen), ponto de partida)
        for k in range(N_RAIOS):
            # meio passo a mais que os triângulos do sol: cai no vão entre eles
            angulo = 2.0 * math.pi * (k + 0.5) / N_RAIOS
            v, i = retangulo_girado(COMPRIMENTO, ESPESSURA, angulo)
            malha = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
            direcao = (math.cos(angulo), math.sin(angulo))
            self.raios.append((malha, direcao, float(gerador.uniform(0.0, PERCURSO))))

    def desenhar(self, r, estado):
        if estado.estacao != Estacao.VERAO or estado.noite or estado.chovendo:
            return
        cx, cy = CENTRO_ASTRO
        for malha, (dx, dy), partida in self.raios:
            percorrido = (partida + VELOCIDADE * estado.tempo) % PERCURSO
            fracao = percorrido / PERCURSO
            # sobe de 0 a 1, segura e desce a 0 no fim do percurso
            intensidade = min(1.0, fracao / FRACAO_SURGIR, (1.0 - fracao) / FRACAO_SUMIR)
            # Some misturando a cor com a do céu (dá certo porque de dia, sem chuva,
            # o u_atenuacao é 1).
            cor = tuple(c_ceu + (c_raio - c_ceu) * intensidade
                        for c_raio, c_ceu in zip(COR_RAIO, estado.cor_do_ceu))
            distancia = DISTANCIA_INICIAL + percorrido
            r.desenhar(malha, intensidade, (cx + distancia * dx, cy + distancia * dy), cor)
