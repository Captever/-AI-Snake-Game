import pygame
import sys

from constants import *

from scripts.map_structure import Map
from scripts.game_entities import Player, FeedSystem
from scripts.game_manager import ScoreManager

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.clock = pygame.time.Clock()

        self.init_ui()

        self.player = Player(self, INIT_LENGTH)
        self.fs = FeedSystem(self)
        self.fs.add_feed_random_coord(FEED_NUM)

        self.score: int = 0

        self.is_gameover = False
        self.is_paused = False

    def init_ui(self):
        screen_rect = self.screen.get_rect()
        self.is_landscape: bool = SCREEN_WIDTH > SCREEN_HEIGHT

        if self.is_landscape:
            map_side_length = (SCREEN_WIDTH // 2)
            self.sm = ScoreManager(self, (SCREEN_WIDTH // 4, SCREEN_HEIGHT), map_side_length * FONT_SIZE_RATIO, WHITE)
            self.score_offset = (SCREEN_WIDTH * 0.75, 0)
        else:
            map_side_length = SCREEN_WIDTH
            self.sm = ScoreManager(self, (SCREEN_WIDTH, SCREEN_HEIGHT // 4), map_side_length * FONT_SIZE_RATIO, WHITE)
            self.score_offset = (0, SCREEN_HEIGHT * 0.75)
        self.sm.set_clear_condition(round(GRID_NUM[0] * GRID_NUM[1] * 0.7) - INIT_LENGTH)
        self.origin = (screen_rect.centerx - map_side_length // 2, screen_rect.centery - map_side_length // 2)

        self.map = Map(self, map_side_length, GRID_NUM, GRID_THICKNESS, WHITE + (GRID_ALPHA,))
        self.map.add_outerline(MAP_OUTERLINE_THICKNESS, WHITE)

    def run(self):
        self.running = True
        while self.running:
            self.start_of_frame()

            if self.is_gameover:
                self.running = False

            if not self.is_paused:
                self.player.move_sequence()

            self.event_handler()

            self.end_of_frame()

        self.end_of_game()
    
    def is_in_bound(self, coord) -> bool:
        return self.map.is_inside(coord)

    def check_collision(self, coord):
        if not self.is_in_bound(coord):
            return 'wall', None
        # 'body' collision is not valid for head
        if coord in self.player.bodies[1:]:
            return 'body', None
        if coord in self.fs.feeds:
            feed = self.fs.feeds[coord]
            return 'feed', feed
        return 'none', None

    def remove_feed(self, coord):
        self.fs.remove_feed(coord)

    def update_score(self, amount: int = 1):
        self.sm.update_score(amount)

    def clear(self):
        self.is_paused = True

    def gameover(self, is_gameover: bool = True):
        self.is_gameover = is_gameover
        self.end_of_game()

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
                if event.key == pygame.K_p:
                    self.is_paused = not self.is_paused
    
    def start_of_frame(self):
        # initialize screen
        self.screen.fill(BLACK + (0,))
        
    def end_of_frame(self):
        self.player.render()
        self.fs.render()
        self.map.render(self.screen, self.origin)
        self.sm.render(self.screen, self.score_offset)

        pygame.display.flip()
        self.clock.tick(60)

    def end_of_game(self):
        pygame.quit()
        sys.exit()

Game().run()