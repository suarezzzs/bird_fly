import pygame
import random
import sys
from const import *

# Inicialização do Pygame
pygame.init()
SCREEN = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT))
pygame.display.set_caption('Bird Fly')

# Carregamento de assets (corrigido)
def load_assets():
    return {
        'background': pygame.image.load(BACKGROUND).convert_alpha(),
        'player': pygame.image.load(BIRD).convert_alpha(),
        'base': pygame.image.load(BASE).convert_alpha(),
        'message': pygame.image.load(MESSAGE).convert_alpha(),
        'numbers': [pygame.image.load(num) for num in NUMBERS],
        'pipes': (
            pygame.transform.flip(
                pygame.image.load(PIPE).convert_alpha(), 
                False, 
                True
            ),  # Cano superior
            pygame.image.load(PIPE).convert_alpha()  # Cano inferior
        )
    }

def load_sounds():
    return {
        'die': pygame.mixer.Sound(DIE),
        'hit': pygame.mixer.Sound(HIT),
        'point': pygame.mixer.Sound(POINT),
        'swoosh': pygame.mixer.Sound(SWOOSH),
        'wing': pygame.mixer.Sound(WING)
    }

GAME_SPRITES = load_assets()
GAME_SOUNDS = load_sounds()
FPSCLOCK = pygame.time.Clock()

# ... (o restante do código permanece igual à versão anterior corrigida)

def welcome_screen():
    base_x = 0
    player_x = SCREENWIDTH // 5
    player_y = (SCREENHEIGHT - GAME_SPRITES['player'].get_height()) // 2
    message_x = (SCREENWIDTH - GAME_SPRITES['message'].get_width()) // 2
    message_y = SCREENHEIGHT * 0.12

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                GAME_SOUNDS['wing'].play()
                return

        # Movimento da base
        base_x = (base_x - 4) % (GAME_SPRITES['base'].get_width() - SCREENWIDTH)

        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        SCREEN.blit(GAME_SPRITES['message'], (message_x, message_y))
        SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
        SCREEN.blit(GAME_SPRITES['base'], (base_x, SCREENHEIGHT * 0.95))
        pygame.display.update()
        FPSCLOCK.tick(30)

def main_game():
    score = 0
    player_x = SCREENWIDTH // 5
    player_y = SCREENHEIGHT // 2
    base_x = 0
    base_shift = GAME_SPRITES['base'].get_width() - SCREENWIDTH

    # Configuração inicial dos canos
    first_pipe = get_random_pipe()
    pipes = [
        {'x': SCREENWIDTH + 200, 'top': first_pipe[0], 'bottom': first_pipe[1]},
        {'x': SCREENWIDTH + 200 + (SCREENWIDTH // 2), 'top': get_random_pipe()[0], 'bottom': get_random_pipe()[1]}
    ]

    player_velocity = -9
    gravity = 1
    game_active = True

    while game_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and (event.key == pygame.K_SPACE or event.key == pygame.K_UP):
                if player_y > 0:
                    player_velocity = -9
                    GAME_SOUNDS['wing'].play()

        # Atualizações do jogador
        player_velocity += gravity
        player_y += player_velocity

        # Movimento da base
        base_x = (base_x - 4) % base_shift

        # Movimento dos canos
        for pipe in pipes:
            pipe['x'] -= 4

            # Verificação de pontos
            if pipe['x'] + GAME_SPRITES['pipes'][0].get_width() // 2 == player_x:
                score += 1
                GAME_SOUNDS['point'].play()

            # Verificação de colisão
            if check_collision(player_x, player_y, pipe):
                GAME_SOUNDS['hit'].play()
                game_active = False

        # Remove canos fora da tela e adiciona novos
        if pipes[0]['x'] < -GAME_SPRITES['pipes'][0].get_width():
            pipes.pop(0)
            new_pipe = get_random_pipe()
            pipes.append({'x': pipes[-1]['x'] + SCREENWIDTH // 2, 'top': new_pipe[0], 'bottom': new_pipe[1]})

        # Renderização
        SCREEN.blit(GAME_SPRITES['background'], (0, 0))
        for pipe in pipes:
            SCREEN.blit(GAME_SPRITES['pipes'][0], (pipe['x'], pipe['top']['y']))
            SCREEN.blit(GAME_SPRITES['pipes'][1], (pipe['x'], pipe['bottom']['y']))
        SCREEN.blit(GAME_SPRITES['base'], (base_x, SCREENHEIGHT * 0.95))
        SCREEN.blit(GAME_SPRITES['player'], (player_x, player_y))
        show_score(score)
        pygame.display.update()
        FPSCLOCK.tick(30)

    # Tela de game over
    GAME_SOUNDS['die'].play()
    pygame.time.wait(1500)

def get_random_pipe():
    pipe_height = GAME_SPRITES['pipes'][0].get_height()
    offset = SCREENHEIGHT // 4
    y2 = offset + random.randint(0, SCREENHEIGHT - 2 * offset)
    y1 = y2 - pipe_height - 150  # Espaço entre os canos
    return [{'y': y1}, {'y': y2}]

def check_collision(player_x, player_y, pipe):
    player_rect = pygame.Rect(
        player_x,
        player_y,
        GAME_SPRITES['player'].get_width(),
        GAME_SPRITES['player'].get_height()
    )

    top_pipe_rect = pygame.Rect(
        pipe['x'],
        pipe['top']['y'],
        GAME_SPRITES['pipes'][0].get_width(),
        GAME_SPRITES['pipes'][0].get_height()
    )

    bottom_pipe_rect = pygame.Rect(
        pipe['x'],
        pipe['bottom']['y'],
        GAME_SPRITES['pipes'][1].get_width(),
        GAME_SPRITES['pipes'][1].get_height()
    )

    return player_rect.colliderect(top_pipe_rect) or player_rect.colliderect(bottom_pipe_rect)

def show_score(score):
    digits = [int(d) for d in str(score)]
    total_width = sum(GAME_SPRITES['numbers'][d].get_width() for d in digits)
    x = (SCREENWIDTH - total_width) // 2
    y = SCREENHEIGHT * 0.1
    for digit in digits:
        SCREEN.blit(GAME_SPRITES['numbers'][digit], (x, y))
        x += GAME_SPRITES['numbers'][digit].get_width()

def main():
    while True:
        welcome_screen()
        main_game()

if __name__ == "__main__":
    main()