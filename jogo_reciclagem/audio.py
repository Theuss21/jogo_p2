import os
import pygame

from config import ARQUIVO_MUSICA, EFEITOS_SONOROS, PASTA_AUDIO, VOLUME_MUSICA


class Audio:
    """Música de fundo e efeitos sonoros.
    Se não houver placa de som (ou faltar algum arquivo), o jogo continua normalmente, sem som."""

    def __init__(self):
        self.efeitos = {}
        self.pronto = self._iniciar_mixer()
        if not self.pronto:
            return
        for nome, (arquivo, volume) in EFEITOS_SONOROS.items():
            try:
                som = pygame.mixer.Sound(os.path.join(PASTA_AUDIO, arquivo))
                som.set_volume(volume)
                self.efeitos[nome] = som
            except (pygame.error, FileNotFoundError):
                pass   # arquivo ausente ou inválido: esse efeito fica mudo

    @staticmethod
    def _iniciar_mixer():
        if pygame.mixer.get_init():
            return True
        try:
            pygame.mixer.init()
            return True
        except pygame.error:
            return False

    def tocar_musica(self):
        if not self.pronto:
            return
        try:
            pygame.mixer.music.load(os.path.join(PASTA_AUDIO, ARQUIVO_MUSICA))
            pygame.mixer.music.set_volume(VOLUME_MUSICA)
            pygame.mixer.music.play(-1, fade_ms=1500)   # -1 = repete para sempre
        except (pygame.error, FileNotFoundError):
            pass

    def tocar(self, nome):
        som = self.efeitos.get(nome)
        if som:
            som.play()