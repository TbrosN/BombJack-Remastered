import pygame
from pygame.locals import *
from constants import *
from sprites import BombjackSprites
from replace_color import replace_all_colors


class Bombjack(object):
    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 175
        self.vy = 0
        self.jumped = True
        self.w = TILEWIDTH*SPRITEFACTOR/2
        self.h = TILEHEIGHT*SPRITEFACTOR/2
        self.collideRadius = min(self.w, self.h)/2
        self.image = None
        self.sprites = BombjackSprites(self)
        self.direction = 0
        self.gliding = False
        self.glideTime = GLIDETIME
        self.glideTimer = 0
        self.dancing = False
        self.dying = False
        self.poweredUp = False

    # Returns the number of points earned during this update
    def update(self, dt, platList):
        score = 0
        self.sprites.update(dt)
        if self.dancing or self.dying:
            return score
        dx = 0
        dy = 0

        # get keypresses
        key = pygame.key.get_pressed()
        if key[K_UP]:
            # Allow speeding up
            if self.jumped:
                if self.vy < 0 and self.vy > -2*GRAVMAX:
                    self.vy -= 2*GRAV*dt
        if key[K_LEFT]:
            self.direction = -1
            dx -= self.vx*dt
        if key[K_RIGHT]:
            self.direction = 1
            dx += self.vx*dt
        if dx == 0:
            self.direction = 0

        # check for player fall
        if key[K_DOWN] and self.jumped:
            if self.vy < 0:
                self.vy = 0

        # add gravity
        self.vy += GRAV*dt
        if self.vy > GRAVMAX:
            self.vy = GRAVMAX
        # Assume gravity is active and prevent jumping
        self.jumped = True

        if self.gliding:
            self.glideTimer += dt
            if self.glideTimer <= self.glideTime:
                self.vy = GLIDEVEL
            else:
                self.gliding = False
                self.glideTimer = 0

        dy += self.vy*dt

        # TODO: Add points when jack hits walls while jumping (we already did ceilings)
        for p in platList:
            # x collision
            if p.get_rect().colliderect(self.x-self.w/2 + dx, self.y, self.w, self.h):
                dx = 0
            # y collision
            if p.get_rect().colliderect(self.x-self.w/2, self.y + dy, self.w, self.h):
                # If hitting the bottom
                if self.vy < 0:
                    dy = p.get_rect().bottom - self.get_rect().top
                    self.vy = 0
                    # For scoring purposes
                    score = 10
                # If hitting the top
                elif self.vy >= 0:
                    dy = p.get_rect().top - self.get_rect().bottom
                    self.vy = 0
                    self.jumped = False

        self.x += dx
        self.y += dy
        # For scoring purposes
        return score

    def eatCherries(self, cherryList):
        for cherry in cherryList:
            if self.collideCheck(cherry):
                return cherry
        return None

    def collideCheck(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        dSquared = dx*dx+dy*dy
        rSquared = (self.collideRadius + other.collideRadius)**2
        if dSquared <= rSquared:
            return True
        return False

    def get_rect(self):
        return pygame.Rect(self.x-self.w/2, self.y, self.w, self.h)

    def render(self, screen):
        if self.image is not None:
            if self.poweredUp:
                copy = self.image.copy()
                replace_all_colors(copy, (255, 255, 0))
                self.image = copy
                # print('powered up')
            screen.blit(self.image, (self.x-self.w, self.y-self.h))
            # pygame.draw.rect(screen, YELLOW, self.get_rect(), 3)
            # pygame.draw.circle(screen, RED, (self.x, self.y), self.collideRadius, 3)
        else:
            pygame.draw.rect(screen, YELLOW, self.get_rect())
