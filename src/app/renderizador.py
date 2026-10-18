"""
Tudo que fala com a GPU fica aqui: shaders, malhas (VBO/VAO/EBO) e draw calls.
Os objetos da cena nunca chamam o moderngl direto.
"""
from typing import Any

import moderngl
import numpy as np

from config import COR_FAIXAS
from geometria import curva_circulo
from utils.shader_utils import get_shaders

class Malha:
    """Uma geometria já na VRAM, com a primitiva padrão pra desenhar."""

    def __init__(self, vbo: moderngl.Buffer, vao: moderngl.VertexArray, primitiva: int,
                 ebo: moderngl.Buffer | None = None) -> None:
        self.vbo = vbo
        self.vao = vao
        self.primitiva = primitiva
        self.ebo = ebo

    def liberar(self) -> None:
        # O moderngl não libera nada sozinho. O VAO vai primeiro porque usa o VBO e o EBO.
        self.vao.release()
        if self.ebo is not None:
            self.ebo.release()
        self.vbo.release()

class Renderizador:
    """
    Um único programa de shaders desenha a cena inteira: cada forma vai pra VRAM
    uma vez só e é posicionada pelos uniforms (posição girada por u_angulo e depois
    * u_escala + u_deslocamento, cor * u_atenuacao).
    """

    def __init__(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx

        vertex_shader, fragment_shader = get_shaders()
        self.prog: moderngl.Program = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

        self._malhas: list[Malha] = []   # tudo que foi criado, pra liberar no fim
        self.atenuacao: float = 1.0      # u_atenuacao do quadro atual

        self.circulo = self.criar_malha(curva_circulo(), moderngl.TRIANGLE_FAN)

    def criar_malha(self, vertices: np.ndarray, primitiva: int,
                    indices: np.ndarray | None = None) -> Malha:
        """Sobe os vértices (e os índices, se tiver) pra VRAM e monta o VAO."""
        vbo = self.ctx.buffer(vertices.tobytes())
        ebo = self.ctx.buffer(indices.tobytes()) if indices is not None else None
        # '4f': cada vértice são 4 floats, que vão pro vPosition.
        vao = self.ctx.vertex_array(self.prog, [(vbo, '4f', 'vPosition')],
                                    index_buffer=ebo)
        malha = Malha(vbo, vao, primitiva, ebo)
        self._malhas.append(malha)
        return malha

    def ajustar(self, nome: str, valor: Any) -> None:
        # O GLSL descarta uniform que não é usado, e aí prog[nome] daria KeyError.
        uniforme = self.prog.get(nome, None)
        if uniforme is not None:
            uniforme.value = valor

    def ajustar_viewport(self, largura: int, altura: int) -> None:
        """
        Desenha no maior quadrado centralizado da tela. Com um viewport retangular a
        cena estica e os círculos viram elipses; as sobras dos lados são pintadas
        em comecar_quadro.
        """
        if largura == 0 or altura == 0:   # janela minimizada
            return
        lado = min(largura, altura)
        self.ctx.viewport = ((largura - lado) // 2, (altura - lado) // 2, lado, lado)

    def comecar_quadro(self, cor_fundo: tuple[float, float, float, float],
                       atenuacao: float) -> None:
        # O clear ignora o viewport: pinta tudo com a cor das faixas e depois só o
        # quadrado da cena com a cor do céu.
        self.ctx.clear(*COR_FAIXAS)
        self.ctx.clear(*cor_fundo, viewport=self.ctx.viewport)
        # O uniform guarda o valor, então basta escrever a atenuação uma vez por quadro.
        self.atenuacao = atenuacao
        self.ajustar('u_atenuacao', atenuacao)

    def desenhar(self, malha: Malha, escala: float, deslocamento: tuple[float, float],
                 cor: tuple[float, float, float, float], primitiva: int | None = None,
                 angulo: float = 0.0) -> None:
        """
        Escreve os uniforms e desenha. `primitiva`, se vier, troca a da malha. O
        `angulo` (radianos) vai sempre, mesmo 0: o uniform guarda o último valor, e
        senão a rotação de um raio passaria pros desenhos seguintes.
        """
        self.ajustar('u_escala', escala)
        self.ajustar('u_angulo', angulo)
        self.ajustar('u_deslocamento', deslocamento)
        self.ajustar('u_cor', cor)
        malha.vao.render(primitiva if primitiva is not None else malha.primitiva)

    def desenhar_emissivo(self, malha: Malha, escala: float, deslocamento: tuple[float, float],
                          cor: tuple[float, float, float, float]) -> None:
        """Pra quem tem luz própria (lua, estrelas, janelas acesas): ignora a atenuação."""
        self.ajustar('u_atenuacao', 1.0)
        self.desenhar(malha, escala, deslocamento, cor)
        self.ajustar('u_atenuacao', self.atenuacao)   # senão o resto do quadro fica "aceso"

    def desenhar_translucido(self, malha: Malha, escala: float, deslocamento: tuple[float, float],
                             cor: tuple[float, float, float, float]) -> None:
        """Desenha por cima com transparência (o painel), também sem atenuação."""
        self.ctx.enable(moderngl.BLEND)
        # Os dois últimos fatores deixam o alpha da tela em 1; senão a janela fica
        # transparente no compositor.
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
                               moderngl.ZERO, moderngl.ONE)
        self.desenhar_emissivo(malha, escala, deslocamento, cor)
        self.ctx.disable(moderngl.BLEND)

    def liberar_malha(self, malha: Malha) -> None:
        """Libera uma malha antes do fim (o texto do painel é refeito quando muda)."""
        self._malhas.remove(malha)
        malha.liberar()

    def liberar(self) -> None:
        for malha in reversed(self._malhas):
            malha.liberar()
        self.prog.release()
