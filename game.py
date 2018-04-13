# import the pygame module, so you can use it
import pygame
import socket
import time

WHITE = (255, 255, 255)
LOCAL_DEBUG = True
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class Player(pygame.sprite.Sprite):
    def __init__(self, screen):
        # Call the parent class (Sprite) constructor
        super().__init__()
        # Pass in the color of the car, and its x and y position, width and height.
        # Set the background color and set it to be transparent

        self.filter = pygame.Surface([30, 30])
        # pygame.draw.rect(self.filter, pygame.Color(255, 0, 0, 255))
        pygame.draw.circle(self.filter, pygame.Color(255, 0, 0, 10), [30 // 2, 30 // 2], 15)
        # self.filter.fill(pygame.Color(255, 0, 0, 128))

        # Instead we could load a proper pciture
        self.image = pygame.image.load("LUL.png").convert_alpha()
        # for

        self.image = self.filter
        # Fetch the rectangle object that has the dimensions of the image.
        # self.rect = self.image.get_rect()
        self.rect = self.filter.get_rect()
        self.screen = screen

    def draw(self, surface):
        pygame.draw.rect(self.screen, pygame.Color(255, 0, 0, 128), self.rect)

    def moveRight(self, pixels):
        self.rect.x += pixels

    def moveLeft(self, pixels):
        self.rect.x -= pixels

    def moveUp(self, pixels):
        self.rect.y -= pixels

    def moveDown(self, pixels):
        self.rect.y += pixels

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
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

    # define a variable to control the main loop
    running = True

    all_sprites_list = pygame.sprite.Group()
    player = Player(screen)
    all_sprites_list.add(player)

    clock = pygame.time.Clock()

    if not LOCAL_DEBUG:
        # Connect to server
        HOST = '217.101.168.167'
        # HOST = 'localhost';
        PORT = 25565
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((HOST, PORT))
        except Exception as e:
            print("Cannot connect to the server:", e)
        print("Connected")


    otherplayers = {}

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

        # Handle keys
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.moveLeft(5)
        if keys[pygame.K_RIGHT]:
            player.moveRight(5)
        if keys[pygame.K_UP]:
            player.moveUp(5)
        if keys[pygame.K_DOWN]:
            player.moveDown(5)

        # socket logic update players
        if not LOCAL_DEBUG:
            sock.send((str(player.rect.x) + ":" + str(player.rect.y)).encode())
            for data in sock.recv(4096).decode().split(";"):
                if not data:
                    break

                print(data)

                port, x, y = data.split(":")
                if port not in otherplayers:
                    p = Player(screen)
                    all_sprites_list.add(p)
                    otherplayers[port] = p
                otherplayers[port].setNewCoords(int(x), int(y))

            all_sprites_list.update()

        # Clear screen
        pygame.draw.rect(screen, pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw all sprites in the group of sprites
        all_sprites_list.draw(screen)

        pygame.display.flip()
        clock.tick(60)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
