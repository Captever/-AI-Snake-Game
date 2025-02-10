from abc import ABC, abstractmethod

import pygame
import sys

from constants import *

from scripts.ui.ui_components import UILayout, RelativeRect, Board, TextBox
from scripts.ui.map_structure import Map
from scripts.ui.instruction import Instruction
from scripts.entity.player import Player
from scripts.entity.feed_system import FeedSystem
from scripts.manager.cell_manager import CellManager

from scripts.manager.game_manager import GameState

from typing import List, Tuple, Dict

class BaseGame(ABC):
    def __init__(self, scene, player_move_delay: int, grid_size: Tuple[int, int], feed_amount: int, clear_goal: float):
        self.scene = scene
        self.player_move_delay = player_move_delay
        self.grid_size = grid_size
        self.feed_amount = feed_amount
        self.clear_condition: int = round(self.grid_size[0] * self.grid_size[1] * clear_goal) - INIT_LENGTH

        self.state: GameState = None
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.map: Map = None
        self.player: Player = None
        self.fs: FeedSystem = None
        self.cell_manager: CellManager = None

        self.score: int = 0

        self.move_accum: int = 0
        self.next_direction: str = None
        
        self.board_list: List[Tuple[str, str, str]] = []
        self.instruction_list: List[Tuple[str, str]] = []

        self.state_layouts: Dict[int, UILayout] = {}
        self.boards: Dict[str, Board] = {}

        self.init_board_list()
        self.init_instruction_list()

        self.init_ui()
    
    @abstractmethod
    def init_board_list(self):
        pass

    @abstractmethod
    def init_instruction_list(self):
        pass

    @abstractmethod
    def init_paused_layout(self, rect: pygame.Rect):
        pass

    @abstractmethod
    def init_gameover_layout(self, rect: pygame.Rect):
        pass

    @abstractmethod
    def init_clear_layout(self, rect: pygame.Rect):
        pass

    def init_states_layout(self):
        state_rect = self.get_state_layout_rect()

        self.init_paused_layout(state_rect)
        self.init_gameover_layout(state_rect)
        self.init_clear_layout(state_rect)

    def init_ui(self):
        if IS_LANDSCAPE:
            map_side_length = (SCREEN_WIDTH // 2)
            board_relative_rect = RelativeRect(0.75, 0.1, 0.25, 0.15)
            board_relative_offset = (0, 0.16)
        else:
            map_side_length = SCREEN_WIDTH
            board_relative_rect = RelativeRect(0.1, 0.75, 0.15, 0.25)
            board_relative_offset = (0.16, 0)
        self.map_origin = (SCREEN_WIDTH // 2 - map_side_length // 2, SCREEN_HEIGHT // 2 - map_side_length // 2)

        self.map = Map(self, map_side_length, GRID_THICKNESS, WHITE + (GRID_ALPHA,))
        self.map.add_outerline(MAP_OUTERLINE_THICKNESS, WHITE)

        for idx, (board_key, board_title, board_format) in enumerate(self.board_list):
            board_offset = (board_relative_offset[0] * idx, board_relative_offset[1] * idx)
            curr_board_relative_rect = RelativeRect(board_relative_rect.relative_x + board_offset[0], board_relative_rect.relative_y + board_offset[1], board_relative_rect.relative_width, board_relative_rect.relative_height)
            board_rect = curr_board_relative_rect.to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.boards[board_key] = Board(board_rect, board_title, WHITE, format=board_format)

        # about state layouts
        self.init_states_layout()
        self.countdown_textbox = TextBox(self.get_state_layout_rect(), "0", YELLOW)

        # about instructions
        self.instruction = Instruction(self.get_instruction_layout_rect(), "Key Instruction", self.instruction_list, WHITE)


    def set_paused_layout(self, layout: UILayout):
        self.state_layouts[GameState.PAUSED] = layout

    def set_gameover_layout(self, layout: UILayout):
        self.state_layouts[GameState.GAMEOVER] = layout

    def set_clear_layout(self, layout: UILayout):
        self.state_layouts[GameState.CLEAR] = layout
    
    def set_state_active(self):
        self.state = GameState.ACTIVE
    
    def set_state_countdown(self):
        self.state = GameState.COUNTDOWN
    
    def set_state_paused(self):
        self.state = GameState.PAUSED
    
    def set_state_gameover(self):
        self.state = GameState.GAMEOVER
    
    def set_state_clear(self):
        self.state = GameState.CLEAR


    def get_state_layout_rect(self):
        return RelativeRect(0, 0.3, 1, 0.35).to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def get_instruction_layout_rect(self):
        return RelativeRect(0, 0.5, 0.25, 0.5).to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def is_state_active(self):
        return self.state == GameState.ACTIVE
    
    def is_state_countdown(self):
        return self.state == GameState.COUNTDOWN
    
    def is_state_paused(self):
        return self.state == GameState.PAUSED
    
    def is_state_gameover(self):
        return self.state == GameState.GAMEOVER
    
    def is_state_clear(self):
        return self.state == GameState.CLEAR
    
    def is_active(self) -> bool:
        return self.state == GameState.ACTIVE
    
    def is_in_bound(self, coord) -> bool:
        return self.map.is_inside(coord)
    
    @abstractmethod
    def is_on_move(self) -> bool:
        pass

    # flip
    def flip_game_pause(self):
        if self.is_state_paused():
            self.set_state_active()
        elif self.is_state_active():
            self.set_state_paused()
    
    # about start
    def start_game(self):
        self.cell_manager = CellManager(self.grid_size)
        self.player = Player(self, INIT_LENGTH)
        self.fs = FeedSystem(self, self.feed_amount)
        self.fs.add_feed_random_coord(self.feed_amount)

    def start_countdown(self, count_ms: int = 3000):
        self.set_state_countdown()
        self.countdown_remaining_time = count_ms / 1000.0
        self.countdown_end_ticks = (pygame.time.get_ticks() + count_ms) / 1000.0
    
    def countdown(self):
        current_ticks = pygame.time.get_ticks() / 1000.0
        self.countdown_remaining_time = max(0.0, self.countdown_end_ticks - current_ticks)
        self.countdown_textbox.update_content(str(round(self.countdown_remaining_time, 1)))
        if not self.countdown_remaining_time:
            self.set_state_active()

    # about every frame routine
    def update(self):
        if self.is_active():
            self.move_sequence()
        elif self.is_state_countdown():
            self.countdown()
        
    def move_sequence(self):
        if self.is_on_move():
            self.move_accum = 0
            self.player.move()
            self.next_direction = None
        else:
            self.move_accum += 1


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
        self.boards["score"].update_content(self.score)
        
        if self.clear_condition is not None and self.score >= self.clear_condition:
            self.set_state_clear()

    def end_of_game(self):
        pygame.quit()
        sys.exit()


    @abstractmethod
    def handle_events(self, events):
        self.handle_state_events(events)

    def handle_state_events(self, events):
        if self.state in [GameState.PAUSED, GameState.GAMEOVER, GameState.CLEAR]:
            self.state_layouts[self.state].handle_events(events)
    

    def render(self, surf: pygame.Surface):
        surf.fill((0, 0, 0))

        self.player.render()
        self.fs.render()
        for board in self.boards.values():
            board.render(surf)
        self.instruction.render(surf)

        self.map.render(surf, self.map_origin)

        self.render_state_objects(surf)

        pygame.display.flip()
        self.clock.tick(60)

    def render_state_objects(self, surf):
        if self.state in [GameState.PAUSED, GameState.CLEAR, GameState.GAMEOVER]:
            self.state_layouts[self.state].render(surf)
            
        elif self.is_state_countdown():
            self.countdown_textbox.render(surf)