# import the pygame module, so you can use it
import pygame
from pygame.math import Vector2
import socket
import time

WHITE = (255, 255, 255)

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height):
        super().__init__()
        self.image = pygame.Surface([width, height])
        self.rect = self.image.get_rect(topleft=(x, y))
        # self.rect.y = y
        # self.rect.x = x

class Player(pygame.sprite.Sprite):
    def __init__(self, screen, walls):
        # Call the parent class (Sprite) constructor
        super().__init__()
        # Pass in the color of the car, and its x and y position, width and height.
        # Set the background color and set it to be transparent
        self.image = pygame.Surface([30, 30])
        self.image.fill(WHITE)
        self.image.set_colorkey(WHITE)

        # Draw the car (a rectangle!)
        pygame.draw.rect(self.image, pygame.Color(255, 0, 0, 128), [0, 0, 30, 30])

        # Instead we could load a proper pciture of a car...
        self.image = pygame.image.load("LUL.png").convert_alpha()

        # Fetch the rectangle object that has the dimensions of the image.
        self.rect = self.image.get_rect()
        self.screen = screen
        self.velocity = Vector2(0, 0)
        self.walls = walls

    def draw(self, surface):
        pygame.draw.rect(self.screen, pygame.Color(255, 0, 0, 128), self.rect)

    def update(self):
        self.rect.x += self.velocity.x
        self.rect.y += self.velocity.y
        move = self.wall_collisions()
        if not move:
            self.rect.x -= self.velocity.x
            self.rect.y -= self.velocity.y

    def wall_collisions(self):
        for wall in self.walls:
            if(pygame.sprite.collide_rect(self, wall)):
                 return False
        return True
    def setNewCoords(self, x, y):
        self.rect.x = x
        self.rect.y = y


def main():

    # initialize the pygame module
    pygame.init()
    # load and set the logo
    logo = pygame.image.load("LUL.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    # create a surface on screen that has the size of 240 x 180
    scr_width = 600
    scr_height = 300;
    screen = pygame.display.set_mode((scr_width, scr_height))

    # define a variable to control the main loop
    running = True


    all_sprites_list = pygame.sprite.Group()
    walls = pygame.sprite.Group()

    wall = Wall(0, 0, 10, scr_height)
    wall2 = Wall(scr_width - 10, 0, 10, scr_height)
    walls.add(wall2)
    all_sprites_list.add(wall2)

    player = Player(screen, walls)
    all_sprites_list.add(player)

    clock = pygame.time.Clock()

    # Connect to server
    # HOST = '217.101.168.167'
    # PORT = 25565
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # try:
    #     sock.connect((HOST, PORT))
    # except Exception as e:
    #     print("Cannot connect to the server:", e)
    # print("Connected")
    #
    #
    # otherplayers = {}

    # main loop
    while running:
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
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

        # socket logic update players
        # sock.send((str(player.rect.x) + ":" + str(player.rect.y)).encode())
        # for data in sock.recv(4096).decode().split(";"):
        #     if not data:
        #         break
        #
        #     print(data)
        #
        #     port, x, y = data.split(":")
        #     if port not in otherplayers:
        #         p = Player(screen)
        #         all_sprites_list.add(p)
        #         otherplayers[port] = p
        #     otherplayers[port].setNewCoords(int(x), int(y))

        all_sprites_list.update()

        # Clear screen
        pygame.draw.rect(screen, pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, scr_width, scr_height))

        # Draw all sprites in the group of sprites
        all_sprites_list.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
