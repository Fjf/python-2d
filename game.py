# import the pygame module, so you can use it
import pygame




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
