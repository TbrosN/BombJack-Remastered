import pygame
from constants import *
import numpy as np
from animation import Animator

BASETILEWIDTH = 10
BASETILEHEIGHT = 10

BGTILESIZE = 223

# TODO: Make everything smaller.


class Spritesheet(object):
    def __init__(self):
        self.sheet = pygame.image.load("spritesheets/spritesheet_bombjack8.png").convert()
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)
        width = int(self.sheet.get_width() / BASETILEWIDTH * TILEWIDTH)
        height = int(self.sheet.get_height() / BASETILEHEIGHT * TILEHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))

    def getImage(self, x, y, width, height):
        x *= TILEWIDTH
        y *= TILEHEIGHT
        self.sheet.set_clip(pygame.Rect(x, y, width, height))
        return self.sheet.subsurface(self.sheet.get_clip())


class BGSpritesheet(object):
    def __init__(self):
        self.sheet = pygame.image.load("spritesheets/spritesheet_background.png").convert()
        width = int(self.sheet.get_width()/BGTILESIZE*SCREENWIDTH)
        height = int(self.sheet.get_height()/BGTILESIZE*SCREENHEIGHT)
        self.sheet = pygame.transform.scale(self.sheet, (width, height))

    def getImage(self, n):
        x = (n % 5)*SCREENWIDTH
        y = 0
        self.sheet.set_clip(pygame.Rect(x, y, SCREENWIDTH, SCREENHEIGHT))
        return self.sheet.subsurface(self.sheet.get_clip())


class CoinSprites(Spritesheet):
    def __init__(self, coin):
        Spritesheet.__init__(self)
        self.coin = coin
        self.coin.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def getStartImage(self):
        return self.getImage(16*2, 4*2)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        pass

    def update(self, dt):
        pass

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class CherrySprites(Spritesheet):
    def __init__(self, cherry):
        Spritesheet.__init__(self)
        self.cherry = cherry
        self.cherry.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def getStartImage(self):
        return self.getImage(2*2, 5*2)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        imgs = [(3*2, 5*2), (4*2, 5*2)]
        self.animations['SPARK'] = Animator(imgs)

    def update(self, dt, isLit):
        if isLit:
            self.cherry.image = self.getImage(*self.animations['SPARK'].update(dt))
            self.stopimage = (2*2, 5*2)
        else:
            self.cherry.image = self.getStartImage()

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class BombjackSprites(Spritesheet):
    def __init__(self, bombjack):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)
        self.bombjack = bombjack
        self.bombjack.image = self.getStartImage()
        self.stopimage = self.getStartImage()
        self.timer = 0
        # Time to wait between animations
        self.waitTime = .1
        self.frameCount = 0
        self.danceCount = 0
        self.deathCount = 0
        self.animations = {}
        self.defineAnimations()
        self.shouldRestart = False

    def getStartImage(self):
        return self.getImage(0, 0)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        right_imgs = []
        left_imgs = []
        for i in range(4):
            right_imgs.append((2*(i+1), 0))
            left_imgs.append((2*(i+5), 0))
        self.animations['RIGHT'] = Animator(right_imgs)
        self.animations['LEFT'] = Animator(left_imgs)
        mid = (17*2, 6*2)
        left = (18*2, 6*2)
        right = (18*2, 7*2)
        up = (19*2, 6*2)
        dance_imgs = [mid, left, mid, right, mid, up, mid, up]
        self.danceCount = 4*len(dance_imgs)
        self.animations['DANCE'] = Animator(dance_imgs)
        death_imgs = []
        for i in range(8):
            death_imgs.append(((20+i % 4)*2, 6*2))
        for i in range(4):
            death_imgs.append((2*(18+i), 2*5))
        death_imgs.append((2*23, 2*5))
        self.deathCount = 2*len(death_imgs)
        self.animations['DEATH'] = Animator(death_imgs)

    def update(self, dt):
        b = self.bombjack
        if b.dancing:
            self.timer += dt
            if self.timer >= self.waitTime:
                b.image = self.getImage(*self.animations['DANCE'].update(dt))
                self.timer = 0
                self.frameCount += 1
                if self.frameCount == self.danceCount:
                    b.dancing = False
                    self.frameCount = 0
                    self.shouldRestart = True
            return
        if b.dying:
            self.timer += dt
            if self.timer >= self.waitTime:
                b.image = self.getImage(*self.animations['DEATH'].update(dt))
                self.timer = 0
                self.frameCount += 1
                if self.frameCount == self.deathCount:
                    b.dying = False
                    self.frameCount = 0
                    self.shouldRestart = True
            return
        if b.direction == 1:
            if not b.jumped:
                b.image = self.getImage(*self.animations['RIGHT'].update(dt))
                self.stopimage = (1*2, 0)
            else:
                if b.vy >= 0:
                    b.image = self.getImage(14*2, 0)
                else:
                    b.image = self.getImage(13*2, 0)
        elif b.direction == -1:
            if not b.jumped:
                b.image = self.getImage(*self.animations['LEFT'].update(dt))
                self.stopimage = (5*2, 0)
            else:
                if b.vy >= 0:
                    b.image = self.getImage(16*2, 0)
                else:
                    b.image = self.getImage(15*2, 0)
        elif b.direction == 0:
            if not b.jumped:
                b.image = self.getStartImage()
            else:
                if b.vy >= 0:
                    b.image = self.getImage(10*2, 0)
                else:
                    b.image = self.getImage(11*2, 0)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class MummySprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def getStartImage(self):
        return self.getImage(0, 1*2)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        right_imgs = []
        left_imgs = []
        for i in range(3):
            right_imgs.append((2*(i+2), 1*2))
            left_imgs.append((2*(i+5), 1*2))
        self.animations['RIGHT'] = Animator(right_imgs)
        self.animations['LEFT'] = Animator(left_imgs)

    def update(self, dt):
        e = self.enemy
        if e.direction == 1:
            e.image = self.getImage(*self.animations['RIGHT'].update(dt))
            self.stopimage = (2*2, 1*2)
        elif e.direction == -1:
            e.image = self.getImage(*self.animations['LEFT'].update(dt))
            self.stopimage = (5*2, 1*2)
        elif e.direction == 0:
            e.image = self.getStartImage()

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class BirdSprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def getStartImage(self):
        return self.getImage(2*14, 2*1)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        horiz_imgs = []
        vert_imgs = []
        for i in range(3):
            horiz_imgs.append((2*(i+8), 2*1))
            vert_imgs.append((2*(i+11), 2*1))
        self.animations['HORIZ'] = Animator(horiz_imgs)
        self.animations['VERT'] = Animator(vert_imgs)

    def update(self, dt):
        e = self.enemy
        # If we are horizontally travelling
        if abs(e.direction) == 1:
            image = self.getImage(*self.animations['HORIZ'].update(dt))
            # If we are moving right, flip the left-pointing image
            if e.direction > 0:
                image = pygame.transform.flip(image, True, False)
                image.set_colorkey(image.get_at((0, 0)))
            e.image = image
            self.stopimage = (8*2, 1*2)
        # If we are veritcally travelling or stationary
        else:
            e.image = self.getImage(*self.animations['VERT'].update(dt))
            self.stopimage = (11*2, 1*2)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class ClubSprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def getStartImage(self):
        return self.getImage(15*2, 3*2)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        imgs = []
        for i in range(4):
            imgs.append((2*(i+15), 3*2))
        self.animations['MOVE'] = Animator(imgs)

    def update(self, dt):
        e = self.enemy
        image = self.getImage(*self.animations['MOVE'].update(dt))
        if e.direction > 0:
            image = pygame.transform.flip(image, True, False)
            image.set_colorkey(image.get_at((0, 0)))
        e.image = image

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class UFOSprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def getStartImage(self):
        return self.getImage(0, 3*2)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, x, y, 2*TILEWIDTH, 2*TILEHEIGHT)

    def defineAnimations(self):
        imgs = []
        for i in range(6):
            imgs.append((2*i, 3*2))
        self.animations['MOVE'] = Animator(imgs)

    def update(self, dt):
        e = self.enemy
        e.image = self.getImage(*self.animations['MOVE'].update(dt))

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()
