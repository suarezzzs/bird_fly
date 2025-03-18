import pygame
import random
import sys
from const import *

# Inicialização do Pygame
pygame.init()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Plane Crash')

# Carregamento de assets
GAME_SPRITES = {
    'background': pygame.image.load(BACKGROUND).convert_alpha(),
    'player': pygame.image.load(BIRD).convert_alpha(),
    'base': pygame.image.load(BASE).convert_alpha(),
    'message': pygame.image.load(MESSAGE).convert_alpha(),
    'numbers': [pygame.image.load(num) for num in NUMBERS],
    'pipes': (
        pygame.transform.flip(pygame.image.load(PIPE).convert_alpha(), False, True),
        pygame.image.load(PIPE).convert_alpha()
    )
}

# Carregamento de sons
GAME_SOUNDS = {
    'die': pygame.mixer.Sound(DIE),
    'hit': pygame.mixer.Sound(HIT),
    'point': pygame.mixer.Sound(POINT),
    'swoosh': pygame.mixer.Sound(SWOOSH),
    'wing': pygame.mixer.Sound(WING)
}

FPSCLOCK = pygame.time.Clock()

# Função: Carregar pontuações salvas
def carregar_pontuacoes():
    try:
        with open(SCORE_FILE, 'r') as f:
            scores = [int(line.strip()) for line in f.readlines()]
            return sorted(scores, reverse=True)[:3]
    except FileNotFoundError:
        return []

# Função: Salvar nova pontuação
def salvar_pontuacao(score):
    scores = carregar_pontuacoes()
    scores.append(score)
    scores = sorted(scores, reverse=True)[:3]
    with open(SCORE_FILE, 'w') as f:
        for s in scores:
            f.write(f"{s}\n")

# Função: Desenhar base móvel
def desenhar_base(base_x):
    base_width = GAME_SPRITES['base'].get_width()
    SCREEN.blit(GAME_SPRITES['base'], (base_x, SCREENHEIGHT * 0.95))
    SCREEN.blit(GAME_SPRITES['base'], (base_x + base_width, SCREENHEIGHT * 0.95))

# Função: Tela de Game Over
def tela_game_over(score):
    fonte_principal = pygame.font.Font(None, 40)
    fonte_secundaria = pygame.font.Font(None, 30)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        
        # Texto "Game Over"
        texto_game_over = fonte_principal.render("Game Over", True, FONT_COLOR)
        pos_x = SCREENWIDTH//2 - texto_game_over.get_width()//2
        SCREEN.blit(texto_game_over, (pos_x, SCREENHEIGHT//2 - 190))
        
        # Pontuação final
        texto_pontuacao = fonte_principal.render(f"Pontuação: {score}", True, FONT_COLOR)
        pos_x = SCREENWIDTH//2 - texto_pontuacao.get_width()//2
        SCREEN.blit(texto_pontuacao, (pos_x, SCREENHEIGHT//2 - 90))
        
        # Instruções
        texto_instrucao1 = fonte_secundaria.render("Tente Novamente", True, FONT_COLOR)
        pos_x = SCREENWIDTH//2 - texto_instrucao1.get_width()//2
        SCREEN.blit(texto_instrucao1, (pos_x, SCREENHEIGHT//2 - 150))
        
        texto_instrucao2 = fonte_secundaria.render("Pressione 'SPAÇO'", True, FONT_COLOR)
        pos_x = SCREENWIDTH//2 - texto_instrucao2.get_width()//2
        SCREEN.blit(texto_instrucao2, (pos_x, SCREENHEIGHT//2 - 130))
        
        pygame.display.update()
        FPSCLOCK.tick(30)

# Função: Tela Inicial/Menu Principal
def tela_inicial():
    pos_player_x = SCREENWIDTH // 5
    pos_player_y = (SCREENHEIGHT - GAME_SPRITES['player'].get_height()) // 2
    pos_msg_x = (SCREENWIDTH - GAME_SPRITES['message'].get_width()) // 2
    pos_msg_y = SCREENHEIGHT * 0.12
    fonte = pygame.font.Font(None, FONT_SIZE)
    pontuacoes = carregar_pontuacoes()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                GAME_SOUNDS['wing'].play()
                return

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['message'], (pos_msg_x, pos_msg_y))
        SCREEN.blit(GAME_SPRITES['player'], (pos_player_x, pos_player_y))

        # Exibição das pontuações
        texto_pontuacoes = fonte.render("Melhores Pontuações:", True, FONT_COLOR)
        SCREEN.blit(texto_pontuacoes, (20, SCREENHEIGHT - 120))
        
        for i, pontuacao in enumerate(pontuacoes):
            texto = fonte.render(f"{i+1}. {pontuacao}", True, FONT_COLOR)
            SCREEN.blit(texto, (40, SCREENHEIGHT - 100 + 30 * i))

        pygame.display.update()
        FPSCLOCK.tick(30)

# Função: Loop principal do jogo
def jogo_principal():
    pontuacao = 0
    pos_player_x = SCREENWIDTH // 5
    pos_player_y = SCREENHEIGHT // 2
    largura_base = GAME_SPRITES['base'].get_width()
    deslocamento_base = largura_base - SCREENWIDTH
    pos_base_x = 0

    # Geração inicial dos canos
    cano1 = gerar_cano_aleatorio()
    cano2 = gerar_cano_aleatorio()

    canos_superiores = [
        {'x': SCREENWIDTH + 200, 'y': cano1[0]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH // 2), 'y': cano2[0]['y']}
    ]
    
    canos_inferiores = [
        {'x': SCREENWIDTH + 200, 'y': cano1[1]['y']},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH // 2), 'y': cano2[1]['y']}
    ]

    velocidade_canos = -4
    velocidade_player = -9
    gravidade = 1
    forca_pulo = -9
    pulo_ativado = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                if pos_player_y > 0:
                    velocidade_player = forca_pulo
                    pulo_ativado = True
                    GAME_SOUNDS['wing'].play()

        # Física do jogador
        if velocidade_player < 10 and not pulo_ativado:
            velocidade_player += gravidade
        pulo_ativado = False
        pos_player_y += velocidade_player

        # Movimento da base
        pos_base_x = (pos_base_x - 4) % deslocamento_base

        # Movimento dos canos
        for cano_sup, cano_inf in zip(canos_superiores, canos_inferiores):
            cano_sup['x'] += velocidade_canos
            cano_inf['x'] += velocidade_canos

        # Gerenciamento dos canos
        if canos_superiores[0]['x'] < -GAME_SPRITES['pipes'][0].get_width():
            canos_superiores.pop(0)
            canos_inferiores.pop(0)
            novo_cano = gerar_cano_aleatorio()
            canos_superiores.append(novo_cano[0])
            canos_inferiores.append(novo_cano[1])

        # Verificação de pontos
        centro_player = pos_player_x + GAME_SPRITES['player'].get_width() / 2
        for cano in canos_superiores:
            centro_cano = cano['x'] + GAME_SPRITES['pipes'][0].get_width() / 2
            if centro_cano <= centro_player < centro_cano + 4:
                pontuacao += 1
                GAME_SOUNDS['point'].play()

        # Verificação de colisão
        if verificar_colisao(pos_player_x, pos_player_y, canos_superiores, canos_inferiores):
            GAME_SOUNDS['hit'].play()
            return pontuacao

        # Renderização
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for cano_sup, cano_inf in zip(canos_superiores, canos_inferiores):
            SCREEN.blit(GAME_SPRITES['pipes'][0], (cano_sup['x'], cano_sup['y']))
            SCREEN.blit(GAME_SPRITES['pipes'][1], (cano_inf['x'], cano_inf['y']))
        
        desenhar_base(pos_base_x)
        SCREEN.blit(GAME_SPRITES['player'], (pos_player_x, pos_player_y))
        mostrar_pontuacao(pontuacao)
        pygame.display.update()
        FPSCLOCK.tick(30)

# Função: Gerar posições aleatórias para os canos
def gerar_cano_aleatorio():
    altura_cano = GAME_SPRITES['pipes'][0].get_height()
    offset = SCREENHEIGHT // 3
    y2 = offset + random.randrange(
        0, 
        int(SCREENHEIGHT - GAME_SPRITES['base'].get_height() - 1.2 * offset)
    )
    y1 = altura_cano - y2 + offset
    pos_x = SCREENWIDTH + 10
    return [
        {'x': pos_x, 'y': -y1},  # Cano superior
        {'x': pos_x, 'y': y2}     # Cano inferior
    ]

# Função: Verificar colisões
def verificar_colisao(pos_x, pos_y, canos_sup, canos_inf):
    altura_player = GAME_SPRITES['player'].get_height()
    largura_player = GAME_SPRITES['player'].get_width()
    
    # Colisão com o chão
    if pos_y + altura_player >= SCREENHEIGHT * 0.95:
        return True
    
    # Colisão com canos
    for cano in canos_sup + canos_inf:
        pos_cano_x = cano['x']
        pos_cano_y = cano['y']
        altura_cano = GAME_SPRITES['pipes'][0].get_height()
        largura_cano = GAME_SPRITES['pipes'][0].get_width()
        
        if (pos_x < pos_cano_x + largura_cano and 
            pos_x + largura_player > pos_cano_x and 
            pos_y < pos_cano_y + altura_cano and 
            pos_y + altura_player > pos_cano_y):
            return True
    
    return False

# Função: Exibir pontuação atual
def mostrar_pontuacao(pontuacao):
    digitos = [int(d) for d in str(pontuacao)]
    largura_total = sum(GAME_SPRITES['numbers'][d].get_width() for d in digitos)
    x = (SCREENWIDTH - largura_total) // 2
    y = SCREENHEIGHT * 0.1
    for digito in digitos:
        SCREEN.blit(GAME_SPRITES['numbers'][digito], (x, y))
        x += GAME_SPRITES['numbers'][digito].get_width()

# Função: Controlador principal do jogo
def main():
    while True:
        tela_inicial()
        pontuacao = jogo_principal()
        salvar_pontuacao(pontuacao)
        tela_game_over(pontuacao)
        GAME_SOUNDS['die'].play()

if __name__ == "__main__":
    main()