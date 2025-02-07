import pygame
from pygame.locals import *
from constants import *
from sprites import BombjackSprites
from replace_color import replace_all_colors

class Bombjack(object):
    """Handles Bombjack character logic including movement, collisions, and rendering.

    The `Bombjack` class is responsible for controlling the Bombjack character's 
    movements, collisions with platforms, and interaction with other objects such 
    as cherries. It also manages the character's state (e.g., gliding, dancing, 
    dying, powered up).

    Attributes:
        x (float): The horizontal position of the character.
        y (float): The vertical position of the character.
        vx (int): The horizontal velocity of the character.
        vy (float): The vertical velocity of the character.
        jumped (bool): Indicates whether the character is in the air (jumped).
        w (float): The width of the character.
        h (float): The height of the character.
        collideRadius (float): The collision radius of the character for detecting 
            proximity with other objects.
        image (:obj:`pygame.Surface`): The image used for rendering the character.
        sprites (:obj:`BombjackSprites`): The sprites object for managing Bombjack's 
            animations.
        direction (int): The movement direction (-1 for left, 1 for right, 0 for none).
        gliding (bool): Whether the character is currently gliding.
        glideTime (float): The total time allowed for gliding.
        glideTimer (float): The timer that tracks how long the character has been gliding.
        dancing (bool): Whether the character is in the dancing state.
        dying (bool): Whether the character is in the dying state.
        poweredUp (bool): Whether the character is powered up (e.g., has eaten cherries).
    """

    def __init__(self):
        self.x = 0
        self.y = 0
        self.vx = 175
        self.vy = 0
        self.jumped = True
        self.w = TILEWIDTH * SPRITEFACTOR / 2
        self.h = TILEHEIGHT * SPRITEFACTOR / 2
        self.collideRadius = min(self.w, self.h) / 2
        self.image = None
        self.sprites = BombjackSprites(self)
        self.direction = 0
        self.gliding = False
        self.glideTime = GLIDETIME
        self.glideTimer = 0
        self.dancing = False
        self.dying = False
        self.poweredUp = False

    def update(self, dt, platList):
        score = 0
        self.sprites.update(dt)
        if self.dancing or self.dying:
            return score

        dx, dy = 0, 0

        # Get keypresses
        key = pygame.key.get_pressed()
        if key[K_UP]:
            if self.jumped and self.vy < 0 and self.vy > -2 * GRAVMAX:
                self.vy -= 2 * GRAV * dt
        if key[K_LEFT]:
            self.direction = -1
            dx -= self.vx * dt
        if key[K_RIGHT]:
            self.direction = 1
            dx += self.vx * dt
        if dx == 0:
            self.direction = 0

        if key[K_DOWN] and self.jumped:
            if self.vy < 0:
                self.vy = 0

        # Apply gravity
        self.vy += GRAV * dt
        if self.vy > GRAVMAX:
            self.vy = GRAVMAX
        self.jumped = True

        if self.gliding:
            self.glideTimer += dt
            if self.glideTimer <= self.glideTime:
                self.vy = GLIDEVEL
            else:
                self.gliding = False
                self.glideTimer = 0

        dy += self.vy * dt

        # Handle platform collisions
        for p in platList:
            if p.get_rect().colliderect(self.x - self.w / 2 + dx, self.y, self.w, self.h):
                dx = 0
            if p.get_rect().colliderect(self.x - self.w / 2, self.y + dy, self.w, self.h):
                if self.vy < 0:
                    dy = p.get_rect().bottom - self.get_rect().top
                    self.vy = 0
                    score = 10
                elif self.vy >= 0:
                    dy = p.get_rect().top - self.get_rect().bottom
                    self.vy = 0
                    self.jumped = False

        self.x += dx
        self.y += dy
        return score

    def eatCherries(self, cherryList):
        for cherry in cherryList:
            if self.collideCheck(cherry):
                return cherry
        return None

    def collideCheck(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        dSquared = dx * dx + dy * dy
        rSquared = (self.collideRadius + other.collideRadius) ** 2
        return dSquared <= rSquared

    def get_rect(self):
        return pygame.Rect(self.x - self.w / 2, self.y, self.w, self.h)

    def render(self, screen):
        if self.image is not None:
            if self.poweredUp:
                copy = self.image.copy()
                replace_all_colors(copy, (255, 255, 0))
                self.image = copy
            screen.blit(self.image, (self.x - self.w, self.y - self.h))
        else:
            pygame.draw.rect(screen, YELLOW, self.get_rect())