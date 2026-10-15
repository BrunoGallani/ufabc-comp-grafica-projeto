"""
Chuva: muitas cópias de uma única malha, a gota.

É o reaproveitamento de geometria levado ao extremo. A gota (uma elipse alta
e fina) vai para a VRAM uma única vez e é desenhada `N_GOTAS` vezes por quadro,
cada vez com um `u_deslocamento` diferente. Cada gota é só um par `[x, y]`
guardado na CPU, numa lista.

Tecla R: liga/desliga a chuva (o `estado.chovendo`, controlado pela :class:`Cena`).
"""
import random

import moderngl

from config import Y_CHAO, Estacao
from geometria import curva_elipse
from objetos.objeto_cena import ObjetoCena

ESCALA_GOTA = 0.02            # tamanho de cada gota na tela
VELOCIDADE_QUEDA = 0.8        # em NDC por segundo
COR_GOTA = (0.35, 0.55, 1.00, 1.0)
TOPO = 1.0                    # y da borda de cima da janela


class Chuva(ObjetoCena):
    """
    Gotas que caem com velocidade constante e voltam ao topo ao atingir o chão.
    """

    def __init__(self, r, estado):
        # Elipse 0.35 x 1.0: bem mais alta do que larga. Como u_escala é igual
        # nos dois eixos, essa proporção precisa estar nos próprios vértices.
        self.gota = r.criar_malha(curva_elipse(0.35, 1.0), moderngl.TRIANGLE_FAN)
        
        # Cada gota começa num ponto aleatório entre o chão e o topo: [x, y].
        n_gotas = self.__calcular_numero_gotas_chuva(estado)
        self.gotas = [[random.uniform(-1.0, 1.0), random.uniform(Y_CHAO, TOPO)]
                      for _ in range(n_gotas)]

    def atualizar(self, dt, estado):
        """
        Faz cada gota descer `VELOCIDADE_QUEDA * dt`; a gota que passa do chão
        volta ao topo, numa posição horizontal sorteada.
        """
        if not estado.chovendo:
            return
        
        n_gotas_esperado = self.__calcular_numero_gotas_chuva(estado)
        atual = len(self.gotas)
        
        if atual < n_gotas_esperado:
            self.gotas.extend([[random.uniform(-1.0, 1.0), random.uniform(Y_CHAO, TOPO)] for _ in range(n_gotas_esperado - atual)])
        else:
            self.gotas = self.gotas[:n_gotas_esperado]
            
        self.gotas = [
                    [x, y - (VELOCIDADE_QUEDA * dt)] if y > Y_CHAO else
                    [random.uniform(-1.0, 1.0), TOPO]
                    for x, y in self.gotas]

    def desenhar(self, r, estado):
        """
        Desenha todas as gotas com a mesma malha, só mudando o deslocamento.
        """
        if not estado.chovendo:
            return
        for x, y in self.gotas:
            r.desenhar(self.gota, ESCALA_GOTA, (x, y), COR_GOTA)

    def __calcular_numero_gotas_chuva(self, estado) -> int:
        """
        Retorna o número de gotas que será usado para renderizar a chuva.
        
        O valor padrão é 80. No verão, a chuva é mais intensa, e usa um valor
        2,5 (definido arbitrariamente) vezes maior de gotas.
        """
        if estado.estacao == Estacao.VERAO:
            return 200
        return 80