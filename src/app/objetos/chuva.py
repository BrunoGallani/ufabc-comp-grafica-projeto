"""
Chuva: uma malha só (a gota) desenhada N_GOTAS vezes por quadro, ou N_GOTAS_VERAO
no verão, cada vez com um u_deslocamento. Cada gota é só um [x, y] na CPU.
"""
import random

import moderngl

from config import Y_CHAO, Estacao
from geometria import curva_elipse
from objetos.objeto_cena import ObjetoCena

N_GOTAS = 80
N_GOTAS_VERAO = 200           # chuva de verão é mais forte
ESCALA_GOTA = 0.02
VELOCIDADE_QUEDA = 0.8        # NDC por segundo
COR_GOTA = (0.35, 0.55, 1.00, 1.0)
TOPO = 1.0                    # borda de cima da cena


class Chuva(ObjetoCena):
    def __init__(self, r):
        self.gota = r.criar_malha(curva_elipse(0.35, 1.0), moderngl.TRIANGLE_FAN)

        # Começam espalhadas entre o chão e o topo. Todas caem, mas fora do verão
        # só as N_GOTAS primeiras aparecem.
        self.gotas = [[random.uniform(-1.0, 1.0), random.uniform(Y_CHAO, TOPO)]
                      for _ in range(N_GOTAS_VERAO)]

    def atualizar(self, dt, estado):
        if not estado.chovendo:
            return
        for gota in self.gotas:
            if gota[1] > Y_CHAO:
                gota[1] -= VELOCIDADE_QUEDA * dt
            else:   # chegou no chão: volta pro topo num x sorteado
                gota[0], gota[1] = random.uniform(-1.0, 1.0), TOPO

    def desenhar(self, r, estado):
        if not estado.chovendo:
            return
        n_gotas = N_GOTAS_VERAO if estado.estacao == Estacao.VERAO else N_GOTAS
        for x, y in self.gotas[:n_gotas]:
            r.desenhar(self.gota, ESCALA_GOTA, (x, y), COR_GOTA)
