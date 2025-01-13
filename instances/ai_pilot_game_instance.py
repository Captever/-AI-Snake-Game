import pygame
import sys

from constants import *

from scripts.map_structure import Map
from scripts.game_entities import Player, FeedSystem
from scripts.game_manager import ScoreManager, GameState, GameStateManager

from scripts.ai.base_ai import BaseAI

from typing import Tuple

class AI_Pilot_Game:
    def __init__(self, pilot_ai: BaseAI, player_move_delay: int, grid_size: Tuple[int, int], feed_amount: int, clear_goal: float):
        self.pilot_ai: BaseAI = pilot_ai
        self.player_move_delay: int = player_move_delay
        self.grid_size: Tuple[int, int] = grid_size
        self.feed_amount: int = feed_amount
        self.clear_goal: float = clear_goal

        self.state: GameState = None
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.running: bool = False
        self.player: Player = None
        self.fs: FeedSystem = None
        self.state_manager: GameStateManager = GameStateManager(self.grid_size)

        self.move_accum: int = 0
        self.next_direction: str = None

        self.init_ui()

        self.start_game()

    def init_ui(self):
        if IS_LANDSCAPE:
            map_side_length = (SCREEN_WIDTH // 2)
            self.sm = ScoreManager(self, (SCREEN_WIDTH // 4, SCREEN_HEIGHT), map_side_length * FONT_SIZE_RATIO, WHITE)
            self.score_offset = (SCREEN_WIDTH * 0.75, 0)
        else:
            map_side_length = SCREEN_WIDTH
            self.sm = ScoreManager(self, (SCREEN_WIDTH, SCREEN_HEIGHT // 4), map_side_length * FONT_SIZE_RATIO, WHITE)
            self.score_offset = (0, SCREEN_HEIGHT * 0.75)
        self.sm.set_clear_condition(round(self.grid_size[0] * self.grid_size[1] * self.clear_goal) - INIT_LENGTH)
        self.origin = (SCREEN_WIDTH // 2 - map_side_length // 2, SCREEN_HEIGHT // 2 - map_side_length // 2)

        self.map = Map(self, map_side_length, GRID_THICKNESS, WHITE + (GRID_ALPHA,))
        self.map.add_outerline(MAP_OUTERLINE_THICKNESS, WHITE)

        self.centered_font = pygame.font.SysFont('consolas', round(map_side_length * FONT_SIZE_RATIO * 3.5), bold=True)

    def start_game(self):
        self.player = Player(self, INIT_LENGTH)
        self.fs = FeedSystem(self, self.feed_amount)
        self.fs.add_feed_random_coord(self.feed_amount)

        self.score: int = 0

        self.start_countdown(3000)

    def update(self):
        if self.is_active():
            self.move_sequence()
        self.countdown()

    def move_sequence(self):
        if self.move_accum >= self.player_move_delay:
            self.move_accum = 0
            self.player.move()
            
            # decide next direction after completing player movement
            self.player.set_direction(self.pilot_ai.decide_direction())
        else:
            self.move_accum += 1
    
    def render_centered_font(self, surf: pygame.Surface, font_content: str):
        self.centered_font_surf = self.centered_font.render(font_content, True, WHITE)
        self.centered_font_offset = self.centered_font_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)).topleft
        surf.blit(self.centered_font_surf, self.centered_font_offset)

    def start_countdown(self, count_ms: int = 3000):
        self.set_state(GameState.COUNTDOWN)
        self.countdown_remaining_time = count_ms / 1000.0
        self.countdown_end_ticks = (pygame.time.get_ticks() + count_ms) / 1000.0
    
    def countdown(self):
        if self.state == GameState.COUNTDOWN:
            current_ticks = pygame.time.get_ticks() / 1000.0
            self.countdown_remaining_time = max(0.0, self.countdown_end_ticks - current_ticks)
            if not self.countdown_remaining_time:
                self.set_state(GameState.ACTIVE)
    
    def is_active(self) -> bool:
        return self.state == GameState.ACTIVE
    
    def is_in_bound(self, coord) -> bool:
        return self.map.is_inside(coord)

    def check_collision(self, coord):
        if not self.is_in_bound(coord):
            return 'wall', None
        # 'body' collision is not valid for tail
        if self.player.is_body_collision(coord):
            return 'body', None
        if self.fs.is_feed_exist(coord):
            feed = self.fs.get_feed(coord)
            return 'feed', feed
        return 'none', None

    def remove_feed(self, coord):
        self.fs.remove_feed(coord)

    def update_score(self, amount: int = 1):
        self.sm.update_score(amount)

    def set_state(self, state: GameState):
        self.state = state

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
    
    def handle_keydown(self, key):
        if key == pygame.K_p:
            if self.state == GameState.PAUSED:
                self.state = GameState.ACTIVE
            elif self.state == GameState.ACTIVE:
                self.state = GameState.PAUSED

    def render(self, surf: pygame.Surface):
        surf.fill((0, 0, 0))

        self.player.render()
        self.fs.render()
        self.map.render(surf, self.origin)
        self.sm.render(surf, self.score_offset)
        if self.state in [GameState.PAUSED, GameState.CLEAR, GameState.GAMEOVER, GameState.COUNTDOWN]:
            if self.state == GameState.PAUSED:
                centered_font_content = "PAUSED"
            elif self.state == GameState.CLEAR:
                centered_font_content = "CLEAR"
            elif self.state == GameState.GAMEOVER:
                centered_font_content = "GAME OVER"
            elif self.state == GameState.COUNTDOWN:
                centered_font_content = str(round(self.countdown_remaining_time, 1))
            self.render_centered_font(surf, centered_font_content)

        pygame.display.flip()
        self.clock.tick(60)

    def end_of_game(self):
        pygame.quit()
        sys.exit()