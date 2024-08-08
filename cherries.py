import pygame
from constants import *
import numpy as np
from sprites import CherrySprites


class Cherry(object):
    def __init__(self, row, column, bunch):
        self.collideRadius = int(TILEWIDTH*SPRITEFACTOR/4)
        self.x = column*TILEWIDTH+self.collideRadius
        self.y = row*TILEHEIGHT
        self.color = RED
        self.points = 10
        self.visible = True
        self.image = None
        self.sprites = CherrySprites(self)
        self.isLit = False
        # The ID of this cherry's bunch
        self.bunch = bunch

    def update(self, dt):
        self.sprites.update(dt, self.isLit)

    def render(self, screen):
        if self.image is not None:
            screen.blit(self.image, (self.x-2*self.collideRadius, self.y-2*self.collideRadius))
            # pygame.draw.circle(screen, WHITE, (self.x, self.y), self.collideRadius, 3)
        else:
            pygame.draw.circle(screen, RED, (self.x, self.y), self.collideRadius)


class CherryGroup(object):
    def __init__(self, cherryfile):
        self.cherryList = []
        self.powerup = None
        self.createCherryList(cherryfile)
        self.numEaten = 0
        self.litCount = 0
        self.hasLitCherry = False

    def createCherryList(self, cherryfile):
        data = self.readCherryFile(cherryfile)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                try:
                    # Each "shifted" number means reverse order.
                    # NOTE: In-order comes before reversed
                    index = '0123456789)!@#$%^&*('.index(data[row][col])
                    bunch = index % 10
                    # If the number is shifted, we need reverse the order of this bunch.
                    i = 0
                    if index > 9:
                        while i < len(self.cherryList) and self.cherryList[i].bunch < bunch:
                            i += 1
                    else:
                        while i < len(self.cherryList) and self.cherryList[i].bunch <= bunch:
                            i += 1
                    self.cherryList.insert(i, Cherry(row, col, bunch))
                except ValueError:
                    pass

    def readCherryFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1', comments=None)

    def isEmpty(self):
        if len(self.cherryList) == 0:
            return True
        return False

    def update(self, dt):
        for cherry in self.cherryList:
            cherry.update(dt)

    def updateLitCherry(self, cherry):
        index = self.cherryList.index(cherry)
        self.cherryList[index].isLit = False
        index = (index+1) % len(self.cherryList)
        self.cherryList[index].isLit = True
        self.hasLitCherry = True

    def render(self, screen):
        for cherry in self.cherryList:
            cherry.render(screen)
