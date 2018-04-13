# import the pygame module, so you can use it
import pygame
from pygame.math import Vector2
import socket, select
import time
import math

WHITE = (255, 255, 255)
LOCAL_DEBUG = False
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(pygame.Color(255, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))

class Player(pygame.sprite.Sprite):
    def __init__(self, screen, walls):
        # Call the parent class (Sprite) constructor
        super().__init__()

        # You start without score (small)
        self.score = 0

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

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color(255, 0, 0, 128), self.rect)

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y

        self.player_collision()

        collision = self.wall_collisions()
        if collision:
            self.die()
            # self.rect.x -= self.velocity.x
            # self.rect.y -= self.velocity.y

    def wall_collisions(self):
        for wall in self.walls:
            if(pygame.sprite.collide_rect(self, wall)):
                 return True
        return False

    def die(self):
        self.score = 0
        self.rect.x = SCREEN_WIDTH / 2
        self.rect.y = SCREEN_HEIGHT / 2
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
    # all_sprites_list.add(wall, wall2, wall3, wall4)

    player = Player(screen, walls)
    all_sprites_list.add(player)

    clock = pygame.time.Clock()

    if not LOCAL_DEBUG:
        # Connect to server
        HOST = '217.101.168.167'
        # HOST = 'localhost';
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
                    sock.close()

                running = False

        player.velocity.x = 0
        player.velocity.y = 0

        # Handle keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.velocity.x = -5
        if keys[pygame.K_RIGHT]:
            player.velocity.x = 5
        if keys[pygame.K_UP]:
            player.velocity.y = -5
        if keys[pygame.K_DOWN]:
            player.velocity.y = 5
        if keys[pygame.K_w]:
            player.eatSomething(5)


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
        all_sprites_list.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__ == "__main__":
    # call the main function
    main()
