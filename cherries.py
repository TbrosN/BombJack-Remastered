import pygame
from constants import *
import numpy as np
from sprites import CherrySprites

class Cherry(object):
    """Represents an individual cherry object in the game.

    The `Cherry` class handles the properties and behavior of a single cherry,
    including its position, state, and rendering. Cherries are part of bunches
    (groups) and may be eaten by the player.

    Attributes:
        collideRadius (int): The radius used for collision detection.
        x (int): The horizontal position of the cherry.
        y (int): The vertical position of the cherry.
        color (tuple): The RGB color of the cherry.
        points (int): The number of points awarded for eating the cherry.
        visible (bool): Indicates if the cherry is visible on the screen.
        image (:obj:`pygame.Surface`): The image used to render the cherry.
        sprites (:obj:`CherrySprites`): The sprite object for cherry animations.
        isLit (bool): Whether the cherry is "lit" (highlighted or active).
        bunch (int): The bunch ID to which the cherry belongs.
    """

    def __init__(self, row, column, bunch):
        self.collideRadius = int(TILEWIDTH * SPRITEFACTOR / 4)
        self.x = column * TILEWIDTH + self.collideRadius
        self.y = row * TILEHEIGHT
        self.color = RED
        self.points = 10
        self.visible = True
        self.image = None
        self.sprites = CherrySprites(self)
        self.isLit = False
        self.bunch = bunch

    def update(self, dt):
        self.sprites.update(dt, self.isLit)

    def render(self, screen):
        if self.image is not None:
            screen.blit(self.image, (self.x - 2 * self.collideRadius, self.y - 2 * self.collideRadius))
        else:
            pygame.draw.circle(screen, RED, (self.x, self.y), self.collideRadius)


class CherryGroup(object):
    """Represents a group of cherry objects in the game.

    The `CherryGroup` class manages a collection of cherries, handles their
    state updates, rendering, and lighting logic.

    Attributes:
        cherryList (list): A list of cherries in the group.
        powerup (NoneType): A placeholder attribute for future power-up functionality.
        numEaten (int): The number of cherries that have been eaten.
        litCount (int): The number of "lit" cherries in the group.
        hasLitCherry (bool): Indicates if there is an active (lit) cherry.

    """

    def __init__(self, cherryfile):
        self.cherryList = []
        self.powerup = None
        self.createCherryList(cherryfile)
        self.numEaten = 0
        self.litCount = 0
        self.hasLitCherry = False

    def createCherryList(self, cherryfile):
        """
        Instantiates the list of cherries in the given cherryfile.

        In any level, the cherries are divided into groups called bunches, which form
        a line. Each bunch is assoc