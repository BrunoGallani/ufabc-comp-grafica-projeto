"""
Casa: várias peças simples, cada uma desenhada com a primitiva que mais combina.

- **Paredes, porta e janelas:** retângulos com EBO, desenhados com `TRIANGLES`;
- **Telhado:** uma malha de triângulo desenhada duas vezes, primeiro com `TRIANGLES`
  (preenchido) e depois com `LINE_LOOP` (só o contorno). Mesmo VBO, mesmo VAO,
  primitivas diferentes;
- **Arco da porta e maçaneta:** o círculo compartilhado (`TRIANGLE_FAN`);
- **Caixilho das janelas:** uma cruz em `LINES`, a mesma malha nas duas janelas.

Tecla C: troca a cor das paredes (percorre a `PALETA_PAREDE`).
À noite as janelas "acendem": são desenhadas como emissivas, ou seja, não
sofrem a atenuação da noite (veja :meth:`Renderizador.desenhar_emissivo`).
"""
import itertools

import moderngl

from config import Y_CHAO
from geometria import cruz, retangulo, triangulo
from objetos.objeto_cena import ObjetoCena

# (nome, cor) de cada parede, na ordem em que a tecla C as percorre.
PALETA_PAREDE = [
    ("creme", (0.93, 0.87, 0.70, 1.0)),
    ("azul-claro", (0.55, 0.75, 0.95, 1.0)),
    ("verde-menta", (0.62, 0.85, 0.66, 1.0)),
    ("salmão", (0.96, 0.66, 0.56, 1.0)),
    ("lilás", (0.78, 0.68, 0.92, 1.0)),
]
COR_TELHADO = (0.80, 0.22, 0.18, 1.0)
COR_CONTORNO_TELHADO = (0.22, 0.04, 0.03, 1.0)
COR_PORTA = (0.45, 0.26, 0.12, 1.0)
COR_MACANETA = (0.95, 0.80, 0.25, 1.0)
COR_VIDRO_DIA = (0.72, 0.87, 0.97, 1.0)    # vidro refletindo o céu
COR_VIDRO_NOITE = (1.00, 0.88, 0.45, 1.0)  # luz acesa lá dentro
COR_CAIXILHO = (0.30, 0.18, 0.10, 1.0)

# Medidas em NDC (a janela inteira tem 2 unidades de largura).
LARGURA_PAREDE, ALTURA_PAREDE = 0.50, 0.40
BASE_TELHADO, ALTURA_TELHADO = 0.62, 0.28
LARGURA_PORTA, ALTURA_PORTA = 0.12, 0.18
LADO_JANELA = 0.11
AFASTAMENTO_JANELA = 0.15   # distância horizontal de cada janela ao centro da casa
ALTURA_JANELA = 0.27        # altura do centro das janelas acima do chão


class Casa(ObjetoCena):
    """
    Casa apoiada no chão, centrada na posição horizontal `centro_x`.
    """

    def __init__(self, r, centro_x=-0.58):
        self.x = centro_x
        self.paleta = itertools.cycle(PALETA_PAREDE)   # volta ao início depois da última cor
        self.nome_cor, self.cor_parede = next(self.paleta)
        self.circulo = r.circulo     # malha compartilhada (arco e maçaneta)

        # Cada peça com proporção diferente precisa da sua própria malha,
        # porque u_escala é um número só (escala igual em x e y).
        v, i = retangulo(LARGURA_PAREDE, ALTURA_PAREDE)
        self.parede = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
        v, i = retangulo(LARGURA_PORTA, ALTURA_PORTA)
        self.porta = r.criar_malha(v, moderngl.TRIANGLES, indices=i)
        v, i = retangulo(LADO_JANELA, LADO_JANELA)
        self.janela = r.criar_malha(v, moderngl.TRIANGLES, indices=i)   # usada 2x
        self.telhado = r.criar_malha(triangulo(BASE_TELHADO, ALTURA_TELHADO),
                                     moderngl.TRIANGLES)
        self.caixilho = r.criar_malha(cruz(), moderngl.LINES)            # usada 2x

    def proxima_cor(self):
        """
        Avança para a próxima cor da paleta (tecla C), voltando ao início no fim.
        """
        self.nome_cor, self.cor_parede = next(self.paleta)

    def desenhar(self, r, estado):
        """
        Desenha paredes, telhado, porta e janelas, do fundo para a frente.
        """
        x = self.x

        # Paredes. O retângulo nasce centrado na origem; para "apoiá-lo" no chão,
        # o centro fica meia altura acima de Y_CHAO.
        r.desenhar(self.parede, 1.0, (x, Y_CHAO + ALTURA_PAREDE / 2), self.cor_parede)

        # Telhado: a mesma malha, duas primitivas.
        centro_telhado = (x, Y_CHAO + ALTURA_PAREDE + ALTURA_TELHADO / 2)
        r.desenhar(self.telhado, 1.0, centro_telhado, COR_TELHADO)
        r.desenhar(self.telhado, 1.0, centro_telhado, COR_CONTORNO_TELHADO,
                   primitiva=moderngl.LINE_LOOP)

        # Porta: retângulo + meio círculo em cima (o arco). O círculo inteiro é
        # desenhado, mas a metade de baixo cai sobre a porta, da mesma cor.
        r.desenhar(self.porta, 1.0, (x, Y_CHAO + ALTURA_PORTA / 2), COR_PORTA)
        r.desenhar(self.circulo, LARGURA_PORTA / 2, (x, Y_CHAO + ALTURA_PORTA), COR_PORTA)
        r.desenhar(self.circulo, 0.012, (x + 0.035, Y_CHAO + ALTURA_PORTA / 2), COR_MACANETA)

        # Janelas: a mesma malha de vidro e a mesma cruz, uma vez de cada lado.
        for lado in (-1.0, 1.0):
            centro = (x + lado * AFASTAMENTO_JANELA, Y_CHAO + ALTURA_JANELA)
            if estado.noite:
                r.desenhar_emissivo(self.janela, 1.0, centro, COR_VIDRO_NOITE)
            else:
                r.desenhar(self.janela, 1.0, centro, COR_VIDRO_DIA)
            # A cruz vai de -1 a 1; escala = meia janela para ela caber exata.
            r.desenhar(self.caixilho, LADO_JANELA / 2, centro, COR_CAIXILHO)
