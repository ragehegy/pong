# pong!
import random
from time import sleep
from network import Network

import pygame

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

scorep1 = 0
scorep2 = 0

class Player:
    width = 10
    height = 50

    def __init__(self, startx, starty, move_dir=0, color=(255,100,0)) -> None:
        self.x = startx
        self.y = starty

        self.width, self.height = (10, 50) if move_dir == 0 else (50, 10)

        self.velocity = 10
        self.move_dir = move_dir
        self.color = color

    def draw(self, g):
        pygame.draw.rect(g, self.color ,(self.x, self.y, self.width, self.height), 0)

    def move(self, direction):
        if self.move_dir == 0:
            if direction == 0 and self.y + self.velocity > 10:
                self.y -= self.velocity
            elif direction == 1 and self.y + self.height < 500:
                self.y += self.velocity
        if self.move_dir == 1:
            if direction == 2:
                self.x += self.velocity
            elif direction == 3:
                self.x -= self.velocity

class Ball:
    dbo = 'right'
    dbv = 'up'

    def __init__(self, startx, starty, color=(255,100,0)) -> None:
        self.x = startx
        self.y = starty
        self.velocity = 5
        self.color = color

    def draw(self, g):
        pygame.draw.ellipse(g, self.color, (self.x, self.y, 10, 10))

    def move(self):
        if self.dbo == "left":
            self.x -= self.velocity
        if self.dbv == 'down':
            self.y += self.velocity
            if self.y > 490:
                self.dbv = 'up'
        if self.dbv == 'up':
            self.y -= self.velocity
            if self.y < 10:
                self.dbv = 'down'
        if self.dbo == "right":
            self.x += self.velocity

    def collide(self, players: [Player]=[]) -> None:
        global scorep1, scorep2    
        
        for player in players:
            if player.move_dir == 0:
                if self.dbo == "left":
                    if self.x < 10:
                        if self.y >= player.y and  self.y < player.y + player.height:
                            self.dbo = "right"
                        else:
                            self.x, self.y = 300, random.randint(0, 300)
                            scorep2 += 10
                            pygame.display.set_caption("My game" + "Score player 1: " + str(scorep1) + " - Score player 2: " + str(scorep2))
                else:
                    if self.x > 490:
                        if self.y >= player.y and  self.y < player.y + player.height:
                            self.dbo = "left"		
                        else:
                            self.x, self.y = 300, random.randint(0, 300)
                            scorep1 += 10
                            pygame.display.set_caption("My game" + "Score player 1: " + str(scorep1) + " - Score player 2: " + str(scorep2))

            elif player.move_dir == 1:
                if self.dbv == "up":
                    if self.y < 10:
                        if self.x >= player.x and  self.x < player.x + player.width:
                            self.dbv = "down"
                        else:
                            self.x, self.y = random.randint(0, 300), 300
                            scorep2 += 10
                            pygame.display.set_caption("My game" + "Score player 1: " + str(scorep1) + " - Score player 2: " + str(scorep2))
                else:
                    if self.y >= 490:
                        if self.x >= player.x and  self.x < player.x + player.width:
                            self.dbv = "up"
                        else:
                            self.x, self.y = random.randint(0, 300), 300
                            scorep1 += 10
                            pygame.display.set_caption("My game" + "Score player 1: " + str(scorep1) + " - Score player 2: " + str(scorep2))

class Game:
    def __init__(self, width, height, players=2) -> None:
        self.net = Network()
        self.width = width
        self.height = height
        self.players = players

        self.ball = Ball(300, 300)

        self.client = self.net.connect().split(":")
        self.net.id = self.client[0]

        pos = tuple([int(x) for x in self.client[1].split(",")])
        print("init pos: ", pos)
        self.player = Player(pos[0], pos[1], int(int(self.net.id)>2))

        self.other_players = [
            Player(490, 235),
            Player(0, 235),
            Player(235, 490, 1),
            Player(235, 0, 1)
        ]

        # self.player2 = Player(0, 235)

        # self.player3 = Player(235, 490, 1)
        # self.player4 = Player(235, 0, 1)

        self.canvas = Canvas(self.width, self.height, "Testing...")

    def run(self) -> None:
        clock = pygame.time.Clock()
        run = True

        while run:
            clock.tick(30)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if event.type == pygame.K_ESCAPE:
                    run = False

            keys = pygame.key.get_pressed()

            if keys[pygame.K_UP]:
                # if self.player.x <= self.player.velocity:
                self.player.move(0)

            if keys[pygame.K_DOWN]:
                # if self.player.x <= self.width - self.player.velocity:
                self.player.move(1)

            if keys[pygame.K_RIGHT]:
                # if self.player.x <= self.width - self.player.velocity:
                self.player.move(2)

            if keys[pygame.K_LEFT]:
                if self.player.x >= self.player.velocity:
                    self.player.move(3)

            data = self.send_data()
            if data == "False":
                print("Waiting...")
                continue

            oplayers = self.parse_data(data)
            if oplayers:
                for i, oplayer in enumerate(oplayers):
                    try:
                        self.other_players[i].x = int(oplayer[0])
                        self.other_players[i].y = int(oplayer[1])
                    except:
                        continue
                    
            self.canvas.draw_background()

            self.player.draw(self.canvas.get_canvas())
            for oplayer in self.other_players:
                oplayer.draw(self.canvas.get_canvas())
            # self.player2.draw(self.canvas.get_canvas())
            # self.player3.draw(self.canvas.get_canvas())
            # self.player4.draw(self.canvas.get_canvas())

            self.ball.draw(self.canvas.get_canvas())

            self.ball.move()
            self.ball.collide([self.player, *self.other_players])

            self.canvas.update()

    def send_data(self):
        data = str(self.net.id) + ":" + str(self.player.x) + "," + str(self.player.y)
        reply = self.net.send(data)
        return reply

    @staticmethod
    def parse_data(data):
        pos = data.split("-")
        try:
            pos = list(map(lambda x: x.split(":")[1].split(","), pos))
            return pos
        except:
            return None

class Canvas:
    def __init__(self, width, height, name=None) -> None:
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width,height))
        pygame.display.set_caption(name)

    @staticmethod
    def update():
        pygame.display.update()

    def draw_text(self, text, size, x, y):
        pygame.font.init()
        font = pygame.font.SysFont("comicsans", size)
        render = font.render(text, 1, (0,0,0))

        self.screen.draw(render, (x,y))

    def get_canvas(self):
        return self.screen

    def draw_background(self):
        self.screen.fill((255,255,255))