# Eco Coleta

**Jogo educativo sobre coleta seletiva e classificação de resíduos.**

## 1. Sobre o projeto

Eco Coleta é um jogo educativo 2D desenvolvido em Python utilizando a biblioteca Pygame Community Edition (pygame-ce).

O projeto tem como objetivo estimular o reconhecimento e a classificação correta de resíduos recicláveis e não recicláveis por meio de uma experiência interativa.

Durante a partida, o jogador controla um personagem que deve recolher os resíduos espalhados pelo cenário e encaminhá-los às lixeiras correspondentes. O jogo apresenta pontuação, penalidades, limite de vidas e dificuldade progressiva.

## 2. Como executar

### Executável para Windows

1. Baixe ou extraia os arquivos do projeto.
2. Localize o arquivo `EcoColeta.exe`.
3. Execute o arquivo com dois cliques.
4. Aguarde a inicialização do jogo.

**Requisitos:** computador com sistema operacional Windows compatível com o executável.

Não é necessário instalar Python ou Pygame para utilizar a versão executável disponibilizada.

Caso o pacote de entrega contenha uma pasta de recursos (`assets`), mantenha sua estrutura e localização original junto ao executável.

## 3. Controles

| Comando | Ação |
|---|---|
| W, A, S, D | Movimentar o personagem |
| Setas direcionais | Movimentar o personagem |
| E | Descartar o resíduo na lixeira próxima |
| Botão esquerdo do mouse | Mirar, carregar e arremessar o resíduo |
| K | Abrir ou fechar o guia educativo |
| Enter | Iniciar ou confirmar |
| R | Reiniciar a partida após o fim |

A coleta dos resíduos acontece automaticamente quando o personagem se aproxima deles.

## 4. Como jogar

1. Inicie a partida pelo menu principal.
2. Movimente o personagem pelo cenário para recolher os resíduos.
3. Identifique o tipo de material recolhido.
4. Encaminhe o resíduo à lixeira correspondente.
5. Utilize o guia educativo para consultar as categorias e exemplos de materiais.
6. Evite descartes incorretos e não deixe os resíduos desaparecerem antes da coleta.

Os descartes corretos concedem pontos, enquanto os incorretos e os resíduos perdidos provocam a perda de vidas.

## 5. Categorias de resíduos

O jogo apresenta cinco categorias de descarte seletivo:

- **Azul:** papel.
- **Vermelho:** plástico.
- **Verde:** vidro.
- **Amarelo:** metal.
- **Cinza:** rejeitos.

O guia educativo disponível durante a partida apresenta exemplos e orientações sobre a classificação dos materiais.

## 6. Informações técnicas

| Item | Tecnologia |
|---|---|
| Linguagem | Python 3.13.7 |
| Biblioteca principal | pygame-ce 2.5.8 |
| SDL | 2.32.10 |
| Plataforma | Windows |
| Resolução | 960 × 640 pixels |
| Taxa de atualização desejada | 60 FPS |

## 7. Estrutura do código-fonte

O projeto é organizado em módulos Python, separados conforme suas responsabilidades:

| Arquivo | Responsabilidade |
|---|---|
| `main.py` | Inicialização da aplicação. |
| `config.py` | Configurações, constantes e parâmetros do jogo. |
| `jogo.py` | Gerenciamento da partida, eventos e regras. |
| `entidades.py` | Classes do jogador, resíduos, lixeiras e projéteis. |
| `ui.py` | Menu, interface, guia educativo e resultados. |
| `assets.py` | Carregamento de imagens e animações. |
| `audio.py` | Reprodução de músicas e efeitos sonoros. |
| `metricas.py` | Registro de eventos e resultados das partidas. |

## 8. Testes

O jogo foi testado em três computadores. Durante os testes, apresentou desempenho próximo à meta de 60 FPS.

A versão executável também foi testada em outro computador com Windows, apresentando funcionamento adequado.

## 9. Equipe de desenvolvimento

- **Eduardo Felipe Rocha Agapito:** desenvolvimento do código, áudio e recursos visuais.
- **Matheus Campos Miguens:** desenvolvimento do código e implementação das mecânicas.
- **Pedro Timon da Costa:** documentação e testes.

## 10. Créditos e recursos utilizados

Os recursos visuais e sonoros utilizados no projeto possuem suas respectivas fontes e atribuições documentadas no arquivo `CREDITOS.txt`, disponibilizado junto aos materiais do projeto.

---

**Projeto acadêmico — Desafio P2: Jogos que Resolvem Problemas**

Desenvolvimento de Jogos Digitais — Engenharia de Software — 7º período.

**Eco Coleta — 2026**
