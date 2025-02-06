import pygame
from constants import *
import numpy as np
from animation import Animator
from constants import SPRITESHEET_FILE

"""Module for extracting sprites from a spritesheet.
"""

BASETILEWIDTH = 20/SPRITEFACTOR
BASETILEHEIGHT = 20/SPRITEFACTOR

BGTILESIZE = 224


class Spritesheet(object):
    """A class for extracting and manipulating sprites from a spritesheet.

    Attributes:
        sheet (pygame.Surface): The loaded and processed spritesheet image.
        startImage (pygame.Surface): The initial image of the sphere.
        animations (dict): A dictionary of animations for the sphere.
        stopimage (pygame.Surface): The static image of the sphere.
    
    Methods:
        getStartImage(self)
        getImage(self, x, y)
        defineAnimations(self)
        update(self, dt)
        reset(self)
    """
    def __init__(self):
        self.sheet = pygame.image.load(SPRITESHEET_FILE).convert()
        transcolor = self.sheet.get_at((0, 0))
        # print(transcolor)
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
    """A class for handling background sprites from a spritesheet.

    Attributes:
        sheet (pygame.Surface): The loaded and processed background spritesheet image.
    """
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
        return self.getImage(16, 4)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

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
        return self.getImage(2, 5)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        imgs = [(3, 5), (4, 5)]
        self.animations['SPARK'] = Animator(imgs)

    def update(self, dt, isLit):
        if isLit:
            self.cherry.image = self.getImage(*self.animations['SPARK'].update(dt))
            self.stopimage = (2, 5)
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
        self.doneDying = False
        self.doneDancing = False

    def getStartImage(self):
        return self.getImage(0, 0)

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        right_imgs = []
        left_imgs = []
        for i in range(4):
            right_imgs.append((i+1, 0))
            left_imgs.append((i+5, 0))
        self.animations['RIGHT'] = Animator(right_imgs)
        self.animations['LEFT'] = Animator(left_imgs)
        mid = (17, 6)
        left = (18, 6)
        right = (18, 7)
        up = (19, 6)
        dance_imgs = [mid, left, mid, right, mid, up, mid, up]
        self.danceCount = 4*len(dance_imgs)
        self.animations['DANCE'] = Animator(dance_imgs)
        death_imgs = []
        for i in range(8):
            death_imgs.append((20+i % 4, 6))
        for i in range(4):
            death_imgs.append((18+i, 5))
        death_imgs.append((23, 5))
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
                    self.doneDancing = True
            return
        if b.dying:
            self.timer += dt
            if self.timer >= self.waitTime:
                b.image = self.getImage(*self.animations['DEATH'].update(dt))
                self.timer = 0
                self.frameCount += 1
                # print(self.frameCount)
                if self.frameCount == self.deathCount:
                    b.dying = False
                    self.frameCount = 0
                    self.doneDying = True
            return
        if b.direction == 1:
            if not b.jumped:
                b.image = self.getImage(*self.animations['RIGHT'].update(dt))
                self.stopimage = (1, 0)
            else:
                if b.vy >= 0:
                    b.image = self.getImage(14, 0)
                else:
                    b.image = self.getImage(13, 0)
        elif b.direction == -1:
            if not b.jumped:
                b.image = self.getImage(*self.animations['LEFT'].update(dt))
                self.stopimage = (5, 0)
            else:
                if b.vy >= 0:
                    b.image = self.getImage(16, 0)
                else:
                    b.image = self.getImage(15, 0)
        elif b.direction == 0:
            if not b.jumped:
                b.image = self.getStartImage()
            else:
                if b.vy >= 0:
                    b.image = self.getImage(10, 0)
                else:
                    b.image = self.getImage(11, 0)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class MummySprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.startImage = self.getImage(0, 1)
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def setStartImage(self, image=None):
        if image is None:
            self.startImage = self.getImage(0, 1)
        else:
            self.startImage = image

    def getStartImage(self):
        return self.startImage

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        right_imgs = []
        left_imgs = []
        for i in range(3):
            right_imgs.append(((i+2), 1))
            left_imgs.append(((i+5), 1))
        self.animations['RIGHT'] = Animator(right_imgs)
        self.animations['LEFT'] = Animator(left_imgs)

        # IDEA: We use a spawn animation something like this for mummies and other enemies
        spawn_imgs = []
        for i in range(4):
            spawn_imgs.append((2+i, 9))
        self.animations['SPAWN'] = Animator(spawn_imgs)

    def update(self, dt):
        e = self.enemy
        if e.direction == 1:
            e.image = self.getImage(*self.animations['RIGHT'].update(dt))
            self.stopimage = (2, 1)
        elif e.direction == -1:
            e.image = self.getImage(*self.animations['LEFT'].update(dt))
            self.stopimage = (5, 1)
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
        self.startImage = self.getImage(14, 1)
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def setStartImage(self, image=None):
        if image is None:
            self.startImage = self.getImage(14, 1)
        else:
            self.startImage = image

    def getStartImage(self):
        return self.startImage

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        horiz_imgs = []
        vert_imgs = []
        for i in range(3):
            horiz_imgs.append(((i+8), 1))
            vert_imgs.append(((i+11), 1))
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
            self.stopimage = (8, 1)
        # If we are veritcally travelling or stationary
        else:
            e.image = self.getImage(*self.animations['VERT'].update(dt))
            self.stopimage = (11, 1)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class ClubSprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.startImage = self.getImage(15, 3)
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def setStartImage(self, image=None):
        if image is None:
            self.startImage = self.getImage(15, 3)
        else:
            self.startImage = image

    def getStartImage(self):
        return self.startImage

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        imgs = []
        for i in range(4):
            imgs.append(((i+15), 3))
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
        self.startImage = self.getImage(0, 3)
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def setStartImage(self, image=None):
        if image is None:
            self.startImage = self.getImage(0, 3)
        else:
            self.startImage = image

    def getStartImage(self):
        return self.startImage

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        imgs = []
        for i in range(6):
            imgs.append((i, 3))
        self.animations['MOVE'] = Animator(imgs)

    def update(self, dt):
        e = self.enemy
        e.image = self.getImage(*self.animations['MOVE'].update(dt))

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class OrbSprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.startImage = self.getImage(11, 2)
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def setStartImage(self, image=None):
        if image is None:
            self.startImage = self.getImage(11, 2)
        else:
            self.startImage = image

    def getStartImage(self):
        return self.startImage

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        imgs = []
        for i in range(7):
            imgs.append((9+i, 2))
        self.animations['MOVE'] = Animator(imgs)

    def update(self, dt):
        e = self.enemy
        image = self.getImage(*self.animations['MOVE'].update(dt))
        if e.direction > 0:
            image = pygame.transform.flip(image, True, False)
            image.set_colorkey(image.get_at((0, 0)))
        e.image = image
        self.stopimage = (14, 2)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()


class SphereSprites(Spritesheet):
    def __init__(self, enemy):
        Spritesheet.__init__(self)
        transcolor = self.sheet.get_at((0, 0))
        self.sheet.set_colorkey(transcolor)

        self.enemy = enemy
        self.startImage = self.getImage(0, 2)
        self.enemy.image = self.getStartImage()
        self.animations = {}
        self.defineAnimations()
        self.stopimage = self.getStartImage()

    def setStartImage(self, image=None):
        if image is None:
            self.startImage = self.getImage(0, 2)
        else:
            self.startImage = image

    def getStartImage(self):
        return self.startImage

    def getImage(self, x, y):
        return Spritesheet.getImage(self, SPRITEFACTOR*x, SPRITEFACTOR*y, SPRITEFACTOR*TILEWIDTH, SPRITEFACTOR*TILEHEIGHT)

    def defineAnimations(self):
        imgs = []
        for i in range(9):
            imgs.append((i, 2))
        self.animations['MOVE'] = Animator(imgs)

    def update(self, dt):
        e = self.enemy
        image = self.getImage(*self.animations['MOVE'].update(dt))
        if e.direction > 0:
            image = pygame.transform.flip(image, True, False)
            image.set_colorkey(image.get_at((0, 0)))
        e.image = image
        self.stopimage = (14, 2)

    def reset(self):
        for key in list(self.animations.keys()):
            self.animations[key].reset()
