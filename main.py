import runpy
import pygame
from pygame.locals import KEYDOWN
from config import WIDTH, HEIGHT, FPS, BLACK
from snake import Snake
from apple import Apple
from ui import Win, GameOver, Start, Pause
from sound import SoundPlayer


def wait():
    start_sprites = pygame.sprite.Group()
    start_sprite = Start()
    start_sprites.add(start_sprite)

    while True:
        for event in pygame.event.get():
            if event.type == KEYDOWN:
                return

        screen.fill(BLACK)
        start_sprites.draw(screen)
        pygame.display.flip()


def check_movement(player: Snake, event: pygame.event.Event):
    if ((event.key == pygame.K_a or event.key == pygame.K_LEFT) and not
        (player.get_coordinates(0)[0] - 20 == player.get_coordinates(1)[0] and
         player.get_coordinates(0)[1] == player.get_coordinates(1)[1])):
        player.parts[0].speed_x = -20
        player.parts[0].speed_y = 0
    if ((event.key == pygame.K_d or event.key == pygame.K_RIGHT) and not
        (player.get_coordinates(0)[0] + 20 == player.get_coordinates(1)[0] and
         player.get_coordinates(0)[1] == player.get_coordinates(1)[1])):
        player.parts[0].speed_x = 20
        player.parts[0].speed_y = 0
    if ((event.key == pygame.K_w or event.key == pygame.K_UP) and not
        (player.get_coordinates(0)[1] - 20 == player.get_coordinates(1)[1] and
         player.get_coordinates(0)[0] == player.get_coordinates(1)[0])):
        player.parts[0].speed_y = -20
        player.parts[0].speed_x = 0
    if ((event.key == pygame.K_s or event.key == pygame.K_DOWN) and not
        (player.get_coordinates(0)[1] + 20 == player.get_coordinates(1)[1] and
         player.get_coordinates(0)[0] == player.get_coordinates(1)[0])):
        player.parts[0].speed_y = 20
        player.parts[0].speed_x = 0


pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()
sound_player = SoundPlayer()
all_sprites = pygame.sprite.Group()
start_sprites = pygame.sprite.Group()
lose_sprites = pygame.sprite.Group()
win_sprite = pygame.sprite.Group()
pause_sprite = pygame.sprite.Group()
player = Snake()
apple = Apple()
pause_img = Pause()
you_win_sprite = Win()
all_sprites.add(player.parts[0])
all_sprites.add(player.parts[1])
all_sprites.add(apple)

# quit_sprite = Quit()
# restart_sprite = Restart()

game_over_sprite = GameOver()
lose_sprites.add([game_over_sprite])
win_sprite.add(you_win_sprite)
pause_sprite.add(pause_img)
snake_move_event = pygame.USEREVENT + 1
pygame.time.set_timer(snake_move_event, 150)
running = True
eat = False
game_over = False
you_win = False
pause = False
coordinates = []

wait()

while running:
    clock.tick(FPS)
    ev = pygame.event.get()
    if not pygame.mixer.music.get_busy() and not game_over and not you_win:
        sound_player.play_music()
    if not game_over and not you_win and not pause:
        for event in ev:

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause = True
                    sound_player.set_music_volume(0.1)
                check_movement(player, event)

            if event.type == snake_move_event:
                pygame.time.set_timer(snake_move_event, 150)
                all_sprites.update()
                coordinates.clear()
                for idx in range(1, len(player.parts)):
                    coordinates.append(player.parts[idx].rect.center)
                player.update_speed()
                if (player.get_coordinates(0)[0] == apple.rect.centerx and
                   player.get_coordinates(0)[1] == apple.rect.centery):
                    player.add_element()
                    all_sprites.remove(apple)
                    all_sprites.add(player.parts[-1])
                    if len(player.parts) == (WIDTH/20) ** 2:
                        you_win = True
                        sound_player.play_victory_snd()
                    else:
                        apple = Apple()
                        while apple.rect.center in coordinates:
                            apple = Apple()
                        all_sprites.add(apple)
                        eat = False
                        sound_player.play_collect_snd()
                if (player.get_coordinates(0) in coordinates or
                   player.get_coordinates(0)[0] <= 0 or
                   player.get_coordinates(0)[1] <= 0 or
                   player.get_coordinates(0)[0] >= WIDTH or
                   player.get_coordinates(0)[1] >= HEIGHT):
                    game_over = True
                    sound_player.play_lose_snd()
                    sound_player.stop_music()

        screen.fill(BLACK)
        all_sprites.draw(screen)

    elif game_over:
        for event in ev:
            if event.type == pygame.QUIT:
                running = False
            if (event.type == KEYDOWN and event.key == pygame.K_q):
                running = False
            if (event.type == KEYDOWN and event.key == pygame.K_r):
                runpy.run_path(path_name='main.py')
                running = False
        screen.fill(BLACK)
        lose_sprites.draw(screen)

    elif you_win:
        for event in ev:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                running = False
        screen.fill(BLACK)
        win_sprite.draw(screen)

    elif pause:
        for event in ev:
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                if event.key == pygame.K_r:
                    runpy.run_path(path_name='main.py')
                    running = False
                if event.key == pygame.K_ESCAPE:
                    pause = False
                    sound_player.set_music_volume(1)
        screen.fill(BLACK)
        pause_sprite.draw(screen)

    pygame.display.flip()

pygame.quit()
