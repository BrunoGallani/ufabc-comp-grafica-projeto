"""
Projeto: Cena 2D Interativa - Computação Gráfica
Baseado no "Senhor Coração" com expansão em POO.

Teclas: 
  SETAS: Movem o Sr. Coracao pela cena
  D:     Alterna Dia / Noite (sol/lua, fundo e atenuação)
  C:     Muda a cor da Casa dinamicamente
  R:     Liga / Desliga a Chuva
  ESC:   Sai do programa
"""
import sys
import random
import glfw
import moderngl
import numpy as np

# --- CONFIGURAÇÕES GLOBAIS E CORES ---
MAGENTA = (0.85, 0.10, 0.45, 1.0)
BRANCO_OLHO = (1.0, 1.0, 1.0, 1.0)
PRETO = (0.05, 0.05, 0.05, 1.0)
FUNDO_DIA = (0.53, 0.81, 0.92, 1.0)    # Azul céu
FUNDO_NOITE = (0.05, 0.05, 0.12, 1.0)  # Azul escuro
COR_GRAMA = (0.13, 0.55, 0.13, 1.0)
COR_TETO = (0.8, 0.2, 0.2, 1.0)
COR_SOL = (1.0, 0.84, 0.0, 1.0)
COR_LUA = (0.9, 0.9, 0.8, 1.0)
COR_CHUVA = (0.0, 0.0, 1.0, 1.0)

ESCALA_CORPO = 0.4
ESCALA_OLHO, ESCALA_PUPILA = 0.085, 0.040
CENTRO_OLHO = (0.17, 0.20)

# --- SHADERS INLINE (Para facilitar o protótipo único) ---
VERT_SHADER = """
#version 400
in vec4 vPosition;
uniform float u_escala;
uniform vec2 u_deslocamento;
void main() {
    // Aplica escala e depois o deslocamento na tela
    gl_Position = vec4((vPosition.xy * u_escala) + u_deslocamento, 0.0, 1.0);
}
"""

FRAG_SHADER = """
#version 400
uniform vec4 u_cor;
uniform float u_atenuacao;
out vec4 fColor;
void main() {
    // Atenua o brilho da cor base (efeito dia/noite)
    fColor = vec4(u_cor.rgb * u_atenuacao, u_cor.a);
}
"""

# --- FUNÇÕES GERADORAS DE GEOMETRIA (MANTIDAS DO ORIGINAL) ---
def leque(x, y):
    """Empacota uma curva fechada como TRIANGLE_FAN"""
    x = np.concatenate(([0.0], x, [x[0]]))
    y = np.concatenate(([0.0], y, [y[0]]))
    return np.column_stack((x, y, np.zeros_like(x), np.ones_like(x))).astype('f4')

def curva_coracao(n=180):
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = 16.0 * np.sin(t) ** 3
    y = (13.0 * np.cos(t) - 5.0 * np.cos(2 * t) - 2.0 * np.cos(3 * t) - np.cos(4 * t))
    y = y - 0.5 * (y.max() + y.min())
    return leque(x / 17.0, y / 17.0)

def curva_circulo(n=48):
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(np.cos(t), np.sin(t))

# --- NOVAS GEOMETRIAS (USANDO TRIANGLES e LINES) ---
def curva_quadrado():
    """Gera vértices para um quadrado usando 2 triângulos (TRIANGLES)"""
    vertices = np.array([
        [-1.0, -1.0, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [-1.0,  1.0, 0.0, 1.0],
        [-1.0,  1.0, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [ 1.0,  1.0, 0.0, 1.0]
    ], dtype='f4')
    return vertices

def curva_triangulo():
    """Gera vértices para um triângulo (TRIANGLES) - Teto da casa"""
    vertices = np.array([
        [-1.0, -1.0, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [ 0.0,  1.0, 0.0, 1.0]
    ], dtype='f4')
    return vertices

def curva_linha():
    """Gera uma linha simples para a chuva (LINES)"""
    vertices = np.array([
        [0.0, 0.0, 0.0, 1.0], [-0.1, -0.2, 0.0, 1.0]
    ], dtype='f4')
    return vertices

# --- CLASSES DA APLICAÇÃO (POO) ---
class RecursosGL:
    """Gerencia a criação de VBOs e VAOs para reuso"""
    def __init__(self, ctx, prog):
        self.ctx = ctx
        self.prog = prog
        
        self.vao_coracao = self.montar(curva_coracao())
        self.vao_circulo = self.montar(curva_circulo())
        self.vao_quadrado = self.montar(curva_quadrado())
        self.vao_triangulo = self.montar(curva_triangulo())
        self.vao_linha = self.montar(curva_linha())

    def montar(self, vertices):
        vbo = self.ctx.buffer(vertices.tobytes())
        return self.ctx.vertex_array(self.prog, [(vbo, '4f', 'vPosition')])

class ObjetoCena:
    """Classe base para qualquer objeto desenhável na cena"""
    def __init__(self, cena, vao, primitiva=moderngl.TRIANGLE_FAN):
        self.cena = cena
        self.vao = vao
        self.primitiva = primitiva
        self.escala = 1.0
        self.posicao = [0.0, 0.0]
        self.cor = (1.0, 1.0, 1.0, 1.0)

    def desenhar(self):
        self.cena.ajustar_uniforme('u_escala', self.escala)
        self.cena.ajustar_uniforme('u_deslocamento', tuple(self.posicao))
        self.cena.ajustar_uniforme('u_cor', self.cor)
        self.vao.render(self.primitiva)

class SenhorCoracao(ObjetoCena):
    """Encapsula o Sr. Coração, mantendo as proporções e geometria originais"""
    def __init__(self, cena, recursos):
        super().__init__(cena, recursos.vao_coracao)
        self.escala = ESCALA_CORPO
        self.cor = MAGENTA
        self.vao_circulo = recursos.vao_circulo
        self.posicao = [-0.3, -0.3] # Inicia à esquerda

    def desenhar(self):
        # 1. Desenha o corpo (coração)
        super().desenhar()

        # 2. Desenha os olhos relativos à posição do corpo
        for lado in (-1.0, 1.0):
            # Escala do corpo afeta a distancia dos olhos
            centro_x = self.posicao[0] + (lado * CENTRO_OLHO[0] * self.escala)
            centro_y = self.posicao[1] + (CENTRO_OLHO[1] * self.escala)
            
            # Branco do olho
            self.cena.ajustar_uniforme('u_escala', ESCALA_OLHO * self.escala)
            self.cena.ajustar_uniforme('u_deslocamento', (centro_x, centro_y))
            self.cena.ajustar_uniforme('u_cor', BRANCO_OLHO)
            self.vao_circulo.render(moderngl.TRIANGLE_FAN)
            
            # Pupila centralizada (pode adicionar lógica de olhar aqui futuramente)
            self.cena.ajustar_uniforme('u_escala', ESCALA_PUPILA * self.escala)
            self.cena.ajustar_uniforme('u_deslocamento', (centro_x, centro_y))
            self.cena.ajustar_uniforme('u_cor', PRETO)
            self.vao_circulo.render(moderngl.TRIANGLE_FAN)

    def mover(self, dx, dy):
        self.posicao[0] += dx
        self.posicao[1] += dy

class Casa(ObjetoCena):
    def __init__(self, cena, recursos):
        super().__init__(cena, recursos.vao_quadrado, moderngl.TRIANGLES)
        self.posicao = [-0.7, -0.4]
        self.escala = 0.2
        self.cor = (0.8, 0.8, 0.8, 1.0)
        self.vao_triangulo = recursos.vao_triangulo
        self.vao_circulo = recursos.vao_circulo

    def mudar_cor_aleatoria(self):
        self.cor = (random.random(), random.random(), random.random(), 1.0)

    def desenhar(self):
        # Base da casa (Quadrado)
        self.primitiva = moderngl.TRIANGLES
        super().desenhar()

        # Teto da casa (Triângulo)
        self.vao = self.vao_triangulo
        pos_teto = [self.posicao[0], self.posicao[1] + self.escala * 1.5]
        self.cena.ajustar_uniforme('u_deslocamento', tuple(pos_teto))
        self.cena.ajustar_uniforme('u_cor', COR_TETO)
        self.vao.render(moderngl.TRIANGLES)
        
        # Porta (Círculo cortado pela grama/base)
        self.vao = self.vao_circulo
        pos_porta = [self.posicao[0], self.posicao[1] - self.escala + 0.08]
        self.cena.ajustar_uniforme('u_escala', 0.08)
        self.cena.ajustar_uniforme('u_deslocamento', tuple(pos_porta))
        self.cena.ajustar_uniforme('u_cor', (0.4, 0.2, 0.1, 1.0))
        self.vao.render(moderngl.TRIANGLE_FAN)
        
        # Restaura a VAO base para o próximo frame
        self.vao = self.cena.recursos.vao_quadrado

class Chuva:
    def __init__(self, cena, recursos, quantidade=30):
        self.cena = cena
        self.vao_linha = recursos.vao_linha
        self.quantidade = quantidade
        self.ativa = True
        self.gotas = [[random.uniform(-1.0, 1.0), random.uniform(-1.0, 1.0)] for _ in range(quantidade)]

    def atualizar(self):
        if not self.ativa: return
        for gota in self.gotas:
            gota[0] -= 0.005 # Vento
            gota[1] -= 0.02  # Gravidade
            if gota[1] < -1.0 or gota[0] < -1.0:
                gota[0] = random.uniform(-0.5, 1.5)
                gota[1] = 1.1

    def desenhar(self):
        if not self.ativa: return
        self.cena.ajustar_uniforme('u_escala', 0.5)
        self.cena.ajustar_uniforme('u_cor', COR_CHUVA)
        for gota in self.gotas:
            self.cena.ajustar_uniforme('u_deslocamento', tuple(gota))
            self.vao_linha.render(moderngl.LINES)

class Cena:
    """Gerencia o contexto OpenGL, eventos e o loop de renderização"""
    def __init__(self):
        self.init_glfw()
        self.prog = self.ctx.program(vertex_shader=VERT_SHADER, fragment_shader=FRAG_SHADER)
        self.recursos = RecursosGL(self.ctx, self.prog)
        
        # Estado Global
        self.noite = False
        
        # Instanciar Elementos da Cena
        self.grama = ObjetoCena(self, self.recursos.vao_quadrado, moderngl.TRIANGLES)
        self.grama.escala = 1.0
        self.grama.posicao = [0.0, -0.9] # Fica no rodapé
        self.grama.cor = COR_GRAMA

        self.sol_lua = ObjetoCena(self, self.recursos.vao_circulo, moderngl.TRIANGLE_FAN)
        self.sol_lua.escala = 0.15
        self.sol_lua.posicao = [0.7, 0.7]
        self.sol_lua.cor = COR_SOL

        self.casa = Casa(self, self.recursos)
        self.sr_coracao = SenhorCoracao(self, self.recursos)
        self.chuva = Chuva(self, self.recursos)

        glfw.set_key_callback(self.janela, self.evento_teclado)

    def init_glfw(self):
        if not glfw.init():
            sys.exit("FALHA: glfw nao inicializou")
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 0)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.SAMPLES, 4)
        glfw.window_hint(glfw.RESIZABLE, False)
        
        self.janela = glfw.create_window(800, 600, "Cena 2D - Sr. Coracao e Amigos", None, None)
        if not self.janela:
            glfw.terminate()
            sys.exit("FALHA: nao foi possivel criar a janela")
        
        glfw.make_context_current(self.janela)
        self.ctx = moderngl.create_context()

    def ajustar_uniforme(self, nome, valor):
        uniforme = self.prog.get(nome, None)
        if uniforme is not None:
            uniforme.value = valor

    def evento_teclado(self, window, key, scancode, action, mods):
        if action != glfw.PRESS and action != glfw.REPEAT:
            return
            
        if key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
        elif key == glfw.KEY_D and action == glfw.PRESS:
            self.noite = not self.noite
            # Muda propriedades do sol/lua baseado no dia/noite
            self.sol_lua.cor = COR_LUA if self.noite else COR_SOL
            self.sol_lua.escala = 0.1 if self.noite else 0.15
        elif key == glfw.KEY_C and action == glfw.PRESS:
            self.casa.mudar_cor_aleatoria()
        elif key == glfw.KEY_R and action == glfw.PRESS:
            self.chuva.ativa = not self.chuva.ativa
            
        # Movimentação do Sr Coracao
        passo = 0.05
        if key == glfw.KEY_LEFT:
            self.sr_coracao.mover(-passo, 0)
        elif key == glfw.KEY_RIGHT:
            self.sr_coracao.mover(passo, 0)
        elif key == glfw.KEY_UP:
            self.sr_coracao.mover(0, passo)
        elif key == glfw.KEY_DOWN:
            self.sr_coracao.mover(0, -passo)

    def rodar(self):
        while not glfw.window_should_close(self.janela):
            # 1. Atualizar logica
            self.chuva.atualizar()

            # 2. Configurar ambiente
            self.ajustar_uniforme('u_atenuacao', 0.35 if self.noite else 1.0)
            self.ctx.clear(*(FUNDO_NOITE if self.noite else FUNDO_DIA))

            # 3. Desenhar elementos de trás para frente (Painter's algorithm)
            self.sol_lua.desenhar()
            self.casa.desenhar()
            self.sr_coracao.desenhar()
            self.grama.desenhar() # Grama na frente da casa para esconder a base da porta
            self.chuva.desenhar() # Chuva na frente de tudo

            glfw.swap_buffers(self.janela)
            glfw.poll_events()

        glfw.terminate()

if __name__ == "__main__":
    app = Cena()
    app.rodar()