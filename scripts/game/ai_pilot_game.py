import pygame
import sys

from constants import *

from scripts.ui.ui_components import UILayout, RelativeRect, Board
from scripts.ui.map_structure import Map
from scripts.ui.instruction import Instruction
from scripts.entity.player import Player
from scripts.entity.feed_system import FeedSystem
from scripts.manager.cell_manager import CellManager

from scripts.ai.base_ai import BaseAI
from scripts.manager.game_manager import GameState

from typing import Tuple, Dict
from functools import partial

from scripts.ai.q_learning import QLearningAI

board_list = [ # key, title, content format
    ("top_score", "TOP", "{:,}"),
    ("score", "Score", "{:,}"),
    ("epoch", "Epoch", "{:,}"),
    ("avg_score_last_100", "Average Last 100", "{:,.3f}"),
    ("total_avg_score", "Total Average", "{:,.3f}")
]
instruction_list = [ # key, act
    ("P", "Pause"),
    ("E", "Set as final epoch"),
    ("Q", "Enable speed limit")
]

class AIPilotGame:
    def __init__(self, scene, pilot_ai: BaseAI, player_move_delay: int, grid_size: Tuple[int, int], feed_amount: int, clear_goal: float, epoch_num: int):
        self.scene = scene
        self.pilot_ai: BaseAI = pilot_ai
        self.player_move_delay: int = player_move_delay
        self.grid_size: Tuple[int, int] = grid_size
        self.feed_amount: int = feed_amount
        self.clear_condition: int = round(self.grid_size[0] * self.grid_size[1] * clear_goal) - INIT_LENGTH
        self.epoch_set_num: int = epoch_num

        self.state: GameState = None
        self.clock: pygame.time.Clock = pygame.time.Clock()
        self.player: Player = None
        self.fs: FeedSystem = None
        self.cell_manager: CellManager = None
        self.score: int = 0
        self.top_score: int = 0
        self.epoch_count: int = 0

        self.final_epoch_flag: bool = False # If true, terminate at the current epoch
        self.enable_speed_limit_flag: bool = False # If true, enable speed restriction

        self.to_resume: bool = False # TODO: Include it in the mode when expanding modes to a global concept

        self.move_accum: int = 0
        self.curr_direction: str = None
        self.next_direction: str = None

        self.state_layouts: Dict[int, UILayout] = {}
        self.resume_layout: UILayout = None
        self.boards: Dict[str, Board] = {}

        self.init_ui()

        self.start_game()

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

        for idx, (board_key, board_title, board_format) in enumerate(board_list):
            board_offset = (board_relative_offset[0] * idx, board_relative_offset[1] * idx)
            curr_board_relative_rect = RelativeRect(board_relative_rect.relative_x + board_offset[0], board_relative_rect.relative_y + board_offset[1], board_relative_rect.relative_width, board_relative_rect.relative_height)
            board_rect = curr_board_relative_rect.to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.boards[board_key] = Board(board_rect, board_title, WHITE, format=board_format)

        # about state layouts
        state_layout_rect = RelativeRect(0, 0.3, 1, 0.35).to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.init_states_layout(state_layout_rect)
        self.resume_layout = self.create_resume_layout(state_layout_rect)

        # about instructions
        instruction_rect = RelativeRect(0, 0.5, 0.25, 0.5).to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.instruction = Instruction(instruction_rect, "Key Instruction", instruction_list, WHITE)

    def init_states_layout(self, rect: pygame.Rect):
        self.state_layouts[GameState.PAUSED] = self.create_paused_layout(rect)
        self.state_layouts[GameState.GAMEOVER] = self.create_gameover_layout(rect)
        self.state_layouts[GameState.CLEAR] = self.create_clear_layout(rect)
    
    def create_paused_layout(self, rect: pygame.Rect):
        layout: UILayout = UILayout((0, 0), rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "PAUSED", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.1, 0, 0.35, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.55, 0, 0.35, 1), "Add Epoch", self.set_to_resume)

        return layout
    
    def create_gameover_layout(self, rect: pygame.Rect):
        layout: UILayout = UILayout((0, 0), rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "GAME OVER", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.025, 0, 0.3, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.35, 0, 0.3, 1), "Add Epoch", self.set_to_resume)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.675, 0, 0.3, 1), "Save")

        return layout
    
    def create_clear_layout(self, rect: pygame.Rect):
        layout: UILayout = UILayout((0, 0), rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "CLEAR", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.025, 0, 0.3, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.35, 0, 0.3, 1), "Add Epoch", self.set_to_resume)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.675, 0, 0.3, 1), "Save")

        return layout

    def create_resume_layout(self, rect: pygame.Rect):
        layout: UILayout = UILayout((0, 0), rect, (0, 0, 0, 0))
        
        layout.add_scrollbar(RelativeRect(0.25, 0, 0.5, 0.6), "Additional Epoch", 500, 100000, 1000, 500)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.1, 0, 0.35, 1), "Resume", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.55, 0, 0.35, 1), "Back", partial(self.set_to_resume, False))

        return layout

    def set_to_resume(self, to_resume: bool = True):
        self.to_resume = to_resume

    def start_game(self):
        self.cell_manager = CellManager(self.grid_size)
        self.player = Player(self, INIT_LENGTH)
        self.fs = FeedSystem(self, self.feed_amount)
        self.fs.add_feed_random_coord(self.feed_amount)

        self.epoch_count += 1
        self.boards["epoch"].update_content(self.epoch_count)
        
        self.state = GameState.ACTIVE

    def resume_game_at_epoch(self):
        additional_epoch = self.resume_layout.get_scrollbar_values()["Additional Epoch"]

        self.epoch_set_num += additional_epoch

        self.set_to_resume(False)

        self.restart_game()
    
    def restart_game(self):
        self.score = 0
        self.boards["score"].reset()
        self.start_game()

    def update(self):
        if self.is_active():
            self.move_sequence()

        if self.player is not None and self.state == GameState.ACTIVE and self.next_direction is None:
            self.next_direction = self.pilot_ai.decide_direction()
            if self.next_direction == "surrender": # Maintain previous movement upon surrender
                self.next_direction = self.curr_direction
            else: # No need to reset when maintaining the same direction
                self.curr_direction = self.next_direction
                self.player.set_direction(self.next_direction, False)

    def move_sequence(self):
        if self.is_on_move():
            self.move_accum = 0
            self.player.move()
            self.next_direction = None
        else:
            self.move_accum += 1
    
    def flip_final_epoch_flag(self):
        self.final_epoch_flag = not self.final_epoch_flag

    def flip_speed_limit_flag(self):
        self.enable_speed_limit_flag = not self.enable_speed_limit_flag

    def flip_game_pause(self):
        if self.state == GameState.PAUSED:
            self.set_state(GameState.ACTIVE)
        elif self.state == GameState.ACTIVE:
            self.set_state(GameState.PAUSED)
    
    def is_active(self) -> bool:
        return self.state == GameState.ACTIVE
    
    def is_in_bound(self, coord) -> bool:
        return self.map.is_inside(coord)
    
    def is_on_move_delay(self) -> bool:
        # If enable_speed_limit_flag is true, enable speed restriction
        return not self.enable_speed_limit_flag or self.move_accum >= self.player_move_delay
    
    def is_decided_next_direction(self) -> bool:
        return self.next_direction is not None

    def is_on_move(self) -> bool:
        return self.is_on_move_delay() and self.is_decided_next_direction()

    def is_all_epoch_completed(self) -> bool:
        return self.epoch_set_num <= self.epoch_count
    
    def is_ended_process(self) -> bool:
        # If final_epoch_flag is true, terminate at the current epoch
        return self.final_epoch_flag or self.is_all_epoch_completed()

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

        if self.score > self.top_score:
            self.top_score = self.score
            self.boards["top_score"].update_content(self.top_score)
        
        if self.clear_condition is not None and self.score >= self.clear_condition:
            self.set_state(GameState.CLEAR)

    def set_state(self, state: GameState):
        self.state = state

        if state == GameState.CLEAR:
            self.handle_game_end()
        elif state == GameState.GAMEOVER:
            if isinstance(self.pilot_ai, QLearningAI):
                self.pilot_ai.learn(-1, None)
            self.handle_game_end()
    
    def handle_game_end(self):
        self.scene.add_score_to_figure(self.epoch_count, self.score)

        self.boards["avg_score_last_100"].update_content(self.scene.get_last_average_score_last_100())
        self.boards["total_avg_score"].update_content(self.scene.get_average_score())

        if not self.is_ended_process():
            self.restart_game()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
        
        if self.to_resume:
            self.resume_layout.handle_events(events)
        elif self.state in [GameState.PAUSED, GameState.GAMEOVER, GameState.CLEAR]:
            self.state_layouts[self.state].handle_events(events)
    
    def handle_keydown(self, key):
        if key == pygame.K_p:
            if self.state in [GameState.PAUSED, GameState.ACTIVE]:
                self.flip_game_pause()
        if key == pygame.K_e:
            if self.state in [GameState.PAUSED, GameState.ACTIVE]:
                self.flip_final_epoch_flag()
        if key == pygame.K_q:
            if self.state in [GameState.PAUSED, GameState.ACTIVE]:
                self.flip_speed_limit_flag()

    def render(self, surf: pygame.Surface):
        surf.fill((0, 0, 0))

        self.player.render()
        self.fs.render()
        for board in self.boards.values():
            board.render(surf)
        self.instruction.render(surf)

        self.map.render(surf, self.map_origin)
        
        if self.to_resume:
            self.resume_layout.render(surf)
        elif self.state in [GameState.PAUSED, GameState.CLEAR, GameState.GAMEOVER]:
            self.state_layouts[self.state].render(surf)

        pygame.display.flip()
        self.clock.tick(60)

    def end_of_game(self):
        pygame.quit()
        sys.exit()