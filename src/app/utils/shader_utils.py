from pathlib import Path

SHADERS = Path(__file__).parent.parent / "shaders"

def get_shaders() -> tuple[str, str]:
    """
    Lê (vertex, fragment). O caminho sai deste arquivo, e não da pasta de onde o
    programa foi rodado, então funciona de qualquer lugar.
    """
    return (
        (SHADERS / "main_vertex_shader.vert").read_text(encoding="utf-8"),
        (SHADERS / "main_frag_shader.frag").read_text(encoding="utf-8")
    )
