"""
Sr. Coração: o personagem do 06_senhor_coracao.py, agora como uma classe.

O que veio do professor SEM ALTERAÇÃO:
- todas as constantes (cores, escalas, centro dos olhos, limites do olhar);
- as curvas (geometria.py) e os shaders (shaders/senhor_coracao.*);
- a lógica das setas com o limite circular da pupila (método olhar);
- os 5 desenhos na mesma ordem: corpo e, para cada lado, branco do olho e pupila.

O que a classe ACRESCENTA, sem mudar o desenho:
- posicao e tamanho, aplicados ao personagem INTEIRO (corpo, olhos, pupilas e
  olhar, todos juntos). Com tamanho = 1.0 e posicao = (0, 0), cada número
  enviado à GPU é exatamente o do professor, e o desenho sai idêntico,
  pixel a pixel (isso foi testado). Na cena usamos um tamanho menor, para ele
  caber ao lado da casa, como no esboço;
- andar(): Shift + setas mudam a posição dele (só o u_deslocamento muda).
"""
import glfw

from objetos.objeto_cena import ObjetoCena

# --- Constantes copiadas do 06_senhor_coracao.py, sem alteração -------------
MAGENTA = (0.85, 0.10, 0.45, 1.0)
BRANCO_OLHO = (1.0, 1.0, 1.0, 1.0)
PRETO = (0.05, 0.05, 0.05, 1.0)
FUNDO_DIA = (0.96, 0.96, 0.94, 1.0)
FUNDO_NOITE = (0.05, 0.05, 0.12, 1.0)

ESCALA_CORPO = 0.62
ESCALA_OLHO, ESCALA_PUPILA = 0.085, 0.040
CENTRO_OLHO = (0.17, 0.20)   # afastamento do eixo e altura de cada olho

# Ate onde a pupila pode sair do centro do olho, sem escapar do branco.
LIMITE_OLHAR = ESCALA_OLHO - ESCALA_PUPILA
PASSO_OLHAR = LIMITE_OLHAR / 2.0
# -----------------------------------------------------------------------------
# (FUNDO_DIA e FUNDO_NOITE ficam só como registro do original: na cena, quem
#  pinta o fundo é a Cena, com as cores do céu definidas em config.py.)

# Novo: quanto o personagem anda (em NDC) a cada toque de Shift + seta.
PASSO_ANDAR = 0.03


class SenhorCoracao(ObjetoCena):
    # Atributo de CLASSE com a cor do corpo. A SraCoracao (herança) muda só isto.
    COR_CORPO = MAGENTA

    def __init__(self, r, posicao=(0.0, 0.0), tamanho=1.0):
        # As duas malhas do personagem (no original: vao_coracao e vao_circulo).
        # São as mesmas malhas compartilhadas por toda a cena (renderizador.py).
        self.coracao = r.coracao
        self.circulo = r.circulo

        self.posicao = list(posicao)   # centro do corpo na tela (em NDC)
        self.tamanho = tamanho         # 1.0 = o tamanho do exemplo do professor

        # O estado do olhar, como no original: olhar_x, olhar_y = 0.0, 0.0
        self.olhar_x, self.olhar_y = 0.0, 0.0

    def olhar(self, key):
        """O trecho das setas do tecla() do 06_senhor_coracao.py, sem alteração.
        A única troca: as variáveis globais viraram atributos do objeto."""
        dx = {glfw.KEY_LEFT: -1.0, glfw.KEY_RIGHT: 1.0}.get(key, 0.0)
        dy = {glfw.KEY_DOWN: -1.0, glfw.KEY_UP: 1.0}.get(key, 0.0)
        self.olhar_x += dx * PASSO_OLHAR
        self.olhar_y += dy * PASSO_OLHAR
        # O branco do olho e um CIRCULO, entao o limite tem de ser no vetor.
        # Limitar cada eixo em separado prende a pupila num quadrado, e na
        # diagonal ela escapa: o centro chega a 0.064 do centro do olho e a
        # borda da pupila a 0.104, contra um raio de 0.085.
        distancia = (self.olhar_x ** 2 + self.olhar_y ** 2) ** 0.5
        if distancia > LIMITE_OLHAR:
            self.olhar_x *= LIMITE_OLHAR / distancia
            self.olhar_y *= LIMITE_OLHAR / distancia

    def andar(self, key):
        """(Novo) Shift + setas: move o personagem inteiro pela tela."""
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
        """Leva um ponto do desenho ORIGINAL (o do professor: centrado em (0, 0)
        e com tamanho 1.0) para a tela: multiplica pelo tamanho e soma a posição.

        Com tamanho = 1.0 e posicao = (0, 0): 0 + x * 1.0 = x, exatamente o
        número que o professor enviava. Por isso o desenho não muda."""
        return (self.posicao[0] + x * self.tamanho,
                self.posicao[1] + y * self.tamanho)

    def desenhar(self, r, estado):
        k = self.tamanho

        # 1) O corpo. (Original: desenhar(vao_coracao, ESCALA_CORPO, (0.0, 0.0), MAGENTA))
        r.desenhar(self.coracao, ESCALA_CORPO * k, self.na_tela(0.0, 0.0), self.COR_CORPO)

        # 2) A mesma geometria de circulo, quatro vezes, so mudando os uniformes.
        for lado in (-1.0, 1.0):
            centro = (lado * CENTRO_OLHO[0], CENTRO_OLHO[1])
            r.desenhar(self.circulo, ESCALA_OLHO * k, self.na_tela(*centro), BRANCO_OLHO)
            r.desenhar(self.circulo, ESCALA_PUPILA * k,
                       self.na_tela(centro[0] + self.olhar_x, centro[1] + self.olhar_y),
                       PRETO)
