import pygame
from constants import *
import numpy as np
from sprites import Spritesheet
from math import ceil


class Platform(object):
    """Represents a platform object in the game.

    A platform can be horizontal or vertical and is defined by its position, size, level, and orientation.
    The platform has a gradient color scheme based on the game level.

    Attributes:
        x (float): The x-coordinate of the platform.
        y (float): The y-coordinate of the platform.
        w (float): The width of the platform.
        h (float): The height of the platform.
        level (int): The game level the platform belongs to.
        orientation (int): The orientation of the platform, where 0 is horizontal, and -1 or 1 are vertical.
        image (Surface): The image of the platform.
        sheet (Surface): The spritesheet used for loading colors.
        colors (list): The list of colors for different levels.
    """
    
    def __init__(self, x, y, w, h, level, orientation=0):
        self.x = x
        self.y = y-PLATFORMSIZE/2
        if abs(orientation) == 0:
            self.y = self.y+h/2
        self.w = w
        self.h = h
        self.level = level
        # Let 0 be in map, 2 be edge horiztonal, -1 be vertical left, 1 be veritcal right
        self.orientation = orientation
        self.image = None
        self.sheet = pygame.image.load(
            "spritesheets/spritesheet_bombjack8.png").convert()
        # Contains the colors for each level
        self.colors = []
        self.init_colors()

    def init_colors(self):
        # NOTE: We want 8 colors per level
        ORANGE = []
        for i in range(2):
            ORANGE.append(self.sheet.get_at((291-8*i, 149)))
        for i in range(6):
            ORANGE.append(self.sheet.get_at((84-8*i, 292)))

        GREEN = []
        for i in range(8):
            GREEN.append(self.sheet.get_at((306+8*i, 280)))

        BLUE = []
        for i in range(6):
            BLUE.append(self.sheet.get_at((144+8*i, 292)))
        BLUE.append(self.sheet.get_at((204, 292)))
        BLUE.append(self.sheet.get_at((204, 292)))

        YELLOW = []
        for i in range(6):
            YELLOW.append(self.sheet.get_at((292-8*i, 148)))
        YELLOW.append(self.sheet.get_at((292-8*5, 148)))
        YELLOW.append(self.sheet.get_at((292-8*5, 148)))

        self.colors = [ORANGE, GREEN, ORANGE, YELLOW, BLUE]

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    # Draws a scaled bitmap on this rect from color start to color end
    def draw_gradient(self, screen, start, end, rect):
        startColor = start
        endColor = end
        bitmap = pygame.Surface((2, 2))
        width = rect.right-rect.left
        height = rect.bottom-rect.top
        # If vertical
        if abs(self.orientation) == 1:
            pygame.draw.line(bitmap, startColor, (0, 0), (0, 1))
            pygame.draw.line(bitmap, endColor, (1, 0), (1, 1))
        # If horizontal
        else:
            pygame.draw.line(bitmap, startColor, (0, 0), (1, 0))
            pygame.draw.line(bitmap, endColor, (0, 1), (1, 1))
        bitmap = pygame.transform.smoothscale(
            bitmap, (round(width), round(height)))
        screen.blit(bitmap, rect)

    def render(self, screen):
        # print(self.get_rect())
        level = self.level
        colors = self.colors[level % len(self.colors)]
        numRects = len(colors)-1
        # print(numRects)
        for i in range(numRects):
            if self.orientation == -1:
                dx = self.w/numRects
                self.draw_gradient(
                    screen, colors[i], colors[i+1], pygame.Rect(self.x+i*dx, self.y+i*dx, ceil(self.w/numRects), self.h-2*i*dx))
            elif self.orientation == 1:
                dx = self.w/numRects
                self.draw_gradient(
                    screen, colors[i], colors[i+1], pygame.Rect(self.x+i*dx, self.y+(numRects-i)*dx, ceil(self.w/numRects), self.h-2*(numRects-i)*dx))
            else:
                # To make it rounded
                if self.orientation == 0 and i <= 0:
                    self.draw_gradient(
                        screen, colors[i], colors[i+1], pygame.Rect(self.x+2, self.y+self.h*i/numRects, self.w-4, ceil(self.h/numRects)))
                elif self.orientation == 0 and i >= numRects-1:
                    self.draw_gradient(
                        screen, colors[i], colors[i+1], pygame.Rect(self.x+2, self.y+self.h*i/numRects, self.w-4, ceil(self.h/numRects)))
                else:
                    self.draw_gradient(
                        screen, colors[i], colors[i+1], pygame.Rect(self.x, self.y+self.h*i/numRects, self.w, ceil(self.h/numRects)))


class PlatformGroup(object):
    def __init__(self, file, level):
        self.platList = []
        self.platSymbol = '-'
        self.level = level
        self.file = file
        data = self.readMapFile(file)
        self.connectHorizontally(data)
        self.connectVertically(data)
        # TOP
        self.platList.append(Platform(0, PLATFORMSIZE/2,
                                      SCREENWIDTH, PLATFORMSIZE, self.level, 2))
        # BOTTOM
        self.platList.append(Platform(0, SCREENHEIGHT-PLATFORMSIZE-PLATFORMSIZE/2,
                                      SCREENWIDTH, PLATFORMSIZE, self.level, 2))
        # LEFT
        self.platList.append(Platform(0, PLATFORMSIZE/2,
                                      PLATFORMSIZE, SCREENHEIGHT-PLATFORMSIZE, self.level, -1))
        # RIGHT
        self.platList.append(Platform(SCREENWIDTH-PLATFORMSIZE, PLATFORMSIZE/2,
                                      PLATFORMSIZE, SCREENHEIGHT-PLATFORMSIZE, self.level, 1))

    def readMapFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1', comments=None)

    def connectHorizontally(self, data, xoffset=0, yoffset=0):
        for row in list(range(data.shape[0])):
            w = 0
            x = -1
            y = row*TILEHEIGHT
            h = PLATFORMSIZE
            for col in list(range(data.shape[1])):
                if data[row][col] == self.platSymbol:
                    if x == -1:
                        x = col*TILEWIDTH
                    w += TILEWIDTH
                    if col + 1 == len(list(range(data.shape[1]))):
                        self.platList.append(Platform(x, y, w, h, self.level))
                else:
                    if x != -1:
                        self.platList.append(Platform(x, y, w, h, self.level))
                        x = -1
                        w = 0

    def connectVertically(self, data):
        dataT = data.transpose()
        for col in list(range(dataT.shape[0])):

            for row in list(range(dataT.shape[1])):
                x = col*TILEWIDTH
                y = -1
                h = 0
                w = PLATFORMSIZE
                if dataT[col][row] == self.platSymbol:
                    if y == -1:
                        y = row*TILEHEIGHT
                    h += TILEHEIGHT
                    if row + 1 == len(list(range(dataT.shape[1]))):
                        self.platList.append(Platform(x, y, w, h, self.level))
                else:
                    if y != -1:
                        self.platList.append(Platform(x, y, w, h, self.level))
                        y = -1
                        h = 0

    def render(self, screen):
        for plat in self.platList:
            plat.render(screen)
