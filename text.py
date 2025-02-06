# NOTE: The code in this file was inspired by Jonathan Richards' Pacmancode tutorial.

import pygame
from constants import *
from math import floor


class Text(object):
    """
    A class to represent a text object in a Pygame environment.

    Attributes:
        id (int, optional): The identifier for the text object. Default is None.
        text (str): The string to be displayed.
        color (tuple): The color of the text, represented as an RGB tuple.
        x (int): The x-coordinate of the text's position on the screen.
        y (int): The y-coordinate of the text's position on the screen.
        size (int): The font size of the text.
        time (int, optional): The duration (in milliseconds) the text should be displayed. Default is None (indefinite).
        visible (bool): A flag indicating whether the text is visible or not. Default is True.
        timer (int): Keeps track of the time elapsed since the text was created.
        lifespan (int, optional): The lifespan of the text. If set, the text will disappear after this time.
        label (pygame.Surface): The rendered text surface.
        destroy (bool): A flag indicating whether the text should be removed.
        font (pygame.font.Font): The font used to render the text.
    """
    def __init__(self, text, color, x, y, size, time=None, id=None, visible=True):
        self.id = id
        self.text = text
        self.color = color
        self.size = size
        self.visible = visible
        self.x = x
        self.y = y
        self.timer = 0
        self.lifespan = time
        self.label = None
        self.destroy = False
        self.setupFont("PressStart2P-Regular.ttf")
        self.createLabel()

    def setupFont(self, fontpath):
        self.font = pygame.font.Font(fontpath, self.size)

    def createLabel(self):
        self.label = self.font.render(self.text, 1, self.color)

    def setText(self, newtext):
        self.text = str(newtext)
        self.createLabel()

    def update(self, dt):
        if self.lifespan is not None:
            self.timer += dt
            if self.timer >= self.lifespan:
                self.timer = 0
                self.lifespan = None
                self.destroy = True

    def render(self, screen):
        if self.visible:
            x, y = (self.x, self.y)
            screen.blit(self.label, (x, y))


class TextGroup(object):
    """
    A class to manage multiple Text objects and render them as a group in a Pygame environment.

    Attributes:
        nextid (int): The next available ID for a new text object.
        alltext (dict): A dictionary mapping text IDs to their respective Text objects.
        highscore (str): The high score read from a file.
    """
    def __init__(self):
        self.nextid = -1
        self.alltext = {}
        with open('highscore.txt', 'r') as f:
            self.highscore = f.readline().split()[0]
        self.setupText()

    def addText(self, text, color, x, y, size, time=None, id=None):
        self.nextid += 1
        self.alltext[self.nextid] = Text(text, color, x, y, size, time=time, id=id)
        return self.nextid

    def removeText(self, id):
        self.alltext.pop(id)

    def setupText(self):
        size = round(TILEHEIGHT/2)
        self.alltext[SCORETXT] = Text("0".zfill(8), WHITE, 0, 2*size, size)
        self.alltext[ROUNDTXT] = Text("1", WHITE, SCREENWIDTH/2 -
                                      TILEWIDTH, SCREENHEIGHT+3*TILEHEIGHT, size)
        self.alltext[HIGHSCORETXT] = Text(self.highscore.zfill(
            8), WHITE, SCREENWIDTH-10*size, 2*size, size)
        self.alltext[3] = Text("SCORE", WHITE, 0, size-5, size)
        self.alltext[4] = Text("ROUND", WHITE, SCREENWIDTH/2-2 *
                               TILEWIDTH, SCREENHEIGHT+2*TILEHEIGHT, size)
        self.alltext[5] = Text("HI-SCORE", WHITE, SCREENWIDTH-10*size, size, size)
        self.nextid = 6

    def update(self, dt):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].update(dt)
            if self.alltext[tkey].destroy:
                self.removeText(tkey)

    def showText(self, id):
        self.hideText()
        self.alltext[id].visible = True

    def hideText(self):
        pass

    def updateScore(self, score):
        self.updateText(SCORETXT, str(score).zfill(8))
        if score > int(self.highscore):
            self.highscore = str(score)
            self.updateText(HIGHSCORETXT, self.highscore.zfill(8))

    def setHighScore(self):
        with open('highscore.txt', 'w') as f:
            f.write(self.highscore)

    def updateRound(self, round):
        self.updateText(ROUNDTXT, str(round))

    def updateText(self, id, value):
        if id in self.alltext.keys():
            self.alltext[id].setText(value)

    def render(self, screen):
        for tkey in list(self.alltext.keys()):
            self.alltext[tkey].render(screen)
