# import the pygame module, so you can use it
import pygame
import random
from pygame.math import Vector2
import socket, select
import time
import math

WHITE = (255, 255, 255)
LOCAL_DEBUG = True
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(pygame.Color(255, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

# Stores data about the game
# - Connection to server
# - Camera position within level
# - Update speed
# Also stores data about the world
# The following information should be in here:
# - Location of all objects within this world including player characters.
# - When loading a world, the sprites might be preloaded into memory to reduce
#    memory access while updating sprite sizes etc.
# - Width and height in the world

class Game:
    def __init__(self):
        self.screen = None;
        self.client_socket = None;
        self.camera_pos = Vector2(20, 20)
        self.width = 5000
        self.height = 5000
        self.active_player = None
        self.objects = []
        self.all_sprites_list = []

    def draw(self):
        self.active_player.draw(screen)
        self.all_sprites_list.draw(screen)


class Player(pygame.sprite.Sprite):
    def __init__(self, screen, walls):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # You start without score (small)
        self.x = 20
        self.y = 20
        self.score = 0
        self.max_speed = 2.5
        self.speed = self.max_speed

        self.image = pygame.Surface([30, 30])
        self.image = pygame.image.load("LUL.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (30, 30))

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen = screen
        self.velocity = Vector2(0, 0)
        self.walls = walls

        self.prev_x = 0
        self.prev_y = 0
        self.prev_score = 0

        self.otherplayers = {}

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        self.velocity.x = round(0.93 * self.velocity.x)
        self.velocity.y = round(0.93 * self.velocity.y)
        if self.velocity.x != 0:
            self.velocity.x -= self.velocity.x / abs(self.velocity.x)
        if self.velocity.y != 0:
            self.velocity.y -= self.velocity.y / abs(self.velocity.y)

        self.player_collision()

        collision = self.wall_collisions()
        if collision:
            self.die()


    def updateKeys(self, keys):
        if keys[pygame.K_LEFT]:
            self.velocity.x += -self.speed
        if keys[pygame.K_RIGHT]:
            self.velocity.x += self.speed
        if keys[pygame.K_UP]:
            self.velocity.y += -self.speed
        if keys[pygame.K_DOWN]:
            self.velocity.y += self.speed
        if keys[pygame.K_w]:
            self.eatSomething(5)


    def wall_collisions(self):
        for wall in self.walls:
            if(pygame.sprite.collide_rect(self, wall)):
                 return True
        return False

    def die(self):
        self.score = 0
        self.rect.x = random.randint(50, SCREEN_WIDTH - 50)
        self.rect.y = random.randint(50, SCREEN_HEIGHT - 50)
        self.speed = self.max_speed
        self.updateSprite()

    def player_collision(self):
        for id in self.otherplayers:
            if pygame.sprite.collide_rect(self, self.otherplayers[id]):
                if self.image.get_width() - self.otherplayers[id].image.get_width() > 3:
                    self.eatSomething(self.otherplayers[id].score)
                    return
                elif self.image.get_width() - self.otherplayers[id].image.get_width() < -3:
                    self.die()

    def eatSomething(self, amount):
        self.score += amount
        self.updateSprite()

    def updateSprite(self):
        move_amount = (math.ceil(30 + math.sqrt(self.score)) - self.image.get_width()) // 2 + 1
        # Update image size.
        self.image = pygame.image.load("LUL.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (int(30 + math.sqrt(self.score)), int(30 + math.sqrt(self.score))))
        # Update rectangle
        self.rect = self.image.get_rect(center=(self.rect.x + self.rect.width//2, self.rect.y + self.rect.height//2))

    def hasUpdated(self):
        if self.rect.x == self.prev_x and self.rect.y == self.prev_y and self.score == self.prev_score:
            return False
        else:
            self.prev_x = self.rect.x
            self.prev_y = self.rect.y
            self.prev_score = self.score
            return True

    def setNewStats(self, x, y, score):
        self.rect.x = x
        self.rect.y = y
        self.score = score
        self.updateSprite()

    def getData(self):
        return str(self.rect.x) + ":" + str(self.rect.y) + ":" + str(self.score) + ";"


def main():
    # initialize the pygame module
    pygame.init()
    # load and set the logo
    logo = pygame.image.load("LUL.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # define a variable to control the main loop
    running = True


    all_sprites_list = pygame.sprite.Group()
    walls = pygame.sprite.Group()

    wall = Wall(0, 0, 10, SCREEN_HEIGHT)
    wall2 = Wall(SCREEN_WIDTH - 10, 0, 10, SCREEN_HEIGHT)
    wall3 = Wall(0, 0, SCREEN_WIDTH, 10)
    wall4 = Wall(0, SCREEN_HEIGHT - 10, SCREEN_WIDTH, 10)
    walls.add(wall, wall2, wall3, wall4)
    all_sprites_list.add(wall, wall2, wall3, wall4)

    player = Player(screen, walls)
    # all_sprites_list.add(player)

    clock = pygame.time.Clock()

    if not LOCAL_DEBUG:
        # Connect to server
        # HOST = '217.101.168.167'
        HOST = 'localhost';
        PORT = 25565
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((HOST, PORT))
        except Exception as e:
            print("Cannot connect to the server:", e)
        print("Connected")

    # main loop
    while running:
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                if not LOCAL_DEBUG:
                    client_socket.close()

                running = False

        # Handle keys
        keys = pygame.key.get_pressed()
        player.updateKeys(keys)

        # socket logic update players
        if not LOCAL_DEBUG:
            if player.hasUpdated():
                client_socket.send((player.getData()).encode())

            read_sockets, write_sockets, error_sockets = select.select([client_socket], [], [], 0.01)
            for sock in read_sockets:
                for data in sock.recv(4096).decode().split(";"):
                    if not data:
                        break

                    if data.startswith("msg"):
                        player.otherplayers[data.split(":")[1]] = None
                        print(data.split(":")[2])
                        break

                    print(data)

                    port, x, y, score = data.split(":")
                    if port not in player.otherplayers:
                        p = Player(screen, walls)
                        all_sprites_list.add(p)
                        player.otherplayers[port] = p
                    player.otherplayers[port].setNewStats(int(x), int(y), int(score))

        all_sprites_list.update()

        # Clear screen
        pygame.draw.rect(screen, pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw all sprites in the group of sprites
        player.draw(screen)
        all_sprites_list.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()
