import random
import sys
import pygame

from assets import (
    ajustar_ao_quadro,
    carregar_animacao_jogador,
    carregar_icone,
    carregar_sprite,
    carregar_sprite_proporcional,
    carregar_variantes_lixo,
    criar_fundo,
    fallback_jogador,
    fallback_lixeira,
)
from audio import Audio
from config import (
    ALCANCE_MAX,
    ALCANCE_MIN,
    ALTURA,
    COR_ACERTO,
    COR_ERRO,
    DISTANCIA_LIXEIRA,
    ESCALA_ICONE,
    ESCALA_JOGADOR,
    FPS,
    INTERVALO_INICIAL,
    INTERVALO_MINIMO,
    ITENS,
    LARGURA,
    MARGEM_COLETA,
    MAX_LIXOS_NA_TELA,
    NOMES_TIPOS,
    POSICAO_LIXEIRAS,
    REJEITO_CHANCE_INICIAL,
    REJEITO_CHANCE_MAX,
    REJEITO_INICIO,
    REJEITO_TEMPO_MAX,
    REDUCAO_INTERVALO,
    TEMPO_CARGA_MAX,
    TEMPO_DE_VIDA_LIXO,
    TEMPO_REDUCAO,
    TIPO_REJEITO,
    TIPOS,
    VELOCIDADE_CARREGANDO,
    VIDAS_INICIAIS,
)
from entidades import Jogador, Lixeira, Lixo, Projetil
from metricas import RegistroPartida
from ui import InterfaceJogo


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

        self.audio = Audio()
        self.audio.tocar_musica()

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
        self.fundo = criar_fundo()
        self.lixeiras = [
            Lixeira(t, pos, self.sprites_lixeira[t]) for t, pos in POSICAO_LIXEIRAS.items()
        ]
        self.icones = {
            n: carregar_icone(n, ESCALA_ICONE, self.fonte)
            for n in ("w", "a", "s", "d", "e", "k", "mouse", "mouse_esquerdo")
        }

        self.metricas = RegistroPartida()
        self.ui = InterfaceJogo(self)
        self.estado = "menu"   # "menu" (tela inicial), "jogando" ou "guia" (guia de lixos)
        self.estado_anterior = "menu"   # para onde voltar ao fechar o guia
        self.reiniciar()

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
        self.metricas.reiniciar()
        self.resumo = None

    @property
    def consultas_guia(self):
        return self.metricas.consultas_guia

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
        fracao = min(
            1.0, (self.tempo_total - REJEITO_INICIO) / (REJEITO_TEMPO_MAX - REJEITO_INICIO)
        )
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

    def finalizar_partida(self):
        self.resumo = self.metricas.calcular_resumo(self.tempo_total, self.pontos)
        self.metricas.salvar_resultado(self.resumo)

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
            self.audio.tocar("acerto")
            self.metricas.registrar(self.tempo_total, "acerto", lixo, lixeira.tipo)
            if lixo.tipo == TIPO_REJEITO:    # acertou uma 'pegadinha': explica por que não é reciclável
                self.mostrar_mensagem("Acertou! +10", f"{lixo.nome}: {lixo.dica}", COR_ACERTO, 3.0)
            else:
                self.mostrar_mensagem("Acertou! +10", "", COR_ACERTO, 1.2)
        else:
            self.metricas.registrar(self.tempo_total, "erro", lixo, lixeira.tipo)
            self.audio.tocar("erro")
            certa = NOMES_TIPOS.get(lixo.tipo, lixo.tipo.upper())
            self.perder_vida(
                "Lixeira errada! -1 vida", f"{lixo.nome} vai no {certa}. {lixo.dica}".strip()
            )

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
                self.metricas.registrar(self.tempo_total, "perdido", lixo)
                self.audio.tocar("sumiu")
                self.perder_vida(
                    "Lixo perdido! -1 vida",
                    f"{lixo.nome} sumiu: pegue o lixo antes de {int(TEMPO_DE_VIDA_LIXO)} segundos.",
                )
                if self.fim_de_jogo:
                    break

        if self.tempo_mensagem > 0:
            self.tempo_mensagem -= dt

    def iniciar(self):
        self.reiniciar()
        self.estado = "jogando"

    def abrir_guia(self):
        if self.estado == "jogando":
            self.metricas.consultas_guia += 1     # métrica: o jogador precisou consultar o guia
        self.estado_anterior = self.estado
        self.estado = "guia"
        self.mirando = False       # cancela um arremesso que estivesse sendo carregado
        self.tempo_carga = 0

    def fechar_guia(self):
        self.estado = self.estado_anterior

    def desenhar(self):
        self.ui.desenhar()

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
                    if (
                        (
                            evento.type == pygame.KEYDOWN
                            and evento.key
                            in (pygame.K_k, pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
                        )
                        or (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)
                    ):
                        self.fechar_guia()
                    continue

                # ----- tela inicial -----
                if self.estado == "menu":
                    if evento.type == pygame.KEYDOWN and evento.key == pygame.K_k:
                        self.abrir_guia()
                    elif (
                        (
                            evento.type == pygame.KEYDOWN
                            and evento.key
                            in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)
                        )
                        or (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1)
                    ):
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
                if (
                    evento.type == pygame.MOUSEBUTTONDOWN
                    and evento.button == 1
                    and not self.fim_de_jogo
                    and self.jogador.carregando
                ):
                    self.mirando = True
                    self.tempo_carga = 0
                if (
                    evento.type == pygame.MOUSEBUTTONUP
                    and evento.button == 1
                    and self.mirando
                    and not self.fim_de_jogo
                ):
                    self.arremessar(evento.pos)
            self.atualizar(dt)
            self.desenhar()