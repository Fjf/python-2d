# import the pygame module, so you can use it
import pygame
import socket
import time
import select

WHITE = (255, 255, 255)

class Player(pygame.sprite.Sprite):
    def __init__(self, screen):
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
    player = Player(screen)
    all_sprites_list.add(player)

    clock = pygame.time.Clock()

    # Connect to server
    HOST = 'localhost'
    PORT = 5000
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


        client_socket.send((str(player.rect.x) + ":" + str(player.rect.y)).encode())

        # socket logic update players
        read_sockets, write_sockets, error_sockets = select.select([client_socket], [], [], 0.01)
        for sock in read_sockets:
            print(sock.recv(4096).decode())



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
