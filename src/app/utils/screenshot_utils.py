from datetime import datetime
from typing import TYPE_CHECKING
from config import PASTA_CAPTURAS
from PIL import Image, ImageOps
from utils.log_utils import Log

if TYPE_CHECKING:
    from cena import Cena

def save_screenshot(cena: 'Cena') -> None:
    """
    Salva como PNG a cena desenhada na tela.

    Deve ser chamada **depois** de desenhar e **antes** de `glfw.swap_buffers`: nesse
    momento a imagem completa está no *backbuffer*. O nome do arquivo indica o estado
    da cena (dia ou noite, com ou sem chuva) e o instante da captura.
    """
    width, height = cena.ctx.fbo.size              # framebuffer atual (a tela)
    pixels = cena.ctx.fbo.read(components=3)       # bytes RGB, linha a linha
    image = Image.frombytes("RGB", (width, height), pixels)
    # OpenGL guarda a imagem de baixo para cima
    # Arquivos de imagem guardam de cima para baixo
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