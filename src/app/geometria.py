"""
Geometrias da cena: o "lado da CPU".

Cada função retorna um arranjo numpy de vértices (e, no caso do retângulo e do
laço, também os índices do EBO). Nenhuma delas interage com a GPU: quem copia os dados
para a VRAM é o :class:`Renderizador`.

Todos os vértices têm o formato `(x, y, z, w)`, em float de 32 bits (`'f4'`):

- **Quatro componentes num desenho 2D:** o vertex shader recebe um `vec4 vPosition`.
  Usamos `z = 0` (tudo no mesmo plano) e `w = 1` (coordenada homogênea);
- **Float de 32 bits:** é o tipo que a GPU espera. Sem o `dtype`, o numpy usaria
  float64 e a GPU leria dados incorretos.

Todas as formas são geradas centradas na origem. O tamanho e a posição de cada
cópia na tela são definidos pelos uniforms `u_escala` e `u_deslocamento`, no
vertex shader: `posição_final = posição * u_escala + u_deslocamento`.
"""
import numpy as np


# ---------------------------------------------------------------------------
# Curvas fechadas do Sr. Coração, desenhadas com TRIANGLE_FAN.
# ---------------------------------------------------------------------------

def leque(x, y):
    """
    Empacota uma curva fechada para a primitiva `TRIANGLE_FAN`.

    O primeiro vértice é o centro; em seguida vêm os pontos da curva, e o primeiro
    ponto é repetido no fim para fechar a volta.
    """
    x = np.concatenate(([0.0], x, [x[0]]))
    y = np.concatenate(([0.0], y, [y[0]]))
    return np.column_stack((x, y, np.zeros_like(x), np.ones_like(x))).astype('f4')


def curva_coracao(n=180):
    """
    Contorno paramétrico do coração com `n` pontos, centrado na origem e
    normalizado para caber em `[-1, 1]`.
    """
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    x = 16.0 * np.sin(t) ** 3
    y = (13.0 * np.cos(t) - 5.0 * np.cos(2 * t)
         - 2.0 * np.cos(3 * t) - np.cos(4 * t))
    y = y - 0.5 * (y.max() + y.min())      # centra a curva na origem
    return leque(x / 17.0, y / 17.0)       # normaliza para caber em [-1, 1]


def curva_circulo(n=48):
    """
    Círculo de raio 1 com `n` pontos: a malha mais reaproveitada da cena.
    """
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(np.cos(t), np.sin(t))


# ---------------------------------------------------------------------------
# Demais formas da cena.
# ---------------------------------------------------------------------------

def curva_elipse(raio_x, raio_y, n=32):
    """
    Elipse para `TRIANGLE_FAN`: um círculo "esticado".

    É usada nas gotas de chuva, que são bem mais altas do que largas. Como o
    uniform `u_escala` é um número só (escala igual em x e em y), a proporção
    da gota precisa estar gravada nos próprios vértices.
    """
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    return leque(raio_x * np.cos(t), raio_y * np.sin(t))


def curva_flor(petalas=5, n=80):
    """
    Flor com `petalas` pétalas, para `TRIANGLE_FAN`, cabendo num círculo de raio 1.

    É uma curva polar: o raio muda com o ângulo, `r = 0.4 + 0.6 * |cos(petalas * t / 2)|`.
    Cada "lombada" do cosseno vira uma pétala (raio 1 na ponta, 0.4 entre duas
    pétalas). Como o centro enxerga toda a borda, o `TRIANGLE_FAN` a preenche.
    """
    t = np.linspace(0.0, 2.0 * np.pi, n, endpoint=False)
    raio = 0.4 + 0.6 * np.abs(np.cos(petalas * t / 2.0))
    return leque(raio * np.cos(t), raio * np.sin(t))


def retangulo(largura, altura):
    """
    Retângulo para `TRIANGLES` com EBO.

    São só 4 vértices únicos. O EBO (lista de índices) diz em que ordem lê-los para
    formar 2 triângulos que compartilham a diagonal v0-v2:

        v3 ------- v2
        |       /  |      triângulo 1: v0, v1, v2
        |     /    |      triângulo 2: v2, v3, v0
        |   /      |
        v0 ------- v1

    Retorna o par (vértices, índices). Os índices são `'u4'` (inteiro sem sinal
    de 32 bits), o tipo `GL_UNSIGNED_INT` que o OpenGL espera num EBO.
    """
    mx, my = largura / 2.0, altura / 2.0
    vertices = np.array([
        [-mx, -my, 0.0, 1.0],   # v0: inferior esquerdo
        [ mx, -my, 0.0, 1.0],   # v1: inferior direito
        [ mx,  my, 0.0, 1.0],   # v2: superior direito
        [-mx,  my, 0.0, 1.0],   # v3: superior esquerdo
    ], dtype='f4')
    indices = np.array([0, 1, 2, 2, 3, 0], dtype='u4')
    return vertices, indices


def retangulo_girado(comprimento, espessura, angulo):
    """
    Retângulo de :func:`retangulo` deitado ao longo de `angulo` (em radianos),
    ainda centrado na origem. É um raio de calor do verão.
     """
    vertices, indices = retangulo(comprimento, espessura)
    c, s = np.cos(angulo), np.sin(angulo)
    x, y = vertices[:, 0].copy(), vertices[:, 1].copy()
    vertices[:, 0] = c * x - s * y
    vertices[:, 1] = s * x + c * y
    return vertices, indices


def triangulo(base, altura):
    """
    Triângulo isósceles (o telhado), centrado na origem.

    Os 3 vértices estão em ordem ao redor da figura. Por isso a mesma malha
    serve para duas primitivas: `TRIANGLES` (triângulo preenchido) e `LINE_LOOP`
    (só o contorno, ligando 0-1, 1-2 e 2-0).
    """
    mb, ma = base / 2.0, altura / 2.0
    return np.array([
        [-mb, -ma, 0.0, 1.0],   # canto inferior esquerdo
        [ mb, -ma, 0.0, 1.0],   # canto inferior direito
        [0.0,  ma, 0.0, 1.0],   # ponta de cima
    ], dtype='f4')


def raios_do_sol(n=12, raio_interno=1.08, raio_externo=1.55, meia_abertura=0.12):
    """
    `n` triângulos pontudos ao redor de um círculo de raio 1, para `TRIANGLES`.

    Cada raio é um triângulo: dois vértices na base (perto do círculo) e uma
    ponta para fora. Os `n` triângulos ficam num único VBO com `3 * n` vértices,
    e uma única chamada `render(TRIANGLES)` desenha todos de uma vez.
    `meia_abertura` é metade da largura da base de cada raio, em radianos.
    """
    vertices = []
    for k in range(n):
        angulo = 2.0 * np.pi * k / n   # direção para onde este raio aponta
        for a, r in ((angulo - meia_abertura, raio_interno),   # base, um lado
                     (angulo + meia_abertura, raio_interno),   # base, outro lado
                     (angulo, raio_externo)):                  # ponta
            vertices.append([r * np.cos(a), r * np.sin(a), 0.0, 1.0])
    return np.array(vertices, dtype='f4')


def galhos(ramos):
    """
    Galhos secos para `TRIANGLES`: cada ramo é um triângulo fino e comprido,
    largo na base e pontudo na ponta. Todos ficam num único VBO, como em
    :func:`raios_do_sol`, e uma única chamada desenha a galhada inteira.

    `ramos` é uma lista de `(base, ponta, meia_largura)`: os pontos `(x, y)` da
    base e da ponta do ramo, e a metade da largura dele na base.
    """
    vertices = []
    for (bx, by), (px, py), meia in ramos:
        # Vetor perpendicular ao ramo, com comprimento `meia`: afasta os dois
        # vértices da base para os lados.
        dx, dy = px - bx, py - by
        comprimento = np.hypot(dx, dy)
        nx, ny = -dy / comprimento * meia, dx / comprimento * meia
        vertices += [[bx + nx, by + ny, 0.0, 1.0],   # base, um lado
                     [bx - nx, by - ny, 0.0, 1.0],   # base, outro lado
                     [px, py, 0.0, 1.0]]             # ponta
    return np.array(vertices, dtype='f4')


def cruz():
    """
    Dois segmentos, um horizontal e um vertical: o caixilho da janela.

    Para `LINES`, cada par de vértices vira um segmento independente. A cruz
    vai de -1 a 1; o `u_escala` a ajusta ao tamanho da janela.
    """
    return np.array([
        [-1.0, 0.0, 0.0, 1.0], [1.0, 0.0, 0.0, 1.0],   # segmento horizontal
        [0.0, -1.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0],   # segmento vertical
    ], dtype='f4')


# ---------------------------------------------------------------------------
# Acessório da Sra. Coração.
# ---------------------------------------------------------------------------

def laco(abertura=0.55):
    """
    Laço para `TRIANGLES` com EBO: duas asas triangulares que se encontram no
    centro, de `x = -1` a `x = 1`.

    O vértice central é compartilhado pelas duas asas: são só 5 vértices
    únicos, e o EBO os lê na ordem de 2 triângulos. `abertura` é a meia altura
    de cada asa na ponta de fora.

        v1         v4
        |  \\     /  |      asa esquerda: v0, v1, v2
        |    v0     |      asa direita:  v0, v3, v4
        |  /     \\  |
        v2         v3

    Retorna o par (vértices, índices), como :func:`retangulo`.
    """
    vertices = np.array([
        [ 0.0,  0.0,      0.0, 1.0],   # v0: centro (compartilhado)
        [-1.0,  abertura, 0.0, 1.0],   # v1: asa esquerda, em cima
        [-1.0, -abertura, 0.0, 1.0],   # v2: asa esquerda, embaixo
        [ 1.0, -abertura, 0.0, 1.0],   # v3: asa direita, embaixo
        [ 1.0,  abertura, 0.0, 1.0],   # v4: asa direita, em cima
    ], dtype='f4')
    indices = np.array([0, 1, 2, 0, 3, 4], dtype='u4')
    return vertices, indices
