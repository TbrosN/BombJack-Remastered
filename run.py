import pygame
from math import floor
from pygame.locals import *
from constants import *
from bombjack import Bombjack
from platforms import PlatformGroup
from cherries import CherryGroup
from coins import PowerCoin
from sprites import BGSpritesheet
from enemies import EnemyGroup, Mummy, Club, Bird
from text import TextGroup


class GameController(object):
    """
    Controls the overall game flow and mechanics, including player movement, 
    enemies, platforms, power-ups, and rendering. Manages game state, levels, 
    rounds, and the main game loop.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.Surface(SCREENSIZE)
        self.screen2 = pygame.display.set_mode((SCREENWIDTH, SCREENHEIGHT+4*TILEHEIGHT), depth=32)
        self.background = None
        self.clock = pygame.time.Clock()
        self.bombjack = Bombjack()
        self.powerCoin = PowerCoin(self.bombjack)
        # Should start at 0
        self.level = 0
        # Should start at 1
        self.round = 1
        self.bgSheet = BGSpritesheet()
        self.textgroup = TextGroup()
        self.score = 0
        self.livesImage = self.bombjack.sprites.getStartImage()
        self.enemy_scores = [100, 200, 300, 500, 800, 1200, 2000]
        self.enemy_index = 0
        self.lives = NUMLIVES
        self.pauseTimer = 0
        self.pauseTime = 1
        self.paused = False

    def setBackground(self):
        self.background = self.bgSheet.getImage(self.level)

    def startGame(self, cherries=True):
        self.setBackground()
        file = f'levels/level{self.level}.txt'
        self.enemies = EnemyGroup(file, self.bombjack)
        self.platforms = PlatformGroup(file, self.level)
        if cherries:
            self.cherries = CherryGroup(file)
        else:
            # Reset the lit cherry
            if self.cherries.hasLitCherry:
                self.cherries.cherryList[0].isLit = False
                self.cherries.hasLitCherry = False
        self.powerCoin.visible = False
        self.powerCoin.x = int(NCOLS/2)*TILEWIDTH
        self.powerCoin.y = int(NROWS/2)*TILEHEIGHT
        self.bombjack.poweredUp = False

        self.bombjack.x = int(NCOLS/2)*TILEWIDTH
        self.bombjack.y = int(NROWS/2)*TILEHEIGHT
        self.bombjack.vy = 0

        self.textgroup.updateRound(self.round)

        pygame.mixer.music.load('ladymadonna.mp3')
        pygame.mixer.music.play(-1)

        # Pause the game for a bit
        self.paused = True

    def update(self):
        dt = self.clock.tick(30) / 1000.0
        if not self.paused:
            pts = self.bombjack.update(dt, self.platforms.platList)
            self.updateScore(pts)
            self.enemies.update(dt, self.platforms.platList)
            self.powerCoin.update(dt, self.platforms.platList)
            self.cherries.update(dt)
            self.textgroup.update(dt)
            self.checkCherryEvents()
            self.checkSpriteEvents()
            self.checkEnemyEvents()
            self.checkCoinEvents()
        else:
            self.pauseTimer += dt
            if self.pauseTimer >= self.pauseTime:
                self.pauseTimer = 0
                self.paused = False
        self.checkEvents()
        self.render()

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

    def winGame(self):
        self.enemies.enemyList.clear()
        self.enemies.respawnList.clear()
        self.bombjack.poweredUp = False
        self.powerCoin.visible = False
        self.bombjack.dancing = True
        self.round += 1
        self.level = (self.round-1) % NUMLEVELS

        # Lit cherry bonus
        if self.cherries.litCount >= 20:
            scores = [5, 3, 2, 1]
            self.updateScore(10000*scores[23-self.cherries.litCount])

    def loseGame(self):
        self.powerCoin.visible = False
        self.bombjack.poweredUp = False
        self.enemies.enemyList.clear()
        self.enemies.respawnList.clear()
        self.bombjack.dying = True
        self.lives -= 1

    def checkSpriteEvents(self):
        if self.bombjack.sprites.doneDying:
            self.bombjack.sprites.doneDying = False
            # Don't reset the cherries if we still have lives
            if self.lives > 0:
                self.startGame(cherries=False)
            else:
                # If we are out of lives, set score to zero and level to 0
                self.level = 0
                self.round = 1
                self.updateScore(-self.score)
                self.lives = NUMLIVES
                # Update high score
                self.textgroup.setHighScore()

                self.startGame()
        elif self.bombjack.sprites.doneDancing:
            self.bombjack.sprites.doneDancing = False
            self.startGame()

    def checkCherryEvents(self):
        cherry = self.bombjack.eatCherries(self.cherries.cherryList)
        # The amount to be added to the count for this cherry
        pCount = 0
        if cherry:
            score = 100
            if cherry.isLit or not self.cherries.hasLitCherry:
                if cherry.isLit:
                    score += 100
                    self.cherries.litCount += 1
                    # We double count lit cherries
                    pCount += 1
                self.cherries.updateLitCherry(cherry)
            # Add to the P count only if the P is not currently active or visible
            if not self.bombjack.poweredUp and not self.powerCoin.visible:
                pCount += 1
                self.cherries.numEaten += pCount
            # Update score
            self.updateScore(score)
            self.textgroup.addText(str(score), WHITE, cherry.x -
                                   cherry.collideRadius, cherry.y+6*cherry.collideRadius, 10, time=TEXTTIME)

            self.cherries.cherryList.remove(cherry)
            # Spawn the P if we have eaten enough cherries
            if self.cherries.numEaten >= 20:
                self.cherries.numEaten = 0
                self.powerCoin.visible = True
            # If bomb jack wins
            if self.cherries.isEmpty():
                self.winGame()

    def checkCoinEvents(self):
        # If bombjack collects the P
        if self.powerCoin.visible and self.bombjack.collideCheck(self.powerCoin):
            self.powerCoin.visible = False
            self.bombjack.poweredUp = True
            self.enemy_index = 0
            self.enemies.freeze()

    def checkEnemyEvents(self):
        for i, enemy in enumerate(self.enemies.enemyList):
            if self.bombjack.collideCheck(enemy):
                # If enemy is a coin
                if enemy.frozen:
                    self.enemies.enemyList.pop(i)
                    self.enemies.respawn(enemy)
                    self.updateScore(self.enemy_scores[self.enemy_index])
                    self.textgroup.addText(str(self.enemy_scores[self.enemy_index]), WHITE, enemy.x-enemy.w/2,
                                           enemy.y+5/2*enemy.h, 10, time=TEXTTIME)
                    if self.enemy_index < len(self.enemy_scores)-1:
                        self.enemy_index += 1
                elif not enemy.friendly:
                    self.loseGame()
            # If a mummy touches the ground, make it transform
            if isinstance(enemy, Mummy) and enemy.platform == self.platforms.platList[len(self.platforms.platList)-3]:
                next = enemy.get_next(enemy.x, enemy.y)
                next.friendly = True
                next.safeImage = next.sprites.getImage(3.5, 8)

                # Add new enemy to enemyList
                self.enemies.enemyList[i] = next

    def checkEvents(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            if event.type == KEYDOWN:
                # Allow gliding if bombjack is in mid air
                if event.key == K_UP or event.key == K_SPACE:
                    if self.bombjack.jumped:
                        self.bombjack.gliding = True
                    else:
                        self.bombjack.vy = -GRAV/2
                        self.bombjack.jumped = True
                        self.updateScore(10)

    def render(self):
        self.screen.blit(self.background, (0, 0))
        self.platforms.render(self.screen)
        self.cherries.render(self.screen)
        self.enemies.render(self.screen)
        self.powerCoin.render(self.screen)
        self.bombjack.render(self.screen)

        # Draw grid
        # for i in range(NROWS):
        #     pygame.draw.line(self.screen, WHITE, (0, TILEHEIGHT*i), (SCREENWIDTH, TILEHEIGHT*i))
        # for i in range(NCOLS):
        #     pygame.draw.line(self.screen, WHITE, (TILEWIDTH*i, 0), (TILEWIDTH*i, SCREENHEIGHT))

        self.screen2.fill(BLACK)
        self.screen2.blit(self.screen, (0, 2*TILEHEIGHT))
        self.textgroup.render(self.screen2)
        for i in range(self.lives-1):
            self.screen2.blit(self.livesImage,
                              (i*TILEWIDTH*SPRITEFACTOR, SCREENHEIGHT+2*TILEHEIGHT))
        pygame.display.update()


if __name__ == "__main__":
    game = GameController()
    game.startGame()
    while True:
        game.update()
