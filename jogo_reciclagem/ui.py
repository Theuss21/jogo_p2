import pygame

from assets import quebrar_texto
from config import (
    ALTURA,
    COR_ACERTO,
    CREDITOS_NA_TELA,
    ITENS,
    LARGURA,
    LEGENDAS_TIPOS,
    NOMES_TIPOS,
    TEMPO_CARGA_MAX,
    TIPOS,
    VIDAS_INICIAIS,
)
from metricas import formatar_taxa


class InterfaceJogo:
    def __init__(self, jogo):
        self.jogo = jogo

    def desenhar_painel(self):
        """Fundo + painel escuro usados pelo menu e pelo guia."""
        jogo = self.jogo
        jogo.tela.blit(jogo.fundo, (0, 0))
        painel = pygame.Surface((LARGURA - 80, ALTURA - 60), pygame.SRCALPHA)
        pygame.draw.rect(painel, (15, 25, 20, 235), painel.get_rect(), border_radius=20)
        jogo.tela.blit(painel, (40, 30))

    def desenhar_menu(self):
        jogo = self.jogo
        tela = jogo.tela
        self.desenhar_painel()
        branco, destaque = (255, 255, 255), (255, 215, 80)
        x_texto = 80

        titulo = jogo.fonte_grande.render("ECO COLETA", True, destaque)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 80)))

        # --- objetivo (curto) ---
        y = 135
        tela.blit(jogo.fonte_media.render("OBJETIVO", True, destaque), (x_texto, y))
        y += 36
        objetivo = (
            f"Jogue cada lixo na lixeira certa; nem tudo é reciclável! Lixo esquecido "
            f"ou lixeira errada custam 1 vida (você tem {VIDAS_INICIAIS})."
        )
        for linha in quebrar_texto(objetivo, jogo.fonte, LARGURA - 2 * x_texto):
            tela.blit(jogo.fonte.render(linha, True, branco), (x_texto, y))
            y += 28
        y += 18

        # --- controles ---
        tela.blit(jogo.fonte_media.render("CONTROLES", True, destaque), (x_texto, y))
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
                img = jogo.icones[nome]
                tela.blit(img, img.get_rect(midleft=(x, cy)))
                x += img.get_width() + 6
            linhas = quebrar_texto(descricao, jogo.fonte, LARGURA - 80 - x_descricao)
            ty = cy - 12 * len(linhas)
            for linha in linhas:
                tela.blit(jogo.fonte.render(linha, True, branco), (x_descricao, ty))
                ty += 24
            y += 52

        # --- créditos (as licenças CC-BY e OGA-BY exigem citar o autor) ---
        for k, linha in enumerate(CREDITOS_NA_TELA):
            img = jogo.fonte_pequena.render(linha, True, (170, 180, 170))
            tela.blit(img, img.get_rect(midtop=(LARGURA // 2, ALTURA - 92 + k * 17)))

        # --- chamada para começar (pisca entre duas cores) ---
        cor = destaque if (pygame.time.get_ticks() // 500) % 2 == 0 else branco
        chamada = jogo.fonte_media.render("Pressione ENTER ou clique para começar", True, cor)
        tela.blit(chamada, chamada.get_rect(center=(LARGURA // 2, ALTURA - 42)))

    def desenhar_guia(self):
        jogo = self.jogo
        tela = jogo.tela
        self.desenhar_painel()
        branco, destaque = (255, 255, 255), (255, 215, 80)

        titulo = jogo.fonte_grande.render("GUIA DE LIXOS", True, destaque)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 75)))
        dica = jogo.fonte.render(
            "Leve cada lixo para a lixeira certa. Cuidado: nem tudo é reciclável!",
            True,
            branco,
        )
        tela.blit(dica, dica.get_rect(center=(LARGURA // 2, 118)))

        largura_coluna = (LARGURA - 80) // len(TIPOS)
        for i, (tipo, cor) in enumerate(TIPOS.items()):
            x_col = 40 + largura_coluna * i
            cx = x_col + largura_coluna // 2
            lixeira = jogo.sprites_lixeira[tipo]
            tela.blit(lixeira, lixeira.get_rect(midtop=(cx, 134)))
            rotulo = jogo.fonte_media.render(NOMES_TIPOS.get(tipo, tipo.upper()), True, cor)
            tela.blit(rotulo, rotulo.get_rect(midtop=(cx, 230)))
            legenda = LEGENDAS_TIPOS.get(tipo)
            if legenda:
                texto = jogo.fonte_pequena.render(legenda, True, branco)
                tela.blit(texto, texto.get_rect(midtop=(cx, 258)))

            itens = ITENS.get(tipo, [])
            for j, sprite in enumerate(jogo.sprites_guia[tipo]):   # uma linha por item
                cy = 312 + j * 70
                tela.blit(sprite, sprite.get_rect(center=(x_col + 36, cy)))
                if j < len(itens):
                    linhas = quebrar_texto(itens[j][0], jogo.fonte_pequena, largura_coluna - 78)
                    ty = cy - 9 * len(linhas)
                    for linha in linhas:
                        tela.blit(jogo.fonte_pequena.render(linha, True, branco), (x_col + 72, ty))
                        ty += 18

        rodape = jogo.fonte_media.render("Pressione K para voltar", True, destaque)
        tela.blit(rodape, rodape.get_rect(center=(LARGURA // 2, ALTURA - 42)))

    def desenhar_mensagem(self):
        """Faixa com o retorno da última ação (acerto, erro e o porquê)."""
        jogo = self.jogo
        titulo, detalhe, cor = jogo.mensagem
        img_titulo = jogo.fonte_media.render(titulo, True, cor)
        imgs = (
            [jogo.fonte.render(l, True, (255, 255, 255)) for l in quebrar_texto(detalhe, jogo.fonte, 620)]
            if detalhe
            else []
        )
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
        jogo.tela.blit(painel, painel.get_rect(midtop=(LARGURA // 2, 48)))

    def desenhar_resultado(self):
        """Tela de fim de jogo com as métricas da partida."""
        jogo = self.jogo
        tela, r = jogo.tela, jogo.resumo
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

        t = jogo.fonte_grande.render("FIM DE JOGO", True, branco)
        tela.blit(t, t.get_rect(center=(cx, y0 + 48)))
        t = jogo.fonte_media.render(f"Pontuação: {r['pontos']}", True, destaque)
        tela.blit(t, t.get_rect(center=(cx, y0 + 100)))

        minutos, segundos = divmod(int(r["duracao"]), 60)
        esquerda = [
            f"Tempo jogado: {minutos}:{segundos:02d}",
            f"Acertos: {r['acertos']}",
            f"Lixeira errada: {r['erros']}",
        ]
        direita = [f"Lixos perdidos: {r['perdidos']}", f"Consultas ao guia: {r['consultas_guia']}"]
        for coluna, x in ((esquerda, x0 + 60), (direita, x0 + 360)):
            for k, linha in enumerate(coluna):
                tela.blit(jogo.fonte.render(linha, True, branco), (x, y0 + 140 + k * 30))

        y = y0 + 250
        tela.blit(
            jogo.fonte_media.render("ERROS DE SEPARAÇÃO POR MINUTO", True, destaque), (x0 + 60, y)
        )
        y += 40
        for nome, taxa, qtd in (
            ("1ª metade da partida", r["taxa_1"], r["erros_1"]),
            ("2ª metade da partida", r["taxa_2"], r["erros_2"]),
        ):
            palavra = "erro" if qtd == 1 else "erros"
            texto = f"{nome}: {formatar_taxa(taxa)} por minuto ({qtd} {palavra})"
            tela.blit(jogo.fonte.render(texto, True, branco), (x0 + 60, y))
            y += 30
        y += 8

        if r["erros"] == 0:
            texto, cor = "Nenhum erro de separação. Excelente!", COR_ACERTO
        elif r["taxa_2"] < r["taxa_1"]:
            texto, cor = "Você errou menos na 2ª metade: está aprendendo!", COR_ACERTO
        elif r["taxa_2"] > r["taxa_1"]:
            texto, cor = (
                "Você errou mais na 2ª metade, quando o jogo acelera. "
                "Consulte o guia (K) e tente de novo."
            ), destaque
        else:
            texto, cor = "O ritmo de erros foi o mesmo nas duas metades.", branco
        for linha in quebrar_texto(texto, jogo.fonte, largura - 120):
            tela.blit(jogo.fonte.render(linha, True, cor), (x0 + 60, y))
            y += 28
        if r["mais_confundido"]:
            item, correta = r["mais_confundido"]
            texto = (
                f"Item que mais confundiu: {item} "
                f"(vai no {NOMES_TIPOS.get(correta, correta.upper())})"
            )
            for linha in quebrar_texto(texto, jogo.fonte, largura - 120):
                tela.blit(jogo.fonte.render(linha, True, branco), (x0 + 60, y))
                y += 28

        cor = destaque if (pygame.time.get_ticks() // 500) % 2 == 0 else branco
        chamada = jogo.fonte_media.render("Pressione R para jogar de novo", True, cor)
        tela.blit(chamada, chamada.get_rect(center=(cx, y0 + altura - 36)))

    def desenhar(self):
        jogo = self.jogo
        if jogo.estado in ("menu", "guia"):
            if jogo.estado == "menu":
                self.desenhar_menu()
            else:
                self.desenhar_guia()
            pygame.display.flip()
            return
        jogo.tela.blit(jogo.fundo, (0, 0))

        lixeira_perto = jogo.lixeira_proxima() if jogo.jogador.carregando else None
        for lixeira in jogo.lixeiras:
            lixeira.desenhar(jogo.tela, jogo.fonte, lixeira is lixeira_perto)

        for lixo in jogo.lixos:
            lixo.desenhar(jogo.tela)

        # mira: linha até o ponto de pouso previsto com a força atual
        if jogo.jogador.carregando and not jogo.fim_de_jogo:
            tempo = jogo.tempo_carga if jogo.mirando else 0
            pouso = jogo.calcular_destino(pygame.mouse.get_pos(), tempo)
            pygame.draw.line(jogo.tela, (255, 255, 255), jogo.jogador.pos, pouso, 1)
            pygame.draw.circle(jogo.tela, (255, 255, 255), pouso, 6, 2)

            if jogo.mirando:  # barra de força acima do jogador
                fracao = min(1.0, jogo.tempo_carga / TEMPO_CARGA_MAX)
                barra = pygame.Rect(0, 0, 56, 8)
                barra.midbottom = (
                    jogo.jogador.pos.x,
                    jogo.jogador.rect.top - jogo.jogador.carregando.sprite.get_height() - 4,
                )
                cor = (int(255 * fracao), int(220 * (1 - fracao)) + 35, 40)
                pygame.draw.rect(jogo.tela, (30, 30, 30), barra.inflate(4, 4), border_radius=4)
                pygame.draw.rect(
                    jogo.tela, cor, (barra.x, barra.y, int(barra.w * fracao), barra.h), border_radius=3
                )

        for p in jogo.projeteis:
            p.desenhar(jogo.tela)

        jogo.jogador.desenhar(jogo.tela)

        # HUD (faixa escura para ler bem sobre a calçada)
        barra = pygame.Surface((610, 34), pygame.SRCALPHA)
        pygame.draw.rect(barra, (15, 25, 20, 190), barra.get_rect(), border_radius=12)
        jogo.tela.blit(barra, barra.get_rect(midtop=(LARGURA // 2, 6)))
        jogo.tela.blit(
            jogo.fonte.render(f"Pontos: {jogo.pontos}", True, (255, 255, 255)),
            (LARGURA // 2 - 280, 14),
        )
        jogo.tela.blit(
            jogo.fonte.render(f"Vidas: {jogo.vidas}", True, (255, 255, 255)),
            (LARGURA // 2 - 130, 14),
        )
        jogo.tela.blit(
            jogo.fonte.render(f"Tempo: {int(jogo.tempo_total)}s", True, (255, 255, 255)),
            (LARGURA // 2, 14),
        )
        jogo.tela.blit(
            jogo.fonte_pequena.render("K - guia de lixos", True, (200, 210, 200)),
            (LARGURA // 2 + 140, 17),
        )

        if jogo.tempo_mensagem > 0 and not jogo.fim_de_jogo:
            self.desenhar_mensagem()
        if jogo.fim_de_jogo and jogo.resumo:
            self.desenhar_resultado()

        pygame.display.flip()