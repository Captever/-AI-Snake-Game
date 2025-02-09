import pygame
import sys

from constants import *

from scripts.ui.ui_components import UILayout, RelativeRect, Board, TextBox
from scripts.ui.map_structure import Map
from scripts.entity.player import Player
from scripts.entity.feed_system import FeedSystem
from scripts.manager.cell_manager import CellManager

from scripts.manager.game_manager import GameState

from typing import Tuple, Dict

class SingleGame:
    def __init__(self, scene, player_move_delay: int, grid_size: Tuple[int, int], feed_amount: int, clear_goal: float):
        self.scene = scene
        self.player_move_delay: int = player_move_delay
        self.grid_size: Tuple[int, int] = grid_size
        self.feed_amount: int = feed_amount
        self.clear_condition: int = round(self.grid_size[0] * self.grid_size[1] * clear_goal) - INIT_LENGTH

        self.state: GameState = None
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.map: Map = None
        self.player: Player = None
        self.fs: FeedSystem = None
        self.cell_manager: CellManager = None
        self.score: int = 0
        
        self.move_accum: int = 0

        self.state_layouts: Dict[int, UILayout] = {}
        self.countdown_textbox: TextBox = None
        self.score_board: Board = None

        self.init_ui()

        self.start_game()

    def init_ui(self):
        if IS_LANDSCAPE:
            map_side_length = (SCREEN_WIDTH // 2)
            board_relative_rect = RelativeRect(0.75, 0.1, 0.25, 0.15)
        else:
            map_side_length = SCREEN_WIDTH
            board_relative_rect = RelativeRect(0.1, 0.75, 0.15, 0.25)
        self.map_origin = (SCREEN_WIDTH // 2 - map_side_length // 2, SCREEN_HEIGHT // 2 - map_side_length // 2)

        self.map = Map(self, map_side_length, GRID_THICKNESS, WHITE + (GRID_ALPHA,))
        self.map.add_outerline(MAP_OUTERLINE_THICKNESS, WHITE)

        board_rect = board_relative_rect.to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.score_board = Board(board_rect, "Score", WHITE, format="{:,}")

        self.state_layout_rect = RelativeRect(0, 0.3, 1, 0.35).to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.countdown_textbox = TextBox(self.state_layout_rect, "0", YELLOW)
        self.init_states_layout()

    def init_states_layout(self):
        self.state_layouts[GameState.PAUSED] = self.create_paused_layout()
        self.state_layouts[GameState.GAMEOVER] = self.create_gameover_layout()
        self.state_layouts[GameState.CLEAR] = self.create_clear_layout()
    
    def create_countdown_layout(self):
        layout: UILayout = UILayout((0, 0), self.state_layout_rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "COUNT DOWN", WHITE)

        return layout
    
    def create_paused_layout(self):
        layout: UILayout = UILayout((0, 0), self.state_layout_rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "PAUSED", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.3, 0, 0.4, 1), "New", self.scene.restart_new_game)

        return layout
    
    def create_gameover_layout(self):
        layout: UILayout = UILayout((0, 0), self.state_layout_rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "GAME OVER", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.1, 0, 0.35, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.55, 0, 0.35, 1), "Save")

        return layout
    
    def create_clear_layout(self):
        layout: UILayout = UILayout((0, 0), self.state_layout_rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "CLEAR", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.1, 0, 0.35, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.55, 0, 0.35, 1), "Save")

        return layout

    def start_game(self):
        self.cell_manager = CellManager(self.grid_size)
        self.player = Player(self, INIT_LENGTH)
        self.fs = FeedSystem(self, self.feed_amount)
        self.fs.add_feed_random_coord(self.feed_amount)

        self.start_countdown(3000)

    def update(self):
        if self.is_active():
            self.move_sequence()
        elif self.state == GameState.COUNTDOWN:
            self.countdown()

    def move_sequence(self):
        if self.move_accum >= self.player_move_delay:
            self.move_accum = 0
            self.player.move()
        else:
            self.move_accum += 1

    def start_countdown(self, count_ms: int = 3000):
        self.set_state(GameState.COUNTDOWN)
        self.countdown_remaining_time = count_ms / 1000.0
        self.countdown_end_ticks = (pygame.time.get_ticks() + count_ms) / 1000.0
    
    def countdown(self):
        current_ticks = pygame.time.get_ticks() / 1000.0
        self.countdown_remaining_time = max(0.0, self.countdown_end_ticks - current_ticks)
        self.countdown_textbox.update_content(str(round(self.countdown_remaining_time, 1)))
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
        self.score += amount
        self.score_board.update_content(self.score)
        
        if self.clear_condition is not None and self.score >= self.clear_condition:
            self.set_state(GameState.CLEAR)

    def set_state(self, state: GameState):
        self.state = state

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
        
        if self.state in [GameState.GAMEOVER, GameState.CLEAR, GameState.PAUSED]:
            self.state_layouts[self.state].handle_events(events)
    
    def handle_keydown(self, key):
        if self.is_active():
            self.handle_active_keydown(key)
        elif self.state == GameState.COUNTDOWN:
            self.handle_countdown_keydown(key)
        elif self.state == GameState.PAUSED:
            self.handle_paused_keydown(key)
    
    def handle_active_keydown(self, key):
        # handle keydown on active state
        if key == pygame.K_UP:
            self.player.set_direction('N')
        elif key == pygame.K_DOWN:
            self.player.set_direction('S')
        elif key == pygame.K_LEFT:
            self.player.set_direction('W')
        elif key == pygame.K_RIGHT:
            self.player.set_direction('E')
        elif key == pygame.K_p:
            self.set_state(GameState.PAUSED)
    
    def handle_paused_keydown(self, key):
        # handle keydown on paused state
        if key == pygame.K_p:
            self.set_state(GameState.ACTIVE)
    
    def handle_countdown_keydown(self, key):
        # handle keydown on countdown state
        if key == pygame.K_UP:
            self.player.set_direction('N')
        elif key == pygame.K_DOWN:
            self.player.set_direction('S')
        elif key == pygame.K_LEFT:
            self.player.set_direction('W')
        elif key == pygame.K_RIGHT:
            self.player.set_direction('E')

    def render(self, surf: pygame.Surface):
        surf.fill((0, 0, 0))

        self.player.render()
        self.fs.render()
        self.map.render(surf, self.map_origin)
        self.score_board.render(surf)
        if self.state in [GameState.PAUSED, GameState.CLEAR, GameState.GAMEOVER]:
            self.state_layouts[self.state].render(surf)
        elif self.state == GameState.COUNTDOWN:
            self.countdown_textbox.render(surf)

        pygame.display.flip()
        self.clock.tick(60)

    def end_of_game(self):
        pygame.quit()
        sys.exit()