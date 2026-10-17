from datetime import datetime
from typing import TYPE_CHECKING
from config import PASTA_CAPTURAS
from PIL import Image, ImageOps
from utils.log_utils import Log

if TYPE_CHECKING:
    from cena import Cena

def save_screenshot(cena: 'Cena') -> None:
    """
    Salva o quadro em PNG. Tem que rodar depois de desenhar e antes do swap_buffers,
    quando o quadro inteiro está no backbuffer.
    """
    # Só o quadrado da cena (o viewport), sem as faixas da tela cheia. O ctx.fbo.size
    # não serve: o moderngl grava ele uma vez só e ele não acompanha a tela cheia.
    viewport = cena.ctx.viewport
    width, height = viewport[2], viewport[3]
    pixels = cena.ctx.fbo.read(viewport=viewport, components=3)
    image = Image.frombytes("RGB", (width, height), pixels)
    # O OpenGL guarda a imagem de baixo pra cima; o PNG, de cima pra baixo.
    image = ImageOps.flip(image)

    prefix = ("noite" if cena.estado.noite else "dia") + ("_chuva" if cena.estado.chovendo else "")
    path = PASTA_CAPTURAS / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    try:
        PASTA_CAPTURAS.mkdir(parents=True, exist_ok=True)
        image.save(path)
    except OSError as erro:
        Log.e(f"não foi possível salvar a captura em {path}: {erro}")
        return
    Log.d(f"Captura salva em {path}")
