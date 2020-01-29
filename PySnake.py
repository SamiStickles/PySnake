try:
    import random
    import os
    import sys
    import time
    import pygame
    from pygame.locals import *
except ImportError as err:
    print (f"Could not load module. {err}")
    sys.exit(2)

div = 20
size = 500
tileSize = size // div
fps = pygame.time.Clock()
difficulty = 15
mode = "on"

darkGreen = pygame.Color(50, 168, 82)
green = pygame.Color(35, 112, 56)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
gray = pygame.Color(180, 180, 180)
red = pygame.Color(255, 0, 0)

#problem is that this function is always going to exception??
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# each tail / head piece are segment class instances with their own positions
class Segment():
    def __init__(self, pos):
        self.pos = pos
        self.color = green

    def draw(self, surface, eyes=False):
        xPos = self.pos[0]
        yPos = self.pos[1]

        pygame.draw.rect(surface, self.color, (xPos * tileSize + 1, yPos * tileSize + 1, tileSize - 1, tileSize - 1))
        if eyes:
            radius = 2
            quarter = tileSize // 4
            threeQuarter = quarter * 3

            # changes the eye positions to match the direction the snake is moving
            if snake.dir == 'down':
                leftEye = (xPos * tileSize + quarter + radius, yPos * tileSize + threeQuarter)
                rightEye = (xPos * tileSize + threeQuarter, yPos * tileSize + threeQuarter)
            elif snake.dir == 'right':
                leftEye = (xPos * tileSize + threeQuarter, yPos * tileSize + quarter + radius)
                rightEye = (xPos * tileSize + threeQuarter, yPos * tileSize + threeQuarter)
            elif snake.dir == 'left':
                leftEye = (xPos * tileSize + quarter, yPos * tileSize + threeQuarter)
                rightEye = (xPos * tileSize + quarter, yPos * tileSize + quarter + radius)
            else:
                leftEye = (xPos * tileSize + quarter + radius, yPos * tileSize + quarter)
                rightEye = (xPos * tileSize + threeQuarter, yPos * tileSize + quarter)

            pygame.draw.circle(surface, black, leftEye, radius)
            pygame.draw.circle(surface, black, rightEye, radius)

# only 1 instance of this per game, holds the segment classes in the tail array
class Snake():
    def __init__(self):
        # creates the head instance, starts it in the center of the grid, and adds it to the tail array
        self.head = Segment([10, 10])
        self.tail = []
        self.tail.append(self.head)
        self.dir = 'stop'
        self.dead = False
        self.winner = False
        self.color = green

    # called when the game is replayed to set values back to their initial state
    def reset(self):
        self.head = Segment([10, 10])
        self.tail = []
        self.tail.append(self.head)
        self.dir = 'stop'
        self.dead = False
        self.winner = False

    # loops through each segment in the tail array and calls its draw method
    def draw(self, surface):
        for seg in self.tail:
            if seg == self.tail[0]:
                seg.draw(surface, True)
            else:
                seg.draw(surface)

    # moves the snake by popping off the last segment in the tail array,
    # changing its position to where the head just was,
    # and moving the head in the necessary direction.
    # With this method, only the head and the last tail segment are recalculated each frame
    def move(self, dir):
        lastHeadPos = self.head.pos
        last = self.tail.pop()
        last.pos = [lastHeadPos[0], lastHeadPos[1]]
        self.tail.insert(1, last)

        if dir == 'up':
            self.head.pos[1] -= 1
        if dir == 'down':
            self.head.pos[1] += 1
        if dir == 'left':
            self.head.pos[0] -= 1
        if dir == 'right':
            self.head.pos[0] += 1

    # checks if the snake head has hit its own tail or the wall if walls are on
    def checkDead(self):
        for seg in self.tail:
            if seg == self.head:
                pass
            else:
                if seg.pos[0] == self.head.pos[0] and seg.pos[1] == self.head.pos[1]:
                    self.dead = True
        # if wall mode is on, snake dies when head touches a wall, if not, snake comes out other side of board
        if mode == "on":
            if self.head.pos[0] >= div or self.head.pos[0] < 0 or self.head.pos[1] < 0 or self.head.pos[1] >= div:
                self.dead = True
        else:
            if self.head.pos[0] >= div:
                self.head.pos[0] = 0
            elif self.head.pos[0] < 0:
                self.head.pos[0] = div - 1
            elif self.head.pos[1] >= div:
                self.head.pos[1] = 0
            elif self.head.pos[1] < 0:
                self.head.pos[1] = div - 1

    # checks if the player has won, meaning filled the entire board with tail
    def checkWin(self):
        if len(self.tail) >= div * div:
            self.dead = True
            self.winner = True

    # spawns the fruit in a new location and adds a new tail segment at the end of the tail
    # by finding which direction around the current last tail segment is occupied by another tail
    # (meaning which direction the body is in) and adding a new segment opposite to that position
    def eatFruit(self):
        fruit.spawn()

        # if it is the first tail segment, location is chosen based on the direction of the head instead
        if len(self.tail) == 1:
            if self.dir == 'up':
                firstX = self.head.pos[0]
                firstY = self.head.pos[1] + 1
            elif self.dir == 'down':
                firstX = self.head.pos[0]
                firstY = self.head.pos[1] - 1
            elif self.dir == 'left':
                firstX = self.head.pos[0] + 1
                firstY = self.head.pos[1]
            elif self.dir == 'right':
                firstX = self.head.pos[0] - 1
                firstY = self.head.pos[1]
            self.tail.append(Segment([firstX, firstY]))
        else:
            if self.tail[-1].pos[0] - 1 == self.tail[-2].pos[0]:
                newX = self.tail[-1].pos[0] + 1
                newY = self.tail[-1].pos[1]
            elif self.tail[-1].pos[0] + 1 == self.tail[-2].pos[0]:
                newX = self.tail[-1].pos[0] - 1
                newY = self.tail[-1].pos[1]
            elif self.tail[-1].pos[1] - 1 == self.tail[-2].pos[1]:
                newX = self.tail[-1].pos[0]
                newY = self.tail[-1].pos[1] + 1
            elif self.tail[-1].pos[1] + 1 == self.tail[-2].pos[1]:
                newX = self.tail[-1].pos[0]
                newY = self.tail[-1].pos[1] - 1
            self.tail.append(Segment([newX, newY]))

# only 1 instance per game that is moved to a new random location when the snake head reaches it
class Fruit():
    def __init__(self):
        self.pos = [-1, -1]
        self.color = red

    # spawns the fruit in a new position and makes sure it is not overlapping any part of the snake
    def spawn(self):
        while True:
            flag = False
            self.pos[0] = random.randint(0, div - 1)
            self.pos[1] = random.randint(0, div - 1)
            for seg in snake.tail:
                if seg.pos[0] == self.pos[0] and seg.pos[1] == self.pos[1]:
                    flag = True
            if flag:
                pass
            else:
                break

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.pos[0] * tileSize + 1, self.pos[1] * tileSize + 1, tileSize - 2, tileSize - 2))

# base class to create buttons from
class Button(pygame.sprite.Sprite):
    def __init__(self, text, path):
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        print (resource_path(path))
        #erase print
        self.image = pygame.image.load(resource_path(path)).convert_alpha()
        self.rect = self.image.get_rect()

        pygame.font.init()
        btnFont = pygame.font.Font(None, 30)
        self.btnText = btnFont.render(self.text, True, black)

    def draw(self, surface, pos, textPos):
        surface.blit(self.image, pos)
        surface.blit(self.btnText, textPos)

    def scale(self):
        if self.text == "Start":
            self.image = pygame.transform.scale(self.image, (200, 100))
            self.rect = self.image.get_rect()
        else:
            self.image = pygame.transform.scale(self.image, (150, 75))
            self.rect = self.image.get_rect()

# class for the stars that indicate which option is currently chosen on start menu
class Star(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(resource_path("resources\gold_star.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (50, 50))

    def draw(self, surface, pos):
        surface.blit(self.image, pos)

# updates the display and redraws all objects
def redrawWindow(surface):
    surface.fill((0,0,0))
    drawGrid(surface)
    snake.draw(surface)
    fruit.draw(surface)
    pygame.display.update()

def drawGrid(surface):
    x = 0
    y = 0
    for i in range(div):
        x += tileSize
        y += tileSize
        pygame.draw.line(surface, gray, (x, 0), (x, size))
        pygame.draw.line(surface, gray, (0, y), (size, y))

def main():
    pygame.init()
    pygame.display.set_caption("Snake")
    screen = pygame.display.set_mode((size, size))
    gameStart = False

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill(black)

    # create global instances of the snake and fruit classes and spawn the fruit in its first location
    global snake, fruit
    snake = Snake()
    fruit = Fruit()
    fruit.spawn()

    # messages to be displayed when a win or loss occurs
    smallFont = pygame.font.SysFont("Courier", 20)
    bigFont = pygame.font.SysFont("Courier", 150)
    replayMessage = smallFont.render("Want to play again?", True, white)
    title = bigFont.render("Snake", True, green)
    difLabel = smallFont.render("Difficulty:", True, white)
    modeLabel = smallFont.render("Wall Mode:", True, white)
    quitText = smallFont.render("Quit", True, white)
    replayText = smallFont.render("Replay", True, white)

    # initialize all buttons and stars, not blitted until loop
    easyBtn = Button("Easy", "resources\yellow_button.png")
    medBtn = Button("Medium", "resources\orange_button.png")
    hardBtn = Button("Hard", "resources\hard_button.png")
    wallOnBtn = Button("On", "resources\purple_button.png")
    wallOffBtn = Button("Off", "resources\gray_button.png")
    startBtn = Button("Start", "resources\green_button.png")
    btns = [easyBtn, medBtn, hardBtn, wallOnBtn, wallOffBtn, startBtn]

    global topStar, bottomStar
    topStar = Star()
    bottomStar = Star()

    # positions of all buttons and possible star positions
    easyPos = (10, 200)
    medPos = (175, 200)
    hardPos = (340, 200)
    wallOnPos = (85, 315)
    wallOffPos = (260, 315)

    starPosEasy = (60, 185)
    starPosMed = (225, 185)
    starPosHard = (390, 185)
    starPosWallOn = (135, 300)
    starPosWallOff = (310, 300)
    
    # start screen loop, infinite until broken by press of the start button
    # difficulty and wall mode sliders are set to defaults and do not break loop
    clickedDif = False
    clickedMode = False

    while not gameStart:

        screen.fill((0, 0, 0))
        global difficulty, mode

        # scale then blit all buttons and their text to screen with draw function
        for btn in btns:
            btn.scale()

        easyBtn.draw(screen, easyPos, (easyPos[0] + 50, easyPos[1] + 30))
        easyBtn.rect.move_ip(easyPos)

        medBtn.draw(screen, medPos, (medPos[0] + 40, medPos[1] + 30))
        medBtn.rect.move_ip(medPos)

        hardBtn.draw(screen, hardPos, (hardPos[0] + 50, hardPos[1] + 30))
        hardBtn.rect.move_ip(hardPos)

        wallOnBtn.draw(screen, (wallOnPos), (wallOnPos[0] + 60, wallOnPos[1] + 30))
        wallOnBtn.rect.move_ip(wallOnPos)

        wallOffBtn.draw(screen, wallOffPos, (wallOffPos[0] + 60, wallOffPos[1] + 30))
        wallOffBtn.rect.move_ip(wallOffPos)

        startBtn.draw(screen, (150, 400), (225, 440))
        startBtn.rect.move_ip(150, 400)

        # blit title and choice labels after buttons so they are never covered up
        screen.blit(title, (30, 0))
        screen.blit(difLabel, (185, 165))
        screen.blit(modeLabel, (195, 295))

        # if user hasn't selected a difficulty, default to medium and draw star over med button
        # once a button is clicked, this changes to true and the else statement is entered
        if clickedDif == False:
            topStar.draw(screen, starPosMed)
        else:
            if difficulty == 10:
                topStar.draw(screen, starPosEasy)
            elif difficulty == 15:
                topStar.draw(screen, starPosMed)
            elif difficulty == 20:
                topStar.draw(screen, starPosHard)

        if clickedMode == False:
            bottomStar.draw(screen, starPosWallOn)
        else:
            if mode == "on":
                bottomStar.draw(screen, starPosWallOn)
            elif mode == "off":
                bottomStar.draw(screen, starPosWallOff)

        # loops through event queue and once a mouse click is detected, checks if it was on a button
        # then changes the difficulty or mode and sets the clicked variable to True to turn off the default
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouseX, mouseY = event.pos
                for btn in btns:
                    if btn.rect.collidepoint(mouseX, mouseY):
                        if btn.text == "Start":
                            gameStart = True
                        else:
                            if btn.text == "Easy":
                                difficulty = 10
                                clickedDif = True
                            elif btn.text == "Medium":
                                difficulty = 15
                                clickedDif = True
                            elif btn.text == "Hard":
                                difficulty = 20
                                clickedDif = True
                            elif btn.text == "On":
                                mode = "on"
                                clickedMode = True
                            elif btn.text == "Off":
                                mode = "off"
                                clickedMode = True
        pygame.display.flip()

    # restart game from here
    while True:
        # main game loop, infinite until broken by win, loss or quit
        while True:
            # controlls the speed of the game
            fps.tick(difficulty)
            pygame.display.set_caption(f"Snake!   Score: {len(snake.tail) - 1}")

            # moved these from main list of messages because the score needs to be updated each frame
            winMessage = smallFont.render(f"You won, amazing! Score: {len(snake.tail) - 1}", True, red)
            deadMessage = smallFont.render(f"You died! Score: {len(snake.tail) - 1}", True, white)

            # changed this from using get_pressed so it will be responsive at low fps (difficulty)
            # loops through all events and changes snake direction, snake will be physically moved in snake.move
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        snake.dir = 'up'
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        snake.dir = 'right'
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        snake.dir = 'down'
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        snake.dir = 'left'

            # moves the snake in its direction until another key is pressed that changes it
            snake.move(snake.dir)
            snake.checkDead()
            snake.checkWin()

            if not snake.dead:
                # if the snake head reaches the fruit, respawn it and add a tail segment, then updates screen
                if snake.head.pos[0] == fruit.pos[0] and snake.head.pos[1] == fruit.pos[1]:
                    snake.eatFruit()
                redrawWindow(screen)
            else:
                break

        # end game loop, broken by replay or quit
        replay = False
        while not replay:
            # draws the end game window
            pygame.draw.rect(screen, black, (75, 75, 350, 350))
            pygame.draw.rect(screen, green, (75, 75, 350, 350), 3)

            # blits the text to the window
            screen.blit(replayMessage, (135, 250))
            if snake.winner == True:
                screen.blit(winMessage, (135, 130))
            else:
                screen.blit(deadMessage, (135, 130))

            # draws the buttons on the end game window
            quitBtn = pygame.Rect(270, 300, 100, 50)
            replayBtn = pygame.Rect(125, 300, 100, 50)

            pygame.draw.rect(screen, white, replayBtn, 1)
            pygame.draw.rect(screen, white, quitBtn, 1)

            # blits the text to the buttons
            screen.blit(quitText, (295, 313))
            screen.blit(replayText, (138, 313))

            # waits for quit or replay selection, then resets the snake and respawns fruit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouseX, mouseY = event.pos
                    if quitBtn.collidepoint(mouseX, mouseY):
                        return
                    elif replayBtn.collidepoint(mouseX, mouseY):
                        replay = True
                        snake.reset()
                        fruit.spawn()
                        redrawWindow(screen)
            pygame.display.flip()

if __name__ == '__main__': main()