import os
import pygame

from config import (
    ALTURA,
    DIRECOES,
    ESCALA_GUIA,
    ESCALA_LIXO,
    LARGURA,
    PASTA_ASSETS,
)


def carregar_sprite(nome_arquivo, tamanho, desenhar_fallback):
    """Tenta carregar assets/<nome_arquivo>. Se não existir, usa o fallback."""
    caminho = os.path.join(PASTA_ASSETS, nome_arquivo)
    if os.path.exists(caminho):
        img = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.smoothscale(img, tamanho)
    surf = pygame.Surface(tamanho, pygame.SRCALPHA)
    desenhar_fallback(surf)
    return surf


def carregar_sprite_proporcional(nome_arquivo, altura, tamanho_fallback, desenhar_fallback):
    """Carrega assets/<nome_arquivo> ajustando a ALTURA e mantendo a proporção da imagem."""
    caminho = os.path.join(PASTA_ASSETS, nome_arquivo)
    if os.path.exists(caminho):
        img = pygame.image.load(caminho).convert_alpha()
        largura = max(1, round(img.get_width() * altura / img.get_height()))
        return pygame.transform.smoothscale(img, (largura, altura))
    return carregar_sprite(nome_arquivo, tamanho_fallback, desenhar_fallback)


def carregar_animacao_jogador(escala, sprite_unico):
    """Carrega assets/jogador/<direcao>_<0..2>.png (4 direções x 3 quadros de caminhada).
    Se faltar algum arquivo, usa o sprite único (sem animação)."""
    pasta = os.path.join(PASTA_ASSETS, "jogador")
    animacao = {}
    try:
        for direcao in DIRECOES:
            quadros = []
            for n in range(3):
                img = pygame.image.load(os.path.join(pasta, f"{direcao}_{n}.png")).convert_alpha()
                quadros.append(
                    pygame.transform.scale(
                        img, (img.get_width() * escala, img.get_height() * escala)
                    )
                )
            animacao[direcao] = quadros
    except (FileNotFoundError, pygame.error):
        animacao = {direcao: [sprite_unico] * 3 for direcao in DIRECOES}
    return animacao


def carregar_variantes_lixo(tipo, cor):
    """Carrega assets/lixos/<tipo>_1.png, <tipo>_2.png... (vários visuais por tipo)."""
    pasta = os.path.join(PASTA_ASSETS, "lixos")
    sprites = []
    if os.path.isdir(pasta):
        for arquivo in sorted(os.listdir(pasta)):
            if arquivo.startswith(f"{tipo}_") and arquivo.lower().endswith(".png"):
                img = pygame.image.load(os.path.join(pasta, arquivo)).convert_alpha()
                tam = (
                    max(1, round(img.get_width() * ESCALA_LIXO)),
                    max(1, round(img.get_height() * ESCALA_LIXO)),
                )
                sprites.append(pygame.transform.smoothscale(img, tam))
    if not sprites:  # sem imagens: usa o arquivo único antigo ou um placeholder colorido
        sprites.append(carregar_sprite(f"lixo_{tipo}.png", (30, 30), fallback_lixo(cor)))
    return sprites


def carregar_icone(nome, escala, fonte):
    """Ícone de tecla/mouse de assets/teclas/<nome>.png (com fallback desenhado)."""
    caminho = os.path.join(PASTA_ASSETS, "teclas", f"{nome}.png")
    if os.path.exists(caminho):
        img = pygame.image.load(caminho).convert_alpha()
        return pygame.transform.scale(img, (img.get_width() * escala, img.get_height() * escala))
    surf = pygame.Surface((20 * escala, 20 * escala), pygame.SRCALPHA)
    pygame.draw.rect(surf, (240, 240, 240), surf.get_rect(), border_radius=8)
    rotulo = {"mouse": "M", "mouse_esquerdo": "M1"}.get(nome, nome.upper())
    txt = fonte.render(rotulo, True, (30, 30, 30))
    surf.blit(txt, txt.get_rect(center=surf.get_rect().center))
    return surf


def criar_fundo():
    """Piso quadriculado simples. Pode trocar por assets/fundo.png."""
    caminho = os.path.join(PASTA_ASSETS, "fundo.png")
    if os.path.exists(caminho):
        img = pygame.image.load(caminho).convert()
        if img.get_size() != (LARGURA, ALTURA):
            img = pygame.transform.smoothscale(img, (LARGURA, ALTURA))
        return img
    fundo = pygame.Surface((LARGURA, ALTURA))
    tam = 64
    for y in range(0, ALTURA, tam):
        for x in range(0, LARGURA, tam):
            cor = (120, 160, 110) if (x // tam + y // tam) % 2 == 0 else (110, 150, 100)
            pygame.draw.rect(fundo, cor, (x, y, tam, tam))
    return fundo


def quebrar_texto(texto, fonte, largura_max):
    """Divide um texto em linhas que cabem na largura dada."""
    linhas, atual = [], ""
    for palavra in texto.split():
        teste = f"{atual} {palavra}".strip()
        if fonte.size(teste)[0] <= largura_max:
            atual = teste
        else:
            if atual:
                linhas.append(atual)
            atual = palavra
    if atual:
        linhas.append(atual)
    return linhas


def ajustar_ao_quadro(sprite, lado=60, escala_max=ESCALA_GUIA):
    """Amplia/reduz o sprite para caber num quadrado (sem passar de escala_max)."""
    esc = min(lado / sprite.get_width(), lado / sprite.get_height(), escala_max)
    return pygame.transform.smoothscale(
        sprite,
        (max(1, round(sprite.get_width() * esc)), max(1, round(sprite.get_height() * esc))),
    )


def desenhar_texto(tela, fonte, texto, cor, **posicao):
    """Desenha texto com uma sombra escura, para ler bem sobre o fundo."""
    img = fonte.render(texto, True, cor)
    rect = img.get_rect(**posicao)
    tela.blit(fonte.render(texto, True, (20, 20, 28)), rect.move(2, 2))
    tela.blit(img, rect)


def fallback_jogador(surf):
    w, h = surf.get_size()
    pygame.draw.ellipse(surf, (40, 40, 40), (4, h - 14, w - 8, 12))          # sombra
    pygame.draw.rect(surf, (30, 90, 200), (8, 16, w - 16, h - 28), border_radius=10)
    pygame.draw.circle(surf, (250, 210, 170), (w // 2, 14), 12)               # cabeça
    pygame.draw.circle(surf, (0, 0, 0), (w // 2 - 4, 12), 2)
    pygame.draw.circle(surf, (0, 0, 0), (w // 2 + 4, 12), 2)


def fallback_lixo(cor):
    def desenhar(surf):
        w, h = surf.get_size()
        pygame.draw.rect(surf, cor, (0, 0, w, h), border_radius=6)
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, w, h), 2, border_radius=6)
    return desenhar


def fallback_lixeira(cor):
    def desenhar(surf):
        w, h = surf.get_size()
        pygame.draw.rect(surf, cor, (6, 14, w - 12, h - 16), border_radius=8)
        pygame.draw.rect(surf, (0, 0, 0), (6, 14, w - 12, h - 16), 3, border_radius=8)
        pygame.draw.rect(surf, (30, 30, 30), (0, 6, w, 12), border_radius=4)  # tampa
    return desenhar