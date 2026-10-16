"""
Painel de informações: um retângulo cinza translúcido, no canto superior
esquerdo, com o estado atual da cena.

O OpenGL não desenha texto. Quem o escreve é o Pillow, numa imagem em preto e
branco, com a fonte bitmap que o acompanha (6 x 11 pixels por letra, com
acentos). Cada pixel aceso dessa imagem vira geometria (veja
:func:`geometria.bitmap`), desenhada com os mesmos shaders do resto da cena.

As malhas só são refeitas quando o texto muda (uma tecla foi apertada). Nos
outros quadros, são reaproveitadas.

Tecla I: mostra ou esconde o painel (o `estado.painel`, controlado pela :class:`Cena`).
"""
import moderngl
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from geometria import bitmap, retangulo
from objetos.objeto_cena import ObjetoCena

FONTE = ImageFont.load_default_imagefont()
ESPACO_LINHAS = 4           # pixels da fonte entre uma linha e outra
# Lado de cada pixel da fonte, em NDC. Com 1/180, ele ocupa um número inteiro
# de pixels da tela (2 na janela de 720, 3 numa tela cheia de 1080), e as
# letras ficam nítidas.
TAMANHO_PIXEL = 1.0 / 180.0
MARGEM = 4                  # do painel às bordas da cena, em pixels da fonte
PREENCHIMENTO = 6           # do texto às bordas do painel, em pixels da fonte
COR_FUNDO = (0.20, 0.20, 0.20, 0.65)   # cinza com alpha < 1: a cena aparece por trás
COR_TEXTO = (0.97, 0.97, 0.97, 1.0)


class PainelInfo(ObjetoCena):
    """
    Painel com os pares (rótulo, valor) do estado da cena.

    Quem fornece esses pares é a função `informacoes`, chamada a cada quadro. Ela
    vem da :class:`Cena`, que conhece todos os objetos (a cor da casa, por exemplo,
    não está no :class:`EstadoCena`).
    """

    def __init__(self, r, informacoes):
        self.informacoes = informacoes
        self.linhas = None     # texto que está nas malhas abaixo
        self.fundo = None
        self.texto = None
        self.centro = (0.0, 0.0)

    def desenhar(self, r, estado):
        """
        Desenha o fundo e, por cima dele, o texto. Os dois estão centrados na
        origem e vão para o mesmo centro.
        """
        if not estado.painel:
            return
        pares = self.informacoes()
        # Fonte monoespaçada: completar os rótulos com espaços alinha os valores.
        largura_rotulo = max(len(rotulo) for rotulo, _ in pares) + 2
        linhas = [f"{rotulo + ':':<{largura_rotulo}}{valor}" for rotulo, valor in pares]
        if linhas != self.linhas:
            self.montar(r, linhas)

        r.desenhar_translucido(self.fundo, TAMANHO_PIXEL, self.centro, COR_FUNDO)
        r.desenhar_translucido(self.texto, TAMANHO_PIXEL, self.centro, COR_TEXTO)

    def montar(self, r, linhas):
        """
        Refaz as malhas do texto e do fundo para as `linhas`, liberando as anteriores.
        """
        if self.texto is not None:
            r.liberar_malha(self.texto)
            r.liberar_malha(self.fundo)

        conteudo = "\n".join(linhas)
        rascunho = ImageDraw.Draw(Image.new("1", (1, 1)))
        _, _, largura, altura = rascunho.multiline_textbbox(
            (0, 0), conteudo, font=FONTE, spacing=ESPACO_LINHAS)
        imagem = Image.new("1", (largura, altura))
        ImageDraw.Draw(imagem).multiline_text(
            (0, 0), conteudo, font=FONTE, fill=1, spacing=ESPACO_LINHAS)
        # Corta as bordas vazias (o espaço das letras que descem abaixo da linha,
        # como "g"), para que o preenchimento fique igual dos quatro lados.
        imagem = imagem.crop(imagem.getbbox())

        v, i = bitmap(np.array(imagem, dtype=bool))
        self.texto = r.criar_malha(v, moderngl.TRIANGLES, indices=i)

        largura_fundo = imagem.width + 2 * PREENCHIMENTO
        altura_fundo = imagem.height + 2 * PREENCHIMENTO
        v, i = retangulo(largura_fundo, altura_fundo)
        self.fundo = r.criar_malha(v, moderngl.TRIANGLES, indices=i)

        # Centro que deixa o canto superior esquerdo do painel a MARGEM do
        # canto superior esquerdo da cena, (-1, 1).
        self.centro = (-1.0 + (MARGEM + largura_fundo / 2) * TAMANHO_PIXEL,
                       1.0 - (MARGEM + altura_fundo / 2) * TAMANHO_PIXEL)
        self.linhas = linhas
