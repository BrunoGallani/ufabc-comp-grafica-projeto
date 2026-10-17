"""O estado global da cena e a classe que orquestra tudo."""
from dataclasses import dataclass

import glfw
import moderngl

from config import (ATENUACAO_CHUVA, ATENUACAO_NOITE, CEU_DIA, CEU_DIA_CHUVA,
                    CEU_NOITE, CEU_NOITE_CHUVA, Y_CHAO, Estacao)
from objetos.arvore import Arvore
from objetos.astros import Estrelas, Lua, Sol
from objetos.casa import Casa
from objetos.chao import Chao
from objetos.chuva import Chuva
from objetos.flores import Flores
from objetos.nuvem import Nuvem
from objetos.painel_info import PainelInfo
from objetos.raios_verao import RaiosVerao
from objetos.senhor_coracao import SenhorCoracao
from objetos.sra_coracao import SraCoracao
from renderizador import Renderizador
from utils.keyboard_utils import AJUDA_TECLAS, SETAS, Key
from utils.log_utils import Log
from utils.screenshot_utils import save_screenshot
from utils.window_utils import toggle_fullscreen


@dataclass
class EstadoCena:
    """A Cena muda, os objetos só leem."""
    noite: bool = False                 # tecla D
    chovendo: bool = False              # tecla R
    estacao: Estacao = Estacao.VERAO    # tecla E
    painel_visivel: bool = False        # tecla I
    tempo: float = 0.0                  # segundos desde o início, pras animações
    cor_do_ceu: tuple[float, float, float, float] = CEU_DIA   # recalculada a cada quadro


class Cena:
    """Cria os objetos, trata o teclado e desenha cada quadro."""

    def __init__(self, ctx: moderngl.Context, window: 'glfw._GLFWwindowPointerT') -> None:
        self.ctx = ctx
        self.window = window
        self.renderizador = Renderizador(ctx)
        self.estado = EstadoCena()
        self.pedir_captura = False   # tecla P: salva o próximo quadro

        # O Sr. Coração e a casa ficam guardados porque recebem comandos do teclado.
        self.sr_coracao = SenhorCoracao(self.renderizador, posicao=(-0.06, Y_CHAO + 0.19), tamanho=0.40)
        sra_coracao = SraCoracao(self.renderizador, alvo=self.sr_coracao,
                                 posicao=(0.38, Y_CHAO + 0.16), tamanho=0.34)
        self.casa = Casa(self.renderizador)
        arvore = Arvore(self.renderizador)

        # Ordem de desenho, do fundo pra frente: quem vem depois fica por cima
        # (não tem teste de profundidade).
        self.objetos = [
            Estrelas(self.renderizador),
            Sol(self.renderizador),
            RaiosVerao(self.renderizador),
            Lua(self.renderizador),
            Nuvem(self.renderizador, x=-0.55, y=0.74, tamanho=1.0, velocidade=0.05),
            Nuvem(self.renderizador, x=0.15, y=0.46, tamanho=0.75, velocidade=0.08),
            Chao(self.renderizador),
            arvore,
            Flores(self.renderizador, arvore=arvore),
            self.casa,
            sra_coracao,
            self.sr_coracao,
            Chuva(self.renderizador),
            PainelInfo(self.renderizador, self.informacoes),
        ]

        # Tecla nova = um método + uma linha aqui.
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
            Key.ESC: self.fechar,
        }

    # ------------------------------------------------------------------ teclado
    def tecla(self, window: 'glfw._GLFWwindowPointerT', key: int, scancode: int,
              action: int, mods: int) -> None:
        """Callback de teclado do GLFW (registrado no main.py)."""
        if action == glfw.RELEASE:
            return

        # As setas aceitam REPEAT (segurou, continua andando/olhando); o resto só
        # PRESS, senão segurar a tecla fica alternando sem parar.
        if key in SETAS:
            if mods & glfw.MOD_SHIFT:
                self.sr_coracao.andar(*SETAS[key])
            else:
                self.sr_coracao.olhar(*SETAS[key])
        elif action == glfw.PRESS and key in self.acoes:
            self.acoes[key]()

    def mostrar_ajuda(self) -> None:
        Log.d(AJUDA_TECLAS)

    def mostrar_hardware(self) -> None:
        info = self.ctx.info
        Log.d("Propriedades do driver/hardware:\n"
              f"GL_VERSION  : {info['GL_VERSION']}\n"
              f"GL_RENDERER : {info['GL_RENDERER']}\n"
              f"GL_VENDOR   : {info['GL_VENDOR']}\n"
              f"GL (código de versão) : {self.ctx.version_code}")

    def alternar_painel(self) -> None:
        self.estado.painel_visivel = not self.estado.painel_visivel
        Log.d("Painel de informações ligado" if self.estado.painel_visivel
              else "Painel de informações desligado")

    def alternar_noite(self) -> None:
        self.estado.noite = not self.estado.noite
        Log.d("Modo noite" if self.estado.noite else "Modo dia")

    def alternar_chuva(self) -> None:
        self.estado.chovendo = not self.estado.chovendo
        Log.d("Chuva ligada" if self.estado.chovendo else "Chuva desligada")

    def trocar_cor_casa(self) -> None:
        self.casa.proxima_cor()
        Log.d(f"Casa: cor '{self.casa.nome_cor}' {self.casa.cor_parede}")

    def trocar_estacao(self) -> None:
        self.estado.estacao = self.estado.estacao.proxima()
        Log.d(f"Estação: {self.estado.estacao.value}")

    def alternar_tela_cheia(self) -> None:
        # O novo tamanho chega logo depois, pelo callback redimensionar.
        tela_cheia = toggle_fullscreen(self.window)
        Log.d("Tela cheia" if tela_cheia else "Modo janela")

    def agendar_captura(self) -> None:
        self.pedir_captura = True

    def fechar(self) -> None:
        glfw.set_window_should_close(self.window, True)

    # ------------------------------------------------------------------ janela
    def redimensionar(self, window: 'glfw._GLFWwindowPointerT', largura: int,
                      altura: int) -> None:
        """Callback do GLFW quando a área de desenho muda de tamanho (em pixels)."""
        self.renderizador.ajustar_viewport(largura, altura)

    # ----------------------------------------------------------- estado global
    def cor_do_ceu(self) -> tuple[float, float, float, float]:
        if self.estado.noite:
            return CEU_NOITE_CHUVA if self.estado.chovendo else CEU_NOITE
        return CEU_DIA_CHUVA if self.estado.chovendo else CEU_DIA

    def informacoes(self) -> list[tuple[str, str]]:
        """Pares (rótulo, valor) do painel (tecla I)."""
        return [
            ("Horário", "noite" if self.estado.noite else "dia"),
            ("Chuva", "ligada" if self.estado.chovendo else "desligada"),
            ("Estação", self.estado.estacao.value),
            ("Cor da casa", self.casa.nome_cor),
            ("Tela cheia", "sim" if glfw.get_window_monitor(self.window) else "não"),
        ]

    def atenuacao(self) -> float:
        """Valor do u_atenuacao: a noite e a chuva escurecem a cena."""
        fator = ATENUACAO_NOITE if self.estado.noite else 1.0
        if self.estado.chovendo:
            fator *= ATENUACAO_CHUVA
        return fator

    # -------------------------------------------------------------- cada quadro
    def atualizar(self, dt: float) -> None:
        self.estado.tempo += dt
        for objeto in self.objetos:
            objeto.atualizar(dt, self.estado)

    def desenhar(self) -> None:
        self.estado.cor_do_ceu = self.cor_do_ceu()
        self.renderizador.comecar_quadro(self.estado.cor_do_ceu, self.atenuacao())
        for objeto in self.objetos:
            objeto.desenhar(self.renderizador, self.estado)

        # A captura sai aqui: o quadro já tá completo e ainda não teve swap_buffers.
        if self.pedir_captura:
            self.pedir_captura = False
            save_screenshot(self)

    def liberar(self) -> None:
        self.renderizador.liberar()
