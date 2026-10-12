from pathlib import Path

SHADERS = Path(__file__).parent.parent / "shaders"

def get_shaders() -> tuple[str, str]:
    """
    Lê os arquivos dos shaders e retorna o par (vertex shader, fragment shader).

    O caminho é relativo a este arquivo, e não à pasta de onde o programa foi
    executado: assim os shaders são encontrados de qualquer lugar.
    """
    return (
        (SHADERS / "main_vertex_shader.vert").read_text(encoding="utf-8"),
        (SHADERS / "main_frag_shader.frag").read_text(encoding="utf-8")
    )