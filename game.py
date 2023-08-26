import runpy
import pygame
import requests
from pygame.locals import KEYDOWN
from config import WIDTH, HEIGHT, FPS, BLACK, GAME_SPEED, SERVER_URL
from snake import Snake
from apple import Apple
from ui import Win, GameOver, Start, Pause
from sound import SoundPlayer


class Game():
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        self.sound_player = SoundPlayer()
        self.player = Snake()
        self.apple = Apple()
        self.pause = Pause()
        self.game_over = GameOver()
        self.you_win = Win()
        self.start = Start()

        self.game_sprites = pygame.sprite.Group()
        self.start_sprites = pygame.sprite.Group()
        self.lose_sprites = pygame.sprite.Group()
        self.win_sprite = pygame.sprite.Group()
        self.pause_sprite = pygame.sprite.Group()

        self.game_sprites.add([self.player.parts[0], self.player.parts[1],
                               self.apple])
        self.lose_sprites.add(self.game_over)
        self.win_sprite.add(self.you_win)
        self.pause_sprite.add(self.pause)
        self.start_sprites.add(self.start)

        self.MUSIC_END = pygame.USEREVENT + 1
        self.SNAKE_MOVE = pygame.USEREVENT + 2

        self.sound_player.set_end_event(self.MUSIC_END)
        self.wait()

    def wait(self):
        loop = True
        while loop:
            self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    loop = False

            self.screen.fill(BLACK)
            self.start_sprites.draw(self.screen)
            pygame.display.flip()
        self.sound_player.play_music()
        self.play_game()

    def check_movement(self, event: pygame.event.Event):
        if ((event.key == pygame.K_a or event.key == pygame.K_LEFT) and not
           (self.player.get_xy(0)[0] - 20 == self.player.get_xy(1)[0] and
           self.player.get_xy(0)[1] == self.player.get_xy(1)[1])):
            self.player.parts[0].speed_x = -20
            self.player.parts[0].speed_y = 0
        if ((event.key == pygame.K_d or event.key == pygame.K_RIGHT) and not
            (self.player.get_xy(0)[0] + 20 == self.player.get_xy(1)[0] and
           self.player.get_xy(0)[1] == self.player.get_xy(1)[1])):
            self.player.parts[0].speed_x = 20
            self.player.parts[0].speed_y = 0
        if ((event.key == pygame.K_w or event.key == pygame.K_UP) and not
           (self.player.get_xy(0)[1] - 20 == self.player.get_xy(1)[1] and
           self.player.get_xy(0)[0] == self.player.get_xy(1)[0])):
            self.player.parts[0].speed_y = -20
            self.player.parts[0].speed_x = 0
        if ((event.key == pygame.K_s or event.key == pygame.K_DOWN) and not
           (self.player.get_xy(0)[1] + 20 == self.player.get_xy(1)[1] and
           self.player.get_xy(0)[0] == self.player.get_xy(1)[0])):
            self.player.parts[0].speed_y = 20
            self.player.parts[0].speed_x = 0

    def collect_apple(self, coordinates):
        self.player.add_element()
        self.game_sprites.remove(self.apple)
        self.game_sprites.add(self.player.parts[-1])
        if len(self.player.parts) == (WIDTH/20) ** 2:
            self.win()
            self.sound_player.play_victory_snd()
        else:
            self.apple = Apple()
            while self.apple.rect.center in coordinates:
                self.apple = Apple()
            self.game_sprites.add(self.apple)
            self.sound_player.play_collect_snd()

    def lose(self):
        self.sound_player.play_lose_snd()
        self.sound_player.stop_music()

        data = {
            'name': 'Antik',
            'score': len(self.player.parts)
        }

        response = requests.post(SERVER_URL + '/player', json=data)
        print(response.text)

        loop = True
        while loop:
            ev = pygame.event.get()
            self.clock.tick(FPS)
            for event in ev:
                if event.type == pygame.QUIT:
                    pygame.quit()
                if (event.type == KEYDOWN and event.key == pygame.K_q):
                    pygame.quit()
                if (event.type == KEYDOWN and event.key == pygame.K_r):
                    runpy.run_path(path_name='main.py')
                    loop = False
            self.screen.fill(BLACK)
            self.lose_sprites.draw(self.screen)
            pygame.display.flip()

    def pause_game(self):
        loop = True
        ev = pygame.event.get()
        while loop:
            ev = pygame.event.get()
            self.clock.tick(FPS)
            for event in ev:
                if event.type == self.MUSIC_END:
                    self.sound_player.play_music()
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        pygame.quit()
                    if event.key == pygame.K_r:
                        runpy.run_path(path_name='main.py')
                        loop = False
                    if event.key == pygame.K_ESCAPE:
                        loop = False
                        self.sound_player.set_music_volume(1)
                self.screen.fill(BLACK)
                self.pause_sprite.draw(self.screen)
                pygame.display.flip()
        self.play_game()

    def win(self):
        self.sound_player.play_lose_snd()
        self.sound_player.stop_music()
        loop = True

        while loop:
            ev = pygame.event.get()
            self.clock.tick(FPS)
            for event in ev:
                if event.type == pygame.QUIT:
                    loop = False
                if event.type == pygame.MOUSEBUTTONUP:
                    loop = False
            self.screen.fill(BLACK)
            self.win_sprite.draw(self.screen)
            pygame.display.flip()

    def play_game(self):
        loop = True
        coords = []
        pygame.time.set_timer(self.SNAKE_MOVE, GAME_SPEED)
        while loop:
            self.clock.tick(FPS)
            ev = pygame.event.get()
            if loop:
                for event in ev:
                    if event.type == self.MUSIC_END:
                        self.sound_player.play_music()

                    if event.type == pygame.QUIT:
                        loop = False
                        pygame.quit()

                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            loop = False
                            self.sound_player.set_music_volume(0.1)
                            self.pause_game()
                        self.check_movement(event)

                    if event.type == self.SNAKE_MOVE:
                        pygame.time.set_timer(self.SNAKE_MOVE, GAME_SPEED)
                        self.game_sprites.update()
                        coords.clear()
                        for idx in range(1, len(self.player.parts)):
                            coords.append(self.player.parts[idx].rect.center)
                        self.player.update_speed()

                        if (self.player.get_xy(0)[0] ==
                           self.apple.rect.centerx and
                           self.player.get_xy(0)[1] ==
                           self.apple.rect.centery):
                            self.collect_apple(coords)

                        if (self.player.get_xy(0) in coords or
                           self.player.get_xy(0)[0] <= 0 or
                           self.player.get_xy(0)[1] <= 0 or
                           self.player.get_xy(0)[0] >= WIDTH or
                           self.player.get_xy(0)[1] >= HEIGHT):
                            loop = False
                            self.lose()

                self.screen.fill(BLACK)
                self.game_sprites.draw(self.screen)

            pygame.display.flip()
