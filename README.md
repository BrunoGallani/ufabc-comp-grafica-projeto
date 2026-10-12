# Cena 2D: Sr. Coração e seus amigos

Trabalho prático de Computação Gráfica (MCCC007-23, UFABC): uma cena 2D interativa em Python, com OpenGL 4.0 Core (`glfw`, `moderngl` e `numpy`). Ela foi construída expandindo o exemplo do **Sr. Coração** visto em aula.

A cena tem:

- casa, árvore, grama e nuvens;
- sol de dia e, à noite, lua crescente e estrelas;
- chuva;
- o Sr. Coração e a Sra. Coração.

Tudo é desenhado com um único par de shaders (`src/app/shaders/`), reaproveitando poucas geometrias.

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate          # no Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/app/main.py
```

## Teclas

| Tecla | Ação |
| --- | --- |
| Setas | o Sr. Coração move o olhar |
| Shift + setas | o Sr. Coração anda |
| D | dia / noite (cor de fundo e atenuação via uniform) |
| R | liga / desliga a chuva |
| C | troca a cor da casa |
| A | troca a estação (cor) da árvore |
| P | salva uma captura de tela em `capturas/` |
| ESC | sai |

## Estrutura

```text
src/app/
├── main.py            janela, contexto OpenGL e laço principal
├── cena.py            Cena (objetos, teclado, estado global) e EstadoCena
├── renderizador.py    Renderizador e Malha: programa de shaders, VBO/VAO/EBO, uniforms
├── geometria.py       funções numpy que geram os vértices de cada forma
├── config.py          constantes globais (janela, chão, cores do céu, atenuação)
├── objetos/           uma classe por elemento da cena (herdam de ObjetoCena)
├── shaders/           senhor_coracao.vert e senhor_coracao.frag
└── utils/             funções auxiliares (data, título, hardware, capturas)
```
