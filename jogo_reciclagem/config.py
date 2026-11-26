import os
import sys

LARGURA, ALTURA = 960, 640
FPS = 60
PASTA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
# onde salvar o resultados.csv (ao lado do .exe, quando empacotado)
PASTA_DADOS = (
    os.path.dirname(sys.executable)
    if getattr(sys, "frozen", False)
    else os.path.dirname(os.path.abspath(__file__))
)
ARQUIVO_RESULTADOS = "resultados.csv"
PASTA_AUDIO = os.path.join(PASTA_ASSETS, "audio")

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
ESCALA_GUIA = 1.4              # ampliação dos lixos no guia (para enxergar bem os detalhes)
TIPO_REJEITO = "rejeito"       # tipo de lixo que NÃO é reciclável (lixeira cinza)
REJEITO_INICIO = 20.0          # segundos de jogo até surgirem os primeiros itens não recicláveis
REJEITO_CHANCE_INICIAL = 0.10  # chance de um lixo novo ser não reciclável quando eles começam
REJEITO_CHANCE_MAX = 0.30      # chance máxima (atingida em REJEITO_TEMPO_MAX)
REJEITO_TEMPO_MAX = 120.0
COR_ACERTO = (120, 225, 130)
COR_ERRO = (255, 120, 100)

# Áudio: música de fundo e efeitos (nome: (arquivo, volume de 0 a 1)).
ARQUIVO_MUSICA = "musica.mp3"
VOLUME_MUSICA = 0.30
EFEITOS_SONOROS = {
    "acerto": ("acerto.wav", 0.8),   # lixo na lixeira certa
    "erro": ("erro.wav", 0.9),       # lixo na lixeira errada
    "sumiu": ("sumiu.wav", 0.6),     # lixo sumiu sem ser coletado
}

# Créditos exigidos pelas licenças (aparecem na tela inicial). Detalhes em CREDITOS.txt.
CREDITOS_NA_TELA = [
    "Lixos: Clint Bellanger (CC-BY 3.0)  |  Música: Bonky (OGA-BY 4.0)",
    "Sons: DavidW (CC-BY 3.0), Fupi (CC0), qubodup (CC0)  |  Ícones: Kenney (CC0)",
]
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
NOMES_TIPOS = {
    "papel": "PAPEL",
    "plastico": "PLÁSTICO",
    "vidro": "VIDRO",
    "metal": "METAL",
    "rejeito": "REJEITO",
}
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
    ],
    "rejeito": [
        ("Caixa de pizza suja", "A gordura contamina o papelão: não é reciclável."),
        ("Copo de isopor", "O isopor costuma não ser aceito na coleta comum."),
        ("Caneca de cerâmica", "Cerâmica não é reciclável (nem no vidro)."),
        ("Aerossol", "Aerossol pressurizado não vai na reciclagem comum."),
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