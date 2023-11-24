import pygame
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Demo v1")

# define player action
moving_left = False
moving_right = False

# define colors
BG = (144, 201, 120)
RED = (255,0,0)

# set frame
clock = pygame.time.Clock()
fps = 60

# define game var
GRAVITY = 0.75

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, RED, (0,400), (SCREEN_WIDTH, 400))


class Human(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed):
        super().__init__()
        self.char_type = char_type
        self.speed = speed
        self.direction = 1
        self.velo_y = 0
        self.flip = False
        self.animation_list = []
        self.frame_i = 0
        self.action = 0
        self.Isalive = True
        self.jump = False
        self.inAir = True
        self.update_time = pygame.time.get_ticks()

        #load all img for players
        animation_types = ["Idle", "Run", "Jump"]
        for animation in animation_types:
            #reset temp imgs
            temp_list = []
            #count number of file in folder
            num_of_frames = len(os.listdir(f"{self.char_type}/{animation}"))

            for i in range(num_of_frames):
                img = pygame.image.load(
                    f"{self.char_type}/{animation}/tile00{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale))
                )
                temp_list.append(img)
            self.animation_list.append(temp_list)


        self.image = self.animation_list[self.action][self.frame_i]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def move(self, moving_left, moving_right):
        # reset movement var
        dx = 0
        dy = 0
        # assign movement var
        if moving_left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.inAir == False:
            self.velo_y = -11
            self.jump = False
            self.inAir = True

        # apply gravity
        self.velo_y += GRAVITY
        if self.velo_y > 10:
            self.velo_y
        dy += self.velo_y

        #check collision
        if self.rect.bottom + dy > 400:
            dy = 400 - self.rect.bottom
            self.inAir = False

        # update rect pos
        self.rect.x += dx
        self.rect.y += dy

    def update_ani(self):
        # update animation
        ANIMATION_CD = 100

        # update img depending on current frame
        self.image = self.animation_list[self.action][self.frame_i]

        # check if enough time passed since last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_CD:
            self.update_time = pygame.time.get_ticks()
            self.frame_i += 1

        # if animation run out, loop back
        if self.frame_i >= len(self.animation_list[self.action]):
            self.frame_i = 0

    def update_action(self, new_action):
        # check if new action is different
        if new_action != self.action:
            self.action = new_action
            # update ani settings
            self.frame_i = 0
            self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


player = Human("player", 200, 200, 1, 5)
# enemy = Human("enemy", 400, 200, 0.7, 5)

run = True
while run:
    clock.tick(fps)

    draw_bg()

    player.update_ani()
    player.draw()
    # enemy.draw()

    if player.Isalive:
        if player.inAir:
            player.update_action(2)  # 2 is run
        elif moving_left or moving_right:
            player.update_action(1)  # 1 is run
        else:
            player.update_action(0)  # 0 is idle
        player.move(moving_left, moving_right)

    for event in pygame.event.get():
        # quit
        if event.type == pygame.QUIT:
            run = False

        # keyboard press
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_UP and player.Isalive:
                player.jump = True
            if event.key == pygame.K_ESCAPE:
                run = False

        # keyboard release
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
    pygame.display.update()

pygame.quit()
