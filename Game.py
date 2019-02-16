import os
import sys
from copy import deepcopy as copy
from random import choice as random

import pygame

pygame.init()
level = open(os.path.join('data', 'levels', 'level1'), 'r').read().split('\n')
size = width, height = 1920, 1080
tile_width = tile_height = 50
screen = pygame.display.set_mode(size, pygame.FULLSCREEN)


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


images = {'player': load_image("Player1.png", -1),
          'block': [load_image("Block.png"), load_image("Block1.png"), load_image("Block2.png"),
                    load_image("Block3.png")], 'corner_ru': load_image("Corner_r_u.png"),
          'corner_lu': load_image("Corner_l_u.png"), 'corner_rd': load_image("Corner_r_d.png"),
          'corner_ld': load_image("Corner_l_d.png"), 'up': load_image("Block_u.png"), 'down': load_image("Block_d.png"),
          'back': [load_image("Back.png"), load_image("Back1.png"), load_image("Back2.png")],
          'enemy': load_image("Enemy1.png", -1), 'button': load_image("Button.png"),
          'right': load_image('Block_l_s.png'), 'left': load_image('Block_r_s.png'),
          'button_1': load_image("Button_1.png")}


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


class Button(pygame.sprite.Sprite):
    def __init__(self, name, x, y):
        super().__init__(buttons)
        self.text = name
        self.font = pygame.font.Font(None, 90)
        self.image = images['button'].copy()
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y

    def update(self, event):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self.image = images['button_1'].copy()
            if event:
                if self.text == 'Выйти':
                    return 'Exit'
                if self.text == 'Продолжить':
                    return 'Game'
        else:
            self.image = images['button'].copy()
        rendered = self.font.render(self.text, True, pygame.Color('white'))
        intro_rect = rendered.get_rect()
        intro_rect.top = 20
        intro_rect.x = 382 - intro_rect.width // 2
        self.image.blit(rendered, intro_rect)


def pause():
    fon = pygame.transform.scale(load_image('Pause.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN:
                if event.key == 9:
                    return


def start_screen():
    fon = pygame.transform.scale(load_image('fon.jpg'), (width, height))
    screen.blit(fon, (0, 0))
    name_list = ['Новая игра', 'Продолжить', 'Выйти']
    for i in range(3):
        Button(name_list[i], 30, 195 + 295 * i)

    while True:
        for eve in pygame.event.get():
            if eve.type == pygame.QUIT:
                terminate()
            if eve.type == pygame.KEYDOWN:
                if eve.key == 293:
                    terminate()
            if eve.type == pygame.MOUSEBUTTONDOWN:
                for i in buttons:
                    ret = i.update(True)
                    if ret == 'Exit':
                        terminate()
                    elif ret == 'Game':
                        return
                    elif ret == 'New':
                        print('zscvgbh')
            else:
                for i in buttons:
                    i.update(False)
        buttons.draw(screen)
        pygame.display.flip()
        clock.tick(fps)


def find_path(x, y, x1, y1):
    lvl = copy(matrix)
    lvl = wave(x, y, 1, lvl)
    if str(lvl[y1][x1]).isdigit():
        if lvl[y1][x1] > 1:
            out = list(reversed(make_path(x1, y1, x, y, lvl, [])))
            return out[0], out[1]
    return None, None


def wave(x, y, lvl, lab):
    lab[y][x] = lvl
    if x + 1 < len(lab[y]):
        if lab[y][x + 1] == '.' and lab[y + 1][x + 1] in ['#', 't', 'y', 'u', 'g', 'j', 'b', 'n', 'm']:
            lab = wave(x + 1, y, lvl + 1, lab)
        elif lab[y][x + 1] in ['#', 't', 'y', 'u', 'g', 'j', 'b', 'n', 'm']:
            if lab[y - 1][x + 1] in ['#', 't', 'y', 'u', 'g', 'j', 'b', 'n', 'm'] and lab[y - 1][x] == '.':
                lab = wave(x, y - 1, lvl + 1, lab)
            elif lab[y - 1][x + 1] == '.' and lab[y - 1][x] == '.':
                lab[y - 1][x] = lvl + 1
                lab = wave(x + 1, y - 1, lvl + 2, lab)
    if x - 1 >= 0:
        if lab[y][x - 1] == '.' and lab[y + 1][x - 1] in ['#', 't', 'y', 'u', 'g', 'j', 'b', 'n', 'm']:
            lab = wave(x - 1, y, lvl + 1, lab)
        elif lab[y][x + 1] == '#':
            if lab[y - 1][x - 1] in ['#', 't', 'y', 'u', 'g', 'j', 'b', 'n', 'm'] and lab[y - 1][x] == '.':
                lab = wave(x, y - 1, lvl + 1, lab)
            elif lab[y - 1][x - 1] == '.' and lab[y - 1][x] == '.' and lab[y][x - 1] in ['#', 't', 'y', 'u', 'g', 'j',
                                                                                         'b', 'n', 'm']:
                lab[y - 1][x] = lvl + 1
                lab = wave(x - 1, y - 1, lvl + 2, lab)
    return lab


def make_path(x, y, x1, y1, lvl, path):
    path.append((x, y))
    if str(lvl[y][x + 1]).isdigit() and lvl[y][x] > lvl[y][x + 1]:
        path = make_path(x + 1, y, x1, y1, lvl, path)
    elif str(lvl[y][x - 1]).isdigit() and lvl[y][x] > lvl[y][x - 1]:
        path = make_path(x - 1, y, x1, y1, lvl, path)
    elif str(lvl[y + 1][x]).isdigit() and lvl[y][x] > lvl[y + 1][x]:
        path = make_path(x, y + 1, x1, y1, lvl, path)
    elif str(lvl[y - 1][x]).isdigit() and lvl[y][x] > lvl[y - 1][x]:
        path = make_path(x, y - 1, x1, y1, lvl, path)
    return path


class Start(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(all_sprites)
        self.rect = pygame.Rect(0, 0, 50, 50)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, image, pos):
        super().__init__(all_sprites, enemies)
        self.image = images[image]
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos[0], tile_height * pos[1]
        self.frames = {}
        self.time = self.cur_frame = self.speed = self.yspeed = 0
        for sheet in [[load_image("Enemy_animation.png"), 5, 1, 'Walk']]:
            self.frames[sheet[3]] = []
            for j in range(sheet[2]):
                for i in range(sheet[1]):
                    frame_location = (self.rect.w * i, self.rect.h * j)
                    self.frames[sheet[3]].append(sheet[0].subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
        # Basic variables:
        self.fall_modifier = 0.3
        self.max_speed = 4.0
        self.jump_speed = 10.0
        self.acceleration = 0.5
        # Conditions:
        self.flying = self.climbing_r = self.climbing_l = self.sprinting = self.climbing_up = False
        self.facing_r = True

    def get_cell(self):
        return (self.rect.x - start.rect.x) // 50, (self.rect.y - start.rect.y) // 50

    def move(self, prev_coords, target_coords):
        if prev_coords and target_coords:
            if prev_coords[0] == target_coords[0] == self.get_cell()[0] and target_coords[1] < prev_coords[1]:
                self.climbing_up = True
                self.yspeed = 2
            else:
                if target_coords[0] > prev_coords[0]:
                    self.speed += self.acceleration
                elif prev_coords[0] > target_coords[0]:
                    self.speed -= self.acceleration
        else:
            if player_sprite.rect.x > self.rect.x:
                self.speed += self.acceleration
            elif player_sprite.rect.x < self.rect.x:
                self.speed -= self.acceleration
            else:
                self.speed = 0
        if 0 < self.speed > self.max_speed:
            self.speed = self.max_speed
        elif 0 > self.speed < -1 * self.max_speed:
            self.speed = -1 * self.max_speed
        self.fall(pygame.sprite.spritecollide(self, blocks, False))
        self.rect.x += self.speed
        self.collide()
        self.climbing_up = False

    def fall(self, list):
        if not self.climbing_up:
            if self.yspeed == 0:
                self.yspeed = -1
            else:
                self.yspeed -= self.fall_modifier
            if list:
                for spr in list:
                    if spr.rect.y + 50 > self.rect.y + 50 > spr.rect.y:
                        self.yspeed = 0
                        self.rect.y = spr.rect.y - 49
        self.rect.y -= self.yspeed

    def collide(self):
        for spr in pygame.sprite.spritecollide(self, blocks, False):
            if not (spr.rect.y < self.rect.y + 50 < spr.rect.y + 25 or spr.rect.y + 55
                    > self.rect.y > spr.rect.y + 35):
                if spr.rect.x < self.rect.x + 50 < spr.rect.x + 25:
                    self.rect.x = spr.rect.x - 50
                    self.speed = 0
                elif spr.rect.x + 50 >= self.rect.x > spr.rect.x + 25:
                    self.rect.x = spr.rect.x + 50
                    self.speed = 0
            elif not (spr.rect.x + 45 < self.rect.x < spr.rect.x + 50
                      or spr.rect.x < self.rect.x + 50 < spr.rect.x + 5):
                if spr.rect.y + 50 > self.rect.y + 50 > spr.rect.y:
                    self.rect.y = spr.rect.y - 49
                    if self.yspeed <= 0:
                        self.yspeed = 0
                if spr.rect.y + 50 > self.rect.y > spr.rect.y:
                    self.rect.y = spr.rect.y + 50
                    self.yspeed = 0

    def update(self):
        move = find_path((self.rect.x - start.rect.x) // 50, (self.rect.y - start.rect.y) // 50,
                         (player_sprite.rect.x - start.rect.x) // 50,
                         (player_sprite.rect.y - start.rect.y) // 50)
        self.move(move[0], move[1])


class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites, player)
        self.image = images['player']
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = tile_width * pos[0], tile_height * pos[1]
        self.speed = self.yspeed = self.prevspeed = 0.0
        self.frames = {}
        self.time = self.cur_frame = 0
        for sheet in [[load_image("Player_animation.png"), 5, 1, 'Walk']]:
            self.frames[sheet[3]] = []
            for j in range(sheet[2]):
                for i in range(sheet[1]):
                    frame_location = (self.rect.w * i, self.rect.h * j)
                    self.frames[sheet[3]].append(sheet[0].subsurface(pygame.Rect(
                        frame_location, self.rect.size)))
        # Basic variables:
        self.prevmove = 1
        self.fall_modifier = 0.3
        self.max_speed = 6.0
        self.jump_speed = 10.0
        self.acceleration = 0.5
        # Conditions:
        self.flying = self.climbing_r = self.climbing_l = self.sprinting = self.climbing_up = False
        self.facing_r = True

    def fall(self):
        if self.yspeed == 0:
            self.yspeed = -10.0
        else:
            self.yspeed -= self.fall_modifier

    def collide(self):
        global w
        if not pygame.sprite.spritecollideany(self, blocks):
            self.flying = True
            self.fall()
        else:
            climb_r, climb_l = self.climbing_r, self.climbing_l
            self.climbing_r = self.climbing_l = False
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
                elif not (spr.rect.x + 45 < self.rect.x < spr.rect.x + 50
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
                self.rect.y -= 18
                w = False
            elif climb_l and not self.climbing_l:
                self.rect.x -= 50
                self.rect.y -= 18
                w = False

    def change_speed(self):
        global w
        if self.climbing_l or self.climbing_r:
            self.yspeed = 0
            if w:
                self.yspeed = 2
            elif s:
                self.yspeed = -2
        else:
            if w and not self.flying and not (self.climbing_r or self.climbing_l):
                self.yspeed = self.jump_speed
            w = False
        if -0.1 < self.speed < 0.1:
            self.speed = 0
        if a:
            if self.climbing_r:
                self.climbing_r = False
                self.speed = -self.max_speed
                self.yspeed = 6
            else:
                if -self.max_speed < self.speed <= 0.0:
                    self.speed -= 0.1
                elif self.speed > 0.0:
                    self.speed -= self.acceleration
        elif d:
            if self.climbing_l:
                self.climbing_l = False
                self.speed = self.max_speed
                self.yspeed = 6
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
            if self.speed > 0:
                self.facing_r = True
            else:
                self.facing_r = False
        elif int(self.speed) == 0 and int(self.prevspeed) != 0:
            self.prevmove = self.prevspeed
            self.prevspeed = self.speed
        if (int(self.speed) != 0 or ((self.climbing_l or self.climbing_r) and self.yspeed != 0)) and not self.flying:
            self.animate('Walk')
            if self.yspeed < 0 and (self.climbing_l or self.climbing_r):
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            self.image = images['player']
        if not self.facing_r:
            self.image = pygame.transform.flip(self.image, True, False)
        if self.climbing_r:
            self.image = pygame.transform.rotate(self.image, 90)
        elif self.climbing_l:
            self.image = pygame.transform.rotate(self.image, 270)

    def animate(self, name):
        self.time = (self.time + 1) % 6
        if self.time == 0:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[name])
        self.image = self.frames[name][self.cur_frame]

    def update(self):
        self.change_speed()
        self.collide()
        self.change_image()


class Block(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        super().__init__(all_sprites, blocks)
        self.image = image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


class Back(pygame.sprite.Sprite):
    def __init__(self, image, pos_x, pos_y):
        super().__init__(all_sprites, back)
        self.image = image
        self.rect = self.image.get_rect().move(tile_width * pos_x, tile_height * pos_y)


def generate_level(level):
    new_x = new_y = None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                Back(random(images['back']), x, y)
            elif level[y][x] == '#':
                Block(random(images['block']), x, y)
            elif level[y][x] == '@':
                Back(random(images['back']), x, y)
                new_x, new_y = x, y
            elif level[y][x] == "'":
                Enemy('enemy', (x, y))
                Back(random(images['back']), x, y)
            elif level[y][x] == 't':
                Block(images['corner_lu'], x, y)
            elif level[y][x] == 'u':
                Block(images['corner_ru'], x, y)
            elif level[y][x] == 'b':
                Block(images['corner_ld'], x, y)
            elif level[y][x] == 'm':
                Block(images['corner_rd'], x, y)
            elif level[y][x] == 'y':
                Block(images['up'], x, y)
            elif level[y][x] == 'n':
                Block(images['down'], x, y)
            elif level[y][x] == 'g':
                Block(images['right'], x, y)
            elif level[y][x] == 'j':
                Block(images['left'], x, y)
    return new_x, new_y


def make_matrix(level):
    global matrix
    matrix = []
    for y in range(len(level)):
        matrix.append([])
        for x in level[y]:
            matrix[y].append(x)


clock = pygame.time.Clock()
running = True
fps = 60
matrix = []
# Keys:
a = d = w = s = False
all_sprites, blocks, back, player, enemies, buttons = pygame.sprite.Group(), pygame.sprite.Group(), \
                                                      pygame.sprite.Group(), pygame.sprite.Group(), \
                                                      pygame.sprite.Group(), pygame.sprite.Group()
player_sprite = Player(generate_level(level))
camera = Camera()
start = Start()
start_screen()
make_matrix(level)
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
            if event.key == 9:
                pause()
    screen.fill((0, 0, 0))
    for i in player:
        i.update()
        camera.update(i)
    for i in enemies:
        i.update()
    for sprite in all_sprites:
        camera.apply(sprite)
    back.draw(screen)
    blocks.draw(screen)
    player.draw(screen)
    enemies.draw(screen)
    clock.tick(fps)
    pygame.display.flip()
