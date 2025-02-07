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
        a line. Each bunch is associated with a number and orientation. The lit cherry
        travels among the bunches in increasing order. The orientation of a bunch determines
        the direction with which the lit cherry traverses the bunch.

        In the level file, cherries are indicated by a bunch tag, which is either a number
        or a symbol that is typed by doing `SHIFT + (a number)`, for instance `$` is `SHIFT + 4`.
        The number used to type the bunch tag is the number of the bunch, which determines its order
        in the lit cherry traversal.
        
        By default, the orientation of a bunch is left-to-right (if the line is horizontal),
        or up-to-down (if the line is vertical). However, if the bunch tag is a symbol rather
        than a number, then the orientation is reversed.
        """
        data = self.readCherryFile(cherryfile)
        # Parse the cherries and sort the cherry list using insertion sort
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                try:
                    bunch_tag = data[row][col]
                    index = '0123456789)!@#$%^&*('.index(bunch_tag)
                    bunch_number = index % 10
                    i = 0
                    # If the bunch tag is a number, keep the order the same as traversed
                    if index > 9:
                        while i < len(self.cherryList) and self.cherryList[i].bunch < bunch_number:
                            i += 1
                    # If the bunch tag is a symbol, reverse the order relative to traversal
                    else:
                        while i < len(self.cherryList) and self.cherryList[i].bunch <= bunch_number:
                            i += 1
                    self.cherryList.insert(i, Cherry(row, col, bunch_number))
                except ValueError:
                    pass

    def readCherryFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1', comments=None)

    def isEmpty(self):
        return len(self.cherryList) == 0

    def update(self, dt):
        for cherry in self.cherryList:
            cherry.update(dt)

    def updateLitCherry(self, cherry):
        index = self.cherryList.index(cherry)
        self.cherryList[index].isLit = False
        index = (index + 1) % len(self.cherryList)
        self.cherryList[index].isLit = True
        self.hasLitCherry = True

    def render(self, screen):
        for cherry in self.cherryList:
            cherry.render(screen)
