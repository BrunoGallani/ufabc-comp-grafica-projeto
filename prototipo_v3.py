"""
Projeto: Cena 2D Interativa - Computação Gráfica
Baseado no "Senhor Coração" com expansão em POO.

Teclas: 
  SETAS: Movem os olhos e, em seguida, o corpo do Sr. Coracao
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
FUNDO_DIA = (0.53, 0.81, 0.92, 1.0)
FUNDO_NOITE = (0.05, 0.05, 0.12, 1.0)
COR_GRAMA = (0.13, 0.55, 0.13, 1.0)
COR_TETO = (0.8, 0.2, 0.2, 1.0)
COR_SOL = (1.0, 0.84, 0.0, 1.0)
COR_LUA = (0.9, 0.9, 0.8, 1.0)
COR_CHUVA = (0.0, 0.4, 1.0, 1.0)

ESCALA_CORPO = 0.3
ESCALA_OLHO, ESCALA_PUPILA = 0.085, 0.040
CENTRO_OLHO = (0.17, 0.20)

# --- SHADERS INLINE ---
VERT_SHADER = """
#version 400
in vec4 vPosition;
uniform float u_escala;
uniform vec2 u_deslocamento;
void main() {
    gl_Position = vec4((vPosition.xy * u_escala) + u_deslocamento, 0.0, 1.0);
}
"""

FRAG_SHADER = """
#version 400
uniform vec4 u_cor;
uniform float u_atenuacao;
out vec4 fColor;
void main() {
    fColor = vec4(u_cor.rgb * u_atenuacao, u_cor.a);
}
"""

# --- FUNÇÕES GERADORAS DE GEOMETRIA ---
def leque(x, y):
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

def curva_quadrado():
    return np.array([
        [-1.0, -1.0, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [-1.0,  1.0, 0.0, 1.0],
        [-1.0,  1.0, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [ 1.0,  1.0, 0.0, 1.0]
    ], dtype='f4')

def curva_chao():
    """Gera um retângulo específico para a grama (ocupa apenas o fundo do ecrã)"""
    return np.array([
        [-1.0, -1.0, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [-1.0, -0.6, 0.0, 1.0],
        [-1.0, -0.6, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [ 1.0, -0.6, 0.0, 1.0]
    ], dtype='f4')

def curva_triangulo():
    return np.array([
        [-1.0, -1.0, 0.0, 1.0], [ 1.0, -1.0, 0.0, 1.0], [ 0.0,  1.0, 0.0, 1.0]
    ], dtype='f4')

def curva_linha():
    return np.array([
        [0.0, 0.0, 0.0, 1.0], [-0.05, -0.15, 0.0, 1.0]
    ], dtype='f4')

# --- CLASSES DA APLICAÇÃO (POO) ---
class RecursosGL:
    def __init__(self, ctx, prog):
        self.ctx = ctx
        self.prog = prog
        
        self.vao_coracao = self.montar(curva_coracao())
        self.vao_circulo = self.montar(curva_circulo())
        self.vao_quadrado = self.montar(curva_quadrado())
        self.vao_chao = self.montar(curva_chao())
        self.vao_triangulo = self.montar(curva_triangulo())
        self.vao_linha = self.montar(curva_linha())

    def montar(self, vertices):
        vbo = self.ctx.buffer(vertices.tobytes())
        return self.ctx.vertex_array(self.prog, [(vbo, '4f', 'vPosition')])

class ObjetoCena:
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
    def __init__(self, cena, recursos):
        super().__init__(cena, recursos.vao_coracao)
        self.escala = ESCALA_CORPO
        self.cor = MAGENTA
        self.vao_circulo = recursos.vao_circulo
        self.posicao = [0.3, -0.3]
        
        # Variáveis originais para a física dos olhos
        self.olhar_x = 0.0
        self.olhar_y = 0.0
        self.limite_olhar = ESCALA_OLHO - ESCALA_PUPILA
        self.passo_olhar = self.limite_olhar / 2.0

    def desenhar(self):
        super().desenhar()
        
        for lado in (-1.0, 1.0):
            # Centro do olho em relação ao corpo
            centro_x = self.posicao[0] + (lado * CENTRO_OLHO[0] * self.escala)
            centro_y = self.posicao[1] + (CENTRO_OLHO[1] * self.escala)
            
            # Fundo branco do olho
            self.cena.ajustar_uniforme('u_escala', ESCALA_OLHO * self.escala)
            self.cena.ajustar_uniforme('u_deslocamento', (centro_x, centro_y))
            self.cena.ajustar_uniforme('u_cor', BRANCO_OLHO)
            self.vao_circulo.render(moderngl.TRIANGLE_FAN)
            
            # Pupila deslocada pelo "olhar"
            centro_pupila_x = centro_x + (self.olhar_x * self.escala)
            centro_pupila_y = centro_y + (self.olhar_y * self.escala)
            
            self.cena.ajustar_uniforme('u_escala', ESCALA_PUPILA * self.escala)
            self.cena.ajustar_uniforme('u_deslocamento', (centro_pupila_x, centro_pupila_y))
            self.cena.ajustar_uniforme('u_cor', PRETO)
            self.vao_circulo.render(moderngl.TRIANGLE_FAN)

    def interagir(self, dx, dy):
        """Move primeiro a pupila. Se bater no limite, arrasta o corpo."""
        self.olhar_x += dx * self.passo_olhar
        self.olhar_y += dy * self.passo_olhar
        
        distancia = (self.olhar_x ** 2 + self.olhar_y ** 2) ** 0.5
        
        if distancia > self.limite_olhar:
            # Mantém a pupila dentro do limite do olho
            self.olhar_x *= self.limite_olhar / distancia
            self.olhar_y *= self.limite_olhar / distancia
            
            # Como a pupila chegou ao limite, a personagem acompanha o movimento
            passo_corpo = 0.05
            self.posicao[0] += dx * passo_corpo
            self.posicao[1] += dy * passo_corpo

class Casa(ObjetoCena):
    def __init__(self, cena, recursos):
        super().__init__(cena, recursos.vao_quadrado, moderngl.TRIANGLES)
        self.posicao = [-0.5, -0.4]
        self.escala = 0.2
        self.cor = (0.8, 0.8, 0.8, 1.0)
        self.vao_triangulo = recursos.vao_triangulo
        self.vao_circulo = recursos.vao_circulo

    def mudar_cor_aleatoria(self):
        self.cor = (random.random(), random.random(), random.random(), 1.0)

    def desenhar(self):
        # Base da casa
        self.primitiva = moderngl.TRIANGLES
        super().desenhar()

        # Teto da casa
        self.vao = self.vao_triangulo
        pos_teto = [self.posicao[0], self.posicao[1] + self.escala * 2.0]
        self.cena.ajustar_uniforme('u_deslocamento', tuple(pos_teto))
        self.cena.ajustar_uniforme('u_cor', COR_TETO)
        self.vao.render(moderngl.TRIANGLES)
        
        # Porta
        self.vao = self.vao_circulo
        pos_porta = [self.posicao[0], self.posicao[1] - self.escala]
        self.cena.ajustar_uniforme('u_escala', 0.08)
        self.cena.ajustar_uniforme('u_deslocamento', tuple(pos_porta))
        self.cena.ajustar_uniforme('u_cor', (0.4, 0.2, 0.1, 1.0))
        self.vao.render(moderngl.TRIANGLE_FAN)
        
        # Restaura a VAO
        self.vao = self.cena.recursos.vao_quadrado

class Chuva:
    def __init__(self, cena, recursos, quantidade=40):
        self.cena = cena
        self.vao_linha = recursos.vao_linha
        self.quantidade = quantidade
        self.ativa = True
        self.gotas = [[random.uniform(-1.0, 1.0), random.uniform(-0.6, 1.0)] for _ in range(quantidade)]

    def atualizar(self):
        if not self.ativa: return
        for gota in self.gotas:
            gota[0] -= 0.003
            gota[1] -= 0.015
            if gota[1] < -0.6 or gota[0] < -1.0:
                gota[0] = random.uniform(-0.5, 1.5)
                gota[1] = random.uniform(1.0, 1.5)

    def desenhar(self):
        if not self.ativa: return
        self.cena.ajustar_uniforme('u_escala', 1.0)
        self.cena.ajustar_uniforme('u_cor', COR_CHUVA)
        for gota in self.gotas:
            self.cena.ajustar_uniforme('u_deslocamento', tuple(gota))
            self.vao_linha.render(moderngl.LINES)

class Cena:
    def __init__(self):
        self.init_glfw()
        self.prog = self.ctx.program(vertex_shader=VERT_SHADER, fragment_shader=FRAG_SHADER)
        self.recursos = RecursosGL(self.ctx, self.prog)
        
        self.noite = False
        
        self.grama = ObjetoCena(self, self.recursos.vao_chao, moderngl.TRIANGLES)
        self.grama.escala = 1.0
        self.grama.posicao = [0.0, 0.0]
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
            self.sol_lua.cor = COR_LUA if self.noite else COR_SOL
            self.sol_lua.escala = 0.1 if self.noite else 0.15
        elif key == glfw.KEY_C and action == glfw.PRESS:
            self.casa.mudar_cor_aleatoria()
        elif key == glfw.KEY_R and action == glfw.PRESS:
            self.chuva.ativa = not self.chuva.ativa
            
        dx, dy = 0.0, 0.0
        if key == glfw.KEY_LEFT: dx = -1.0
        elif key == glfw.KEY_RIGHT: dx = 1.0
        elif key == glfw.KEY_UP: dy = 1.0
        elif key == glfw.KEY_DOWN: dy = -1.0
        
        if dx != 0.0 or dy != 0.0:
            self.sr_coracao.interagir(dx, dy)

    def rodar(self):
        while not glfw.window_should_close(self.janela):
            self.chuva.atualizar()

            self.ajustar_uniforme('u_atenuacao', 0.35 if self.noite else 1.0)
            self.ctx.clear(*(FUNDO_NOITE if self.noite else FUNDO_DIA))

            self.sol_lua.desenhar()
            self.casa.desenhar()
            self.sr_coracao.desenhar()
            self.grama.desenhar() 
            self.chuva.desenhar()

            glfw.swap_buffers(self.janela)
            glfw.poll_events()

        glfw.terminate()

if __name__ == "__main__":
    app = Cena()
    app.rodar()