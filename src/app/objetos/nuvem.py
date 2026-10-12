"""
Nuvem: cinco círculos sobrepostos (o círculo compartilhado) que andam
devagar para a direita e reaparecem pela esquerda.

A animação é por TEMPO, como no 07_triangulo_animado.py: a velocidade está em
unidades de NDC por segundo e é multiplicada por dt (os segundos desde o quadro
anterior). Assim a nuvem anda na mesma velocidade em qualquer computador, rode
ele a 30 ou a 144 quadros por segundo.
"""
from objetos.objeto_cena import ObjetoCena

# Partes da nuvem: (deslocamento x, deslocamento y, raio), para tamanho 1.0.
PARTES = [
    (-0.12, -0.01, 0.070),
    (-0.04, 0.035, 0.090),
    (0.05, 0.030, 0.080),
    (0.13, -0.005, 0.065),
    (0.00, -0.025, 0.080),
]
MEIA_LARGURA = 0.21   # metade da largura da nuvem inteira, com tamanho 1.0

COR_NUVEM = (0.98, 0.98, 0.98, 1.0)
COR_NUVEM_CHUVA = (0.62, 0.64, 0.70, 1.0)   # nuvem carregada


class Nuvem(ObjetoCena):
    def __init__(self, r, x, y, tamanho=1.0, velocidade=0.05):
        self.circulo = r.circulo
        self.x, self.y = x, y
        self.tamanho = tamanho
        self.velocidade = velocidade   # NDC por segundo

    def atualizar(self, dt, estado):
        self.x += self.velocidade * dt
        margem = MEIA_LARGURA * self.tamanho
        if self.x - margem > 1.0:      # saiu inteira pela borda direita...
            self.x = -1.0 - margem     # ...volta, escondida, logo antes da esquerda

    def desenhar(self, r, estado):
        cor = COR_NUVEM_CHUVA if estado.chovendo else COR_NUVEM
        for dx, dy, raio in PARTES:
            centro = (self.x + dx * self.tamanho, self.y + dy * self.tamanho)
            r.desenhar(self.circulo, raio * self.tamanho, centro, cor)
