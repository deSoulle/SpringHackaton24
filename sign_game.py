import pygame
import sys
import random
import pygame
import sys
import random
import pickle
import cv2
import mediapipe as mp
import numpy as np
import pickle
from time import sleep

WINDOW_WIDTH, WINDOW_HEIGHT = 600, 800

ALFABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

BLACK = (0, 0, 0)

MISSES_LIMIT = 10
INITIAL_SPAWN_INTERVAL = 3000

model_dict = pickle.load(open('./gandsigns/model.p', 'rb'))
model = model_dict['model']
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.80)

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
        self.start_button = pygame.Rect(WINDOW_WIDTH // 2 - 100, WINDOW_HEIGHT // 2 - 50, 200, 100)

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
        game.startGame()


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
        self.foe_speed = 3
        self.spawn_interval = INITIAL_SPAWN_INTERVAL
        self.last_spawn_time = pygame.time.get_ticks()

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
        self.level = 0 #CARALHO

    def startGame(self):
        self.sky = Sky()
        self.next_level() # get to first level
        self.run()

    def run(self):
        self.running = True
        while self.running:
            self.events()
            self.update()
            ret, frame = cap.read()
            input_sign = getSign(frame)
            if self.sky.pop(input_sign):
                self.fallenFoes += 1
            # Pass frame to getSign function
            self.draw()
            #TODO:
            #draw_input
            self.CLOCK.tick(self.FPS)

    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()

    def update(self):
        current_time = pygame.time.get_ticks()

        # Game over if missedFoes exceeds MISSES_LIMIT
        if self.missedFoes >= MISSES_LIMIT:
            self.game_over_screen()

        # Spawning foes
        # They stop when interval is 1 second, and then for a clean screen to skip level
        if current_time - self.last_spawn_time > self.spawn_interval and self.spawn_interval > 1000:
            self.sky.addFoe(self.foe_speed, self.level)
            self.last_spawn_time = current_time
            self.spawn_interval -= 200
        if self.spawn_interval <= 1000 and len(self.sky.foes) == 0:
            self.next_level()

        for foe in self.sky.foes:
            foe.update()
            if foe.rect.y + 25 > WINDOW_HEIGHT:
                self.sky.foes.remove(foe)
                self.missedFoes += 1
                if self.fallenFoes > self.highscore:
                    self.highscore = self.fallenFoes
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

    def next_level(self):
        self.level += 1
        self.spawn_interval = INITIAL_SPAWN_INTERVAL + self.level*500
        self.level_tutorial()

    def display_letter(self, letter):
        letter_sign = pygame.image.load(f"./media/{letter}.png")
        letter_sign = pygame.transform.scale(letter_sign, (80, 90))
        letter_character = pygame.image.load(f"./media/letters/{letter}{letter}.png")
        letter_character = pygame.transform.scale(letter_character, (80, 90))
        self.SCREEN.blit(letter_sign, (
            WINDOW_WIDTH // 2 - letter_sign.get_width() // 2, WINDOW_HEIGHT * 1 / 4 - letter_sign.get_height() // 2))
        self.SCREEN.blit(letter_character, (WINDOW_WIDTH // 2 - letter_character.get_width() // 2,
                                            WINDOW_HEIGHT // 2 - letter_character.get_height() // 2 + 100))
        pygame.display.flip()

    def level_tutorial(self):
        self.SCREEN.fill(BLACK)

        for letter in ALFABET[0:self.level * 4]:
            # Display letter character and sign
            self.display_letter(letter)

            # Wait for user to get it right
            while True:
                ret, frame = cap.read()
                input_sign = getSign(frame)
                if input_sign == letter:
                    # Change background to green
                    pygame.draw.rect(self.SCREEN, (0, 255, 0), (0, 0, WINDOW_WIDTH, WINDOW_HEIGHT), 10)
                    self.display_letter(letter)
                    pygame.display.flip()
                    sleep(0.5)
                    break

                self.events()  # must keep running

            # Clean screen
            self.SCREEN.fill(BLACK)

    def game_over_screen(self):
        game_over = self.game_font.render("Game Over! Try Again", True, BLACK)
        game_over = pygame.transform.scale(game_over, (400, 400))
        self.SCREEN.blit(game_over, (WINDOW_WIDTH // 2 - game_over.get_width() // 2, WINDOW_HEIGHT // 2 - game_over.get_height() // 2))
        pygame.display.flip()
        pygame.time.wait(3000)
        self.quit()

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

    def addFoe(self, speed, level):
        letter = random.choice(ALFABET[0:level*4]) # 4 more leters each level
        new_foe = Foe(letter, speed)
        new_foe.rect.x = random.randint(50,
                                        WINDOW_WIDTH - 50)  # Ensure x coordinate is between 25 and (WINDOW_WIDTH - 25)

        # Add balloons to sprite group
        self.foes.append(new_foe)
        self.all_sprites.add(new_foe)
        self.all_sprites.add(new_foe.parachute)

    def pop(self, letter):
        for foe in self.foes:
            if foe.letter == letter:
                foe.parachute.kill()
                foe.kill()

                # foes may not be needed
                self.foes.remove(foe)

                return True
            
        return False
    
    def update(self):
        self.all_sprites.update()

    def draw(self, screen):
        self.all_sprites.draw(screen)


class Foe(pygame.sprite.Sprite):
    def __init__(self, letter, speed):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(f"./media/letters/{letter}{letter}.png")
        self.image = pygame.transform.scale(self.image, (80, 90))
        self.letter = letter
        self.speed = speed
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(50, WINDOW_WIDTH - 50)
        self.rect.y = -self.rect.height

        self.parachute = Parachute(self.rect.x, self.rect.y)

    def update(self):
        self.rect.y += self.speed

        self.parachute.rect.y = self.rect.y - 70  # Update the balloon's position
        self.parachute.rect.x = self.rect.x - 35  # Update the balloon's position

        if self.rect.y > WINDOW_HEIGHT:
            self.has_fallen = True
            self.parachute.kill()
            self.kill()


class Parachute(pygame.sprite.Sprite):  # New class for balloons
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("media/parachute.png")  # Load balloon image
        self.image = pygame.transform.scale(self.image, (110, 110))  # Scale the balloon image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y



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
        self.image = None
        self.rect = None
        self.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

    def update(self):
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

def getSign(frame):
    ret, frame = cap.read()

    labels_dict = {
        0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J',
        10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S',
        19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z'
    }

    H, W, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )

        data_aux = []
        x_ = []
        y_ = []

        for hand_landmarks in results.multi_hand_landmarks:
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y

                x_.append(x)
                y_.append(y)

            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))

        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10

        x2 = int(max(x_) * W) - 10
        y2 = int(max(y_) * H) - 10

        try:
            prediction = model.predict([np.asarray(data_aux)])

            predicted_character = labels_dict[int(prediction[0])]

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
            cv2.putText(frame, predicted_character, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3,
                        cv2.LINE_AA)

            prediction_proba = max(max(model.predict_proba([np.asarray(data_aux)])))
            if prediction_proba > 0.10:
                # Print prediction and metrics
                print("Predicted Character:", predicted_character)
                print("Prediction Probability:", prediction_proba)
                return predicted_character

            return None
        except Exception as e:
            print("hello")
            return None

# Start the main menu
menu = MainMenu()
menu.run()

pygame.quit()
sys.exit()
