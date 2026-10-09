from moderngl import Context

def get_hardware_properties(ctx: Context) -> str:
    return f"GL_VERSION  : {ctx.info['GL_VERSION']}\
    \nGL_RENDERER : {ctx.info['GL_RENDERER']}\
    \nGL_VENDOR   : {ctx.info['GL_VENDOR']}\
    \nGL (código de versão) : {ctx.version_code}"