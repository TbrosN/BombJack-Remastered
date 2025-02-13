"""
This file contains constants used throughout this project.
"""

# (25, 27)
TILEWIDTH = 25
TILEHEIGHT = 30
# (23, 20)
NROWS = 19
NCOLS = 19
SCREENWIDTH = NCOLS*TILEWIDTH
SCREENHEIGHT = NROWS*TILEHEIGHT
PLATFORMSIZE = min(TILEHEIGHT, TILEWIDTH)*3/4
SCREENSIZE = (SCREENWIDTH, SCREENHEIGHT-PLATFORMSIZE)

SPRITESHEET_FILE = "spritesheets/spritesheet_bombjack8.png"
SPRITEFACTOR = 5/3
NUMLEVELS = 5
NUMLIVES = 5

BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

BOMBJACK = 0
PCHERRIES = 11
MUMMYLAPS = 3

GRAV = 400
GRAVMAX = 800
GLIDEVEL = 25

GLIDETIME = .3
FREEZETIME = 6
FLASHTIME = .3
# Number of on and offs, counted separately
NUMFLASHES = 4
# The time that the user is safe, measured in FLASHTIMEs
SAFETIME = FLASHTIME*2
RESPAWNTIME = FREEZETIME

SCORETXT = 0
ROUNDTXT = 1
HIGHSCORETXT = 2
TEXTTIME = .3
