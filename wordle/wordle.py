import pygame
import random

def get_words():
    with open("data/valid_words.txt", "r") as file:
        return file.read().split()

def get_answers():
    with open("data/answer_words.txt", "r") as file:
        return file.read().split()

def choose_answer():
    return random.choice(get_answers())

def get_letters_in_word(word):
    letter_counts = {}
    for c in word:
        letter_counts[c] = letter_counts.get(c, 0) + 1
    return letter_counts

WORDS = get_words()

WIDTH = 425
HEIGHT = 550

MSG_INVALID = "Invalid word!"
MSG_LENGTH = "Word must be 5 letters!"
MSG_WIN = "You got it!"
MSG_LOSE = lambda word: f"The word was: {word.upper()}"

class Text(pygame.sprite.Sprite):

    def __init__(self, center, font_size, text="", font="Consolas"):
        super().__init__()
        self.font = pygame.font.SysFont(font, font_size)
        self.text = text
        self.center = center

        self.image = self.font.render(text, True, "White")
        self.rect = self.image.get_rect(center=center)

    def reload(self):
        self.image = self.font.render(self.text, True, "White")
        self.rect = self.image.get_rect(center=self.center)

    def update(self):
        self.reload()

    def change_text(self, text=""):
        self.text = text

class Cell(pygame.sprite.Sprite):

    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.letter = ""
        self.color = "empty"

        self.image = pygame.image.load(f"graphics/empty_cell.png").convert()
        self.rect = self.image.get_rect(topleft=(x, y))

        self.text = pygame.sprite.GroupSingle()
        self.text.add(Text((self.rect.width / 2, self.rect.height / 2 + 4), 60))

    def reload(self):
        self.image = pygame.image.load(f"graphics/{self.color}_cell.png").convert()
        self.rect = self.image.get_rect(topleft=(self.x, self.y))
        self.text.draw(self.image)

    def update(self):
        self.reload()
        self.text.update()

    def set_cell_text(self, text=""):
        self.text.sprite.change_text(text)
        self.letter = text

    def set_cell_color(self, color=None):
        if color == None:
            self.color = "empty"
        elif color in ("gray", "yellow", "green"):
            self.color = color
        else:
            print("invalid color")
        self.update()

class Message(pygame.sprite.Sprite):

    def __init__(self, msg, fade):
        super().__init__()
        self.font = pygame.font.SysFont("Consolas", 25)
        self.fade = fade
        self.alpha = 255

        self.image = self.font.render(msg, True, "White")
        self.rect = self.image.get_rect(center=(WIDTH/2, 520))

    def update(self):
        self.apply_fade()
        self.destroy()

    def apply_fade(self):
        if self.alpha > 0 and self.fade:
            self.alpha -= 2
        self.image.set_alpha(self.alpha)

    def destroy(self):
        if self.alpha < 0:
            self.kill()

class TitleScene():

    def __init__(self):
        self.next = self

        self.titles = pygame.sprite.Group()
        self.titles.add(Text((WIDTH/2, 215), 100, "Wordle", "Rockwell"))
        self.titles.add(Text((WIDTH/2, 285), 25, "Press SPACE to play"))
        self.titles.add(Text((WIDTH/2, 320), 25, "Pres ESCAPE to restart"))

        self.snd_start = pygame.mixer.Sound("audio/start.wav")
        self.snd_start.set_volume(0.1)

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.switch_to_scene(GameScene())
                    self.snd_start.play()

    def render(self, surface):
        surface.fill("Black")
        self.titles.draw(surface)
        self.titles.update()

    def switch_to_scene(self, scene):
        self.next = scene

class GameScene():

    def __init__(self):
        self.next = self

        self.messages = pygame.sprite.GroupSingle()
        self.cells = pygame.sprite.Group()
        for r in range(6):
            for c in range(5):
                self.cells.add(Cell(80 * c + 15, 80 * r + 15))

        self.snd_restart = pygame.mixer.Sound("audio/restart.wav")
        self.snd_restart.set_volume(0.2)
        self.snd_button = pygame.mixer.Sound("audio/button.wav")
        self.snd_button.set_volume(0.2)
        self.snd_win = pygame.mixer.Sound("audio/win.wav")
        self.snd_win.set_volume(0.2)
        self.snd_lose = pygame.mixer.Sound("audio/lose.wav")
        self.snd_lose.set_volume(0.2)

        self.answer = choose_answer()
        self.grid = self.cells.sprites()
        self.guess = ""
        self.count = 0
        self.active = True

        print(f"\nAnswer: {self.answer.upper()}")

    def process_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switch_to_scene(TitleScene())
                    self.snd_restart.play()

                if self.active:
                    if event.key == pygame.K_BACKSPACE and len(self.guess) > 0:
                        self.guess = self.guess[:-1]
                        self.snd_button.play()
                        
                    elif event.key == pygame.K_RETURN:
                        self.check_guess()
                        self.snd_button.play()

                    elif event.unicode.isalpha() and len(self.guess) < 5:
                        self.guess += event.unicode.upper()
                        self.snd_button.play()

                    self.reload_grid()

    def render(self, surface):
        surface.fill("Black")
        self.cells.draw(surface)
        self.cells.update()
        self.messages.draw(surface)
        self.messages.update()

    def switch_to_scene(self, scene):
        self.next = scene

    def reload_grid(self):
        for i in range(5):
            if i <= len(self.guess) - 1: 
                self.grid[self.count * 5 + i].set_cell_text(self.guess[i])
            else:
                self.grid[self.count * 5 + i].set_cell_text()

    def check_guess(self):
        if len(self.guess) != 5:
            self.messages.add(Message(MSG_LENGTH, True))
            self.snd_lose.play()

        elif self.guess.lower() not in WORDS:
            self.messages.add(Message(MSG_INVALID, True))
            self.snd_lose.play()

        else:
            self.check_letters()

            if self.count == 5:
                self.messages.add(Message(MSG_LOSE(self.answer), False))
                self.active = False
                self.snd_lose.play()

            elif self.guess.lower() == self.answer:
                self.messages.add(Message(MSG_WIN, False))
                self.active = False
                self.snd_win.play()

            else:
                self.guess = ""
                self.count += 1

    def check_letters(self):
        answer_letters = get_letters_in_word(self.answer)

        for j in range(3):
            for i in range(5):
                cell = self.grid[self.count * 5 + i]
                letter = cell.letter.lower()

                if j == 0:
                    if letter == self.answer[i]:
                        cell.set_cell_color("green")
                        answer_letters[letter] -= 1
                
                elif j == 1:
                    if letter in self.answer and answer_letters[letter] > 0 and cell.color != "green":
                        cell.set_cell_color("yellow")
                        answer_letters[letter] -= 1
                
                else:
                    if cell.color == "empty":
                        cell.set_cell_color("gray")

pygame.init()

def main():
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    scene = TitleScene()

    pygame.display.set_caption("Wordle")

    while True:
        scene.process_input()
        scene.render(screen)
        scene = scene.next

        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()
