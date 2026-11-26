import csv
import datetime
import os

from config import ARQUIVO_RESULTADOS, PASTA_DADOS


def formatar_taxa(valor):
    return f"{valor:.1f}".replace(".", ",")


class RegistroPartida:
    def __init__(self):
        self.eventos = []
        self.consultas_guia = 0

    def reiniciar(self):
        self.eventos = []
        self.consultas_guia = 0

    def registrar(self, tempo_total, resultado, lixo, escolhida=None):
        """Guarda o que aconteceu: 'acerto', 'erro' (lixeira errada) ou 'perdido' (lixo sumiu)."""
        self.eventos.append({
            "t": tempo_total,
            "resultado": resultado,
            "item": lixo.nome,
            "correta": lixo.tipo,
            "escolhida": escolhida,
        })

    def calcular_resumo(self, tempo_total, pontos):
        eventos = self.eventos
        erros = [e for e in eventos if e["resultado"] == "erro"]
        meio = tempo_total / 2
        erros_1 = sum(1 for e in erros if e["t"] < meio)
        erros_2 = len(erros) - erros_1
        minutos = meio / 60
        confusoes = {}
        for e in erros:
            chave = (e["item"], e["correta"])
            confusoes[chave] = confusoes.get(chave, 0) + 1
        return {
            "duracao": tempo_total,
            "pontos": pontos,
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
        colunas = [
            "data_hora", "duracao_s", "pontos", "acertos", "erros_lixeira",
            "lixos_perdidos", "erros_1a_metade", "erros_2a_metade",
            "erros_por_min_1a", "erros_por_min_2a", "consultas_guia",
        ]
        linha = [
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            round(r["duracao"]),
            r["pontos"],
            r["acertos"],
            r["erros"],
            r["perdidos"],
            r["erros_1"],
            r["erros_2"],
            formatar_taxa(r["taxa_1"]),
            formatar_taxa(r["taxa_2"]),
            r["consultas_guia"],
        ]
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