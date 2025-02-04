import pygame
import sys

from constants import *

from scripts.ui.ui_components import UILayout, RelativeRect, Board
from scripts.ui.map_structure import Map
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
        self.running: bool = False
        self.player: Player = None
        self.fs: FeedSystem = None
        self.cell_manager: CellManager = None
        self.score: int = 0
        self.top_score: int = 0
        self.epoch_count: int = 0

        self.to_resume: bool = False # TODO: Include it in the mode when expanding modes to a global concept

        self.move_accum: int = 0
        self.curr_direction: str = None
        self.next_direction: str = None

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
            curr_board_relative_rect = RelativeRect(board_relative_rect.x + board_offset[0], board_relative_rect.y + board_offset[1], board_relative_rect.width, board_relative_rect.height)
            board_rect = curr_board_relative_rect.to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.boards[board_key] = Board(board_rect, board_title, WHITE, format=board_format)

        self.centered_font_size = round(map_side_length * FONT_SIZE_RATIO * 3.5)
        self.centered_font = pygame.font.SysFont('consolas', self.centered_font_size, bold=True)
        self.state_layout: UILayout = self.create_state_layout(self.map_origin, map_side_length)

        self.resume_layout: UILayout = self.create_resume_layout(self.map_origin, map_side_length)

    def create_state_layout(self, map_origin: Tuple[int, int], map_side_length: int):
        offset_y = (map_side_length + self.centered_font_size) // 2
        top = map_origin[1] + offset_y
        height = map_side_length * 0.2

        layout: UILayout = UILayout((0, 0), pygame.Rect(map_origin[0], top, map_side_length, height), (0, 0, 0, 0))

        layout.add_button(RelativeRect(0.025, 0.1, 0.3, 0.5), "New", self.scene.restart_new_game)
        layout.add_button(RelativeRect(0.35, 0.1, 0.3, 0.5), "Add Epoch", self.set_to_resume)
        layout.add_button(RelativeRect(0.675, 0.1, 0.3, 0.5), "Save")

        return layout

    def create_resume_layout(self, map_origin: Tuple[int, int], map_side_length: int):
        layout_size: Tuple[int, int] = (round(map_side_length * 0.75), round(map_side_length * 0.25))
        layout_pos: Tuple[int, int] = (map_origin[0] + (map_side_length - layout_size[0]) // 2, map_origin[1] + (map_side_length - layout_size[1]) // 2)

        layout: UILayout = UILayout((0, 0), pygame.Rect(layout_pos + layout_size), (0, 0, 0, 0))

        layout.add_scrollbar(RelativeRect(0, 0, 1, 0.4), "Additional Epoch", 500, 100000, 1000, 500)
        layout.add_button(RelativeRect(0.05, 0.6, 0.4, 0.4), "Resume", self.resume_game_at_epoch)
        layout.add_button(RelativeRect(0.55, 0.6, 0.4, 0.4), "Back", partial(self.set_to_resume, False))

        return layout

    def set_to_resume(self, to_resume: bool = True):
        self.to_resume = to_resume

    def start_game(self):
        self.cell_manager = CellManager(self.grid_size)
        self.player = Player(self, INIT_LENGTH)
        self.fs = FeedSystem(self, self.feed_amount)
        self.fs.add_feed_random_coord(self.feed_amount)

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
        if self.move_accum >= self.player_move_delay:
            self.move_accum = 0
            self.player.move()
            self.next_direction = None
        else:
            self.move_accum += 1
    
    def render_centered_font(self, surf: pygame.Surface, font_content: str):
        self.centered_font_surf = self.centered_font.render(font_content, True, WHITE)
        self.centered_font_offset = self.centered_font_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)).topleft
        surf.blit(self.centered_font_surf, self.centered_font_offset)
    
    def is_active(self) -> bool:
        return self.state == GameState.ACTIVE
    
    def is_in_bound(self, coord) -> bool:
        return self.map.is_inside(coord)

    def is_epoch_completed(self) -> bool:
        return self.epoch_set_num <= self.epoch_count

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
        self.scene.add_score_to_figure(self.epoch_count + 1, self.score)

        self.epoch_count += 1
        self.boards["epoch"].update_content(self.epoch_count)
        self.boards["avg_score_last_100"].update_content(self.scene.get_last_average_score_last_100())
        self.boards["total_avg_score"].update_content(self.scene.get_average_score())
        if not self.is_epoch_completed():
            self.restart_game()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
        
        if self.to_resume:
            self.resume_layout.handle_events(events)
        elif self.state in [GameState.GAMEOVER, GameState.CLEAR]:
            self.state_layout.handle_events(events)
    
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
        self.map.render(surf, self.map_origin)
        for board in self.boards.values():
            board.render(surf)
        
        if self.to_resume:
            self.resume_layout.render(surf)
        elif self.state in [GameState.PAUSED, GameState.CLEAR, GameState.GAMEOVER]:
            if self.state == GameState.PAUSED:
                centered_font_content = "PAUSED"
            elif self.state == GameState.CLEAR:
                centered_font_content = "CLEAR"
                self.state_layout.render(surf)
            elif self.state == GameState.GAMEOVER:
                centered_font_content = "GAME OVER"
                self.state_layout.render(surf)
            self.render_centered_font(surf, centered_font_content)

        pygame.display.flip()
        self.clock.tick(60)

    def end_of_game(self):
        pygame.quit()
        sys.exit()