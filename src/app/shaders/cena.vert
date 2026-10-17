#version 400 core

layout(location = 0) in vec4 vPosition;

uniform float u_escala;
uniform float u_angulo;
uniform vec2  u_deslocamento;
uniform vec4  u_cor;

out vec4 v2fcolor;

void main() {
    float c = cos(u_angulo);
    float s = sin(u_angulo);
    float x = vPosition.x * c - vPosition.y * s;
    float y = vPosition.x * s + vPosition.y * c;

    gl_Position = vec4(vec2(x, y) * u_escala + u_deslocamento, vPosition.zw);

    v2fcolor = u_cor;
}
