"""
Renderizador: o "lado da GPU".

Concentra tudo o que conversa com a placa de vídeo:
- o programa de shaders (vertex + fragment), lido dos arquivos em shaders/;
- a criação das malhas: VBO, VAO e, quando houver, EBO (slides04, p.44 e p.73);
- a escrita dos uniforms e as chamadas de desenho (draw calls).

Os objetos da cena nunca chamam o moderngl diretamente. Eles pedem ao
Renderizador: "desenhe esta malha, deste tamanho, neste lugar, com esta cor".
Os métodos ajustar() e desenhar() são as funções de mesmo nome do
06_senhor_coracao.py, agora dentro de uma classe.

Um único programa de shaders desenha a cena INTEIRA: os shaders do Sr. Coração
(copiados sem alteração) só fazem "posição * escala + deslocamento" e
"cor * atenuação", e isso basta para qualquer forma.
"""
from pathlib import Path

import moderngl

from geometria import curva_circulo, curva_coracao

# Caminho relativo a ESTE arquivo, e não à pasta de onde o terminal foi aberto
# (slides04, p.63). Assim o programa acha os shaders de qualquer lugar.
SHADERS = Path(__file__).parent / "shaders"


class Malha:
    """Uma geometria que já está na memória da GPU.

    - vbo: os bytes dos vértices na VRAM (memória "bruta", sem significado);
    - ebo: os índices (opcional), para reaproveitar vértices;
    - vao: a "receita de leitura": diz que cada vértice são 4 floats ('4f') e
      que eles alimentam a entrada vPosition do vertex shader;
    - primitiva: como os vértices viram forma (TRIANGLES, TRIANGLE_FAN...).
    """

    def __init__(self, vbo, vao, primitiva, ebo=None):
        self.vbo = vbo
        self.vao = vao
        self.primitiva = primitiva
        self.ebo = ebo

    def liberar(self):
        """Devolve a VRAM: o moderngl não faz isso sozinho (slides04, p.61).
        Recomendado: ordem inversa da criação (o VAO usa o VBO e o EBO)."""
        self.vao.release()
        if self.ebo is not None:
            self.ebo.release()
        self.vbo.release()


class Renderizador:
    def __init__(self, ctx):
        self.ctx = ctx

        # O driver compila e liga os dois shaders aqui, em tempo de execução
        # (slides04, p.40). São os arquivos do 06_senhor_coracao.py, intactos.
        self.prog = ctx.program(
            vertex_shader=(SHADERS / "senhor_coracao.vert").read_text(encoding="utf-8"),
            fragment_shader=(SHADERS / "senhor_coracao.frag").read_text(encoding="utf-8"),
        )

        self._malhas = []      # tudo o que for criado, para liberar no fim
        self.atenuacao = 1.0   # valor de u_atenuacao do quadro atual

        # Malhas COMPARTILHADAS: cada uma vai para a VRAM uma única vez e é
        # desenhada muitas vezes por quadro, só mudando os uniforms
        # (reaproveitamento de geometria, slides04, p.107). O círculo é o
        # campeão: olhos, pupilas, sol, lua, estrelas, nuvens, copa da árvore,
        # arco da porta e maçaneta.
        self.coracao = self.criar_malha(curva_coracao(), moderngl.TRIANGLE_FAN)
        self.circulo = self.criar_malha(curva_circulo(), moderngl.TRIANGLE_FAN)

    def criar_malha(self, vertices, primitiva, indices=None):
        """Copia os vértices (e os índices, se houver) da RAM para a VRAM e monta
        o VAO. É o montar() do 06_senhor_coracao.py, agora com EBO opcional."""
        vbo = self.ctx.buffer(vertices.tobytes())
        ebo = self.ctx.buffer(indices.tobytes()) if indices is not None else None
        # '4f' = cada vértice são 4 floats, entregues à entrada vPosition.
        vao = self.ctx.vertex_array(self.prog, [(vbo, '4f', 'vPosition')],
                                    index_buffer=ebo)
        malha = Malha(vbo, vao, primitiva, ebo)
        self._malhas.append(malha)
        return malha

    def ajustar(self, nome, valor):
        """Escreve num uniforme, se ele existir.

        (Igual ao 06_senhor_coracao.py.) O compilador do GLSL descarta um
        uniforme que não influencia o resultado, e prog[nome] daria KeyError
        (slides04, p.135). Com prog.get(nome, None) o programa tolera isso,
        o que é útil quando se comenta linhas do shader em experimentos."""
        uniforme = self.prog.get(nome, None)
        if uniforme is not None:
            uniforme.value = valor

    def comecar_quadro(self, cor_fundo, atenuacao):
        """Início de cada quadro: limpa a tela e escreve u_atenuacao UMA vez.

        Um uniform faz parte do estado do programa e mantém o valor até ser
        sobrescrito (slides04, p.96 e p.108). Por isso basta escrever a
        atenuação uma vez: todos os desenhos do quadro a usam."""
        self.ctx.clear(*cor_fundo)
        self.atenuacao = atenuacao
        self.ajustar('u_atenuacao', atenuacao)

    def desenhar(self, malha, escala, deslocamento, cor, primitiva=None):
        """Carrega os três uniforms daquele desenho e dispara a chamada.

        É o desenhar() do professor, com uma diferença: a primitiva vem da
        malha (ou do parâmetro), porque nem tudo na cena é TRIANGLE_FAN."""
        self.ajustar('u_escala', escala)
        self.ajustar('u_deslocamento', deslocamento)
        self.ajustar('u_cor', cor)
        malha.vao.render(primitiva if primitiva is not None else malha.primitiva)

    def desenhar_emissivo(self, malha, escala, deslocamento, cor):
        """Desenha algo com luz própria (lua, estrelas, janela acesa).

        À noite, u_atenuacao vale 0.35 e escurece tudo. Um objeto emissivo não
        deve escurecer, então trocamos a atenuação para 1.0 só neste desenho
        e, logo depois, devolvemos o valor do quadro. Se esquecêssemos de
        devolver, todos os desenhos seguintes também ficariam "acesos",
        porque o uniform guarda o último valor escrito."""
        self.ajustar('u_atenuacao', 1.0)
        self.desenhar(malha, escala, deslocamento, cor)
        self.ajustar('u_atenuacao', self.atenuacao)

    def liberar(self):
        """Libera todas as malhas e o programa (ordem inversa da criação)."""
        for malha in reversed(self._malhas):
            malha.liberar()
        self.prog.release()
