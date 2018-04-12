# import the pygame module, so you can use it
import pygame
import time

WHITE = (255, 255, 255)

class Player(object):
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

    def handle_keys(self):
        key = pygame.key.get_pressed()
        dist = 1
        if key[pygame.K_LEFT]:
           self.rect.move_ip(-1, 0)
        if key[pygame.K_RIGHT]:
           self.rect.move_ip(1, 0)
        if key[pygame.K_UP]:
           self.rect.move_ip(0, -1)
        if key[pygame.K_DOWN]:
           self.rect.move_ip(0, 1)

    def draw(self, surface):
        pygame.draw.rect(self.screen, pygame.Color(255, 0, 0, 128), self.rect)




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

    player = Player(screen)

    img = pygame.image.load('LUL.png').convert_alpha()

    x = 0
    y = 0

    clock = pygame.time.Clock()
    # main loop
    while running:
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False

        # Key handling
        if pygame.key.get_pressed()[pygame.K_a]:
            x -= 1
        if pygame.key.get_pressed()[pygame.K_d]:
            x += 1
        if pygame.key.get_pressed()[pygame.K_w]:
            y -= 1
        if pygame.key.get_pressed()[pygame.K_s]:
            y += 1

        # Clear screen
        pygame.draw.rect(screen, pygame.Color(0, 0, 0, 255), pygame.Rect(0, 0, scr_width, scr_height))
        # Draw rect
        pygame.draw.rect(screen, pygame.Color(255, 0, 0, 128), pygame.Rect(x, y, 20, 20))
        pygame.display.flip()
        clock.tick(60)


# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
