# Cena 2D: Sr. Coração e seus amigos

Trabalho prático de Computação Gráfica (MCCC007-23, UFABC): uma cena 2D interativa em Python, com OpenGL 4.0 Core (`glfw`, `moderngl`, `numpy` e `pillow`). Ela expande o exemplo do **Sr. Coração**.

A cena tem:

- casa, árvore, grama e nuvens;
- sol de dia e, à noite, lua crescente e estrelas;
- chuva;
- estações do ano: raios de calor saindo do sol no verão, árvore sem folhas no outono, neve no inverno e flores na primavera;
- o Sr. Coração e a Sra. Coração, de laço;
- um painel com o estado da cena (horário, chuva, estação, cor da casa, tela cheia), num retângulo cinza translúcido.

Tudo é desenhado com um único par de shaders (`src/app/shaders/`), reaproveitando poucas geometrias. Até o texto do painel: o Pillow escreve as letras numa imagem em preto e branco, e cada pixel aceso vira um retângulo.

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
| K | exibe no terminal o tutorial com as teclas de controle |
| H | exibe no terminal as informações do driver e da placa de vídeo |
| I | mostra / esconde o painel com o estado da cena |
| D | dia / noite (cor de fundo e atenuação via uniform) |
| R | liga / desliga a chuva |
| C | troca a cor da casa |
| E | troca a estação do ano (verão, outono, inverno, primavera) |
| F | liga / desliga a tela cheia (a cena fica quadrada, no centro do monitor) |
| P | salva uma captura de tela em `capturas/` |
| ESC | encerra o programa |

## Logs

O programa registra no terminal, com data e hora, o que acontece durante a execução:

- início e encerramento;
- cada mudança de estado (dia/noite, chuva, cor da casa, estação do ano, tela cheia, painel);
- capturas de tela salvas;
- erros, em `stderr`.

## Estrutura

```text
src/app/
├── main.py            janela, contexto OpenGL e laço principal
├── cena.py            Cena (objetos, teclado, estado global) e EstadoCena
├── renderizador.py    Renderizador e Malha: programa de shaders, VBO/VAO/EBO, uniforms
├── geometria.py       funções numpy que geram os vértices de cada forma
├── config.py          constantes globais (janela, chão, cores do céu, atenuação)
├── objetos/           uma classe por elemento da cena (herdam de ObjetoCena)
├── shaders/           main_vertex_shader.vert e main_frag_shader.frag
└── utils/             funções auxiliares (logs, teclado, shaders, tela cheia, capturas)
```
