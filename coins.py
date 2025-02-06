import pygame
from constants import *
from sprites import CoinSprites

class PowerCoin(object):
    """Represents a power-up coin in the game.

    The `PowerCoin` class controls the movement and interaction of the coin,
    which grants a temporary power-up to the `bombjack` character when collected.

    Attributes:
        x (int): The horizontal position of the coin.
        y (int): The vertical position of the coin.
        vx (int): The horizontal velocity of the coin.
        vy (int): The vertical velocity of the coin.
        w (int): The width of the coin (for collision detection).
        h (int): The height of the coin (for collision detection).
        collideRadius (float): The radius used for collision detection.
        image (:obj:`pygame.Surface`): The image used to render the coin.
        sprites (:obj:`CoinSprites`): The sprite object for coin animations.
        visible (bool): Whether the coin is visible on the screen.
        timer (float): Tracks the duration of the power-up effect.
        bombjack (:obj:`Bombjack`): The `bombjack` character that can collect this coin.
    """

    def __init__(self, bombjack):
        self.x = TILEWIDTH * (NCOLS - 3)
        self.y = 3 * TILEHEIGHT
        self.vx = 100
        self.vy = 100
        self.w = TILEWIDTH * SPRITEFACTOR / 2
        self.h = TILEHEIGHT * SPRITEFACTOR / 2
        self.collideRadius = min(self.w, self.h) / 2
        self.image = None
        self.sprites = CoinSprites(self)
        self.visible = False
        self.timer = 0
        self.bombjack = bombjack

    def update(self, dt, platList):
        self.sprites.update(dt)
        self.updatePower(dt)

        # Update position
        dx = self.vx * dt
        dy = self.vy * dt

        # Check for collisions with platforms and change direction
        for p in platList:
            # X-axis collision
            if p.get_rect().colliderect(self.x - self.w / 2 + dx, self.y, self.w, self.h):
                dx = 0
                self.vx *= -1  # Reverse direction on collision
            # Y-axis collision
            if p.get_rect().colliderect(self.x - self.w / 2, self.y + dy, self.w, self.h):
                dy = 0
                self.vy *= -1  # Reverse direction on collision

        # Apply updated positions
        self.x += dx
        self.y += dy

    def updatePower(self, dt):
        if self.bombjack.poweredUp:
            self.timer += dt

        if self.timer >= FREEZETIME:
            self.bombjack.poweredUp = False
            self.timer = 0

    def get_rect(self):
        return pygame.Rect(self.x - self.w / 2, self.y - self.h / 2, self.w, self.h)

    def render(self, screen):
        if self.visible:
            screen.blit(self.image, (self.x - self.w, self.y - self.h))
            # Uncomment to draw debug shapes
            # pygame.draw.rect(screen, YELLOW, self.get_rect(), 3)
            # pygame.draw.circle(screen, RED, (self.x, self.y), self.collideRadius, 3)
