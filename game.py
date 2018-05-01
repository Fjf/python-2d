# import the pygame module, so you can use it
import pygame
import random
from pygame.math import Vector2
import socket, select
import time
import math
import encoder

WHITE = (255, 255, 255)
LOCAL_DEBUG = False
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
MAP_WIDTH = 2000
MAP_HEIGHT = 2000
SERVER_ADDR = 'localhost'

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.image.fill(pygame.Color(255, 255, 0))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coord = Vector2(x, y)

class Player(pygame.sprite.Sprite):
    def __init__(self, screen, walls):
        # Call the parent class (Sprite) constructor
        super().__init__()


        # You start without score (small)
        self.score = 0
        self.max_speed = 2.5
        self.speed = self.max_speed

        self.image = pygame.Surface([30, 30])
        self.original_image = pygame.image.load("LUL.png").convert_alpha()

        iw = self.original_image.get_width()
        ih = self.original_image.get_height()
        for x in range(iw):
            for y in range(ih):
                if int((x-iw/2)**2 + (y-ih/2)**2) > int((iw/2)**2):
                    self.original_image.set_at((x, y), pygame.Color(0, 0, 0, 0))
                    continue

                if self.original_image.get_at((x, y)).a == 0:
                    self.original_image.set_at((x, y), pygame.Color(40, 40, 40))


        self.image = pygame.transform.scale(self.image, (30, 30))

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
        self.screen = screen
        self.velocity = Vector2(0, 0)
        self.walls = walls

        self.coord = Vector2(0, 0)

        self.prev_x = 0
        self.prev_y = 0
        self.prev_score = 0

        self.otherplayers = {}

    def draw(self, surface):
        pygame.draw.rect(surface, pygame.Color(255, 0, 0, 128), self.rect)

    def update(self):
        self.coord.x += round(self.velocity.x)
        self.coord.y += round(self.velocity.y)

        self.velocity.x = round(0.89 * self.velocity.x)
        self.velocity.y = round(0.89 * self.velocity.y)
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
        self.coord.x = random.randint(10, MAP_WIDTH - 10)
        self.coord.y = random.randint(10, MAP_HEIGHT - 10)
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
        # Update image size
        self.image = pygame.transform.scale(self.original_image, (int(30 + math.sqrt(self.score)), int(30 + math.sqrt(self.score))))
        # Update rectangle
        self.rect = self.image.get_rect(center=(self.rect.x + self.rect.width//2, self.rect.y + self.rect.height//2))

    def hasUpdated(self):
        if self.coord.x == self.prev_x and self.coord.y == self.prev_y and self.score == self.prev_score:
            return False
        else:
            self.prev_x = self.coord.x
            self.prev_y = self.coord.y
            self.prev_score = self.score
            return True

    def setNewStats(self, x, y, score):
        self.coord.x = x
        self.coord.y = y
        self.score = score
        self.updateSprite()


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

    wall = Wall(0, 0, 10, MAP_HEIGHT)
    wall2 = Wall(MAP_WIDTH - 10, 0, 10, MAP_HEIGHT)
    wall3 = Wall(0, 0, MAP_WIDTH, 10)
    wall4 = Wall(0, MAP_HEIGHT - 10, MAP_WIDTH, 10)
    walls.add(wall, wall2, wall3, wall4)
    all_sprites_list.add(wall, wall2, wall3, wall4)

    player = Player(screen, walls)
    all_sprites_list.add(player)

    encd = encoder.Encoder()
    decd = encoder.Decoder()

    clock = pygame.time.Clock()

    if not LOCAL_DEBUG:
        # Connect to server
        # HOST = '217.101.168.167'
        HOST = SERVER_ADDR;
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
                # Encode player data and send over socket
                encd.setCoordData(player.coord - Vector2(player.rect.width // 2, player.rect.height // 2), player.score)

                client_socket.send(encd.getBytes())

            read_sockets, write_sockets, error_sockets = select.select([client_socket], [], [], 0.01)
            for sock in read_sockets:
                bytes = sock.recv(4096)

                if bytes and len(bytes) > 0:
                    decd.addData(bytes)
                    if decd.processData():
                        if decd.getDataType() == encoder.Types.COORDINATE.value:
                            id, x, y, score = decd.getData()
                            # Add unknown player to possible players.
                            if id not in player.otherplayers:
                                p = Player(screen, walls)
                                all_sprites_list.add(p)
                                player.otherplayers[id] = p
                            player.otherplayers[id].setNewStats(int(x), int(y), int(score))

                        elif decd.getDataType() == encoder.Types.MESSAGE.value:
                            pass


        for sprite in all_sprites_list:
            if sprite != player:
                sprite.rect.x = sprite.coord.x - player.coord.x + SCREEN_WIDTH // 2
                sprite.rect.y = sprite.coord.y - player.coord.y + SCREEN_HEIGHT // 2

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
