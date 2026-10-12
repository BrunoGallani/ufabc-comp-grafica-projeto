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

    def comecar_quadro(self, cor_fundo: tuple[float, float, float, float],
                       atenuacao: float) -> None:
        """
        Limpa a tela e escreve `u_atenuacao` uma única vez por quadro.

        Um uniform mantém o valor até ser sobrescrito, então todos os desenhos do
        quadro usam a mesma atenuação.
        """
        self.ctx.clear(*cor_fundo)
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

    def liberar(self) -> None:
        """
        Libera todas as malhas e o programa de shaders, na ordem inversa da criação.
        """
        for malha in reversed(self._malhas):
            malha.liberar()
        self.prog.release()
