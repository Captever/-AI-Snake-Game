import pygame
import sys

from scripts.map_structure import Map
from scripts.game_entities import Player, Feed

# define color
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
BLACK = (0, 0, 0)

# define h-param
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

GRID_NUM = 20
GRID_ALPHA = 128
FEED_NUM = 1
MOVE_DELAY = 30 # frame
INIT_LENGTH = 3 # initial length of snake
OUTLINE_THICKNESS = 3 # outline thickness of map

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()

        if SCREEN_WIDTH > SCREEN_HEIGHT: # case: landscape
            self.origin = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - SCREEN_WIDTH // 4)
            map_size = SCREEN_WIDTH // 2
        else: # case: portrait
            self.origin = (0, SCREEN_HEIGHT // 2 - SCREEN_WIDTH // 2)
            map_size = SCREEN_WIDTH

        self.map = Map(self, map_size, GRID_NUM, WHITE + (GRID_ALPHA,), OUTLINE_THICKNESS)
        self.grid_num = GRID_NUM

        self.player = Player(self, INIT_LENGTH)
        self.direction = 'E'

        self.feeds = []
        for _ in range(FEED_NUM):
            self.feeds.append(Feed(self))

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK + (0,))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.direction = 'N'
                    if event.key == pygame.K_DOWN:
                        self.direction = 'S'
                    if event.key == pygame.K_LEFT:
                        self.direction = 'W'
                    if event.key == pygame.K_RIGHT:
                        self.direction = 'E'
            
            self.map.render(self.screen, self.origin)

            pygame.display.flip()
            self.clock.tick(60)

        # end of program
        pygame.quit()
        sys.exit()

Game().run()