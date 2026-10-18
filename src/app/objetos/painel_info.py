"""
Painel com o estado da cena (tecla I): um retângulo cinza translúcido com texto.

O OpenGL não desenha texto, então o Pillow escreve numa imagem preto e branco
(com a fonte bitmap que vem com ele) e cada pixel aceso vira geometria
(geometria.bitmap). As malhas só são refeitas quando o texto muda.
"""
import moderngl
import numpy as np
from PIL import Image, ImageDraw, ImageFont

from geometria import bitmap, retangulo
from objetos.objeto_cena import ObjetoCena

FONTE = ImageFont.load_default_imagefont()
ESPACO_LINHAS = 4           # em pixels da fonte
# Com 1/180 de NDC, cada pixel da fonte vira um número inteiro de pixels da tela
# (2 na janela de 720, 3 numa tela de 1080) e a letra fica nítida.
TAMANHO_PIXEL = 1.0 / 180.0
MARGEM = 4                  # do painel até a borda da cena, em pixels da fonte
PREENCHIMENTO = 6           # do texto até a borda do painel, em pixels da fonte
COR_FUNDO = (0.20, 0.20, 0.20, 0.65)   # alpha < 1: dá pra ver a cena atrás
COR_TEXTO = (0.97, 0.97, 0.97, 1.0)


class PainelInfo(ObjetoCena):
    """
    Mostra os pares (rótulo, valor) que vêm de `informacoes`, uma função da Cena
    (ela sabe de coisas que não estão no EstadoCena, tipo a cor da casa).
    """

    def __init__(self, r, informacoes):
        self.informacoes = informacoes
        self.linhas = None     # texto que está nas malhas agora
        self.fundo = None
        self.texto = None
        self.centro = (0.0, 0.0)

    def desenhar(self, r, estado):
        if not estado.painel_visivel:
            return
        pares = self.informacoes()
        # A fonte é monoespaçada: completando os rótulos com espaço, os valores alinham.
        largura_rotulo = max(len(rotulo) for rotulo, _ in pares) + 2
        linhas = [f"{rotulo + ':':<{largura_rotulo}}{valor}" for rotulo, valor in pares]
        if linhas != self.linhas:
            self.montar(r, linhas)

        r.desenhar_translucido(self.fundo, TAMANHO_PIXEL, self.centro, COR_FUNDO)
        r.desenhar_translucido(self.texto, TAMANHO_PIXEL, self.centro, COR_TEXTO)

    def montar(self, r, linhas):
        """Refaz as malhas do texto e do fundo, liberando as antigas."""
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
        # Corta as bordas vazias (tipo o espaço embaixo do "g"), pra margem ficar
        # igual nos quatro lados.
        imagem = imagem.crop(imagem.getbbox())

        v, i = bitmap(np.array(imagem, dtype=bool))
        self.texto = r.criar_malha(v, moderngl.TRIANGLES, indices=i)

        largura_fundo = imagem.width + 2 * PREENCHIMENTO
        altura_fundo = imagem.height + 2 * PREENCHIMENTO
        v, i = retangulo(largura_fundo, altura_fundo)
        self.fundo = r.criar_malha(v, moderngl.TRIANGLES, indices=i)

        # Encosta o canto superior esquerdo do painel a MARGEM do canto (-1, 1) da cena.
        self.centro = (-1.0 + (MARGEM + largura_fundo / 2) * TAMANHO_PIXEL,
                       1.0 - (MARGEM + altura_fundo / 2) * TAMANHO_PIXEL)
        self.linhas = linhas
