from abc import ABC, abstractmethod

import pygame

import random

from constants import *

from scripts.ui.ui_components import UILayout, RelativeRect, Button, Board, TextBox
from scripts.ui.map_structure import Map
from scripts.ui.instruction import Instruction
from scripts.entity.player import Player
from scripts.entity.feed_system import FeedSystem
from scripts.manager.cell_manager import CellManager

from scripts.manager.state_manager import GameState
from scripts.render.render import GameRenderer

from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.scene.base_scene import BaseScene
    from scripts.entity.feed_system import Feed

class BaseGame(ABC):
    def __init__(self, scene: "BaseScene", rect: pygame.Rect, player_move_delay: int, grid_size: Tuple[int, int], feed_amount: int, clear_goal: float):
        self.scene = scene
        self.rect = rect
        self.size = rect.size
        self.origin: Tuple[int, int] = tuple(scene.origin[i] + rect.topleft[i] for i in [0, 1])

        self.renderer = GameRenderer()

        self.player_move_delay = player_move_delay
        self.grid_size = grid_size
        self.feed_amount = feed_amount
        self.clear_condition: int = round(self.grid_size[0] * self.grid_size[1] * clear_goal) - INIT_LENGTH

        self.surf = pygame.Surface(self.size)

        self.map: Map = None
        self.map_surface: pygame.Surface = None
        self.player: Player = None
        self.fs: FeedSystem = None
        self.cell_manager: CellManager = None

        self.score_info_list: List[Tuple[str, str, str]] = [] # key, title, content format
        self.instruction_list: List[Tuple[str, str]] = [] # key, act
        self.scores: Dict[str, any] = {}

        self.init_score_info_list()
        self.init_scores()
        
        self.init_instruction_list()

        self.state_layouts: Dict[int, UILayout] = {}

        self.save_buttons: List[Button] = []

        self.init_ui()

        self.state: GameState = None

        self.move_accum: int = 0
        self.direction: str = 'E'
        self.next_direction: str = None  # use for ai pilot game
    
    @abstractmethod
    def init_score_info_list(self):
        pass

    def init_scores(self):
        for key, _, _ in self.score_info_list:
            self.scores[key] = 0

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
        is_landscape = self.rect.size[0] >= self.rect.size[1]
        if is_landscape:
            map_side_len = (self.rect.size[0] // 2)
            board_relative_rect = RelativeRect(0.75, 0.1, 0.25, 0.15)
            board_relative_offset = (0, 0.16)
            instruction_relative_rect = RelativeRect(0, 0.5, 0.25, 0.5)
        else:
            map_side_len = self.rect.size[0]
            board_relative_rect = RelativeRect(0.1, 0.75, 0.15, 0.25)
            board_relative_offset = (0.16, 0)
            instruction_relative_rect = RelativeRect(0, 0.5, 0.25, 0.5)
        self.map_origin = (self.rect.size[0] // 2 - map_side_len // 2, self.rect.size[1] // 2 - map_side_len // 2)

        self.map, self.map_surface = self.create_map(map_side_len, self.grid_size)

        self.renderer.set_cell_side_len(self.map.cell_side_len)
        self.renderer.set_grid_origin(self.map.grid_rect.topleft)
        self.renderer.set_boards(self.create_boards(board_relative_rect, board_relative_offset))
        self.renderer.set_instruction(self.create_instruction(instruction_relative_rect, "Key Instruction", self.instruction_list))

        # about state layouts
        self.init_states_layout()
        self.countdown_textbox = TextBox(self.get_state_layout_rect(), "0", YELLOW)


    # about class object creation
    def create_map(self, map_side_len: int, grid_size: Tuple[int, int], map_outerline_thickness: int = 3, map_outerline_color = (255, 255, 255, 255), grid_outerline_thickness: int = 1, grid_outerline_color=(255, 255, 255, 255), grid_thickness: int = 1, grid_color = (255, 255, 255, 128)) -> Tuple[Map, pygame.Surface]:
        map_rect = pygame.Rect(0, 0, map_side_len, map_side_len)
        map = Map(map_rect, grid_size, map_outerline_thickness, map_outerline_color, grid_outerline_thickness, grid_outerline_color, grid_thickness, grid_color)
        
        surf_size = (map_side_len, map_side_len)
        map_surface = pygame.Surface(surf_size, pygame.SRCALPHA)
        return (map, map_surface)
    
    def create_boards(self, relative_rect: RelativeRect, relative_offset: Tuple[float, float]):
        boards: Dict[str, "Board"] = {}

        for idx, (key, board_title, board_format) in enumerate(self.score_info_list):
            board_offset = (relative_offset[0] * idx, relative_offset[1] * idx)
            curr_board_relative_rect = RelativeRect(relative_rect.relative_x + board_offset[0], relative_rect.relative_y + board_offset[1], relative_rect.relative_width, relative_rect.relative_height)
            board_rect = curr_board_relative_rect.to_absolute(self.size)

            boards[key] = Board(board_rect, board_title, WHITE, format=board_format)
        
        return boards

    def create_instruction(self, relative_rect: RelativeRect, title: str, instruction_list: List[Tuple[str, str]]):
        instruction_rect = relative_rect.to_absolute(self.size)
        instruction = Instruction(instruction_rect, title, instruction_list, WHITE)

        return instruction


    # about setter
    def set_paused_layout(self, layout: UILayout):
        self.state_layouts[GameState.PAUSED] = layout

    def set_gameover_layout(self, layout: UILayout):
        self.state_layouts[GameState.GAMEOVER] = layout

    def set_clear_layout(self, layout: UILayout):
        self.state_layouts[GameState.CLEAR] = layout
    
    def set_state(self, state: GameState):
        if state not in GameState:
            raise ValueError(f"Invalid GameState on `set_state()`: {state}")
        
        self.state = state
        self.on_state_changed() # hooking

    def on_state_changed(self):
        """Methods to be overridden in subclasses"""
        pass


    # about getter
    def get_state_layout_rect(self):
        return RelativeRect(0, 0.3, 1, 0.35).to_absolute(self.rect.size)
    
    def is_state(self, state: GameState) -> bool:
        if state not in GameState:
            raise ValueError(f"Invalid GameState on `is_state()`: {state}")
        
        return self.state == state
    
    def is_in_bound(self, coord) -> bool:
        return self.map.is_inside(coord)
    
    @abstractmethod
    def is_on_move(self) -> bool:
        pass


    # flip
    def flip_game_pause(self):
        if self.is_state(GameState.PAUSED):
            self.set_state(GameState.ACTIVE)
        elif self.is_state(GameState.ACTIVE):
            self.set_state(GameState.PAUSED)
    

    # about progress
    def start_game(self):
        self.cell_manager = CellManager(self.grid_size)
        self.player = Player(self.create_random_bodies(INIT_LENGTH))
        self.fs = FeedSystem()
        self.add_feed_random_coord(self.feed_amount)

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
    
    def start_to_record(self, replay_title: str):
        self.scene.manager.start_to_record(replay_title, self.grid_size, self.score_info_list)

    def add_replay_step(self):
        self.scene.manager.add_replay_step(self.player.get_bodies(), self.direction, self.fs.get_feeds(), self.scores.copy().items())
    
    def save_game(self):
        self.set_save_buttons_selected()
        self.scene.manager.finish_to_record(True) # save replay

    def set_save_buttons_selected(self, is_selected: bool = True):
        """ use to prevent duplicate save """
        for btn in self.save_buttons:
            btn.set_selected(is_selected)


    # functions to update every frame
    def update(self):
        if self.is_state(GameState.ACTIVE):
            self.move_sequence()
        elif self.is_state(GameState.COUNTDOWN):
            self.countdown()
        
    def move_sequence(self):
        if self.is_on_move():
            self.move_accum = 0
            self.add_replay_step()
            self.move_player()
            self.next_direction = None  # valid for ai pilot game
        self.move_accum += 1


    # about game logic
    ## about player logic
    def create_random_bodies(self, length: int) -> List[Tuple[int, int]]:
        grid_num = self.cell_manager.get_grid_size()
        rand_coord = (random.randint(0, grid_num[0] - 1), random.randint(0, grid_num[1] - 1))
        ret = [rand_coord]
        self.cell_manager.mark_cell_used(rand_coord)
        
        dirs = ['E', 'W', 'S', 'N']
        for _ in range(length - 1):
            prev_body_coord = ret[-1]
            dirs_copy = dirs.copy()
            while True:
                dir = dirs_copy[random.randint(0, len(dirs_copy) - 1)]
                dir_offset = DIR_OFFSET_DICT[dir]
                body_coord = (prev_body_coord[0] + dir_offset[0], prev_body_coord[1] + dir_offset[1])
                # validation
                if self.is_in_bound(body_coord) and body_coord not in ret:
                    ret.append(body_coord)
                    self.cell_manager.mark_cell_used(body_coord)

                    # set the player's initial direction to
                    #  the opposite direction of the second body part
                    if self.direction == None:
                        if dir == 'E':
                            self.direction = 'W'
                        elif dir == 'W':
                            self.direction = 'E'
                        elif dir == 'S':
                            self.direction = 'N'
                        else:
                            self.direction = 'S'

                    break
                else:
                    dirs_copy.remove(dir)
        
        return ret

    def set_direction(self, dir: str, with_validate: bool = True):
        if dir not in DIR_OFFSET_DICT:
            raise ValueError("parameter(dir) must be the one of [EWSN]")
        
        if with_validate and not self.validate_direction(dir):
            return
        
        self.direction = dir
    
    def validate_direction(self, dir: str) -> bool:
        next_head = self.player.get_next_head(dir)
        neck = self.player.get_neck()

        # restrict movement towards walls or the neck direction
        return self.is_in_bound(next_head) and next_head != neck
    
    def is_player_body_collision(self, coord: Tuple[int, int]) -> bool:
        """
        Check if the given coordinate collides with the player's body
        (excluding the tail).
        """
        return coord in self.player.get_bodies_without_tail()
    
    def move_player(self):
        tail = self.player.get_tail()
        next_head = self.player.get_next_head(self.direction)

        collision = self.check_collision(next_head)
        # game over when colliding with walls or the player's own body
        if collision[0] in ['wall', 'body']:
            self.set_state(GameState.GAMEOVER)
        elif collision[0] == 'feed':
            curr_feed = collision[1]
            self.eat_feed(next_head, curr_feed)
        else:
            self.basic_movement(next_head, tail)
    
    def eat_feed(self, new_head: Tuple[int, int], feed: "Feed"):
        self.player.add_head(new_head)
        self.fs.remove_feed(feed.get_coord())

        if feed.get_type() == 'normal':
            self.update_score(1)

        # If no feed exists, generate
        if self.is_state(GameState.ACTIVE) and self.fs.is_feed_empty(feed.get_type()):
            self.add_feed_random_coord(self.feed_amount, feed.get_type())

    def basic_movement(self, next_head: Tuple[int, int], tail: Tuple[int, int]):
        self.player.add_head(next_head)
        self.cell_manager.mark_cell_used(next_head)

        self.player.remove_tail()
        self.cell_manager.mark_cell_free(tail)


    ## about feed system logic
    def add_feed(self, coord: Tuple[int, int], feed_type: str = 'normal'):
        self.fs.add_feed(coord, feed_type)
        self.cell_manager.mark_cell_used(coord)
    
    def add_feed_random_coord(self, k: int, feed_type: str = 'normal'):
        if k < 1:
            return

        random_cell_coords = self.cell_manager.get_random_available_cells(k)

        for rand_coord in random_cell_coords:
            self.add_feed(rand_coord, feed_type)

    ## about coordinate system
    def check_collision(self, coord):
        if not self.is_in_bound(coord):
            return 'wall', None
        # 'body' collision is not valid for tail
        if self.is_player_body_collision(coord):
            return 'body', None
        if self.fs.is_feed_exist(coord):
            feed = self.fs.get_feed(coord)
            return 'feed', feed
        return 'none', None

    ## about game flow
    def update_score(self, amount: int = 1):
        self.scores["score"] += amount
        self.renderer.update_board_content("score", self.scores["score"])
        
        if self.clear_condition is not None and self.scores["score"] >= self.clear_condition:
            self.set_state(GameState.CLEAR)
            self.add_replay_step()


    # about handler
    @abstractmethod
    def handle_events(self, events):
        self.handle_state_events(events)

    def handle_state_events(self, events):
        if self.state in [GameState.PAUSED, GameState.GAMEOVER, GameState.CLEAR]:
            self.state_layouts[self.state].handle_events(events)
    

    # about renderer
    def render(self, surf: pygame.Surface):
        self.surf.fill((0, 0, 0))

        self.map_surface.fill((0, 0, 0, 0))

        # render entities
        if self.fs is not None:
            self.renderer.render_feeds(self.map_surface, self.fs.get_feeds())
        if self.player is not None:
            self.renderer.render_player(self.map_surface, self.player.get_bodies())
            self.renderer.render_direction_arrow(self.map_surface, self.player.get_head(), self.direction)

        # render map
        if self.map is not None:
            self.renderer.render_map(self.map_surface, self.map)
            map_rect = self.map_surface.get_rect()
            map_rect.center = self.surf.get_rect().center
            self.renderer.render_outerline(self.surf, map_rect,
                                           self.map.outerline_thickness, self.map.outerline_color)

            self.surf.blit(self.map_surface, map_rect)

        self.renderer.render_ui(self.surf)

        self.render_state_objects(self.surf)

        surf.blit(self.surf, self.rect)

    def render_state_objects(self, surf):
        if self.state in [GameState.PAUSED, GameState.CLEAR, GameState.GAMEOVER]:
            self.state_layouts[self.state].render(surf)
            
        elif self.is_state(GameState.COUNTDOWN):
            self.countdown_textbox.render(surf)