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

        self.start_game()

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

        self.centered_font = pygame.font.SysFont('consolas', round(map_side_length * FONT_SIZE_RATIO * 3.5), bold=True)

    def start_game(self):
        self.player = Player(self, INIT_LENGTH)
        self.fs = FeedSystem(self)
        self.fs.add_feed_random_coord(FEED_NUM)

        self.score: int = 0

        self.is_countdown = False
        self.is_paused = False
        self.is_clear = False
        self.is_gameover = False

        self.start_countdown(3000)
    
    def render_centered_font(self, surf: pygame.Surface, font_content: str):
        self.centered_font_surf = self.centered_font.render(font_content, True, WHITE)
        self.centered_font_offset = self.centered_font_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)).topleft
        surf.blit(self.centered_font_surf, self.centered_font_offset)

    def run(self):
        self.running = True
        while self.running:
            self.start_of_frame()

            if not self.is_countdown and not self.is_paused and not self.is_clear and not self.is_gameover:
                self.player.move_sequence()

            self.event_handler()

            self.end_of_frame()

        self.end_of_game()
    
    def start_countdown(self, count_ms: int = 3000):
        self.is_countdown = True
        self.countdown_remaining_time = count_ms / 1000.0
        self.countdown_end_ticks = (pygame.time.get_ticks() + count_ms) / 1000.0
    
    def countdown(self):
        if self.is_countdown:
            current_ticks = pygame.time.get_ticks() / 1000.0
            self.countdown_remaining_time = max(0.0, self.countdown_end_ticks - current_ticks)
            if not self.countdown_remaining_time:
                self.is_countdown = False
    
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
        self.is_clear = True

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
                if event.key == pygame.K_p:
                    self.is_paused = not self.is_paused
    
    def start_of_frame(self):
        # initialize screen
        self.screen.fill(BLACK + (0,))

        self.countdown()
        
    def end_of_frame(self):
        self.player.render()
        self.fs.render()
        self.map.render(self.screen, self.origin)
        self.sm.render(self.screen, self.score_offset)
        if self.is_clear or self.is_gameover or self.is_countdown:
            centered_font_content = ("CLEAR" if self.is_clear else "GAME OVER") if not self.is_countdown else str(round(self.countdown_remaining_time, 1))
            self.render_centered_font(self.screen, centered_font_content)

        pygame.display.flip()
        self.clock.tick(60)

    def end_of_game(self):
        pygame.quit()
        sys.exit()

Game().run()