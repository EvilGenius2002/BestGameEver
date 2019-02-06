import os
import sys

import pygame

pygame.init()
level = open(os.path.join('data', 'levels', 'level1'), 'r').read().split('\n')


def load_image(name, colorkey=None):
    fullname = os.path.join('data', 'images', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        print('Cannot load image:', name)
        raise SystemExit(message)
    if colorkey is not None:
        if colorkey is -1:
            colorkey = image.get_at((1, 1))
        image.set_colorkey(colorkey)
    image = image.convert_alpha()
    return image


class Camera:
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.mx = 0
        self.my = 0

    def apply(self, obj):
        obj.rect.x += self.dx + self.mx
        obj.rect.y += self.dy + self.my

    def update(self, target):
        mouse = pygame.mouse.get_pos()
        self.dx = -(target.rect.x + target.rect.w // 2 - width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - height // 2)
        if mouse[0] > width // 2 + width // 3:
            self.mx = -(mouse[0] - width // 2 - width // 3)
        elif mouse[0] < width // 2 - width // 3:
            self.mx = -(mouse[0] - width // 2 + width // 3)
        else:
            self.mx = 0
        if mouse[1] > height // 2 + height // 3:
            self.my = -(mouse[1] - height // 2 - height // 3)
        elif mouse[1] < height // 2 - height // 3:
            self.my = -(mouse[1] - height // 2 + height // 3)
        else:
            self.my = 0


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["ЗАСТАВКА", "",
                  "Правила игры :",
                  "Для управления используйте WASD"]

    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for eve in pygame.event.get():
            if eve.type == pygame.QUIT:
                terminate()
            elif eve.type == pygame.KEYDOWN:
                if eve.key == 293:
                    terminate()
                else:
                    return
            elif eve.type == pygame.MOUSEBUTTONDOWN:
                return
        pygame.display.flip()
        clock.tick(fps)


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites, player)
        self.image = load_image("Player1.png", -1)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos[0], tile_height * pos[1]
        self.speed = self.yspeed = self.prevspeed = 0.0
        # Basic variables:
        self.prevmove = 1
        self.fall_modifier = 0.5
        self.max_speed = 12.0
        self.jump_speed = 15.0
        self.acceleration = 0.5
        # Conditions:
        self.flying = self.climbing_r = self.climbing_l = self.sprinting = self.facing_r = self.climbing_up = False

    def fall(self):
        if self.yspeed == 0:
            self.yspeed = -10.0
        else:
            self.yspeed -= self.fall_modifier

    def collide(self):
        if not pygame.sprite.spritecollideany(self, blocks):
            self.flying = True
            self.fall()
        else:
            climb_r, climb_l = self.climbing_r, self.climbing_l
            self.climbing_r = self.climbing_l = False
            print(self.climbing_r, self.climbing_l)
            for spr in pygame.sprite.spritecollide(self, blocks, False):
                if not (
                        spr.rect.y < self.rect.y + 50 < spr.rect.y + 25 or spr.rect.y + 55
                        > self.rect.y > spr.rect.y + 35):
                    if spr.rect.x < self.rect.x + 50 < spr.rect.x + 25:
                        self.rect.x = spr.rect.x - 49
                        self.speed = 0
                        self.flying = False
                        self.climbing_r = True
                    elif spr.rect.x + 50 >= self.rect.x > spr.rect.x + 25:
                        self.rect.x = spr.rect.x + 49
                        self.speed = 0
                        self.flying = False
                        self.climbing_l = True
                elif not (
                        spr.rect.x + 45 < self.rect.x < spr.rect.x + 50
                        or spr.rect.x < self.rect.x + 50 < spr.rect.x + 5):
                    if spr.rect.y + 50 > self.rect.y + 50 > spr.rect.y:
                        self.rect.y = spr.rect.y - 49
                        if self.yspeed <= 0:
                            self.yspeed = 0
                            self.flying = False
                    if spr.rect.y + 50 > self.rect.y > spr.rect.y:
                        self.rect.y = spr.rect.y + 50
                        self.yspeed = 0
            if climb_r and not self.climbing_r:
                self.rect.x += 50
                self.rect.y -= 35
                self.climbing_up = True
            elif climb_l and not self.climbing_l:
                self.rect.x -= 50
                self.rect.y -= 35
                self.climbing_up = True

    def change_speed(self):
        global w
        if self.climbing_l or self.climbing_r:
            self.yspeed = 0
            if w:
                self.rect.y -= 2
            elif s:
                self.rect.y += 2
        else:
            if w and not self.flying and not self.climbing_up:
                self.yspeed = self.jump_speed
            w = False
            self.climbing_up = False

        if -0.1 < self.speed < 0.1:
            self.speed = 0
        if a:
            if self.climbing_r:
                self.climbing_r = False
                self.rect.x -= 2
            else:
                if -self.max_speed < self.speed <= 0.0:
                    self.speed -= 0.1
                elif self.speed > 0.0:
                    self.speed -= self.acceleration
        elif d:
            if self.climbing_l:
                self.climbing_l = False
                self.rect.x += 2
            else:
                if 0.0 <= self.speed < self.max_speed:
                    self.speed += 0.1
                elif self.speed < 0.0:
                    self.speed += self.acceleration
        else:
            if self.speed > 0.0:
                self.speed -= self.acceleration
            elif self.speed < 0.0:
                self.speed += self.acceleration
        self.rect.x += int(self.speed)
        self.rect.y -= int(self.yspeed)

    def change_image(self):
        if int(self.speed) != 0 and int(self.prevspeed) == 0:
            if not ((self.prevmove > 0 and self.speed > 0) or (self.prevmove < 0 and self.speed < 0)):
                self.image = pygame.transform.flip(self.image, True, False)
        elif int(self.speed) == 0 and int(self.prevspeed) != 0:
            self.prevmove = self.prevspeed
        self.prevspeed = self.speed

    def update(self):
        self.change_speed()
        self.collide()
        self.change_image()


class Block(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, blocks)
        self.image = images['block']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Back(pygame.sprite.Sprite):
    def __init__(self, pos_x, pos_y):
        super().__init__(all_sprites, back)
        self.image = images['back']
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


def generate_level(level):
    new_x, new_y, x, y = None, None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Back(x, y)
            elif level[y][x] == '#':
                Block(x, y)
            elif level[y][x] == '@':
                Back(x, y)
                new_x, new_y = x, y
    return new_x, new_y


size = width, height = 1920, 1080
tile_width = tile_height = 50
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
clock = pygame.time.Clock()
running = True
fps = 60
images = {'block': load_image("Block.png"), 'back': load_image("Block_B.png")}
# Keys:
a = d = w = s = False
all_sprites = pygame.sprite.Group()
blocks = pygame.sprite.Group()
back = pygame.sprite.Group()
player = pygame.sprite.Group()
player_sprite = Player(generate_level(level))
camera = Camera()
start_screen()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYUP:
            if event.key == 97:
                a = False
            if event.key == 100:
                d = False
            if event.key == 119:
                w = False
            if event.key == 115:
                s = False
        if event.type == pygame.KEYDOWN:
            if event.key == 293:
                running = False
            if event.key == 97:
                a = True
                d = False
            if event.key == 100:
                d = True
                a = False
            if event.key == 119:
                w = True
                s = False
            if event.key == 115:
                s = True
                w = False
    screen.fill((0, 0, 0))
    for i in player:
        i.update()
        camera.update(i)
    for sprite in all_sprites:
        camera.apply(sprite)
    # back.draw(screen)
    blocks.draw(screen)
    player.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
