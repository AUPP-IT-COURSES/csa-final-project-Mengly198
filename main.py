import pygame
import os
import random
import csv
import button
from pygame import mixer
from subprocess import call

mixer.init()
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Shooterista")

# define game var
GRAVITY = 0.75
SCROLL_TH = 200
ROW = 16
COLUMN = 150
TILE_SIZE = SCREEN_HEIGHT // ROW
TILETYPES = 21
MAX_LEVELS = 3

screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

# define player action
moving_left = False
moving_right = False
shoot = False
grenadeCD = False
grenade_thrown = False

# load musics
pygame.mixer.music.load("audio/music2.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 3500)

jump_fx = pygame.mixer.Sound("audio/jump.wav")
jump_fx.set_volume(0.5)

shot_fx = pygame.mixer.Sound("audio/shot.wav")
jump_fx.set_volume(0.5)

grenade_fx = pygame.mixer.Sound("audio/grenade.wav")
grenade_fx.set_volume(0.5)

# load img
# button img
start_img = pygame.image.load("img/start_btn.png").convert_alpha()
exit_img = pygame.image.load("img/exit_btn.png").convert_alpha()
restart_img = pygame.image.load("img/restart_btn.png").convert_alpha()
logo_name_img = pygame.image.load("img/logoname.png").convert_alpha()
logo_name_img = pygame.transform.scale(logo_name_img, (750, 500))
edit_img = pygame.image.load("img/edit_logo.png").convert_alpha()
game_over_img = pygame.image.load("img/game_over.png").convert_alpha()
game_over_img = pygame.transform.scale(game_over_img, (250,150))


# background img

pine1_img = pygame.image.load("img/Background/pine1.png").convert_alpha()
pine2_img = pygame.image.load("img/Background/pine2.png").convert_alpha()
mountain_img = pygame.image.load("img/Background/mountain.png").convert_alpha()
sky_img = pygame.image.load("img/Background/sky_cloud.png").convert_alpha()
background = pygame.image.load("img/Background/Background.png").convert_alpha()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))


# store tile in list
img_list = []
for x in range(TILETYPES):
    img = pygame.image.load(f"img/Tile/{x}.png").convert_alpha()
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# bullet
bullet_img = pygame.image.load("img/icons/bullet.png").convert_alpha()
bullet_img = pygame.transform.scale(bullet_img, (TILE_SIZE // 2, TILE_SIZE // 2 - 0.3))
# grenades
grenade_img = pygame.image.load("img/icons/grenade.png").convert_alpha()
grenade_img = pygame.transform.scale(
    grenade_img, (TILE_SIZE // 2, TILE_SIZE // 2 - 0.3)
)
# boxes
health_box_img = pygame.image.load("img/icons/health_box.png").convert_alpha()
ammo_box_img = pygame.image.load("img/icons/ammo_box.png").convert_alpha()
grenade_box_img = pygame.image.load("img/icons/grenade_box.png").convert_alpha()

item_boxes = {
    "Health": health_box_img,
    "Ammo": ammo_box_img,
    "Grenade": grenade_box_img,
}

# define colors
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# set frame
clock = pygame.time.Clock()
fps = 60


# define font
font = pygame.font.SysFont("Futura", 30)


def open_editor_file():
    call(["python", "level_editor.py"])


def draw_text(text, font, text_color, x, y):
    img = font.render(text, True, text_color)
    screen.blit(img, (x, y))


def reset_lvl():
    enemy_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group.empty()
    bullet_group.empty()
    decoration_group.empty()
    nextlevel_group.empty()
    water_group.empty()

    # create empty tile list
    data = []
    for row in range(ROW):
        r = [-1] * COLUMN
        data.append(r)
    return data


def draw_bg():
    screen.fill(BG)

    width = sky_img.get_width()
    for x in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(
            mountain_img,
            (
                (x * width) - bg_scroll * 0.6,
                SCREEN_HEIGHT - mountain_img.get_height() - 300,
            ),
        )
        screen.blit(
            pine1_img,
            (
                (x * width) - bg_scroll * 0.7,
                SCREEN_HEIGHT - pine1_img.get_height() - 150,
            ),
        )
        screen.blit(
            pine2_img,
            ((x * width) - bg_scroll * 0.8, SCREEN_HEIGHT - pine2_img.get_height()),
        )


class Human(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        super().__init__()
        self.char_type = char_type
        self.speed = speed
        self.shootCD = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.ammo = ammo
        self.startAmmo = ammo
        self.direction = 1
        self.velo_y = 0
        self.flip = False
        self.animation_list = []
        self.frame_i = 0
        self.action = 0
        self.isAlive = True
        self.jump = False
        self.inAir = True
        self.update_time = pygame.time.get_ticks()

        # ai char vars
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)

        self.idling = False
        self.idling_counter = 0

        # load all img for players
        animation_types = ["Idle", "Run", "Jump", "Death"]
        for animation in animation_types:
            # reset temp imgs
            temp_list = []
            # count number of file in folder
            num_of_frames = len(os.listdir(f"img/{self.char_type}/{animation}"))

            for i in range(num_of_frames):
                img = pygame.image.load(
                    f"img/{self.char_type}/{animation}/tile00{i}.png"
                ).convert_alpha()
                img = pygame.transform.scale(
                    img, (int(img.get_width() * scale), int(img.get_height() * scale))
                )
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_i]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.update_ani()
        self.check_alive()
        # update CD
        if self.shootCD > 0:
            self.shootCD -= 1

    def move(self, moving_left, moving_right):
        screen_scroll = 0

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

        # check for collision
        for tile in world.obstacle_list:
            # check collision in x dir
            if tile[1].colliderect(
                self.rect.x + dx, self.rect.y, self.width, self.height
            ):
                dx = 0
                # if ai hit wall, make it turn
                if self.char_type == "enemy":
                    self.direction *= -1
                    self.move_counter = 0

            # check collision in y dir
            if tile[1].colliderect(
                self.rect.x, self.rect.y + dy, self.width, self.height
            ):
                # check below ground
                if self.velo_y < 0:
                    self.velo_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check above ground
                elif self.velo_y >= 0:
                    self.velo_y = 0
                    self.inAir = False
                    dy = tile[1].top - self.rect.bottom

        # check for collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        # check for collision with next level
        level_complete = False
        if pygame.sprite.spritecollide(self, nextlevel_group, False):
            level_complete = True

        # check if player fell out map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0

        # check if going off edge of screen
        if self.char_type == "player":
            if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
                dx = 0

        # update rect pos
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player pos
        if self.char_type == "player":
            if (
                self.rect.right > SCREEN_WIDTH - SCROLL_TH
                and bg_scroll < (world.lvl_length * TILE_SIZE) - SCREEN_WIDTH
            ) or (self.rect.left < SCROLL_TH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
        return screen_scroll, level_complete

    def shoot(self):
        if self.shootCD == 0 and self.ammo > 0:
            self.shootCD = 20
            bullet = Bullet(
                self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),
                self.rect.centery,
                self.direction,
            )
            bullet_group.add(bullet)
            # reduce ammo
            self.ammo -= 1
            shot_fx.play()

    def ai(self):
        if self.isAlive and player.isAlive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)  # 0 is idling
                self.idling = True
                self.idling_counter = 50

            # check if ai near player
            if self.vision.colliderect(player.rect):
                # change ai state
                self.update_action(0)  # idling
                # shoot player
                self.shoot()

            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)  # 1 for running
                    self.move_counter += 1

                    # update vision ai
                    self.vision.center = (
                        self.rect.centerx + 75 * self.direction,
                        self.rect.centery,
                    )

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1

                else:
                    self.idling_counter -= 1
                    if self.idling_counter <= 0:
                        self.idling = False

        # scroll
        self.rect.x += screen_scroll

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
            if self.action == 3:
                self.frame_i = len(self.animation_list[self.action]) - 1
            else:
                self.frame_i = 0

    def update_action(self, new_action):
        # check if new action is different
        if new_action != self.action:
            self.action = new_action
            # update ani settings
            self.frame_i = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.isAlive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World:
    def __init__(self):
        self.obstacle_list = []

    # load data
    def process_data(self, data):
        self.lvl_length = len(data[0])
        # iterate thru each in lvl datafile
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if tile >= 0 and tile <= 8:
                        self.obstacle_list.append(tile_data)
                    elif tile >= 9 and tile <= 10:
                        water = Water(img, x * TILE_SIZE, y * TILE_SIZE)
                        water_group.add(water)
                    elif tile >= 11 and tile <= 14:
                        decoration = Decoration(img, x * TILE_SIZE, y * TILE_SIZE)
                        decoration_group.add(decoration)
                    elif tile == 15:  # create player
                        player = Human(
                            "player", x * TILE_SIZE, y * TILE_SIZE, 0.65, 7, 10, 5
                        )
                        health_bar = HealthBar(20, 10, player.health, player.max_health)
                    elif tile == 16:  # create enemies
                        enemy = Human(
                            "enemy", x * TILE_SIZE, y * TILE_SIZE, 0.65, 2, 100, 0
                        )
                        enemy_group.add(enemy)
                    elif tile == 17:  # create ammobox
                        item_box = ItemBox("Ammo", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18:  # create grenades box
                        item_box = ItemBox("Grenade", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19:  # create healthbox
                        item_box = ItemBox("Health", x * TILE_SIZE, y * TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20:  # create exit
                        nextlevel = NextLevel(img, x * TILE_SIZE, y * TILE_SIZE)
                        nextlevel_group.add(nextlevel)
        return player, health_bar

    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        self.rect.x += screen_scroll


class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        self.rect.x += screen_scroll


class NextLevel(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        self.rect.x += screen_scroll


class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        super().__init__()
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (
            x + TILE_SIZE // 2,
            y + (TILE_SIZE - self.image.get_height()),
        )

    def update(self):
        # scroll
        self.rect.x += screen_scroll
        # check if player picked up box
        if pygame.sprite.collide_rect(self, player):
            # check the kind of box
            if self.item_type == "Health":
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == "Ammo":
                player.ammo += 10
            elif self.item_type == "Grenade":
                player.grenades += 3
            # delete item box
            self.kill()


class HealthBar:
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = max_health

    def draw(self, health):
        # change current health
        self.health = health

        # ratio calculation
        ratio = self.health / self.max_health

        pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 150 + 4, 20 + 4))
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        # move bullet
        self.rect.x += self.direction * self.speed + screen_scroll
        # check if bullet off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # check collision with lvl
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.isAlive:
                player.health -= 5
                self.kill()

        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.isAlive:
                    enemy.health -= 25
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.timer = 100
        self.vel_y = -11
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction

    def update(self):
        self.vel_y += GRAVITY
        dx = self.direction * self.speed
        dy = self.vel_y

        # check collision with level
        for tile in world.obstacle_list:
            # check collision with wall
            if tile[1].colliderect(
                self.rect.x + dx, self.rect.y, self.width, self.height
            ):
                self.direction *= -1
                dx = self.direction * self.speed

            # check collision in y dir
            if tile[1].colliderect(
                self.rect.x, self.rect.y + dy, self.width, self.height
            ):
                self.speed = 0
                # check below ground
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                # check above ground
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom

        # update grenade pos
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        # countdown before explode
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y - 30, 1)
            explosion_group.add(explosion)
            # damage check collision
            # explode within player 2 tiles radius
            if (
                abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2
                and abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2
            ):
                player.health -= 25
            # explode within player 1 tile radius
            elif (
                abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE
                and abs(self.rect.centery - player.rect.centery) < TILE_SIZE
            ):
                player.health -= 50

            # check collision damage enemies
            for enemy in enemy_group:
                if (
                    abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2
                    and abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2
                ):
                    enemy.health -= 25
                elif (
                    abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE
                    and abs(self.rect.centery - player.rect.centery) < TILE_SIZE
                ):
                    enemy.health -= 50
                    print(enemy.health)


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(
                f"img/explosion/Explosion_two_colors{num}.png"
            ).convert_alpha()
            img = pygame.transform.scale(
                img, (int(img.get_width() * scale), int(img.get_height() * scale))
            )
            self.images.append(img)
        self.frame_i = 0
        self.image = self.images[self.frame_i]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        self.rect.x += screen_scroll
        EXPLODE_SPEED = 4
        # update explode animation
        self.counter += 1

        if self.counter >= EXPLODE_SPEED:
            self.counter = 0
            self.frame_i += 1
            # check if animation complete
            if self.frame_i >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_i]


class ScreenFade:
    def __init__(self, direction, color, speed):
        self.direction = direction
        self.color = color
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed

        if self.direction == 1:  # whole screen fade
            pygame.draw.rect(
                screen,
                self.color,
                (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT),
            )
            pygame.draw.rect(
                screen,
                self.color,
                (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT),
            )
            pygame.draw.rect(
                screen,
                self.color,
                (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2),
            )
            pygame.draw.rect(
                screen,
                self.color,
                (
                    0,
                    SCREEN_HEIGHT // 2 + self.fade_counter,
                    SCREEN_WIDTH,
                    SCREEN_HEIGHT,
                ),
            )

        if self.direction == 2:  # vertical fade down
            pygame.draw.rect(
                screen, self.color, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter)
            )
            if self.fade_counter >= SCREEN_WIDTH:
                fade_complete = True

        return fade_complete


# create transitions
intro_trans = ScreenFade(1, BLACK, 4)
death_trans = ScreenFade(2, PINK, 8)

# create buttons
start_button = button.Button(
    SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 100, start_img, 0.3
)
exit_button = button.Button(SCREEN_WIDTH - 350, SCREEN_HEIGHT // 2 + 50, exit_img, 0.25)
exit1_button = button.Button(
    SCREEN_WIDTH - 475, SCREEN_HEIGHT // 2 + 50, exit_img, 0.25
)
restart_button = button.Button(
    SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 - 50, restart_img, 2
)
edit_button = button.Button(
    SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 + 20, edit_img, 0.2
)


# create sprite group
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
nextlevel_group = pygame.sprite.Group()


# create tile lists
world_data = []
for row in range(ROW):
    r = [-1] * COLUMN
    world_data.append(r)
# load data and world
with open(f"level{level}_data.csv", newline="") as csvfile:
    reader = csv.reader(csvfile, delimiter=",")
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

world = World()
player, health_bar = world.process_data(world_data)
pygame.display.set_icon(bullet_img)

run = True
while run:
    clock.tick(fps)

    if start_game == False:
        # draw menu
        screen.blit(background, (0, 0))
        screen.blit(logo_name_img, (0, -130))
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False
        if edit_button.draw(screen):
            print("edit button pressed")
            open_editor_file()

    else:
        # update bg
        draw_bg()

        # draw worldmap
        world.draw()

        # show health
        health_bar.draw(player.health)

        # show ammo
        draw_text("AMMO: ", font, WHITE, 20, 40)
        for x in range(player.ammo):
            screen.blit(bullet_img, (110 + (x * 10), 40))
        # show grenades
        draw_text("GRENADES: ", font, WHITE, 20, 70)
        for x in range(player.grenades):
            screen.blit(grenade_img, (155 + (x * 15), 67))

        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        nextlevel_group.update()

        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        nextlevel_group.draw(screen)

        # show intro trans
        if start_intro:
            if intro_trans.fade():
                start_intro = False
                intro_trans.fade_counter = 0

        if player.isAlive:
            # shoot bullet
            if shoot:
                player.shoot()
            # throw grenade
            elif grenadeCD and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(
                    player.rect.centerx
                    + (player.rect.size[0] * 0.5 * player.direction),
                    player.rect.top,
                    player.direction,
                )
                grenade_group.add(grenade)
                # reduce grenades
                grenade_thrown = True
                player.grenades -= 1
            if player.inAir:
                player.update_action(2)  # 2 is run
            elif moving_left or moving_right:
                player.update_action(1)  # 1 is run
            else:
                player.update_action(0)  # 0 is idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # check if lvl up
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_lvl()
                if level <= MAX_LEVELS:
                    with open(f"level{level}_data.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
        else:
            screen_scroll = 0
            if death_trans.fade():
                screen.blit(game_over_img, (SCREEN_WIDTH // 2 - 125, 100))
                if restart_button.draw(screen):
                    death_trans.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_lvl()
                    with open(f"level{level}_data.csv", newline="") as csvfile:
                        reader = csv.reader(csvfile, delimiter=",")
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

                if exit1_button.draw(screen):
                    run = False

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
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenadeCD = True
            if event.key == pygame.K_UP and player.isAlive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

    # keyboard release

    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            moving_left = False
        if event.key == pygame.K_RIGHT:
            moving_right = False
        if event.key == pygame.K_SPACE:
            shoot = False
        if event.key == pygame.K_q:
            grenadeCD = False
            grenade_thrown = False
    pygame.display.update()

pygame.quit()
