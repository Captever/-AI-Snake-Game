import pygame
import sys

from constants import *

from scripts.map_structure import Map
from scripts.game_entities import Player, FeedSystem

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

        self.player = Player(self, INIT_LENGTH)

        self.feedSystem = FeedSystem(self)
        self.feedSystem.add_feed_random_pos(FEED_NUM)

        self.is_gameover = False

    def run(self):
        self.running = True
        while self.running:
            self.start_of_frame()

            if self.is_gameover:
                self.running = False

            self.player.move_sequence()

            self.event_handler()
            
            self.map.render(self.screen, self.origin)

            self.end_of_frame()

        self.end_of_game()
    
    def is_in_bound(self, pos) -> bool:
        return self.map.is_inside(pos)

    def check_collision(self, pos):
        if not self.is_in_bound(pos):
            return 'wall', None
        if pos in self.player.bodies:
            return 'body', None
        if pos in self.feedSystem.feeds:
            feed = self.feedSystem.feeds[pos]
            return 'feed', feed
        return 'none', None

    def remove_feed(self, pos):
        self.feedSystem.remove_feed(pos)

    def gameover(self, is_gameover: bool = True):
        self.is_gameover = is_gameover

    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.set_direction('N')
                if event.key == pygame.K_DOWN:
                    self.player.set_direction('S')
                if event.key == pygame.K_LEFT:
                    self.player.set_direction('W')
                if event.key == pygame.K_RIGHT:
                    self.player.set_direction('E')
    
    def start_of_frame(self):
        # initialize screen
        self.screen.fill(BLACK + (0,))
        
    def end_of_frame(self):
        pygame.display.flip()
        self.clock.tick(60)

    def end_of_game(self):
        pygame.quit()
        sys.exit()

Game().run()