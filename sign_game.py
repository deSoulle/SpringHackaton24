import pygame
import sys
import random

WINDOW_WIDTH, WINDOW_HEIGHT = 600, 800


BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255 , 0)
BLUE = (0, 0, 255)

pygame.init()


# game system class
class Game:
    def __init__(self):
        self.SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sign 'Em Off")

        # Load the background image
        background_image = pygame.image.load("media/background.jpg")
        self.background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.SCREEN.blit(background_image, (0, 0))

        self.CLOCK = pygame.time.Clock()
        self.FPS = 60

        self.foe_speed = 1
        self.spawn_interval = 5000
        self.missedFoes = 0
        self.killedFoes = 0
        # Mouse may not be needed if no menu is implemented
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        self.mouseClick = False
        self.clickPos = [-100, -100]
        # Same goes for the highscore file
        self.file = open('highscore.txt', 'r')
        self.highscore = int(self.file.read())
        self.file.close()
        self.gameStarted = False
        self.paused = False
    
    def newGame(self): 
        self.sky = Sky()

        self.run()
    
    def run(self):
        self.running = True
        while self.running:
            self.events() # handle events
            self.update()
            self.draw()
            self.CLOCK.tick(self.FPS)

    def events(self):
        for event in pygame.event.get():
                match event:
                    case pygame.QUIT: 
                        self.quit()
                    #case pygame.SIGN: # special USEREVENT for hand sign language inputs
                        #Sky.pop(letter) #  need to get letter from event


    # move foes and add more foes to sky, increasse speed of new foes (?)
    def update(self):


        # move foes and check positons
        for foe in self.sky.foes:
            foe.update()
            if foe.rect.y > WINDOW_HEIGHT:
                self.sky.foes.remove(foe)
                self.missedFoes += 1
                if self.missedFoes > self.highscore:
                    self.highscore = self.missedFoes    
        # add new foes
        self.sky.addFoe(self.foe_speed)
        self.sky.update()

    def draw(self):

        self.SCREEN.blit(self.background_image, (0, 0))
        self.sky.draw(self.SCREEN)
        pygame.display.flip()

    def quit(self): 
        pygame.display.quit()   
        pygame.quit()
        self.running = False
        self.file = open('highscore.txt', 'w')
        self.file.write(str(self.highscore))
        self.file.close()
        sys.exit()
        
# game envrioment class meter no Game
class Sky:
    def __init__(self):
        self.foes = []
        self.all_sprites = pygame.sprite.Group()

    def addFoe(self, speed):
        letter = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        new_foe = Foe(letter, speed)
        self.foes.append(new_foe)
        self.all_sprites.add(new_foe)


    def pop(self, letter):
        for foe in self.foes:
            if foe.letter == letter:
                pygame.sprite.Sprite.kill(foe)
                self.killedFoes += 1

    def update(self):
        self.all_sprites.update()


    def draw(self, screen):
        self.all_sprites.draw(screen)

    
# Target class
class Foe(pygame.sprite.Sprite):
    def __init__(self, letter, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("media/foe.jpg")
       
        self.letter = letter
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WINDOW_WIDTH)
        self.rect.y = -self.rect.height

    def update(self):
        self.rect.y += self.speed
         # foe y-pos reached the bottom of the screen    
        if self.rect.y > WINDOW_HEIGHT:
            pygame.sprite.Sprite.kill(self)
            self.missedFoes += 1
    

game = Game()
game.newGame()


pygame.quit()
sys.exit()
