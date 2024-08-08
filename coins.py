import pygame
from constants import *
from sprites import CoinSprites


class PowerCoin(object):
    def __init__(self, bombjack):
        self.x = TILEWIDTH*(NCOLS-3)
        self.y = 3*TILEHEIGHT
        self.vx = 100
        self.vy = 100
        self.w = TILEWIDTH*SPRITEFACTOR/2
        self.h = TILEHEIGHT*SPRITEFACTOR/2
        self.collideRadius = min(self.w, self.h)/2
        self.image = None
        self.sprites = CoinSprites(self)
        self.visible = False
        self.timer = 0
        self.bombjack = bombjack

    def update(self, dt, platList):
        self.sprites.update(dt)
        self.updatePower(dt)
        dx = 0
        dy = 0

        dx = self.vx*dt
        dy = self.vy*dt

        for p in platList:
            # check for collision in x direction
            if p.get_rect().colliderect(self.x-self.w/2 + dx, self.y, self.w, self.h):
                dx = 0
                self.vx *= -1
            # check for collision in y direction
            if p.get_rect().colliderect(self.x-self.w/2, self.y + dy, self.w, self.h):
                dy = 0
                self.vy *= -1

        self.x += dx
        self.y += dy

    def updatePower(self, dt):
        if self.bombjack.poweredUp:
            self.bombjack.poweredUp = True
            self.timer += dt
        if self.timer >= FREEZETIME:
            self.bombjack.poweredUp = False
            self.timer = 0

    def get_rect(self):
        return pygame.Rect(self.x-self.w/2, self.y-self.h/2, self.w, self.h)

    def render(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x-self.w, self.y-self.h))
            # pygame.draw.rect(screen, YELLOW, self.get_rect(), 3)
            # pygame.draw.circle(screen, RED, (self.x, self.y), self.collideRadius, 3)
