import pygame
import sys
import random


WINDOW_WIDTH, WINDOW_HEIGHT = 600, 800

ALFABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
transparent = (255, 255, 255, 128)

pygame.init()

class MainMenu:
    def __init__(self):
        self.SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Main Menu")
        self.background_image = pygame.image.load("./media/background.jpg").convert()
        self.background_image = pygame.transform.scale(self.background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.menu_font = pygame.font.Font("media/font.ttf", 30)
        self.FPS = 60
        # Load custom font

        # Define start button
        self.start_button = pygame.Rect(WINDOW_WIDTH//2 - 100, WINDOW_HEIGHT//2 - 50, 200, 100)

    def run(self):
        while True:
            self.events()
            self.draw()
            pygame.display.update()
            self.clock.tick(self.FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.start_button.collidepoint(mouse_pos):
                        self.start_game()

    def draw(self):
        self.SCREEN.blit(self.background_image, (0, 0))
        start_text = self.menu_font.render("Start Game", True, BLACK)
        text_rect = start_text.get_rect(center=self.start_button.center)

        self.SCREEN.blit(start_text, text_rect)

    def start_game(self):
        # You need to define the Game class somewhere
        game = Game()
        game.newGame()


class Game:
    def __init__(self):
        # Initialize game window
        self.SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Sign 'Em Off")
        background_image = pygame.image.load("./media/background.jpg")
        self.background_image = pygame.transform.scale(background_image, (WINDOW_WIDTH, WINDOW_HEIGHT))
        self.game_font = pygame.font.Font("media/font.ttf", 10)
        # Initialize game clock
        self.CLOCK = pygame.time.Clock()
        self.FPS = 60

        # Foe behavior variables
        self.foe_speed = 2
        self.initial_spawn_interval = 3000
        self.spawn_interval = self.initial_spawn_interval
        self.last_spawn_time = pygame.time.get_ticks()
        self.max_foes = 3

        # Statistics 
        self.missedFoes = 0
        self.fallenFoes = 0
        self.file = open('highscore.txt', 'r')
        self.highscore = int(self.file.read())
        self.file.close()

        # Mouse Interface
        self.mouseClick = False
        self.clickPos = [-100, -100]
        
        # Game state
        self.gameStarted = False
        self.paused = False
        self.explosions = []

    def newGame(self):
        self.sky = Sky()
        self.run()

    def run(self):
        self.running = True
        while self.running:
            self.events()
            self.update()
            self.draw()
            # TODO: 
            # draw_input()
            self.CLOCK.tick(self.FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_interval and len(self.sky.foes) < self.max_foes:
            self.sky.addFoe(self.foe_speed)
            self.last_spawn_time = current_time
            self.spawn_interval = max(self.initial_spawn_interval * 0.9, 500)

        for foe in self.sky.foes:
            foe.update()
            if foe.rect.y + 25 > WINDOW_HEIGHT:
                self.sky.foes.remove(foe)
                self.missedFoes += 1
                if self.missedFoes > self.highscore:
                    self.highscore = self.missedFoes
                explosion = Explosion()
                explosion.center = (foe.rect.centerx, foe.rect.centery - 25)
                self.explosions.append(explosion)

        for explosion in self.explosions:
            explosion.update()

        self.sky.update()

    def draw(self):
        self.SCREEN.blit(self.background_image, (0, 0))
        self.sky.draw(self.SCREEN)
        self.draw_counter()

        for explosion in self.explosions:
            explosion.draw(self.SCREEN)
        pygame.display.flip()

    def draw_counter(self):
        missed_counter = self.game_font.render("Missed Foes: " + str(self.missedFoes), True, BLACK)
        self.SCREEN.blit(missed_counter, (20, 20))

        fallen_counter = self.game_font.render("Fallen Foes: " + str(self.fallenFoes), True, BLACK)
        self.SCREEN.blit(fallen_counter, (20, 50))

        highscore = self.game_font.render("Highscore: " + str(self.highscore), True, BLACK)
        self.SCREEN.blit(highscore, (WINDOW_WIDTH - 140, 20))

    def quit(self):
        pygame.display.quit()
        pygame.quit()
        self.running = False
        self.file = open('highscore.txt', 'w')
        self.file.write(str(self.highscore))
        self.file.close()
        sys.exit()

class Sky:
    def __init__(self):
        self.foes = []
        self.all_sprites = pygame.sprite.Group()

    def addFoe(self, speed):
        letter = random.choice('ALFABET')
        new_foe = Foe(letter, speed)
        new_foe.rect.x = random.randint(50, WINDOW_WIDTH - 50)  # Ensure x coordinate is between 25 and (WINDOW_WIDTH - 25)

        # Add balloons to sprite group
        self.foes.append(new_foe)
        self.all_sprites.add(new_foe)
        # 
        self.all_sprites.add(new_foe.parachute)


    def pop(self, letter):
        for foe in self.all_sprites:
            if foe.letter == letter:
                pygame.sprite.Sprite.kill(foe.parachute)                
                pygame.sprite.Sprite.kill(foe)
                # foes may not be needed
                self.foes.remove(foe)
                self.fallenFoes += 1

    def update(self):
        self.all_sprites.update()

    def draw(self, screen):
        self.all_sprites.draw(screen)

class Foe(pygame.sprite.Sprite):
    def __init__(self, letter, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(f"./media/{letter}.png")
        self.image = pygame.transform.scale(self.image, (80, 90))
        self.letter = letter
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WINDOW_WIDTH-50)
        self.rect.y = -self.rect.height

        self.parachute = Parachute(self.rect.x, self.rect.y)


    def update(self):
        self.rect.y += self.speed
        
        self.parachute.rect.y = self.rect.y - 70 # Update the balloon's position
        self.parachute.rect.x = self.rect.x - 35 # Update the balloon's position

        if self.rect.y > WINDOW_HEIGHT:
            self.has_fallen = True
            self.parachute.kill()
            self.kill()


class Parachute(pygame.sprite.Sprite): # New class for balloons
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("media/parachute.png") # Load balloon image
        self.image = pygame.transform.scale(self.image, (110, 110)) # Scale the balloon image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        pass

class Explosion:
    def __init__(self):
        self.explosion_sequence = [
            pygame.image.load("media/explosion/explosion1.png"),
            pygame.image.load("media/explosion/explosion2.png"),
            pygame.image.load("media/explosion/explosion3.png"),
            pygame.image.load("media/explosion/explosion4.png"),
            pygame.image.load("media/explosion/explosion5.png"),
            pygame.image.load("media/explosion/explosion6.png")
        ]
        self.frame_index = 0
        self.frame_rate = 6
        self.current_tick = 0
        self.image = None
        self.rect = None
        self.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    def update(self):
        self.current_tick += 1
        if self.current_tick % self.frame_rate == 0:
            if self.frame_index < len(self.explosion_sequence):
                self.image = self.explosion_sequence[self.frame_index]
                self.image = pygame.transform.scale(self.image, (100, 100))
                self.frame_index += 1
            else:
                self.image = None

    def draw(self, screen):
        if self.image:
            self.rect = self.image.get_rect(center=self.center)
            screen.blit(self.image, self.rect)

# Start the main menu
menu = MainMenu()
menu.run()

pygame.quit()
sys.exit()
