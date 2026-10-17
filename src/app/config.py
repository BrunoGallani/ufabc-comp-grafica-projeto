"""
Configurações globais da cena.

Possui os "botões de ajuste" usados por várias partes do programa: tamanho e
título da janela, altura do chão, cores do céu, fatores de atenuação, estações
do ano e pasta das capturas. As cores de cada objeto (casa, árvore...) ficam no
arquivo do próprio objeto.

Todas as medidas estão em NDC (*Normalized Device Coordinates*): o OpenGL desenha
num quadrado que vai de -1 a +1 nos dois eixos, em que `(0, 0)` é o centro da
janela, `(-1, -1)` é o canto inferior esquerdo e `(+1, +1)` é o canto superior
direito, qualquer que seja o tamanho da janela em pixels.
"""
from enum import Enum
from pathlib import Path

# Janela quadrada: numa janela retangular, uma unidade de NDC em x teria mais
# pixels do que uma unidade em y, e os círculos virariam elipses.
LARGURA_JANELA = 720
ALTURA_JANELA = 720
TITULO_JANELA = "Cena 2D: Sr. e Sra. Coração e seus amigos"

# Em tela cheia (tecla F), a cena continua quadrada, no centro do monitor; as
# faixas que sobram nas laterais são pintadas com esta cor.
COR_FAIXAS = (0.0, 0.0, 0.0, 1.0)

# Altura (em NDC) do topo da grama: é onde a casa, a árvore e os corações "pisam".
Y_CHAO = -0.70

# Cor do fundo (passada ao ctx.clear) para cada combinação do estado global.
CEU_DIA = (0.53, 0.81, 0.92, 1.0)          # azul-céu
CEU_DIA_CHUVA = (0.55, 0.62, 0.68, 1.0)    # céu nublado
CEU_NOITE = (0.05, 0.05, 0.12, 1.0)        # azul-noite
CEU_NOITE_CHUVA = (0.04, 0.04, 0.07, 1.0)  # noite nublada

# Fatores enviados ao fragment shader pelo uniform u_atenuacao: a cor final de
# cada pixel é a cor do objeto multiplicada por este número.
ATENUACAO_NOITE = 0.35   # a noite escurece bastante a cena
ATENUACAO_CHUVA = 0.85   # a chuva escurece um pouco a cena (multiplica o anterior)


class Estacao(Enum):
    """
    Estações do ano, na ordem em que a tecla E as percorre.

    O valor de cada uma é o nome exibido no log.
    """
    VERAO = "verão"          # o padrão: o sol solta raios de calor
    OUTONO = "outono"        # a árvore perde as folhas
    INVERNO = "inverno"      # a grama e a copa ficam brancas de neve
    PRIMAVERA = "primavera"  # aparecem flores na grama e na árvore

    def proxima(self) -> "Estacao":
        """
        Retorna a estação seguinte, voltando ao verão depois da primavera.
        """
        estacoes = list(Estacao)
        return estacoes[(estacoes.index(self) + 1) % len(estacoes)]


# Cor da neve no inverno: usada pela grama e pela copa da árvore.
COR_NEVE = (0.93, 0.96, 0.99, 1.0)

# Pasta onde a tecla P salva as capturas de tela, na raiz do projeto
# (src/app/config.py -> src/app -> src -> raiz).
PASTA_CAPTURAS = Path(__file__).resolve().parents[2] / "capturas"
