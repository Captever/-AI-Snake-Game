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

GRID_NUM = (20, 20)
GRID_ALPHA = 128
GRID_THICKNESS = 1 # grid line thickness of map
FEED_NUM = 1
MOVE_DELAY = 30 # frame
INIT_LENGTH = 3 # initial length of snake
OUTERLINE_THICKNESS = 3 # outline thickness of map

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()

        if SCREEN_WIDTH > SCREEN_HEIGHT: # case: landscape
            self.origin = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 - SCREEN_WIDTH // 4)
            map_size = (SCREEN_WIDTH // 2, SCREEN_WIDTH // 2)
        else: # case: portrait
            self.origin = (0, SCREEN_HEIGHT // 2 - SCREEN_WIDTH // 2)
            map_size = (SCREEN_WIDTH, SCREEN_WIDTH)

        self.map = Map(self, map_size, GRID_NUM, GRID_THICKNESS, WHITE + (GRID_ALPHA,))
        self.map.add_outerline(OUTERLINE_THICKNESS, WHITE)
        self.grid_num = GRID_NUM

        self.player = Player(self, INIT_LENGTH)
        self.move_accum = 0
        self.direction = 'E'

        self.feeds = []
        for _ in range(FEED_NUM):
            self.feeds.append(Feed(self))
            
        self.is_gameover = False

    def run(self):
        self.running = True
        while self.running:
            self.start_of_frame()

            if self.is_gameover:
                self.running = False

            self.move()

            self.event_handler()
            
            self.map.render(self.screen, self.origin)

            self.end_of_frame()

        self.end_of_game()
    
    def move(self):
        if self.move_accum >= MOVE_DELAY:
            self.move_accum = 0
            self.player.move()
    
    def is_in_bound(self, pos) -> bool:
        return self.map.is_inside(pos)

    def get_feed(self, pos) -> Feed:
        for feed in self.feeds:
            if pos == feed.pos:
                return feed
        return None

    def check_entity(self, pos) -> int:
        if not self.is_in_bound(pos):
            return 99 # out of bound = collide walls
        if pos in self.player.bodies:
            return 0
        feed = self.get_feed(pos)
        if feed is not None:
            return 1

        return -1

    def gameover(self, is_gameover: bool = True):
        self.is_gameover = is_gameover

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.direction = 'N'
                if event.key == pygame.K_DOWN:
                    self.direction = 'S'
                if event.key == pygame.K_LEFT:
                    self.direction = 'W'
                if event.key == pygame.K_RIGHT:
                    self.direction = 'E'
    
    def start_of_frame(self):
        # initialize screen
        self.screen.fill(BLACK + (0,))
        
    def end_of_frame(self):
        pygame.display.flip()
        self.clock.tick(60)

        self.move_accum += 1

    def end_of_game(self):
        pygame.quit()
        sys.exit()

Game().run()