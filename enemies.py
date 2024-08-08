import pygame
import numpy as np
from pygame.locals import *
from constants import *
from math import sqrt
from sprites import Spritesheet, MummySprites, BirdSprites, ClubSprites, UFOSprites, OrbSprites, SphereSprites
from replace_color import replace_color


class Enemy(object):
    def __init__(self, bombjack):
        self.w = TILEWIDTH*SPRITEFACTOR/2
        self.h = TILEHEIGHT*SPRITEFACTOR/2-1
        self.timer = 0
        self.bombjack = bombjack
        self.image = None
        self.sprites = MummySprites(self)
        self.collideRadius = TILEWIDTH/2
        self.frozen = False
        self.freezeTimer = 0
        self.flashTimer = 0
        self.flashTime = FLASHTIME
        self.safeTimer = 0
        self.friendly = False
        self.safeImage = self.sprites.getStartImage()
        self.visible = True
        self.v = 100

    # Called when the P is collected
    # Freezes the enemy, temporarily turning it into a coin
    def freeze(self):
        self.frozen = True
        self.image = self.sprites.getImage(0, 4)
        self.safeImage = self.sprites.getStartImage()

    def updateFreeze(self, dt):
        self.freezeTimer += dt
        if FREEZETIME - self.freezeTimer <= NUMFLASHES*FLASHTIME:
            self.flashTimer += dt
        if self.flashTimer >= self.flashTime:
            self.visible = not self.visible
            self.flashTimer = 0
            # Exponential flashing
            self.flashTime /= 1.3
        if self.freezeTimer >= FREEZETIME:
            self.visible = True
            self.frozen = False
            self.freezeTimer = 0
            # Reset flash time
            self.flashTime = FLASHTIME
            # Initiate safe time
            self.friendly = True

    def updateSafe(self, dt):
        self.image = self.safeImage
        self.safeTimer += dt
        if self.safeTimer >= SAFETIME:
            self.safeTimer = 0
            self.friendly = False

    def get_rect(self):
        return pygame.Rect(self.x-self.w/2, self.y-3*self.h/5, self.w, self.h)

    def render(self, screen):
        if not self.visible:
            return
        if self.image is not None:
            y_shifted = self.get_rect().y
            screen.blit(self.image, (self.x-self.w, y_shifted))
            # pygame.draw.rect(screen, YELLOW, self.get_rect(), 3)
            # pygame.draw.circle(screen, RED, (self.x, self.y), self.collideRadius, 3)
        else:
            pygame.draw.rect(screen, YELLOW, self.get_rect())


class EnemyGroup(object):
    def __init__(self, enemyfile, bombjack):
        self.enemyList = []
        self.respawnList = []
        self.bombjack = bombjack
        self.createEnemyList(enemyfile)
        self.respawnTimer = RESPAWNTIME
        # The spawn location
        self.row = 0
        self.col = 0

    def createEnemyList(self, enemyfile):
        data = self.readEnemyFile(enemyfile)
        for row in range(data.shape[0]):
            for col in range(data.shape[1]):
                if data[row][col] == 's':
                    self.row = row
                    self.col = col
                elif data[row][col] == 'b':
                    self.enemyList.append(Bird(self.bombjack, row, col))
                # NOTE: Enemies other than birds are put at the last row of the file.
                # Club
                if data[row][col] == 'c':
                    mummy = Mummy(self.bombjack, self.row, self.col, None)
                    mummy.next = Club(self.bombjack, -1, -1, mummy)
                    self.respawnList.append(mummy)
                # UFO
                elif data[row][col] == 'u':
                    mummy = Mummy(self.bombjack, self.row, self.col, None)
                    mummy.next = UFO(self.bombjack, -1, -1, mummy)
                    self.respawnList.append(mummy)
                # Sphere
                elif data[row][col] == 'p':
                    mummy = Mummy(self.bombjack, self.row, self.col, None)
                    mummy.next = Sphere(self.bombjack, -1, -1, mummy)
                    self.respawnList.append(mummy)
                # Orb
                elif data[row][col] == 'o':
                    mummy = Mummy(self.bombjack, self.row, self.col, None)
                    mummy.next = Orb(self.bombjack, -1, -1, mummy)
                    self.respawnList.append(mummy)

    def readEnemyFile(self, textfile):
        return np.loadtxt(textfile, dtype='<U1', comments=None)

    def isEmpty(self):
        if len(self.enemyList) == 0:
            return True
        return False

    def update(self, dt, platList):
        self.updateRespawn(dt)
        for enemy in self.enemyList:
            enemy.update(dt, platList)

    def render(self, screen):
        for enemy in self.enemyList:
            enemy.render(screen)

    def freeze(self):
        for enemy in self.enemyList:
            enemy.freeze()

    def respawn(self, enemy):
        enemy.frozen = False
        enemy.friendly = False
        enemy.freezeTimer = 0
        enemy.flashTimer = 0
        if hasattr(enemy, 'mummy'):
            mummy = enemy.mummy
            mummy = Mummy(self.bombjack, mummy.row, mummy.col, mummy.next)
            self.respawnList.append(mummy)
        else:
            self.respawnList.append(enemy)

    def updateRespawn(self, dt):
        if len(self.enemyList) > 0 and self.enemyList[0].frozen:
            return
        # If there are enemies to respawn
        if len(self.respawnList) > 0:
            self.respawnTimer += dt
        if self.respawnTimer >= RESPAWNTIME:
            # Remove an enemy from respawnList and add it to enemyList
            enemy = self.respawnList.pop(0)
            enemy.friendly = True
            self.enemyList.append(enemy)
            self.respawnTimer = 0


class Mummy(Enemy):
    def __init__(self, bombjack, row, col, next, platform=None):
        Enemy.__init__(self, bombjack)
        self.row = row
        self.col = col
        self.x = col*TILEWIDTH
        self.y = row*TILEHEIGHT
        self.vx = self.v
        self.vy = 0
        self.platform = platform
        self.sprites = MummySprites(self)
        self.image = self.sprites.getImage(0, 1)
        self.direction = 1
        self.next = next
        self.numLaps = 0
        self.safeImage = self.sprites.getImage(2, 8)
        # Mummys are slow
        self.v = 50

        # Color shifting the poof to blue
        sheet = pygame.image.load(
            "spritesheets/spritesheet_bombjack8.png").convert()
        replace = sheet.get_at((49, 171))
        new = (0, 0, 255)
        replace_color(self.safeImage, replace, new)
        replace = sheet.get_at((41, 171))
        new = (255, 255, 255)
        replace_color(self.safeImage, replace, new)
        replace = sheet.get_at((42, 171))
        new = (255, 0, 0)
        replace_color(self.safeImage, replace, new)

    def get_rect(self):
        return pygame.Rect(self.x-self.w/2, self.y-self.h, self.w, self.h)

    def update(self, dt, platList):
        if self.frozen:
            self.updateFreeze(dt)
            return
        if self.friendly:
            self.updateSafe(dt)
            return
        self.sprites.update(dt)
        dx = 0
        dy = 0

        dx = self.vx*dt

        p = self.platform
        # Used for x-collision detection
        margin = 1
        # If falling
        if p is None or self.numLaps >= MUMMYLAPS and self.x+dx+margin > p.x+p.w or self.x+dx+self.w < p.x+margin:
            self.vx = 0
            # Add gravity
            self.vy += GRAV*dt
            if self.vy > GRAVMAX:
                self.vy = GRAVMAX
            # Update change in y-position
            dy += self.vy*dt
            # Set image to falling image
            self.image = self.sprites.getImage(1, 1)
        # If walking on the platform
        elif self.numLaps < MUMMYLAPS:
            if self.x+dx+self.w > p.x+p.w or self.x+dx < p.x:
                self.vx *= -1
                self.direction *= -1
                self.numLaps += 1
                dx = self.vx*dt

        for plat in platList:
            # Vertical collision
            if plat is not self.platform and plat.get_rect().colliderect(self.x-self.w/2, self.y+dy, self.w, self.h):
                self.vy = 0
                dy = 0
                self.vx = self.v
                self.direction = 1
                self.numLaps = 0
                self.platform = plat
                # Perfectly align the mummy vertically
                self.y = plat.y-self.h
            # Horizontal collision
            if plat.get_rect().colliderect(self.x-self.w/2+dx, self.y, self.w, self.h):
                self.vx *= -1
                self.direction *= -1
                self.numLaps += 1
                dx = self.vx*dt

        self.x += dx
        self.y += dy

    def get_next(self, x, y):
        self.next.x = x
        self.next.y = y
        return self.next

# TODO: Let us only update the Club's position every n seconds


class Club(Enemy):
    def __init__(self, bombjack, x, y, mummy):
        Enemy.__init__(self, bombjack)
        self.mummy = mummy
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.sprites = ClubSprites(self)
        self.image = self.sprites.getImage(15, 3)
        self.direction = 0
        self.timer = 0
        self.time = .5

    def update(self, dt, platList):
        if self.frozen:
            self.updateFreeze(dt)
            return
        if self.friendly:
            self.updateSafe(dt)
            return
        self.sprites.update(dt)
        dx = 0
        dy = 0

        self.timer += dt
        if self.timer > self.time:
            diffx = self.bombjack.x-self.x
            diffy = self.bombjack.y-self.y
            dist = sqrt(diffx*diffx+diffy*diffy)

            self.vx = self.v*diffx/dist*dt
            self.vy = self.v*diffy/dist*dt
            self.direction = diffx
            self.timer = 0
        dx += self.vx
        dy += self.vy
        # check for collision
        for p in platList:
            # check for collision in x direction
            if p.get_rect().colliderect(self.x-self.w/2 + dx, self.y, self.w, self.h):
                self.direction *= -1
                self.vx *= -1
                self.timer = 0
            # check for collision in y direction
            if p.get_rect().colliderect(self.x-self.w/2, self.y + dy, self.w, self.h):
                self.vy *= -1
                self.timer = 0

        self.x += dx
        self.y += dy


class Bird(Enemy):
    def __init__(self, bombjack, row, col):
        Enemy.__init__(self, bombjack)
        self.x = col*TILEWIDTH
        self.y = row*TILEHEIGHT
        self.vx = 0
        self.vy = 0
        self.timer = 0
        self.time = 1
        self.direction = 0
        self.sprites = BirdSprites(self)
        self.image = self.sprites.getImage(8, 1)

    # We need to make him go in one direction for longer to avoid diagonal "cheating"
    def update(self, dt, platList):
        if self.frozen:
            self.updateFreeze(dt)
            return
        if self.friendly:
            self.updateSafe(dt)
            return
        self.sprites.update(dt)
        dx = 0
        dy = 0
        self.timer += dt
        if self.timer >= self.time:
            self.vx = 0
            self.vy = 0
            self.direction = 0
            if self.timer >= 1.5*self.time:
                diffx = self.bombjack.x-self.x
                diffy = self.bombjack.y-self.y

                if abs(diffx) > abs(diffy):
                    self.direction = diffx/abs(diffx)
                    self.vx = self.v*self.direction
                else:
                    self.direction = 2*diffy/abs(diffy)
                    self.vy = self.v*(self.direction/2)
                self.timer = 0

        dx = self.vx*dt
        dy = self.vy*dt

        # check for collision
        for p in platList:
            # check for collision in x direction
            if p.get_rect().colliderect(self.x-self.w/2 + dx, self.y, self.w, self.h):
                dx = 0
            # check for collision in y direction
            if p.get_rect().colliderect(self.x-self.w/2, self.y + dy, self.w, self.h):
                dy = 0

        self.x += dx
        self.y += dy


class UFO(Enemy):
    def __init__(self, bombjack, x, y, mummy):
        Enemy.__init__(self, bombjack)
        self.mummy = mummy
        self.x = x
        self.y = y
        self.vx = 1
        self.vy = 1
        self.setVelocity(self.vx, self.vy)
        self.sprites = UFOSprites(self)
        self.image = self.sprites.getImage(15, 3)

    # Note dx = 0 means ignore x direction, dy = 0 means ignore y direction
    def setVelocity(self, dx, dy):
        diffx = self.bombjack.x-self.x
        diffy = self.bombjack.y-self.y
        # If dx and diffx point in the same direction
        if dx*diffx > 0:
            diffx *= -1
        # If dy and diffy point in the same direction
        elif dy*diffy > 0:
            diffy *= -1
        dist = sqrt(diffx*diffx+diffy*diffy)

        self.v = dist
        self.vx = self.v*diffx/dist
        self.vy = self.v*diffy/dist

    def update(self, dt, platList):
        if self.frozen:
            self.updateFreeze(dt)
            return
        if self.friendly:
            self.updateSafe(dt)
            return
        self.sprites.update(dt)
        dx = self.vx*dt
        dy = self.vy*dt

        # check for collision
        for p in platList:
            if p.get_rect().colliderect(self.x-self.w/2 + dx, self.y, self.w, self.h):
                self.setVelocity(dx, 0)
            elif p.get_rect().colliderect(self.x-self.w/2, self.y+dy, self.w, self.h):
                self.setVelocity(0, dy)

        dx = self.vx*dt
        dy = self.vy*dt

        self.x += dx
        self.y += dy


class Orb(Enemy):
    def __init__(self, bombjack, x, y, mummy):
        Enemy.__init__(self, bombjack)
        self.mummy = mummy
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.v = 150
        self.sprites = OrbSprites(self)
        self.image = self.sprites.getImage(15, 3)
        self.direction = 1
        self.timer = 0
        self.time = 1

    def update(self, dt, platList):
        if self.frozen:
            self.updateFreeze(dt)
            return
        if self.friendly:
            self.updateSafe(dt)
            return
        self.sprites.update(dt)
        dx = 0
        dy = 0

        self.timer += dt
        if self.timer >= self.time:
            diffy = self.bombjack.y-self.y
            self.vx = self.v*dt*self.direction
            self.vy = self.v*diffy/200*dt
            self.timer = 0

        dx += self.vx
        dy += self.vy

        # check for collision
        for p in platList:
            # check for collision in x direction
            if p.get_rect().colliderect(self.x-self.w/2 + dx, self.y, self.w, self.h):
                self.direction *= -1
                self.vx *= -1
            # check for collision in y direction
            elif p.get_rect().colliderect(self.x-self.w/2, self.y + dy, self.w, self.h):
                self.vy *= -1
                self.timer = 0

        self.x += dx
        self.y += dy


class Sphere(Enemy):
    def __init__(self, bombjack, x, y, mummy):
        Enemy.__init__(self, bombjack)
        self.mummy = mummy
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.v = 150
        self.sprites = SphereSprites(self)
        self.image = self.sprites.getImage(15, 3)
        self.direction = 1
        self.timer = 0
        self.time = 2/30

    def update(self, dt, platList):
        if self.frozen:
            self.updateFreeze(dt)
            return
        if self.friendly:
            self.updateSafe(dt)
            return
        self.sprites.update(dt)
        dx = 0
        dy = 0

        self.timer += dt
        if self.timer >= self.time:
            diffx = self.bombjack.x-self.x
            self.vx = self.v*diffx/200*dt
            self.vy = self.v*self.direction*dt
            self.timer = 0

        dx += self.vx
        dy += self.vy

        # check for collision
        for p in platList:
            # check for collision in x direction
            if p.get_rect().colliderect(self.x-self.w/2 + dx, self.y, self.w, self.h):
                self.vx *= -1
                self.timer = 0
            # check for collision in y direction
            elif p.get_rect().colliderect(self.x-self.w/2, self.y + dy, self.w, self.h):
                self.direction *= -1
                self.vy *= -1
                self.timer = 0

        self.x += dx
        self.y += dy
