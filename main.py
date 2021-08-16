import pygame
from pygame.constants import K_SPACE, K_UP
import random
pygame.init()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
FPS = 60

BACKGROUND = pygame.image.load("assets/background.png")
DINOSAUR_RUN = [pygame.image.load("assets/dino-walk-1-96.png"), 
                pygame.image.load("assets/dino-walk-2-96.png")]
DINOSAUR_IDLE = [pygame.image.load("assets/dino-idle-96.png")]
DINOSAUR_JUMP = [pygame.image.load("assets/dino-jump-96.png")]
DINOSAUR_LOST = [pygame.image.load("assets/dino-kill-96.png")]
CACTUS = pygame.image.load("assets/cactus-96.png")
ICON = pygame.image.load("assets/icon.png")

pygame.display.set_caption("Dinosaur game")
pygame.display.set_icon(ICON)

class Dinosaur:
    def __init__(self, x, y):
        # position
        self.x = x
        self.y = y
        # sprite
        self.sprites = {
            "idle": DINOSAUR_IDLE,
            "run": DINOSAUR_RUN,
            "jump": DINOSAUR_JUMP,
            "lost": DINOSAUR_LOST,
        }
        self.state = "idle"
        self.step = 0
        self.sprite = self.sprites[self.state][self.step]
        self.ANIMATION_SPEED = 10 # counts required to increase step by 1
        self.animation_step = 0 # current step
        # jumping
        self.JUMP_VELOCITY = 10
        self.velocity_y = 0
        # collision
        self.collision_box = self.sprite.get_rect() #pygame.Rect(self.x, self.y, 64, 64)

    def change_state(self, state):
        if self.state == state: # if old state is same as new state, do nothing
            return
        self.state = state
        self.step = 0
        if state == "jump":
            self.velocity_y = self.JUMP_VELOCITY
        elif state == "run":
            self.velocity_y = 0
        self.sprite = self.sprites[self.state][self.step]

    def move(self):
        #jumping
        if self.state == "jump":
            self.y -= 5 * self.velocity_y
            self.velocity_y -= 1
            if self.velocity_y < self.JUMP_VELOCITY * -1:
                #when reached ground
                self.change_state("run")
        # change sprite image
        self.sprite = self.sprites[self.state][self.step]
        #animation timing
        self.animation_step = (self.animation_step + 1)
        if self.animation_step == self.ANIMATION_SPEED:
            self.animation_step = 0
            self.step = (self.step + 1) % len(self.sprites[self.state])
        #move collision box
        self.collision_box.topleft = (self.x, self.y)

class Cactus:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 14 #squares moving per loop
        self.out_of_screen = False
        self.sprite = CACTUS
        self.collision_box = self.sprite.get_rect()

    def move(self):
        self.x -= self.velocity
        self.collision_box.topleft = (self.x, self.y)
        if self.x < -81:
            self.out_of_screen = True

def handle_exit():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

def draw_sprites(*sprites):
    SCREEN.blit(BACKGROUND, (0, 0))
    for sprite in sprites:
        SCREEN.blit(sprite.sprite, (sprite.x, sprite.y))

def score_board(font, score):
    score_text = font.render(f"SCORE: {score}", True, (255, 255, 255))
    SCREEN.blit(score_text, (20, 20))
    return score + 1

def has_collided(player, cacti):
    for cactus in cacti:
        if cactus.collision_box.colliderect(player.collision_box):
            return True

def handle_player_input(player):
    keys = pygame.key.get_pressed()
    if keys[K_SPACE] or keys[K_UP]:
        player.change_state("jump")

def spawn_obstacles(cacti, spawn_delay):
    for cactus in cacti:
        cactus.move()
        if cactus.out_of_screen:
            cacti.remove(cactus)
    if spawn_delay <= 0:
        cacti.append(Cactus(700, 386))
        return random.randint(36, 80) # delay between other cactus
    return spawn_delay - 1

def display_center_text(main_font, main_text, small_font, small_text):
    main = main_font.render(main_text, True, (255, 255, 255))
    small = small_font.render(small_text, True, (255, 255, 255))
    main_rect = main.get_rect(center=(WIDTH/2, HEIGHT/2))
    small_rect = small.get_rect(center=(WIDTH/2, HEIGHT/2 + 40))
    SCREEN.blit(main, main_rect)
    SCREEN.blit(small, small_rect)

def main():
    clock = pygame.time.Clock()
    player = Dinosaur(100, 410)
    cacti = []
    cactus_spawn_delay = 0
    score = 0
    main_font = pygame.font.SysFont(None, 48)
    small_font = pygame.font.SysFont(None, 24)
    game_state = -1 # -1 is paused, 0 is playing, 1 is end
    while game_state == -1:
        clock.tick(FPS)
        handle_exit()
        draw_sprites(player)
        display_center_text(main_font, "DINOSAUR GAME", small_font, "Press SPACE to play/jump")
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] or keys[K_UP]:
            player.change_state("run")
            game_state = 0

        pygame.display.update()
    while game_state == 0:
        clock.tick(FPS)
        handle_exit()

        handle_player_input(player)
        player.move()
        cactus_spawn_delay = spawn_obstacles(cacti, cactus_spawn_delay)
        draw_sprites(*cacti, player)
        collided = has_collided(player, cacti)
        if collided:
            player.change_state("lost")
            game_state = 1
        else:
            score = score_board(small_font, score)

        pygame.display.update()

    while game_state == 1: # game end
        clock.tick(FPS)
        handle_exit()
        draw_sprites(*cacti, player)
        display_center_text(main_font, "GAME OVER (Press SPACE to restart)", small_font, f"SCORE: {score}")
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] or keys[K_UP]:
            return # exit from the function (while loop inside the function will call itself again)
        pygame.display.update()

while 1:
    main()