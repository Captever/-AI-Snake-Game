import pygame
import sys

import random

from scripts.map import Map

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

        # values in game
        self.direction = 'E'
        self.bodies = []
        self.feeds = {}

    def run(self):
        running = True
        while running:
            self.screen.fill(BLACK + (0,))
          
            if not len(self.bodies):
                rand_pos_value = random.randint(0, pow(GRID_NUM, 2) - 1)
                start_pos = (rand_pos_value // GRID_NUM, rand_pos_value % GRID_NUM)
                
                self.bodies.append(start_pos)
                
                pos_possibilities = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                for _ in range(INIT_LENGTH - 1):
                    prev_body_pos = self.bodies[-1]
                    while True:
                        possibilities = pos_possibilities.copy()
                        curr_poss = possibilities[random.randint(0, len(possibilities) - 1)]
                        curr_body_pos = (prev_body_pos[0] + curr_poss[0], prev_body_pos[1] + curr_poss[1])
                        # validation
                        if 0 <= curr_body_pos[0] < GRID_NUM and 0 <= curr_body_pos[1] < GRID_NUM and curr_body_pos not in self.bodies:
                            self.bodies.append(curr_body_pos)
                            break
                        else:
                            possibilities.remove(curr_poss)
                
            if not len(self.feeds):
                for _ in range(FEED_NUM):
                    while True:
                        rand_pos_value = random.randint(0, pow(GRID_NUM, 2) - 1)
                        curr_feed_pos = (rand_pos_value // GRID_NUM, rand_pos_value % GRID_NUM)
                        # validation
                        if 0 <= curr_feed_pos[0] < GRID_NUM and 0 <= curr_feed_pos[1] < GRID_NUM and curr_feed_pos not in self.bodies:
                            self.feeds[curr_feed_pos] = 'normal'
                            break
                print(self.feeds)

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