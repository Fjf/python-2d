# import the pygame module, so you can use it
import pygame

# define a main function
def main():

    # initialize the pygame module
    pygame.init()
    # load and set the logo
    logo = pygame.image.load("LUL.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("minimal program")

    # create a surface on screen that has the size of 240 x 180
    screen = pygame.display.set_mode((600,300))

    # define a variable to control the main loop
    running = True

    # main loop
    while running:
        # event handling, gets all event from the eventqueue
        for event in pygame.event.get():
            # only do something if the event is of type QUIT
            if event.type == pygame.QUIT:
                # change the value to False, to exit the main loop
                running = False
<<<<<<< HEAD
        pygame.draw.rect(screen, RED, [75, 10, 50, 20], 2)
        pygame.display.flip()
=======

        pygame.draw.rect(screen, pygame.Color(255, 0, 0, 128), pygame.Rect(0, 0, 20, 20))
        pygame.display.flip()

>>>>>>> 2691a2ceefe67532ff9671ea84f1708cc079b489

# run the main function only if this module is executed as the main script
# (if you import this as a module then nothing is executed)
if __name__=="__main__":
    # call the main function
    main()
