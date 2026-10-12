from datetime import datetime
from pathlib import Path

from moderngl import Context
from PIL import Image, ImageOps


def save_screenshot(ctx: Context, folder: Path, prefix: str) -> Path:
    """
    Salva como PNG o quadro que acabou de ser desenhado e retorna o caminho.

    Deve ser chamada DEPOIS de desenhar e ANTES de `glfw.swap_buffers`: nesse
    momento a imagem completa está no backbuffer (slides02, p.44).
    O Pillow é a biblioteca indicada no curso para salvar capturas (slides04, p.17).
    """
    width, height = ctx.fbo.size              # framebuffer atual (a tela)
    pixels = ctx.fbo.read(components=3)       # bytes RGB, linha a linha
    image = Image.frombytes("RGB", (width, height), pixels)
    # O OpenGL guarda a imagem de BAIXO para CIMA; arquivos de imagem guardam
    # de cima para baixo. Por isso a imagem é espelhada na vertical.
    image = ImageOps.flip(image)

    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{prefix}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    image.save(path)
    return path
