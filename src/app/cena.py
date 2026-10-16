"""
Módulo orquestrador do programa. Possui as seguintes classes:

- :class:`EstadoCena`
- :class:`Cena`
"""

import glfw
import moderngl

from config import (ATENUACAO_CHUVA, ATENUACAO_NOITE, CEU_DIA, CEU_DIA_CHUVA,
                    CEU_NOITE, CEU_NOITE_CHUVA, Y_CHAO, Estacao)
from objetos.arvore import Arvore
from objetos.astros import Estrelas, Lua, Sol
from objetos.casa import PALETA_PAREDE, Casa
from objetos.chao import Chao
from objetos.chuva import Chuva
from objetos.flores import Flores
from objetos.nuvem import Nuvem
from objetos.painel_info import PainelInfo
from objetos.raios_verao import RaiosVerao
from objetos.senhor_coracao import SenhorCoracao
from objetos.sra_coracao import SraCoracao
from renderizador import Renderizador
from utils.screenshot_utils import save_screenshot
from utils.keyboard_utils import AJUDA_TECLAS, Key
from utils.log_utils import log_hardware_properties, Log
from utils.window_utils import toggle_fullscreen

class EstadoCena:
    """
    Estado da cena: a cena altera, os objetos só leem.

    Possui os seguintes atributos:

    - **Noite:** define se está dia ou noite (controle pela tecla D);
    - **Chovendo:** define se está chovendo ou não (controle pela tecla R);
    - **Estação:** define a estação do ano (controle pela tecla E);
    - **Painel:** define se o painel com o estado da cena aparece (controle pela tecla I);
    - **Tempo:** representa os segundos transcorridos desde o início (é usado em animações);
    - **Cor do céu:** define a cor do céu.
    """

    def __init__(self) -> None:
        self.noite = False
        self.chovendo = False
        self.estacao = Estacao.VERAO
        self.painel = False
        self.tempo = 0.0
        self.cor_do_ceu = CEU_DIA

class Cena:
    """
    Cria os objetos da cena, trata o teclado e desenha cada quadro.

    Possui os seguintes atributos:

    - **Contexto:** o contexto `moderngl` da janela;
    - **Janela:** a janela do GLFW, usada pela tecla F (tela cheia);
    - **Renderizador:** o :class:`Renderizador`, único ponto de contato com a GPU;
    - **Estado:** o :class:`EstadoCena`, alterado pelas teclas e lido pelos objetos;
    - **Pedido de captura:** quando verdadeiro, o próximo quadro é salvo em PNG (tecla P);
    - **Objetos:** os objetos da cena, na ordem em que são desenhados;
    - **Ações:** liga cada tecla de ação ao método que a trata.

    O Sr. Coração e a casa também ficam em atributos próprios, pois recebem
    comandos do teclado; a árvore, porque as flores precisam saber onde ela está.
    """

    __slots__ = ("ctx", "window", "render", "estado",
                 "pedir_captura", "sr_coracao", "sra_coracao",
                 "casa", "arvore", "objetos", "acoes")

    def __init__(self, ctx: moderngl.Context, window: 'glfw._GLFWwindowPointerT') -> None:
        self.ctx = ctx
        self.window = window
        self.render = Renderizador(ctx)
        self.estado = EstadoCena()
        self.pedir_captura = False

        self.sr_coracao = SenhorCoracao(self.render, posicao=(-0.06, Y_CHAO + 0.19), tamanho=0.40)
        self.sra_coracao = SraCoracao(self.render, alvo=self.sr_coracao,
                                      posicao=(0.38, Y_CHAO + 0.16), tamanho=0.34)
        self.casa = Casa(self.render)
        self.arvore = Arvore(self.render)

        # A ORDEM desta lista é a ordem de desenho: do fundo para a frente.
        # Quem é desenhado depois fica POR CIMA (não há teste de profundidade).
        self.objetos = [
            Estrelas(self.render),
            Sol(self.render),
            RaiosVerao(self.render),
            Lua(self.render),
            Nuvem(self.render, x=-0.55, y=0.74, tamanho=1.0, velocidade=0.05),
            Nuvem(self.render, x=0.15, y=0.46, tamanho=0.75, velocidade=0.08),
            Chao(self.render),
            self.arvore,
            Flores(self.render, arvore=self.arvore),   # por cima da grama e da copa
            self.casa,
            self.sra_coracao,
            self.sr_coracao,
            Chuva(self.render, self.estado),   # a chuva cai na frente de tudo...
            PainelInfo(self.render, self.informacoes),   # ...menos do painel (tecla I)
        ]

        # Teclas de ação: cada uma aponta para o método que a trata.
        # Uma tecla nova só precisa de um método e de uma linha aqui.
        self.acoes = {
            Key.K: self.mostrar_ajuda,
            Key.H: self.mostrar_hardware,
            Key.I: self.alternar_painel,
            Key.D: self.alternar_noite,
            Key.R: self.alternar_chuva,
            Key.C: self.trocar_cor_casa,
            Key.E: self.trocar_estacao,
            Key.F: self.alternar_tela_cheia,
            Key.P: self.agendar_captura,
        }

    # ------------------------------------------------------------------ teclado
    def tecla(self, window: 'glfw._GLFWwindowPointerT', key: int, scancode: int,
              action: int, mods: int) -> None:
        """
        Callback de teclado: o GLFW a chama uma vez por evento.

        É registrada em `main.py` com `glfw.set_key_callback(window, cena.tecla)`.
        As setas aceitam `PRESS` e `REPEAT` (segurar a tecla gera movimento contínuo);
        as demais teclas são do tipo liga/desliga e só reagem a `PRESS`: cada uma
        chama o seu método, procurado no dicionário `acoes`.
        """
        if action == glfw.RELEASE:
            return

        if key == Key.ESC:
            glfw.set_window_should_close(window, True)
            return

        if key in Key.setas():
            if mods & glfw.MOD_SHIFT:     # Shift apertado junto
                self.sr_coracao.andar(key)
            else:
                self.sr_coracao.olhar(key)
            return

        # Com REPEAT, segurar a tecla ficaria alternando sem parar.
        if action == glfw.REPEAT:
            return

        acao = self.acoes.get(key)
        if acao is not None:   # teclas sem ação são ignoradas
            acao()

    def mostrar_ajuda(self) -> None:
        """
        Exibe no terminal o tutorial com as teclas de controle (tecla K).
        """
        Log.d(AJUDA_TECLAS)

    def mostrar_hardware(self) -> None:
        """
        Exibe no terminal as informações do driver e da placa de vídeo (tecla H).
        """
        Log.d(f"Propriedades do driver/hardware:\n{log_hardware_properties(self.ctx)}")

    def alternar_painel(self) -> None:
        """
        Mostra ou esconde o painel com o estado da cena (tecla I).
        """
        self.estado.painel = not self.estado.painel
        Log.d("Painel de informações ligado" if self.estado.painel
              else "Painel de informações desligado")

    def alternar_noite(self) -> None:
        """
        Alterna entre dia e noite (tecla D).
        """
        self.estado.noite = not self.estado.noite
        Log.d("Modo noite" if self.estado.noite else "Modo dia")

    def alternar_chuva(self) -> None:
        """
        Liga ou desliga a chuva (tecla R).
        """
        self.estado.chovendo = not self.estado.chovendo
        Log.d("Chuva ligada" if self.estado.chovendo else "Chuva desligada")

    def trocar_cor_casa(self) -> None:
        """
        Passa a casa para a próxima cor da paleta (tecla C).
        """
        Log.d(f"Casa: cor '{self.casa.proxima_cor()}' {PALETA_PAREDE[self.casa.indice_cor][1]}")

    def trocar_estacao(self) -> None:
        """
        Passa a cena para a próxima estação do ano (tecla E).
        """
        self.estado.estacao = self.estado.estacao.proxima()
        Log.d(f"Estação: {self.estado.estacao.value}")

    def alternar_tela_cheia(self) -> None:
        """
        Alterna entre janela e tela cheia (tecla F).

        O novo tamanho chega logo depois, pelo callback :meth:`redimensionar`.
        """
        tela_cheia = toggle_fullscreen(self.window)
        Log.d("Tela cheia" if tela_cheia else "Modo janela")

    def agendar_captura(self) -> None:
        """
        Pede que o próximo quadro seja salvo em PNG (tecla P).
        """
        self.pedir_captura = True

    # ------------------------------------------------------------------ janela
    def redimensionar(self, window: 'glfw._GLFWwindowPointerT', largura: int,
                      altura: int) -> None:
        """
        Callback de framebuffer: o GLFW a chama quando o tamanho da área de
        desenho muda, ou seja, ao entrar e ao sair da tela cheia.

        É registrada em `main.py` com
        `glfw.set_framebuffer_size_callback(window, cena.redimensionar)`.
        `largura` e `altura` vêm em pixels, que podem ser mais numerosos do que
        o tamanho da janela em telas de alta densidade (ex.: Retina).
        """
        self.render.ajustar_viewport(largura, altura)

    # ----------------------------------------------------------- estado global
    def cor_do_ceu(self) -> tuple[float, float, float, float]:
        """
        Retorna a cor do fundo (usada no `ctx.clear`), que depende de ser dia ou
        noite e de estar chovendo ou não.
        """
        if self.estado.noite:
            return CEU_NOITE_CHUVA if self.estado.chovendo else CEU_NOITE
        return CEU_DIA_CHUVA if self.estado.chovendo else CEU_DIA

    def informacoes(self) -> list[tuple[str, str]]:
        """
        Retorna os pares (rótulo, valor) exibidos no painel de informações (tecla I).
        """
        return [
            ("Horário", "noite" if self.estado.noite else "dia"),
            ("Chuva", "ligada" if self.estado.chovendo else "desligada"),
            ("Estação", self.estado.estacao.value),
            ("Cor da casa", PALETA_PAREDE[self.casa.indice_cor][0]),
            ("Tela cheia", "sim" if glfw.get_window_monitor(self.window) else "não"),
        ]

    def atenuacao(self) -> float:
        """
        Retorna o fator enviado ao fragment shader pelo uniform `u_atenuacao`.

        A noite e a chuva escurecem a cena; os dois fatores se multiplicam.
        """
        fator = ATENUACAO_NOITE if self.estado.noite else 1.0
        if self.estado.chovendo:
            fator *= ATENUACAO_CHUVA
        return fator

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt: float) -> None:
        """
        Avança o tempo em `dt` segundos e atualiza cada objeto (animações).
        """
        self.estado.tempo += dt
        for objeto in self.objetos:
            objeto.atualizar(dt, self.estado)

    def desenhar(self) -> None:
        """
        Desenha o quadro inteiro no *backbuffer*, do fundo para a frente.

        Se uma captura foi pedida (tecla P), ela é salva ao final, com o quadro completo.
        """
        self.estado.cor_do_ceu = self.cor_do_ceu()
        self.render.comecar_quadro(self.estado.cor_do_ceu, self.atenuacao())
        for objeto in self.objetos:
            objeto.desenhar(self.render, self.estado)

        if self.pedir_captura:
            self.pedir_captura = False
            save_screenshot(self)

    def liberar(self) -> None:
        """
        Libera da VRAM tudo o que a cena criou.
        """
        self.render.liberar()
