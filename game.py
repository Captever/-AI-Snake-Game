import pygame
import sys

from scripts.map import Map

# define color
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
BLACK = (0, 0, 0)

# define h-param
GRID_NUM = 8
FEED_NUM = 1
MOVE_DELAY = 30 # frame
INIT_LENGTH = 3 # initial length of snake
OUTLINE_THICKNESS = 3 # outline thickness of map

class Game:
    def __init__(self):
        # initialize Pygame
        pygame.init()

        # initialize screen
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((1280, 720))
        self.screen.fill(BLACK)

        # initialize map
        map_length = self.screen.get_width() // 2
        self.map = Map(map_length, GRID_NUM, WHITE, OUTLINE_THICKNESS)
        self.map.draw_by_center(self.screen, (self.screen.get_width() // 2, self.screen.get_height() // 2))

        # initialize clock
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            pygame.display.flip()
            self.clock.tick(60)

        # end of program
        pygame.quit()
        sys.exit()

Game().run()