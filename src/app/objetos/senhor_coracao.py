"""
Sr. Coração: o personagem principal da cena.

O personagem é formado por cinco desenhos, nesta ordem: o corpo (coração) e,
para cada lado, o branco do olho e a pupila. As setas movem o olhar, com a
pupila presa dentro do branco do olho por um limite circular.

Além do desenho, a classe oferece:

- **Posição e tamanho:** aplicados ao personagem inteiro (corpo, olhos, pupilas e
  olhar, todos juntos). Com `tamanho = 1.0` e `posicao = (0, 0)`, o personagem
  aparece no centro da tela, no tamanho base;
- **Andar:** Shift + setas mudam a posição dele (só o `u_deslocamento` muda).
"""
import glfw
import moderngl

from objetos.objeto_cena import ObjetoCena
from geometria import curva_coracao

# --- Cores e medidas do personagem, no tamanho base --------------------------
MAGENTA = (0.85, 0.10, 0.45, 1.0)
BRANCO_OLHO = (1.0, 1.0, 1.0, 1.0)
PRETO = (0.05, 0.05, 0.05, 1.0)
FUNDO_DIA = (0.96, 0.96, 0.94, 1.0)
FUNDO_NOITE = (0.05, 0.05, 0.12, 1.0)

ESCALA_CORPO = 0.62
ESCALA_OLHO, ESCALA_PUPILA = 0.085, 0.040
CENTRO_OLHO = (0.17, 0.20)   # afastamento do eixo e altura de cada olho

# Até onde a pupila pode sair do centro do olho, sem escapar do branco.
LIMITE_OLHAR = ESCALA_OLHO - ESCALA_PUPILA
PASSO_OLHAR = LIMITE_OLHAR / 2.0
# -----------------------------------------------------------------------------
# (FUNDO_DIA e FUNDO_NOITE não são usados: na cena, quem pinta o fundo é a
#  Cena, com as cores do céu definidas em config.py.)

# Quanto o personagem anda (em NDC) a cada toque de Shift + seta.
PASSO_ANDAR = 0.03


class SenhorCoracao(ObjetoCena):
    """
    O Sr. Coração, controlado pelas setas (olhar) e por Shift + setas (andar).

    Possui os seguintes atributos:

    - **Cor do corpo:** atributo de classe; a :class:`SraCoracao` muda só ele;
    - **Malhas:** o coração e o círculo compartilhado (olhos e pupilas);
    - **Posição:** centro do corpo na tela, em NDC;
    - **Tamanho:** fator aplicado ao personagem inteiro (1.0 é o tamanho base);
    - **Olhar:** deslocamento das pupilas em relação ao centro dos olhos.
    """
    COR_CORPO = MAGENTA

    def __init__(self, r, posicao=(0.0, 0.0), tamanho=1.0):
        self.coracao = r.criar_malha(curva_coracao(), moderngl.TRIANGLE_FAN)
        self.circulo = r.circulo

        self.posicao = list(posicao)   # centro do corpo na tela (em NDC)
        self.tamanho = tamanho         # 1.0 = tamanho base

        self.olhar_x, self.olhar_y = 0.0, 0.0

    def olhar(self, key):
        """
        Move as pupilas na direção da seta pressionada, sem deixá-las sair do
        branco do olho.
        """
        dx = {glfw.KEY_LEFT: -1.0, glfw.KEY_RIGHT: 1.0}.get(key, 0.0)
        dy = {glfw.KEY_DOWN: -1.0, glfw.KEY_UP: 1.0}.get(key, 0.0)
        self.olhar_x += dx * PASSO_OLHAR
        self.olhar_y += dy * PASSO_OLHAR
        # O branco do olho é um círculo, então o limite tem de ser no vetor.
        # Limitar cada eixo em separado prende a pupila num quadrado, e na
        # diagonal ela escapa: o centro chega a 0.064 do centro do olho e a
        # borda da pupila a 0.104, contra um raio de 0.085.
        distancia = (self.olhar_x ** 2 + self.olhar_y ** 2) ** 0.5
        if distancia > LIMITE_OLHAR:
            self.olhar_x *= LIMITE_OLHAR / distancia
            self.olhar_y *= LIMITE_OLHAR / distancia

    def andar(self, key):
        """
        Move o personagem inteiro pela tela (Shift + setas), sem deixar o corpo
        sair da janela.
        """
        dx = {glfw.KEY_LEFT: -1.0, glfw.KEY_RIGHT: 1.0}.get(key, 0.0)
        dy = {glfw.KEY_DOWN: -1.0, glfw.KEY_UP: 1.0}.get(key, 0.0)
        # A curva do coração foi normalizada para caber em [-1, 1]
        # (geometria.py). Na tela, então, ela nunca passa de
        # ESCALA_CORPO * tamanho a partir do centro. Mantendo o centro a essa
        # distância da borda, o corpo nunca sai da janela.
        limite = 1.0 - ESCALA_CORPO * self.tamanho
        self.posicao[0] = min(max(self.posicao[0] + dx * PASSO_ANDAR, -limite), limite)
        self.posicao[1] = min(max(self.posicao[1] + dy * PASSO_ANDAR, -limite), limite)

    def na_tela(self, x, y):
        """
        Leva um ponto do desenho base (centrado em `(0, 0)` e com tamanho 1.0)
        para a tela: multiplica pelo tamanho e soma a posição.
        """
        return (self.posicao[0] + x * self.tamanho,
                self.posicao[1] + y * self.tamanho)

    def desenhar(self, r, estado):
        """
        Desenha o corpo e, por cima, os olhos e as pupilas.
        """
        k = self.tamanho

        # 1) O corpo.
        r.desenhar(self.coracao, ESCALA_CORPO * k, self.na_tela(0.0, 0.0), self.COR_CORPO)

        # 2) A mesma geometria de círculo, quatro vezes, só mudando os uniforms.
        for lado in (-1.0, 1.0):
            centro = (lado * CENTRO_OLHO[0], CENTRO_OLHO[1])
            r.desenhar(self.circulo, ESCALA_OLHO * k, self.na_tela(*centro), BRANCO_OLHO)
            r.desenhar(self.circulo, ESCALA_PUPILA * k,
                       self.na_tela(centro[0] + self.olhar_x, centro[1] + self.olhar_y),
                       PRETO)
