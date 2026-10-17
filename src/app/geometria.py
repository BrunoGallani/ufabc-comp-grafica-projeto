"""
Geometrias da cena, só com numpy (nada aqui fala com a GPU).

Todo vértice é (x, y, 0, 1) em float32, o formato do `vec4 vPosition` do shader;
sem o dtype, o numpy usaria float64 e a GPU leria lixo. Tudo nasce centrado na
origem: tamanho e posição vêm depois, pelos uniforms `u_escala` e `u_deslocamento`.
"""
import numpy as np


def leque(x, y):
    """Fecha uma curva pro TRIANGLE_FAN: o centro vem primeiro e o 1º ponto se repete no fim."""
    x = np.concatenate(([0.0], x, [x[0]]))
    y = np.concatenate(([0.0], y, [y[0]]))
    return np.column_stack((x, y, np.zeros_like(x), np.ones_like(x))).astype('f4')


def curva_coracao(n=180):
    """Coração paramétrico com `n` pontos, cabendo em [-1, 1]."""
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = 16.0 * np.sin(t) ** 3
    y = (13.0 * np.cos(t) - 5.0 * np.cos(2 * t)
         - 2.0 * np.cos(3 * t) - np.cos(4 * t))
    y = y - 0.5 * (y.max() + y.min())      # centraliza
    return leque(x / 17.0, y / 17.0)


def curva_circulo(n=48):
    """Círculo de raio 1: a malha mais reaproveitada da cena."""
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(np.cos(t), np.sin(t))


def curva_elipse(raio_x, raio_y, n=32):
    """
    Elipse (a gota da chuva). Como a escala é uma só pros dois eixos, a proporção
    tem que ficar nos vértices.
    """
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(raio_x * np.cos(t), raio_y * np.sin(t))


def curva_flor(petalas=5, n=80):
    """Flor polar: r = 0.4 + 0.6 * |cos(petalas * t / 2)|, cada "lombada" vira uma pétala."""
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    raio = 0.4 + 0.6 * np.abs(np.cos(petalas * t / 2.0))
    return leque(raio * np.cos(t), raio * np.sin(t))


def retangulo(largura, altura):
    """
    Retângulo com EBO: 4 vértices e 6 índices, 2 triângulos que dividem a diagonal.

        v3 --- v2
        |    / |
        |  /   |
        v0 --- v1
    """
    mx, my = largura / 2.0, altura / 2.0
    vertices = np.array([
        [-mx, -my, 0.0, 1.0],
        [ mx, -my, 0.0, 1.0],
        [ mx,  my, 0.0, 1.0],
        [-mx,  my, 0.0, 1.0],
    ], dtype='f4')
    indices = np.array([0, 1, 2, 2, 3, 0], dtype='u4')   # u4 = GL_UNSIGNED_INT, o tipo do EBO
    return vertices, indices


def retangulo_girado(comprimento, espessura, angulo):
    """O retângulo de cima girado de `angulo` radianos (um raio de calor do verão)."""
    vertices, indices = retangulo(comprimento, espessura)
    c, s = np.cos(angulo), np.sin(angulo)
    x, y = vertices[:, 0].copy(), vertices[:, 1].copy()
    vertices[:, 0] = c * x - s * y
    vertices[:, 1] = s * x + c * y
    return vertices, indices


def triangulo(base, altura):
    """Triângulo isósceles (o telhado). Serve pra TRIANGLES e pra LINE_LOOP (contorno)."""
    mb, ma = base / 2.0, altura / 2.0
    return np.array([
        [-mb, -ma, 0.0, 1.0],
        [ mb, -ma, 0.0, 1.0],
        [0.0,  ma, 0.0, 1.0],
    ], dtype='f4')


def raios_do_sol(n=12, raio_interno=1.08, raio_externo=1.55, meia_abertura=0.12):
    """`n` triângulos em volta do círculo de raio 1, todos num VBO só (uma draw call)."""
    vertices = []
    for k in range(n):
        angulo = 2.0 * np.pi * k / n
        # dois vértices na base, perto do círculo, e a ponta pra fora
        for a, r in ((angulo - meia_abertura, raio_interno),
                     (angulo + meia_abertura, raio_interno),
                     (angulo, raio_externo)):
            vertices.append([r * np.cos(a), r * np.sin(a), 0.0, 1.0])
    return np.array(vertices, dtype='f4')


def galhos(ramos):
    """
    Galhos secos, um triângulo fino por ramo, todos num VBO só. Cada ramo é
    (base, ponta, meia largura na base).
    """
    vertices = []
    for (bx, by), (px, py), meia in ramos:
        # A normal ao ramo, com tamanho `meia`, abre a base pros lados.
        dx, dy = px - bx, py - by
        comprimento = np.hypot(dx, dy)
        nx, ny = -dy / comprimento * meia, dx / comprimento * meia
        vertices += [[bx + nx, by + ny, 0.0, 1.0],
                     [bx - nx, by - ny, 0.0, 1.0],
                     [px, py, 0.0, 1.0]]
    return np.array(vertices, dtype='f4')


def cruz():
    """Caixilho da janela pra LINES: um segmento horizontal e um vertical, de -1 a 1."""
    return np.array([
        [-1.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 1.0],
        [0.0, -1.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0],
    ], dtype='f4')


def laco(abertura=0.55):
    """
    Laço da Sra. Coração com EBO: duas asas que dividem o vértice do centro (5
    vértices, 2 triângulos). `abertura` é a meia altura da ponta de cada asa.

        v1         v4
        |  \\     /  |
        |    v0     |
        |  /     \\  |
        v2         v3
    """
    vertices = np.array([
        [ 0.0,  0.0,      0.0, 1.0],
        [-1.0,  abertura, 0.0, 1.0],
        [-1.0, -abertura, 0.0, 1.0],
        [ 1.0, -abertura, 0.0, 1.0],
        [ 1.0,  abertura, 0.0, 1.0],
    ], dtype='f4')
    indices = np.array([0, 1, 2, 0, 3, 4], dtype='u4')
    return vertices, indices


def bitmap(mascara):
    """
    Imagem preto e branco (array booleano, linha 0 em cima) virando retângulos com
    EBO, centrada na origem, com cada pixel de lado 1. Pixels acesos vizinhos na
    mesma linha viram um retângulo só.
    """
    altura, largura = mascara.shape
    # Em cada linha, +1 onde começa uma sequência de pixels acesos e -1 onde ela termina.
    bordas = np.diff(np.pad(mascara.astype(np.int8), ((0, 0), (1, 1))), axis=1)
    linhas, inicio = np.nonzero(bordas == 1)
    _, fim = np.nonzero(bordas == -1)

    esquerda, direita = inicio - largura / 2.0, fim - largura / 2.0
    topo = altura / 2.0 - linhas
    base = topo - 1.0

    n = len(linhas)
    vertices = np.zeros((n, 4, 4), dtype='f4')
    vertices[:, :, 0] = np.column_stack((esquerda, direita, direita, esquerda))
    vertices[:, :, 1] = np.column_stack((base, base, topo, topo))
    vertices[:, :, 3] = 1.0
    indices = np.array([0, 1, 2, 2, 3, 0], dtype='u4') + 4 * np.arange(n, dtype='u4')[:, None]
    return vertices.reshape(-1, 4), indices.reshape(-1)
