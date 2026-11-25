import csv
import datetime
import os
import random
import sys

import pygame

# ---------------------------------------------------------------
# CONFIGURAÇÕES
# ---------------------------------------------------------------
LARGURA, ALTURA = 960, 640
FPS = 60
PASTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
# onde salvar o resultados.csv (ao lado do .exe, quando empacotado)
PASTA_DADOS = (os.path.dirname(sys.executable) if getattr(sys, "frozen", False)
               else os.path.dirname(os.path.abspath(__file__)))
ARQUIVO_RESULTADOS = "resultados.csv"

VELOCIDADE_JOGADOR = 260       # pixels por segundo
MARGEM_COLETA = 16             # folga (px) ao redor do jogador para pegar o lixo
DISTANCIA_LIXEIRA = 100        # alcance para jogar na lixeira
MAX_LIXOS_NA_TELA = 8
INTERVALO_INICIAL = 5.0        # segundos entre lixos no começo do jogo
REDUCAO_INTERVALO = 0.15       # quanto o intervalo diminui a cada ciclo
TEMPO_REDUCAO = 10.0           # de quantos em quantos segundos o intervalo diminui
INTERVALO_MINIMO = 1.0         # o intervalo nunca fica menor que isso
TEMPO_DE_VIDA_LIXO = 5.0       # segundos até o lixo sumir se não for coletado
VELOCIDADE_ARREMESSO = 750     # pixels por segundo do lixo arremessado
TEMPO_CARGA_MAX = 1.5          # segundos segurando o clique até a força máxima
ALCANCE_MIN = 150              # alcance (px) de um toque rápido no clique
ALCANCE_MAX = 900              # alcance (px) com a força máxima
VELOCIDADE_CARREGANDO = 0.4    # fração da velocidade ao andar enquanto carrega
VIDAS_INICIAIS = 3
ESCALA_LIXO = 0.8              # tamanho dos sprites de lixo em relação ao PNG original
ESCALA_JOGADOR = 2             # ampliação (inteira) do personagem: pixels nítidos
TEMPO_PASSO = 0.12             # segundos que cada quadro da caminhada fica na tela
DIRECOES = ("frente", "costas", "esq", "dir")
ESCALA_GUIA = 1.4               # ampliação dos lixos no guia (para enxergar bem os detalhes)
TIPO_REJEITO = "rejeito"          # tipo de lixo que NÃO é reciclável (lixeira cinza)
REJEITO_INICIO = 20.0          # segundos de jogo até surgirem os primeiros itens não recicláveis
REJEITO_CHANCE_INICIAL = 0.10  # chance de um lixo novo ser não reciclável quando eles começam
REJEITO_CHANCE_MAX = 0.30      # chance máxima (atingida em REJEITO_TEMPO_MAX)
REJEITO_TEMPO_MAX = 120.0
COR_ACERTO = (120, 225, 130)
COR_ERRO = (255, 120, 100)
ESCALA_ICONE = 2               # ampliação (inteira) dos ícones de teclas na tela inicial

# Tipos de lixo: nome -> cor (usada nos placeholders)
# Para adicionar mais tipos, basta colocar aqui e posicionar a lixeira.
TIPOS = {
    "papel":    (60, 120, 220),
    "plastico": (220, 60, 60),
    "vidro":    (60, 170, 90),
    "metal":    (240, 200, 40),
    "rejeito":  (170, 176, 186),
}

# Nome de cada tipo como aparece na tela (com acento)
NOMES_TIPOS = {"papel": "PAPEL", "plastico": "PLÁSTICO", "vidro": "VIDRO", "metal": "METAL",
               "rejeito": "REJEITO"}
LEGENDAS_TIPOS = {"rejeito": "não reciclável"}   # texto pequeno sob o nome, no guia

# Cada item: (nome, dica). A ordem é a dos arquivos assets/lixos/<tipo>_1.png, <tipo>_2.png...
# A dica aparece na tela quando o jogador erra (ou acerta um item não reciclável).
ITENS = {
    "plastico": [
        ("Garrafa d'água", "Garrafa PET é plástico: esvazie e amasse."),
        ("Galão de leite", "Embalagem plástica limpa é reciclável."),
        ("Detergente", "Frasco plástico vazio vai no plástico."),
    ],
    "papel": [
        ("Caixa de papelão", "Papelão limpo e seco é reciclável."),
        ("Jornal", "Jornal é papel reciclável."),
        ("Saco de papel", "Papel limpo e seco é reciclável."),
    ],
    "vidro": [
        ("Garrafa", "Garrafa de vidro é reciclável."),
        ("Pote de vidro", "Vidro de embalagem é reciclável."),
        ("Garrafa de cerveja", "Garrafa de vidro é reciclável."),
    ],
    "metal": [
        ("Lata de atum", "Lata de conserva: enxágue e recicle como metal."),
        ("Lata de conserva", "Latas de aço são recicláveis."),
        ("Lata de refrigerante", "Lata de alumínio é muito valorizada na reciclagem."),
        ("Aerossol", "Aerossol só é reciclável se estiver vazio."),
    ],
    "rejeito": [
        ("Caixa de pizza suja", "A gordura contamina o papelão: não é reciclável."),
        ("Copo de isopor", "O isopor costuma não ser aceito na coleta comum."),
        ("Caneca de cerâmica", "Cerâmica não é reciclável (nem no vidro)."),
    ],
}

# Posição (centro) de cada lixeira nas extremidades da tela
MARGEM = 70
POSICAO_LIXEIRAS = {
    "papel":    (MARGEM, MARGEM),
    "plastico": (LARGURA - MARGEM, MARGEM),
    "vidro":    (MARGEM, ALTURA - MARGEM),
    "metal":    (LARGURA - MARGEM, ALTURA - MARGEM),
    "rejeito":  (LARGURA // 2, ALTURA - MARGEM),
}


# ---------------------------------------------------------------
# CARREGAMENTO DE IMAGENS (com fallback caso o arquivo não exista)
# ---------------------------------------------------------------
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
                quadros.append(pygame.transform.scale(
                    img, (img.get_width() * escala, img.get_height() * escala)))
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
                tam = (max(1, round(img.get_width() * ESCALA_LIXO)),
                       max(1, round(img.get_height() * ESCALA_LIXO)))
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
        sprite, (max(1, round(sprite.get_width() * esc)), max(1, round(sprite.get_height() * esc))))


def formatar_taxa(valor):
    return f"{valor:.1f}".replace(".", ",")


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


# ---------------------------------------------------------------
# CLASSES
# ---------------------------------------------------------------
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
        desenhar_texto(tela, fonte, NOMES_TIPOS.get(self.tipo, self.tipo.upper()), (255, 255, 255),
                       midtop=(self.pos.x, self.rect.bottom + 2))


# ---------------------------------------------------------------
# JOGO
# ---------------------------------------------------------------
class Jogo:
    def __init__(self):
        pygame.init()
        self.tela = pygame.display.set_mode((LARGURA, ALTURA))
        pygame.display.set_caption("Eco Coleta - Jogo da Reciclagem")
        self.relogio = pygame.time.Clock()
        self.fonte = pygame.font.SysFont(None, 28)
        self.fonte_grande = pygame.font.SysFont(None, 72)
        self.fonte_media = pygame.font.SysFont(None, 36)
        self.fonte_pequena = pygame.font.SysFont(None, 22)

        # sprites (arquivo em assets/ ou fallback desenhado)
        sprite_unico = carregar_sprite_proporcional("jogador.png", 64, (48, 60), fallback_jogador)
        self.animacao_jogador = carregar_animacao_jogador(ESCALA_JOGADOR, sprite_unico)
        self.sprites_lixo = {   # cada tipo tem uma LISTA de visuais; um é sorteado a cada lixo
            t: carregar_variantes_lixo(t, cor) for t, cor in TIPOS.items()
        }
        self.sprites_lixeira = {
            t: carregar_sprite(f"lixeira_{t}.png", (80, 90), fallback_lixeira(cor))
            for t, cor in TIPOS.items()
        }
        self.sprites_guia = {   # versões maiores dos lixos, só para a tela do guia
            t: [ajustar_ao_quadro(s) for s in lista] for t, lista in self.sprites_lixo.items()
        }
        self.fundo = self.criar_fundo()
        self.lixeiras = [
            Lixeira(t, pos, self.sprites_lixeira[t]) for t, pos in POSICAO_LIXEIRAS.items()
        ]
        self.icones = {
            n: carregar_icone(n, ESCALA_ICONE, self.fonte)
            for n in ("w", "a", "s", "d", "e", "k", "mouse", "mouse_esquerdo")
        }
        self.estado = "menu"   # "menu" (tela inicial), "jogando" ou "guia" (guia de lixos)
        self.estado_anterior = "menu"   # para onde voltar ao fechar o guia
        self.reiniciar()

    def criar_fundo(self):
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

    def reiniciar(self):
        self.jogador = Jogador(self.animacao_jogador)
        self.lixos = []
        self.projeteis = []
        self.mirando = False      # True enquanto segura o clique
        self.tempo_carga = 0
        self.pontos = 0
        self.vidas = VIDAS_INICIAIS
        self.intervalo_spawn = INTERVALO_INICIAL
        self.tempo_spawn = INTERVALO_INICIAL   # faz o 1º lixo aparecer logo no começo
        self.tempo_total = 0
        self.proxima_reducao = TEMPO_REDUCAO
        self.mensagem = ("", "", (255, 255, 255))   # (título, detalhe, cor)
        self.tempo_mensagem = 0
        self.fim_de_jogo = False
        self.eventos = []          # registro de cada acerto/erro/lixo perdido (para as métricas)
        self.consultas_guia = 0    # quantas vezes abriu o guia durante a partida
        self.resumo = None

    # ----- lógica -----
    def spawnar_lixo(self):
        if len(self.lixos) >= MAX_LIXOS_NA_TELA:
            return
        for _ in range(30):  # tenta achar uma posição livre
            pos = pygame.Vector2(
                random.randint(60, LARGURA - 60), random.randint(60, ALTURA - 60)
            )
            longe_das_lixeiras = all(pos.distance_to(l.pos) > 140 for l in self.lixeiras)
            longe_do_jogador = pos.distance_to(self.jogador.pos) > 100
            if longe_das_lixeiras and longe_do_jogador:
                if random.random() < self.chance_de_rejeito():
                    tipo = TIPO_REJEITO
                else:
                    tipo = random.choice([t for t in TIPOS if t != TIPO_REJEITO])
                indice = random.randrange(len(self.sprites_lixo[tipo]))
                nome, dica = self.dados_do_item(tipo, indice)
                self.lixos.append(Lixo(tipo, pos, self.sprites_lixo[tipo][indice], nome, dica))
                return

    def coletar_automatico(self):
        """Se a mão está vazia e o jogador encosta em um lixo, pega na hora."""
        if self.jogador.carregando is not None:
            return
        area = self.jogador.rect.inflate(MARGEM_COLETA, MARGEM_COLETA)
        for lixo in self.lixos:
            if area.colliderect(lixo.rect):
                self.lixos.remove(lixo)
                self.jogador.carregando = lixo
                return

    def lixeira_proxima(self):
        for lixeira in self.lixeiras:
            if lixeira.pos.distance_to(self.jogador.pos) <= DISTANCIA_LIXEIRA:
                return lixeira
        return None

    def chance_de_rejeito(self):
        """Itens não recicláveis (as 'pegadinhas') entram depois de um tempo e vão aumentando."""
        if TIPO_REJEITO not in TIPOS or self.tempo_total < REJEITO_INICIO:
            return 0.0
        fracao = min(1.0, (self.tempo_total - REJEITO_INICIO) / (REJEITO_TEMPO_MAX - REJEITO_INICIO))
        return REJEITO_CHANCE_INICIAL + (REJEITO_CHANCE_MAX - REJEITO_CHANCE_INICIAL) * fracao

    @staticmethod
    def dados_do_item(tipo, indice):
        itens = ITENS.get(tipo, [])
        if indice < len(itens):
            return itens[indice]
        return (NOMES_TIPOS.get(tipo, tipo).capitalize(), "")

    def mostrar_mensagem(self, titulo, detalhe="", cor=(255, 255, 255), duracao=1.2):
        self.mensagem = (titulo, detalhe, cor)
        self.tempo_mensagem = duracao

    def perder_vida(self, titulo, detalhe=""):
        self.vidas -= 1
        self.mostrar_mensagem(titulo, detalhe, COR_ERRO, 3.5)
        if self.vidas <= 0:
            self.fim_de_jogo = True
            self.finalizar_partida()

    # ----- métricas da partida -----
    def registrar(self, resultado, lixo, escolhida=None):
        """Guarda o que aconteceu: 'acerto', 'erro' (lixeira errada) ou 'perdido' (lixo sumiu)."""
        self.eventos.append({"t": self.tempo_total, "resultado": resultado, "item": lixo.nome,
                             "correta": lixo.tipo, "escolhida": escolhida})

    def calcular_resumo(self):
        eventos = self.eventos
        erros = [e for e in eventos if e["resultado"] == "erro"]
        meio = self.tempo_total / 2
        erros_1 = sum(1 for e in erros if e["t"] < meio)
        erros_2 = len(erros) - erros_1
        minutos = meio / 60
        confusoes = {}
        for e in erros:
            chave = (e["item"], e["correta"])
            confusoes[chave] = confusoes.get(chave, 0) + 1
        return {
            "duracao": self.tempo_total,
            "pontos": self.pontos,
            "acertos": sum(1 for e in eventos if e["resultado"] == "acerto"),
            "erros": len(erros),
            "perdidos": sum(1 for e in eventos if e["resultado"] == "perdido"),
            "erros_1": erros_1,
            "erros_2": erros_2,
            "taxa_1": erros_1 / minutos if minutos > 0 else 0.0,
            "taxa_2": erros_2 / minutos if minutos > 0 else 0.0,
            "consultas_guia": self.consultas_guia,
            "mais_confundido": max(confusoes, key=confusoes.get) if confusoes else None,
        }

    def salvar_resultado(self, r):
        """Acrescenta uma linha em resultados.csv (para usar nas métricas do GDD)."""
        colunas = ["data_hora", "duracao_s", "pontos", "acertos", "erros_lixeira", "lixos_perdidos",
                   "erros_1a_metade", "erros_2a_metade", "erros_por_min_1a", "erros_por_min_2a",
                   "consultas_guia"]
        linha = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), round(r["duracao"]),
                 r["pontos"], r["acertos"], r["erros"], r["perdidos"], r["erros_1"], r["erros_2"],
                 formatar_taxa(r["taxa_1"]), formatar_taxa(r["taxa_2"]), r["consultas_guia"]]
        caminho = os.path.join(PASTA_DADOS, ARQUIVO_RESULTADOS)
        try:
            novo = not os.path.exists(caminho)
            with open(caminho, "a", newline="", encoding="utf-8") as arquivo:
                escritor = csv.writer(arquivo, delimiter=";")
                if novo:
                    escritor.writerow(colunas)
                escritor.writerow(linha)
        except OSError:
            pass   # sem permissão para gravar: o jogo segue normalmente

    def finalizar_partida(self):
        self.resumo = self.calcular_resumo()
        self.salvar_resultado(self.resumo)

    def acao(self):
        """Tecla E: deposita o lixo da mão se estiver perto de uma lixeira."""
        jogador = self.jogador
        if jogador.carregando is not None:
            lixeira = self.lixeira_proxima()
            if lixeira:
                self.entregar(jogador.carregando, lixeira)
                jogador.carregando = None

    def entregar(self, lixo, lixeira):
        """Resolve acerto ou erro (vale tanto para depositar quanto para arremessar)."""
        if lixeira.tipo == lixo.tipo:
            self.pontos += 10
            self.registrar("acerto", lixo, lixeira.tipo)
            if lixo.tipo == TIPO_REJEITO:    # acertou uma 'pegadinha': explica por que não é reciclável
                self.mostrar_mensagem("Acertou! +10", f"{lixo.nome}: {lixo.dica}", COR_ACERTO, 3.0)
            else:
                self.mostrar_mensagem("Acertou! +10", "", COR_ACERTO, 1.2)
        else:
            self.registrar("erro", lixo, lixeira.tipo)
            certa = NOMES_TIPOS.get(lixo.tipo, lixo.tipo.upper())
            self.perder_vida("Lixeira errada! -1 vida", f"{lixo.nome} vai no {certa}. {lixo.dica}".strip())

    def calcular_destino(self, pos_mouse, tempo):
        """Ponto de pouso: o mouse dá a direção e o tempo de carga dá a distância."""
        fracao = min(1.0, tempo / TEMPO_CARGA_MAX)
        alcance = ALCANCE_MIN + (ALCANCE_MAX - ALCANCE_MIN) * fracao
        direcao = pygame.Vector2(pos_mouse) - self.jogador.pos
        if direcao.length_squared() == 0:
            direcao = pygame.Vector2(0, -1)
        destino = self.jogador.pos + direcao.normalize() * alcance
        return pygame.Vector2(
            max(20, min(LARGURA - 20, destino.x)),
            max(20, min(ALTURA - 20, destino.y)),
        )

    def arremessar(self, pos_mouse):
        """Soltar o clique: joga o lixo da mão com a força carregada."""
        jogador = self.jogador
        self.mirando = False
        if jogador.carregando is None:
            return
        destino = self.calcular_destino(pos_mouse, self.tempo_carga)
        self.projeteis.append(Projetil(jogador.carregando, jogador.pos, destino))
        jogador.carregando = None
        self.tempo_carga = 0

    def atualizar(self, dt):
        if self.estado != "jogando" or self.fim_de_jogo:
            return
        self.jogador.atualizar(dt, VELOCIDADE_CARREGANDO if self.mirando else 1.0)
        if self.mirando:
            self.jogador.olhar_para(pygame.mouse.get_pos())
        self.coletar_automatico()

        # sem lixo na mão (ex.: depositou com E), cancela a carga
        if self.jogador.carregando is None:
            self.mirando = False
        if self.mirando:
            self.tempo_carga = min(TEMPO_CARGA_MAX, self.tempo_carga + dt)
        self.tempo_total += dt

        # lixos em voo: acertam a primeira lixeira no caminho ou caem no chão
        for p in self.projeteis[:]:
            p.atualizar(dt)
            lixeira = next((l for l in self.lixeiras if l.rect.collidepoint(p.pos)), None)
            if lixeira:
                self.projeteis.remove(p)
                self.entregar(p.lixo, lixeira)
                if self.fim_de_jogo:
                    return
            elif p.chegou:
                self.projeteis.remove(p)
                p.lixo.pos = pygame.Vector2(p.pos)
                self.lixos.append(p.lixo)  # volta pro chão, com o tempo que sobrava

        # a cada TEMPO_REDUCAO segundos o intervalo entre lixos diminui
        if self.tempo_total >= self.proxima_reducao:
            self.intervalo_spawn = max(INTERVALO_MINIMO, self.intervalo_spawn - REDUCAO_INTERVALO)
            self.proxima_reducao += TEMPO_REDUCAO

        # surgimento de lixos
        self.tempo_spawn += dt
        if self.tempo_spawn >= self.intervalo_spawn:
            self.tempo_spawn = 0
            self.spawnar_lixo()

        # lixos no chão têm tempo limite; se sumirem, o jogador perde vida
        for lixo in self.lixos[:]:
            lixo.tempo_restante -= dt
            if lixo.tempo_restante <= 0:
                self.lixos.remove(lixo)
                self.registrar("perdido", lixo)
                self.perder_vida("Lixo perdido! -1 vida",
                                 f"{lixo.nome} sumiu: pegue o lixo antes de {int(TEMPO_DE_VIDA_LIXO)} segundos.")
                if self.fim_de_jogo:
                    break

        if self.tempo_mensagem > 0:
            self.tempo_mensagem -= dt

    # ----- desenho -----
    def iniciar(self):
        self.reiniciar()
        self.estado = "jogando"

    def abrir_guia(self):
        if self.estado == "jogando":
            self.consultas_guia += 1     # métrica: o jogador precisou consultar o guia
        self.estado_anterior = self.estado
        self.estado = "guia"
        self.mirando = False       # cancela um arremesso que estivesse sendo carregado
        self.tempo_carga = 0

    def fechar_guia(self):
        self.estado = self.estado_anterior

    def desenhar_painel(self):
        """Fundo + painel escuro usados pelo menu e pelo guia."""
        self.tela.blit(self.fundo, (0, 0))
        painel = pygame.Surface((LARGURA - 80, ALTURA - 60), pygame.SRCALPHA)
        pygame.draw.rect(painel, (15, 25, 20, 235), painel.get_rect(), border_radius=20)
        self.tela.blit(painel, (40, 30))

    def desenhar_menu(self):
        tela = self.tela
        self.desenhar_painel()
        branco, destaque = (255, 255, 255), (255, 215, 80)
        x_texto = 80

        titulo = self.fonte_grande.render("ECO COLETA", True, destaque)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 80)))

        # --- objetivo (curto) ---
        y = 135
        tela.blit(self.fonte_media.render("OBJETIVO", True, destaque), (x_texto, y))
        y += 36
        objetivo = (f"Jogue cada lixo na lixeira certa; nem tudo é reciclável! Lixo esquecido "
                    f"ou lixeira errada custam 1 vida (você tem {VIDAS_INICIAIS}).")
        for linha in quebrar_texto(objetivo, self.fonte, LARGURA - 2 * x_texto):
            tela.blit(self.fonte.render(linha, True, branco), (x_texto, y))
            y += 28
        y += 18

        # --- controles ---
        tela.blit(self.fonte_media.render("CONTROLES", True, destaque), (x_texto, y))
        y += 40
        controles = [
            (["w", "a", "s", "d"], "Andar. Encoste no lixo para pegar."),
            (["mouse"], "Mire com o mouse."),
            (["mouse_esquerdo"], "Segure para dar força, solte para jogar."),
            (["e"], "Deposita direto, se estiver perto da lixeira."),
            (["k"], "Guia de lixos: veja onde cada um vai."),
        ]
        x_descricao = 290
        for icones, descricao in controles:
            cy = y + 24
            x = x_texto
            for nome in icones:
                img = self.icones[nome]
                tela.blit(img, img.get_rect(midleft=(x, cy)))
                x += img.get_width() + 6
            linhas = quebrar_texto(descricao, self.fonte, LARGURA - 80 - x_descricao)
            ty = cy - 12 * len(linhas)
            for linha in linhas:
                tela.blit(self.fonte.render(linha, True, branco), (x_descricao, ty))
                ty += 24
            y += 52

        # --- chamada para começar (pisca entre duas cores) ---
        cor = destaque if (pygame.time.get_ticks() // 500) % 2 == 0 else branco
        chamada = self.fonte_media.render("Pressione ENTER ou clique para começar", True, cor)
        tela.blit(chamada, chamada.get_rect(center=(LARGURA // 2, ALTURA - 42)))

    def desenhar_guia(self):
        tela = self.tela
        self.desenhar_painel()
        branco, destaque = (255, 255, 255), (255, 215, 80)

        titulo = self.fonte_grande.render("GUIA DE LIXOS", True, destaque)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 75)))
        dica = self.fonte.render("Leve cada lixo para a lixeira certa. Cuidado: nem tudo é reciclável!",
                                 True, branco)
        tela.blit(dica, dica.get_rect(center=(LARGURA // 2, 118)))

        largura_coluna = (LARGURA - 80) // len(TIPOS)
        for i, (tipo, cor) in enumerate(TIPOS.items()):
            x_col = 40 + largura_coluna * i
            cx = x_col + largura_coluna // 2
            lixeira = self.sprites_lixeira[tipo]
            tela.blit(lixeira, lixeira.get_rect(midtop=(cx, 134)))
            rotulo = self.fonte_media.render(NOMES_TIPOS.get(tipo, tipo.upper()), True, cor)
            tela.blit(rotulo, rotulo.get_rect(midtop=(cx, 230)))
            legenda = LEGENDAS_TIPOS.get(tipo)
            if legenda:
                texto = self.fonte_pequena.render(legenda, True, branco)
                tela.blit(texto, texto.get_rect(midtop=(cx, 258)))

            itens = ITENS.get(tipo, [])
            for j, sprite in enumerate(self.sprites_guia[tipo]):   # uma linha por item
                cy = 312 + j * 70
                tela.blit(sprite, sprite.get_rect(center=(x_col + 36, cy)))
                if j < len(itens):
                    linhas = quebrar_texto(itens[j][0], self.fonte_pequena, largura_coluna - 78)
                    ty = cy - 9 * len(linhas)
                    for linha in linhas:
                        tela.blit(self.fonte_pequena.render(linha, True, branco), (x_col + 72, ty))
                        ty += 18

        rodape = self.fonte_media.render("Pressione K para voltar", True, destaque)
        tela.blit(rodape, rodape.get_rect(center=(LARGURA // 2, ALTURA - 42)))

    def desenhar_mensagem(self):
        """Faixa com o retorno da última ação (acerto, erro e o porquê)."""
        titulo, detalhe, cor = self.mensagem
        img_titulo = self.fonte_media.render(titulo, True, cor)
        imgs = ([self.fonte.render(l, True, (255, 255, 255))
                 for l in quebrar_texto(detalhe, self.fonte, 620)] if detalhe else [])
        largura = max([img_titulo.get_width()] + [i.get_width() for i in imgs]) + 40
        altura = 10 + img_titulo.get_height() + 4 + sum(i.get_height() + 2 for i in imgs) + 8
        painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(painel, (15, 25, 20, 215), painel.get_rect(), border_radius=14)
        y = 10
        painel.blit(img_titulo, img_titulo.get_rect(midtop=(largura // 2, y)))
        y += img_titulo.get_height() + 4
        for img in imgs:
            painel.blit(img, img.get_rect(midtop=(largura // 2, y)))
            y += img.get_height() + 2
        self.tela.blit(painel, painel.get_rect(midtop=(LARGURA // 2, 48)))

    def desenhar_resultado(self):
        """Tela de fim de jogo com as métricas da partida."""
        tela, r = self.tela, self.resumo
        branco, destaque = (255, 255, 255), (255, 215, 80)
        escurecer = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        escurecer.fill((0, 0, 0, 170))
        tela.blit(escurecer, (0, 0))
        largura, altura = 680, 540
        x0, y0 = (LARGURA - largura) // 2, (ALTURA - altura) // 2
        painel = pygame.Surface((largura, altura), pygame.SRCALPHA)
        pygame.draw.rect(painel, (15, 25, 20, 245), painel.get_rect(), border_radius=20)
        tela.blit(painel, (x0, y0))
        cx = LARGURA // 2

        t = self.fonte_grande.render("FIM DE JOGO", True, branco)
        tela.blit(t, t.get_rect(center=(cx, y0 + 48)))
        t = self.fonte_media.render(f"Pontuação: {r['pontos']}", True, destaque)
        tela.blit(t, t.get_rect(center=(cx, y0 + 100)))

        minutos, segundos = divmod(int(r["duracao"]), 60)
        esquerda = [f"Tempo jogado: {minutos}:{segundos:02d}", f"Acertos: {r['acertos']}",
                    f"Lixeira errada: {r['erros']}"]
        direita = [f"Lixos perdidos: {r['perdidos']}", f"Consultas ao guia: {r['consultas_guia']}"]
        for coluna, x in ((esquerda, x0 + 60), (direita, x0 + 360)):
            for k, linha in enumerate(coluna):
                tela.blit(self.fonte.render(linha, True, branco), (x, y0 + 140 + k * 30))

        y = y0 + 250
        tela.blit(self.fonte_media.render("ERROS DE SEPARAÇÃO POR MINUTO", True, destaque), (x0 + 60, y))
        y += 40
        for nome, taxa, qtd in (("1ª metade da partida", r["taxa_1"], r["erros_1"]),
                                ("2ª metade da partida", r["taxa_2"], r["erros_2"])):
            palavra = "erro" if qtd == 1 else "erros"
            texto = f"{nome}: {formatar_taxa(taxa)} por minuto ({qtd} {palavra})"
            tela.blit(self.fonte.render(texto, True, branco), (x0 + 60, y))
            y += 30
        y += 8

        if r["erros"] == 0:
            texto, cor = "Nenhum erro de separação. Excelente!", COR_ACERTO
        elif r["taxa_2"] < r["taxa_1"]:
            texto, cor = "Você errou menos na 2ª metade: está aprendendo!", COR_ACERTO
        elif r["taxa_2"] > r["taxa_1"]:
            texto, cor = ("Você errou mais na 2ª metade, quando o jogo acelera. "
                          "Consulte o guia (K) e tente de novo."), destaque
        else:
            texto, cor = "O ritmo de erros foi o mesmo nas duas metades.", branco
        for linha in quebrar_texto(texto, self.fonte, largura - 120):
            tela.blit(self.fonte.render(linha, True, cor), (x0 + 60, y))
            y += 28
        if r["mais_confundido"]:
            item, correta = r["mais_confundido"]
            texto = f"Item que mais confundiu: {item} (vai no {NOMES_TIPOS.get(correta, correta.upper())})"
            for linha in quebrar_texto(texto, self.fonte, largura - 120):
                tela.blit(self.fonte.render(linha, True, branco), (x0 + 60, y))
                y += 28

        cor = destaque if (pygame.time.get_ticks() // 500) % 2 == 0 else branco
        chamada = self.fonte_media.render("Pressione R para jogar de novo", True, cor)
        tela.blit(chamada, chamada.get_rect(center=(cx, y0 + altura - 36)))

    def desenhar(self):
        if self.estado in ("menu", "guia"):
            if self.estado == "menu":
                self.desenhar_menu()
            else:
                self.desenhar_guia()
            pygame.display.flip()
            return
        self.tela.blit(self.fundo, (0, 0))

        lixeira_perto = self.lixeira_proxima() if self.jogador.carregando else None
        for lixeira in self.lixeiras:
            lixeira.desenhar(self.tela, self.fonte, lixeira is lixeira_perto)

        for lixo in self.lixos:
            lixo.desenhar(self.tela)

        # mira: linha até o ponto de pouso previsto com a força atual
        if self.jogador.carregando and not self.fim_de_jogo:
            tempo = self.tempo_carga if self.mirando else 0
            pouso = self.calcular_destino(pygame.mouse.get_pos(), tempo)
            pygame.draw.line(self.tela, (255, 255, 255), self.jogador.pos, pouso, 1)
            pygame.draw.circle(self.tela, (255, 255, 255), pouso, 6, 2)

            if self.mirando:  # barra de força acima do jogador
                fracao = min(1.0, self.tempo_carga / TEMPO_CARGA_MAX)
                barra = pygame.Rect(0, 0, 56, 8)
                barra.midbottom = (self.jogador.pos.x,
                                   self.jogador.rect.top - self.jogador.carregando.sprite.get_height() - 4)
                cor = (int(255 * fracao), int(220 * (1 - fracao)) + 35, 40)
                pygame.draw.rect(self.tela, (30, 30, 30), barra.inflate(4, 4), border_radius=4)
                pygame.draw.rect(self.tela, cor, (barra.x, barra.y, int(barra.w * fracao), barra.h),
                                 border_radius=3)

        for p in self.projeteis:
            p.desenhar(self.tela)

        self.jogador.desenhar(self.tela)

        # HUD (faixa escura para ler bem sobre a calçada)
        barra = pygame.Surface((610, 34), pygame.SRCALPHA)
        pygame.draw.rect(barra, (15, 25, 20, 190), barra.get_rect(), border_radius=12)
        self.tela.blit(barra, barra.get_rect(midtop=(LARGURA // 2, 6)))
        self.tela.blit(self.fonte.render(f"Pontos: {self.pontos}", True, (255, 255, 255)),
                       (LARGURA // 2 - 280, 14))
        self.tela.blit(self.fonte.render(f"Vidas: {self.vidas}", True, (255, 255, 255)),
                       (LARGURA // 2 - 130, 14))
        self.tela.blit(self.fonte.render(f"Tempo: {int(self.tempo_total)}s", True, (255, 255, 255)),
                       (LARGURA // 2, 14))
        self.tela.blit(self.fonte_pequena.render("K - guia de lixos", True, (200, 210, 200)),
                       (LARGURA // 2 + 140, 17))

        if self.tempo_mensagem > 0 and not self.fim_de_jogo:
            self.desenhar_mensagem()
        if self.fim_de_jogo and self.resumo:
            self.desenhar_resultado()

        pygame.display.flip()

    # ----- loop principal -----
    def rodar(self):
        while True:
            dt = self.relogio.tick(FPS) / 1000
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    if self.estado == "guia":
                        self.fechar_guia()
                        continue
                    pygame.quit()
                    sys.exit()

                # ----- guia de lixos (o jogo fica pausado enquanto ele está aberto) -----
                if self.estado == "guia":
                    if ((evento.type == pygame.KEYDOWN
                         and evento.key in (pygame.K_k, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE))
                            or (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)):
                        self.fechar_guia()
                    continue

                # ----- tela inicial -----
                if self.estado == "menu":
                    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_k:
                        self.abrir_guia()
                    elif ((evento.type == pygame.KEYDOWN
                           and evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE))
                          or (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)):
                        self.iniciar()
                    continue

                # ----- jogo -----
                if evento.type == pygame.KEYDOWN:
                    if evento.key == pygame.K_k and not self.fim_de_jogo:
                        self.abrir_guia()
                        continue
                    if evento.key == pygame.K_e and not self.fim_de_jogo:
                        self.acao()
                    if evento.key == pygame.K_r and self.fim_de_jogo:
                        self.reiniciar()
                if (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1
                        and not self.fim_de_jogo and self.jogador.carregando):
                    self.mirando = True
                    self.tempo_carga = 0
                if (evento.type == pygame.MOUSEBUTTONUP and evento.button == 1
                        and self.mirando and not self.fim_de_jogo):
                    self.arremessar(evento.pos)
            self.atualizar(dt)
            self.desenhar()


if __name__ == "__main__":
    Jogo().rodar()
