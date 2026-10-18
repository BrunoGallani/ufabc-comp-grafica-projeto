"""
Constantes globais. As cores de cada objeto ficam no arquivo dele.

Fora o tamanho da janela (em pixels), tudo é em NDC: de -1 a 1 nos dois eixos,
com (0, 0) no centro da cena.
"""
from enum import Enum
from pathlib import Path

# Tamanho inicial: quadrada como a cena, pra não sobrar faixa nas bordas.
LARGURA_JANELA = 720
ALTURA_JANELA = 720
TITULO_JANELA = "Cena 2D: Sr. e Sra. Coração e seus amigos"

# A cena fica sempre quadrada, mesmo em tela cheia ou com a janela redimensionada;
# as sobras ficam com essa cor.
COR_FAIXAS = (0.0, 0.0, 0.0, 1.0)

Y_CHAO = -0.70   # topo da grama: onde a casa, a árvore e os corações pisam

CEU_DIA = (0.53, 0.81, 0.92, 1.0)
CEU_DIA_CHUVA = (0.55, 0.62, 0.68, 1.0)
CEU_NOITE = (0.05, 0.05, 0.12, 1.0)
CEU_NOITE_CHUVA = (0.04, 0.04, 0.07, 1.0)

# Vão pro u_atenuacao: a cor de cada pixel é multiplicada por eles (e noite com
# chuva multiplica os dois).
ATENUACAO_NOITE = 0.35
ATENUACAO_CHUVA = 0.85


class Estacao(Enum):
    """Na ordem da tecla E. O valor é o nome que aparece no log e no painel."""
    VERAO = "verão"
    OUTONO = "outono"
    INVERNO = "inverno"
    PRIMAVERA = "primavera"

    def proxima(self) -> "Estacao":
        estacoes = list(Estacao)
        return estacoes[(estacoes.index(self) + 1) % len(estacoes)]


COR_NEVE = (0.93, 0.96, 0.99, 1.0)   # grama e copa no inverno

# capturas/ na raiz do projeto (src/app/config.py -> src/app -> src -> raiz)
PASTA_CAPTURAS = Path(__file__).resolve().parents[2] / "capturas"
