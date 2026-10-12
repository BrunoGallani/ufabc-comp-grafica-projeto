"""
A Cena: o "maestro" do programa.

- Cria o Renderizador e todos os objetos (casa, árvore, Sr. Coração...).
- Guarda o estado GLOBAL (EstadoCena): é dia ou noite? está chovendo?
- Recebe as teclas (callback do GLFW) e repassa a quem interessa.
- A cada quadro, atualiza todos os objetos e depois desenha todos, do fundo
  para a frente (algoritmo do pintor, slides04, p.134).

Como as classes se comunicam:

    main.py  --cria-->  Cena  --chama atualizar()/desenhar()-->  cada ObjetoCena
                          |                                          |
                          +--possui--> EstadoCena <--só lê-----------+
                          |                                          |
                          +--possui--> Renderizador <--pede desenhos-+
                                           |
                                           +--uniforms e draw calls--> GPU (shaders)
"""
import glfw

from config import (ATENUACAO_CHUVA, ATENUACAO_NOITE, CEU_DIA, CEU_DIA_CHUVA,
                    CEU_NOITE, CEU_NOITE_CHUVA, PASTA_CAPTURAS, Y_CHAO)
from objetos.arvore import Arvore
from objetos.astros import Estrelas, Lua, Sol
from objetos.casa import Casa
from objetos.chao import Chao
from objetos.chuva import Chuva
from objetos.nuvem import Nuvem
from objetos.senhor_coracao import SenhorCoracao
from objetos.sra_coracao import SraCoracao
from renderizador import Renderizador
from utils.date_utils import get_date_prefix
from utils.screenshot_utils import save_screenshot

SETAS = (glfw.KEY_LEFT, glfw.KEY_RIGHT, glfw.KEY_UP, glfw.KEY_DOWN)

AJUDA_TECLAS = """Teclas:
  Setas ............ o Sr. Coração olha (como no exemplo do professor)
  Shift + setas .... o Sr. Coração anda
  D ................ dia / noite
  R ................ liga / desliga a chuva
  C ................ troca a cor da casa
  A ................ troca a estação (cor) da árvore
  P ................ salva uma captura de tela em capturas/
  ESC .............. sai"""


class EstadoCena:
    """O estado GLOBAL da cena: a Cena altera, os objetos só leem."""

    def __init__(self):
        self.noite = False
        self.chovendo = False
        self.tempo = 0.0           # segundos desde o início (para as animações)
        self.cor_do_ceu = CEU_DIA  # a Lua precisa dela para fazer o crescente


class Cena:
    def __init__(self, ctx):
        self.ctx = ctx
        self.r = Renderizador(ctx)
        self.estado = EstadoCena()
        self.pedir_captura = False   # a tecla P liga; desenhar() salva e desliga

        # Objetos que recebem comandos do teclado ficam guardados em atributos.
        # Tamanho 0.40: o Sr. Coração do tamanho do esboço, apoiado na grama. A
        # metade da altura dele na tela é 0.53 * tamanho; afundamos 0.02 na grama.
        self.sr_coracao = SenhorCoracao(self.r, posicao=(-0.06, Y_CHAO + 0.19), tamanho=0.40)
        self.sra_coracao = SraCoracao(self.r, alvo=self.sr_coracao,
                                      posicao=(0.38, Y_CHAO + 0.16), tamanho=0.34)
        self.casa = Casa(self.r)
        self.arvore = Arvore(self.r)

        # A ORDEM desta lista é a ordem de desenho: do fundo para a frente.
        # Quem é desenhado depois fica POR CIMA (não há teste de profundidade).
        self.objetos = [
            Estrelas(self.r),
            Sol(self.r),
            Lua(self.r),
            Nuvem(self.r, x=-0.55, y=0.74, tamanho=1.0, velocidade=0.05),
            Nuvem(self.r, x=0.15, y=0.46, tamanho=0.75, velocidade=0.08),
            Chao(self.r),
            self.arvore,
            self.casa,
            self.sra_coracao,
            self.sr_coracao,
            Chuva(self.r),   # por último: a chuva cai na frente de tudo
        ]

    # ------------------------------------------------------------------ teclado
    def tecla(self, window, key, scancode, action, mods):
        """Callback de teclado: o GLFW a chama uma vez por evento (slides04, p.81).
        É registrada em main.py com glfw.set_key_callback(window, cena.tecla)."""
        if action != glfw.PRESS and action != glfw.REPEAT:
            return   # ignora o soltar da tecla (RELEASE)

        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
            return

        # Setas aceitam PRESS e REPEAT: segurar a tecla = movimento contínuo,
        # exatamente como no 06_senhor_coracao.py.
        if key in SETAS:
            if mods & glfw.MOD_SHIFT:          # Shift apertado junto?
                self.sr_coracao.andar(key)
            else:
                self.sr_coracao.olhar(key)
            return

        # As demais teclas são "liga/desliga": só reagem ao toque (PRESS).
        # Com REPEAT, segurar a tecla ficaria alternando sem parar.
        if action != glfw.PRESS:
            return
        if key == glfw.KEY_D:
            self.estado.noite = not self.estado.noite
            self.registrar("Modo noite" if self.estado.noite else "Modo dia")
        elif key == glfw.KEY_R:
            self.estado.chovendo = not self.estado.chovendo
            self.registrar("Chuva ligada" if self.estado.chovendo else "Chuva desligada")
        elif key == glfw.KEY_C:
            self.casa.proxima_cor()
            self.registrar("Nova cor da casa")
        elif key == glfw.KEY_A:
            self.registrar(f"Árvore: {self.arvore.proxima_estacao()}")
        elif key == glfw.KEY_P:
            self.pedir_captura = True   # salva no fim do próximo desenhar()

    # ----------------------------------------------------------- estado global
    def cor_do_ceu(self):
        """A cor do fundo (ctx.clear) depende dos dois estados globais."""
        if self.estado.noite:
            return CEU_NOITE_CHUVA if self.estado.chovendo else CEU_NOITE
        return CEU_DIA_CHUVA if self.estado.chovendo else CEU_DIA

    def atenuacao(self):
        """O fator enviado ao shader pelo uniform u_atenuacao."""
        fator = ATENUACAO_NOITE if self.estado.noite else 1.0
        if self.estado.chovendo:
            fator *= ATENUACAO_CHUVA
        return fator

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt):
        """Avança o tempo e deixa cada objeto se atualizar (animações)."""
        self.estado.tempo += dt
        for objeto in self.objetos:
            objeto.atualizar(dt, self.estado)

    def desenhar(self):
        """Desenha o quadro inteiro no backbuffer, do fundo para a frente."""
        self.estado.cor_do_ceu = self.cor_do_ceu()
        self.r.comecar_quadro(self.estado.cor_do_ceu, self.atenuacao())
        for objeto in self.objetos:
            objeto.desenhar(self.r, self.estado)

        if self.pedir_captura:   # o quadro está completo: hora de fotografar
            self.pedir_captura = False
            self.salvar_captura()

    # -------------------------------------------------------------- utilidades
    def salvar_captura(self):
        nome = ("noite" if self.estado.noite else "dia") + ("_chuva" if self.estado.chovendo else "")
        caminho = save_screenshot(self.ctx, PASTA_CAPTURAS, nome)
        self.registrar(f"Captura salva em {caminho}")

    def registrar(self, mensagem):
        """Mostra no terminal o que aconteceu, com data e hora (utils do projeto)."""
        print(f"{get_date_prefix()} {mensagem}")

    def liberar(self):
        """Libera da VRAM tudo o que a cena criou."""
        self.r.liberar()
