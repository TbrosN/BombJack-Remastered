# For the sake of version control, this file contains past rendering methods for platforms.py (namely the Platform class)
def init_bitmap(self, start, end, rect):
    self.startColor = start
    self.endColor = end
    self.bitmap = pygame.Surface((2, 2))
    # If vertical
    if abs(self.orientation) == 1:
        pygame.draw.line(self.bitmap, self.startColor, (0, 0), (0, 1))
        pygame.draw.line(self.bitmap, self.endColor, (1, 0), (1, 1))
        self.bitmap = pygame.transform.smoothscale(
            self.bitmap, (round(self.w), round(self.h-2*PLATFORMSIZE)))
    # If horizontal
    else:
        pygame.draw.line(self.bitmap, self.startColor, (0, 0), (1, 0))
        pygame.draw.line(self.bitmap, self.endColor, (0, 1), (1, 1))
        # In in map
        if self.orientation == 0:
            self.bitmap = pygame.transform.smoothscale(
                self.bitmap, (round(self.w), round(self.h)-4))
        else:
            self.bitmap = pygame.transform.smoothscale(
                self.bitmap, (round(self.w), round(self.h)))


def render2(self, screen):
    if self.orientation == 0:
        pygame.draw.rect(screen, self.startColor, (self.x+3, self.y, self.w-6, 2))
        pygame.draw.rect(screen, self.endColor, (self.x+3, self.y+self.h-2, self.w-6, 2))
        screen.blit(self.bitmap, (self.x, self.y+2, self.w, self.h-4))
    elif self.orientation == 2:
        screen.blit(self.bitmap, (self.x, self.y, self.w, self.h))
    else:
        screen.blit(self.bitmap, (self.x, self.y+PLATFORMSIZE, self.w, self.h-2*PLATFORMSIZE))


def renderOld(self, screen):
    # print(self.get_rect())
    level = self.level
    colors = self.colors[level]
    numRects = len(colors)
    for i in range(numRects):
        if self.orientation == -1:
            dx = self.w/numRects
            pygame.draw.polygon(
                screen, colors[i], [(self.x+i*dx, self.y+i*dx), (self.x+(i+1)*dx, self.y+(i+1)*dx), (self.x+(i+1)*dx, self.y+self.h-(i+1)*dx), (self.x+i*dx, self.y+self.h-i*dx)])
        elif self.orientation == 1:
            dx = self.w/numRects
            pygame.draw.polygon(screen, colors[len(colors)-1-i], [(self.x+self.w-i*dx, self.y+i*dx), (self.x+self.w-(i+1)*dx, self.y+(
                i+1)*dx), (self.x+self.w-(i+1)*dx, self.y+self.h-(i+1)*dx), (self.x+self.w-i*dx, self.y+self.h-i*dx)])
        else:
            if self.orientation == 0 and self.h*i/numRects <= 2:
                pygame.draw.rect(
                    screen, colors[i], (self.x+3, self.y+self.h*i/numRects, self.w-6, ceil(self.h/numRects)))
            elif self.orientation == 0 and self.h*i/numRects >= PLATFORMSIZE-4:
                pygame.draw.rect(
                    screen, colors[i], (self.x+3, self.y+self.h*i/numRects, self.w-6, ceil(self.h/numRects)))
            else:
                pygame.draw.rect(
                    screen, colors[i], (self.x, self.y+self.h*i/numRects, self.w, ceil(self.h/numRects)))
