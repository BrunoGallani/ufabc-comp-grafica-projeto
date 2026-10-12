"""
Configurações globais da cena.

Aqui ficam os "botões de ajuste" usados por várias partes do programa:
tamanho da janela, altura do chão, cores do céu e fatores de atenuação.
As cores de cada objeto (casa, árvore...) ficam no arquivo do próprio objeto.

Lembrete sobre coordenadas (slides02, p.32): o OpenGL desenha num quadrado que
vai de -1 a +1 nos dois eixos, chamado NDC (Normalized Device Coordinates).
(0, 0) é o centro da janela, (-1, -1) é o canto inferior esquerdo e (+1, +1) é
o canto superior direito, qualquer que seja o tamanho da janela em pixels.
"""
from pathlib import Path

# Janela QUADRADA, como no 06_senhor_coracao.py. O NDC vai de -1 a 1 nos dois
# eixos; numa janela retangular, uma unidade em x teria mais pixels do que uma
# unidade em y, e os círculos virariam elipses (o Sr. Coração ficaria esticado).
LARGURA_JANELA = 720
ALTURA_JANELA = 720

# Altura (em NDC) do topo da grama: é onde a casa, a árvore e os corações "pisam".
Y_CHAO = -0.70

# Cor do fundo (passada ao ctx.clear) para cada combinação do estado global.
CEU_DIA = (0.53, 0.81, 0.92, 1.0)          # azul-céu
CEU_DIA_CHUVA = (0.55, 0.62, 0.68, 1.0)    # céu nublado
CEU_NOITE = (0.05, 0.05, 0.12, 1.0)        # o mesmo FUNDO_NOITE do professor
CEU_NOITE_CHUVA = (0.04, 0.04, 0.07, 1.0)  # noite nublada

# Fatores enviados ao fragment shader pelo uniform u_atenuacao: a cor final de
# cada pixel é a cor do objeto multiplicada por este número.
ATENUACAO_NOITE = 0.35   # o mesmo valor do 06_senhor_coracao.py
ATENUACAO_CHUVA = 0.85   # a chuva escurece um pouco a cena (multiplica o anterior)

# Pasta onde a tecla P salva as capturas de tela (na raiz do repositório).
# Path(__file__) é este arquivo (src/app/config.py); .parents[2] sobe dois
# níveis acima da pasta dele: src/app -> src -> raiz do projeto.
PASTA_CAPTURAS = Path(__file__).resolve().parents[2] / "capturas"
