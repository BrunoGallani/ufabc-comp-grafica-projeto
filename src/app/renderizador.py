"""
Concentra tudo o que interage com a placa de vídeo (GPU):

- o programa de shaders (vertex + fragment), lido dos arquivos em `shaders/`;
- a criação das malhas: VBO, VAO e, quando houver, EBO;
- as *draw calls*.

Os objetos da cena nunca chamam o moderngl diretamente. Eles delegam esta tarefa ao
:class:`Renderizador`.
"""
import moderngl
import numpy as np

from config import COR_FAIXAS
from geometria import curva_circulo
from utils.shader_utils import get_shaders
from typing import Any

class Malha:
    """
    Uma geometria que já está na memória da GPU.

    Possui os seguintes atributos:

    - **VBO:** os bytes dos vértices na VRAM;
    - **EBO:** os índices (opcional), para reaproveitar vértices;
    - **VAO:** a "receita de leitura" do VBO: cada vértice são 4 floats (`'4f'`)
      que alimentam a entrada `vPosition` do vertex shader;
    - **Primitiva:** como os vértices viram forma (`TRIANGLES`, `TRIANGLE_FAN`...).
    """

    def __init__(self, vbo: moderngl.Buffer, vao: moderngl.VertexArray, primitiva: int,
                 ebo: moderngl.Buffer | None = None) -> None:
        self.vbo = vbo
        self.vao = vao
        self.primitiva = primitiva
        self.ebo = ebo

    def liberar(self) -> None:
        """
        Devolve a VRAM ocupada pela malha.

        O moderngl não libera os objetos sozinho. A liberação segue a ordem inversa
        da criação, pois o VAO depende do VBO e do EBO.
        """
        self.vao.release()
        if self.ebo is not None:
            self.ebo.release()
        self.vbo.release()

class Renderizador:
    """
    Intermediário entre os objetos da cena e a GPU.

    Um único programa de shaders desenha a cena inteira: o vertex shader calcula
    `posição * u_escala + u_deslocamento` e o fragment shader, `u_cor * u_atenuacao`.
    Cada forma é enviada uma única vez à VRAM e posicionada pelos uniforms.

    Possui os seguintes atributos:

    - **Contexto:** o contexto `moderngl` da janela;
    - **Programa:** o programa de shaders compilado;
    - **Atenuação:** o valor de `u_atenuacao` do quadro atual;
    - **Círculo:** a malha compartilhada mais usada na cena.
    """

    __slots__ = ("ctx", "prog", "_malhas", "atenuacao", "circulo")

    def __init__(self, ctx: moderngl.Context) -> None:
        self.ctx = ctx

        vertex_shader, fragment_shader = get_shaders()
        self.prog: moderngl.Program = ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )

        self._malhas: list[Malha] = []
        self.atenuacao: float = 1.0

        # O círculo é a geometria mais usada na cena
        self.circulo = self.criar_malha(curva_circulo(), moderngl.TRIANGLE_FAN)

    def criar_malha(self, vertices: np.ndarray, primitiva: int,
                    indices: np.ndarray | None = None) -> Malha:
        """
        Copia os vértices (e os índices, se houver) da RAM para a VRAM e monta o VAO.

        A malha criada fica registrada para ser liberada em :meth:`liberar`.
        """
        vbo = self.ctx.buffer(vertices.tobytes())
        ebo = self.ctx.buffer(indices.tobytes()) if indices is not None else None
        # '4f' = cada vértice são 4 floats, entregues à entrada vPosition.
        vao = self.ctx.vertex_array(self.prog, [(vbo, '4f', 'vPosition')],
                                    index_buffer=ebo)
        malha = Malha(vbo, vao, primitiva, ebo)
        self._malhas.append(malha)
        return malha

    def ajustar(self, nome: str, valor: Any) -> None:
        """
        Escreve em um uniform, se ele existir.

        O compilador GLSL descarta uniforms que não influenciam o resultado, e
        `prog[nome]` lançaria `KeyError`. Com `prog.get(nome, None)`, o programa
        tolera essa situação.
        """
        uniforme = self.prog.get(nome, None)
        if uniforme is not None:
            uniforme.value = valor

    def ajustar_viewport(self, largura: int, altura: int) -> None:
        """
        Faz a cena ocupar o maior quadrado centralizado que cabe na tela.

        A cena é desenhada em NDC (de -1 a 1 nos dois eixos), e o viewport é o
        retângulo de pixels para onde esse quadrado é levado. Se o viewport fosse
        a tela inteira de um monitor 16:9, tudo seria esticado na horizontal e os
        círculos virariam elipses. Com um viewport quadrado, as proporções se
        mantêm e sobram faixas nas laterais, pintadas em :meth:`comecar_quadro`.
        """
        if largura == 0 or altura == 0:   # janela minimizada: nada a ajustar
            return
        lado = min(largura, altura)
        self.ctx.viewport = ((largura - lado) // 2, (altura - lado) // 2, lado, lado)

    def comecar_quadro(self, cor_fundo: tuple[float, float, float, float],
                       atenuacao: float) -> None:
        """
        Limpa a tela e escreve `u_atenuacao` uma única vez por quadro.

        Um uniform mantém o valor até ser sobrescrito, então todos os desenhos do
        quadro usam a mesma atenuação.
        """
        # O clear ignora o viewport e pinta a tela inteira: primeiro tudo com a
        # cor das faixas e depois, só no quadrado da cena, a cor do céu.
        self.ctx.clear(*COR_FAIXAS)
        self.ctx.clear(*cor_fundo, viewport=self.ctx.viewport)
        self.atenuacao = atenuacao
        self.ajustar('u_atenuacao', atenuacao)

    def desenhar(self, malha: Malha, escala: float, deslocamento: tuple[float, float],
                 cor: tuple[float, float, float, float], primitiva: int | None = None) -> None:
        """
        Carrega os uniforms de um desenho e dispara a *draw call*.

        A primitiva vem da malha, a menos que outra seja passada: assim a mesma
        malha pode ser desenhada de formas diferentes (ex.: o telhado preenchido
        e o seu contorno).
        """
        self.ajustar('u_escala', escala)
        self.ajustar('u_deslocamento', deslocamento)
        self.ajustar('u_cor', cor)
        malha.vao.render(primitiva if primitiva is not None else malha.primitiva)

    def desenhar_emissivo(self, malha: Malha, escala: float, deslocamento: tuple[float, float],
                          cor: tuple[float, float, float, float]) -> None:
        """
        Desenha algo com luz própria (lua, estrelas, janelas acesas).

        A atenuação vai a 1.0 só durante este desenho e, logo depois, volta ao valor
        do quadro. Sem essa restauração, todos os desenhos seguintes também
        ficariam "acesos", pois o uniform guarda o último valor escrito.
        """
        self.ajustar('u_atenuacao', 1.0)
        self.desenhar(malha, escala, deslocamento, cor)
        self.ajustar('u_atenuacao', self.atenuacao)

    def desenhar_translucido(self, malha: Malha, escala: float, deslocamento: tuple[float, float],
                             cor: tuple[float, float, float, float]) -> None:
        """
        Desenha algo por cima da cena, como o painel de informações (tecla I).

        Há duas diferenças em relação a :meth:`desenhar`:

        - **Transparência:** com o *blending* ligado, o alpha da cor passa a valer, e a
          cor do pixel vira `alpha * cor + (1 - alpha) * cor que já estava lá`. Ele só
          fica ligado durante este desenho: o resto da cena tem alpha 1;
        - **Sem atenuação:** como em :meth:`desenhar_emissivo`, a noite e a chuva
          não escurecem o desenho.
        """
        self.ctx.enable(moderngl.BLEND)
        # Os dois últimos fatores valem para o canal alpha: o alpha da tela
        # continua 1, para que a janela não fique transparente no compositor.
        self.ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
                               moderngl.ZERO, moderngl.ONE)
        self.desenhar_emissivo(malha, escala, deslocamento, cor)
        self.ctx.disable(moderngl.BLEND)

    def liberar_malha(self, malha: Malha) -> None:
        """
        Libera uma malha antes do fim do programa: é o caso do texto do painel de
        informações, refeito sempre que o estado da cena muda.
        """
        self._malhas.remove(malha)
        malha.liberar()

    def liberar(self) -> None:
        """
        Libera todas as malhas e o programa de shaders, na ordem inversa da criação.
        """
        for malha in reversed(self._malhas):
            malha.liberar()
        self.prog.release()
