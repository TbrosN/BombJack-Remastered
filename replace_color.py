import pygame

"""

    Helper functions that replace one color with another in a surface.

    Inspired by kevintodisco on Game Development Stack Exchange:
    https://gamedev.stackexchange.com/questions/26550/how-can-a-pygame-image-be-colored
"""

# Replaces color c1 with c2
def replace_color(surface, c1, c2):
    arr = pygame.surfarray.pixels3d(surface)
    for row in arr:
        for p in row:
            if (p[0], p[1], p[2]) == c1:
                (p[0], p[1], p[2]) = c2


transcolor = (186, 252, 202)


# Replaces all non-transparent colors with c
def replace_all_colors(surface, c):
    arr = pygame.surfarray.pixels3d(surface)
    for row in arr:
        for p in row:
            # If it is not transparent
            if (p[0], p[1], p[2]) != transcolor:
                (p[0], p[1], p[2]) = c
