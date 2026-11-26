import pygame

from assets import desenhar_texto
from config import (
    ALTURA,
    LARGURA,
    NOMES_TIPOS,
    TEMPO_DE_VIDA_LIXO,
    TEMPO_PASSO,
    VELOCIDADE_ARREMESSO,
    VELOCIDADE_JOGADOR,
)


class Jogador:
    SEQUENCIA = (0, 1, 0, 2)   # ordem dos quadros da caminhada: parado, passo, parado, outro passo

    def __init__(self, animacao):
        self.pos = pygame.Vector2(LARGURA / 2, ALTURA / 2)
        self.animacao = animacao     # dict: direção -> lista de 3 quadros
        self.direcao = "frente"
        self.tempo_anim = 0.0
        self.andando = False
        self.carregando = None       # guarda o Lixo que está na mão

    @property
    def sprite(self):
        quadros = self.animacao[self.direcao]
        if not self.andando:
            return quadros[0]
        return quadros[self.SEQUENCIA[int(self.tempo_anim / TEMPO_PASSO) % len(self.SEQUENCIA)]]

    @property
    def rect(self):
        return self.sprite.get_rect(center=self.pos)

    @staticmethod
    def nome_da_direcao(vetor):
        if abs(vetor.x) > abs(vetor.y):
            return "dir" if vetor.x > 0 else "esq"
        return "frente" if vetor.y > 0 else "costas"

    def olhar_para(self, ponto):
        """Vira o personagem na direção de um ponto da tela (usado ao mirar)."""
        self.direcao = self.nome_da_direcao(pygame.Vector2(ponto) - self.pos)

    def atualizar(self, dt, fator=1.0):
        teclas = pygame.key.get_pressed()
        direcao = pygame.Vector2(
            (teclas[pygame.K_d] or teclas[pygame.K_RIGHT]) - (teclas[pygame.K_a] or teclas[pygame.K_LEFT]),
            (teclas[pygame.K_s] or teclas[pygame.K_DOWN]) - (teclas[pygame.K_w] or teclas[pygame.K_UP]),
        )
        self.andando = direcao.length_squared() > 0
        if self.andando:
            direcao = direcao.normalize()  # evita andar mais rápido na diagonal
            self.direcao = self.nome_da_direcao(direcao)
            self.tempo_anim += dt * fator  # caminha em câmera lenta enquanto carrega o arremesso
        else:
            self.tempo_anim = 0.0
        self.pos += direcao * VELOCIDADE_JOGADOR * fator * dt

        # mantém dentro da tela
        meio_w, meio_h = self.sprite.get_width() / 2, self.sprite.get_height() / 2
        self.pos.x = max(meio_w, min(LARGURA - meio_w, self.pos.x))
        self.pos.y = max(meio_h, min(ALTURA - meio_h, self.pos.y))

    def desenhar(self, tela):
        tela.blit(self.sprite, self.rect)
        if self.carregando:
            # desenha o lixo flutuando sobre a cabeça do jogador
            img = self.carregando.sprite
            tela.blit(img, img.get_rect(midbottom=(self.pos.x, self.rect.top + 4)))


class Lixo:
    def __init__(self, tipo, pos, sprite, nome="Lixo", dica=""):
        self.tipo = tipo
        self.nome = nome
        self.dica = dica
        self.pos = pygame.Vector2(pos)
        self.sprite = sprite
        self.tempo_restante = TEMPO_DE_VIDA_LIXO

    @property
    def rect(self):
        return self.sprite.get_rect(center=self.pos)

    def desenhar(self, tela):
        # pisca nos últimos 2 segundos para avisar que vai sumir
        if self.tempo_restante < 2 and int(self.tempo_restante * 6) % 2 == 0:
            return
        tela.blit(self.sprite, self.rect)


class Projetil:
    """Lixo em voo, indo do jogador até o ponto clicado."""

    def __init__(self, lixo, origem, destino):
        self.lixo = lixo
        self.pos = pygame.Vector2(origem)
        self.destino = pygame.Vector2(destino)
        self.chegou = False

    def atualizar(self, dt):
        falta = self.destino - self.pos
        passo = VELOCIDADE_ARREMESSO * dt
        if falta.length() <= passo:
            self.pos = pygame.Vector2(self.destino)
            self.chegou = True
        else:
            self.pos += falta.normalize() * passo

    def desenhar(self, tela):
        tela.blit(self.lixo.sprite, self.lixo.sprite.get_rect(center=self.pos))


class Lixeira:
    def __init__(self, tipo, pos, sprite):
        self.tipo = tipo
        self.pos = pygame.Vector2(pos)
        self.sprite = sprite

    @property
    def rect(self):
        return self.sprite.get_rect(center=self.pos)

    def desenhar(self, tela, fonte, destacada):
        tela.blit(self.sprite, self.rect)
        if destacada:
            pygame.draw.rect(tela, (255, 255, 255), self.rect.inflate(10, 10), 3, border_radius=10)
        desenhar_texto(
            tela,
            fonte,
            NOMES_TIPOS.get(self.tipo, self.tipo.upper()),
            (255, 255, 255),
            midtop=(self.pos.x, self.rect.bottom + 2),
        )