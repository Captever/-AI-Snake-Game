import pygame

from constants import *

from scripts.ui.ui_components import RelativeRect, Board
from scripts.ui.map_structure import Map
from scripts.ui.instruction import Instruction

from scripts.manager.state_manager import GameState
from scripts.render.render import GameRenderer

from typing import Dict, List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.manager.replay_manager import Replay

class ReplayGame:
    def __init__(self, rect: pygame.Rect, replay: "Replay"):
        self.rect = rect
        self.size = rect.size
        self.origin = rect.topleft

        self.renderer = GameRenderer()

        self.move_delay: int = 16 # Ensure that 2x, 4x, 8x, and 16x speeds all divide evenly
        self.grid_size = replay.grid_size

        self.surf = pygame.Surface(self.size)

        self.map: Map = None
        self.map_surface: pygame.Surface = None

        self.score_info_list: List[Tuple[str, str, str]] = replay.score_info_list # key, title, content format
        self.instruction_list: List[Tuple[str, str]] = [] # key, act
        self.scores: Dict[str, any] = {}
        
        self.init_instruction_list()

        self.init_ui()

        self.state: GameState = None

        self.move_accum: int = 0
        self.direction: str = None

        self.step: int = 0
        self.steps = replay.steps
    
    def init_instruction_list(self):
        self.instruction_list = [ # key, act
            ("Space/K", "Play/Pause"),
            ("J", "Prev Step"),
            ("L", "Next Step"),
            ("[", "Rewind"),
            ("]", "Fast-Forward")
        ]

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
    def set_state(self, state: GameState):
        if state not in GameState:
            raise ValueError(f"Invalid GameState on `set_state()`: {state}")
        
        self.state = state
        self.on_state_change() # hooking

    def on_state_change(self):
        """Methods to be overridden in subclasses"""
        pass


    # about getter
    def is_state(self, state: GameState) -> bool:
        if state not in GameState:
            raise ValueError(f"Invalid GameState on `is_state()`: {state}")
        
        return self.state == state

    def is_on_move(self) -> bool:
        return self.move_accum >= self.move_delay


    # flip
    def flip_game_pause(self):
        if self.is_state(GameState.PAUSED):
            self.set_state(GameState.ACTIVE)
        elif self.is_state(GameState.ACTIVE):
            self.set_state(GameState.PAUSED)


    # about progress
    def go_to_step(self, step: int):
        """
        Go to a specific step
        """
        pass

    def go_to_next_step(self):
        """
        Move to the next step
        """
        pass

    def go_to_prev_step(self):
        """
        Move to the previous step
        """
        pass

    def rewind(self):
        pass

    def fastforward(self):
        pass


    # functions to update every frame
    def update(self):
        if self.is_state(GameState.ACTIVE):
            self.move_sequence()

    def move_sequence(self):
        if self.is_on_move():
            self.move_accum = 0
            self.go_to_next_step()
        else:
            self.move_accum += 1
    
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
    
    def handle_keydown(self, key):
        if key == pygame.K_SPACE or key == pygame.K_k:
            # flip play/pause
            self.flip_game_pause()
        elif key == pygame.K_j:
            # prev step
            self.go_to_step(self.step - 1)
        elif key == pygame.K_l:
            # next step
            self.go_to_step(self.step + 1)
        elif key == pygame.K_LEFTBRACKET:
            # rewind
            self.rewind()
        elif key == pygame.K_RIGHTBRACKET:
            # fast forward
            self.fastforward()
    

    # about renderer
    def render(self, surf: pygame.Surface):
        self.surf.fill((0, 0, 0))

        self.map_surface.fill((0, 0, 0, 0))

        curr_step_data = self.steps[self.step]

        # render entities
        self.renderer.render_feeds(self.map_surface, curr_step_data.feeds)
        self.renderer.render_player(self.map_surface, curr_step_data.player_bodies)
        self.renderer.render_direction_arrow(self.map_surface, curr_step_data.player_bodies[0], curr_step_data.player_direction)

        # render map
        if self.map is not None:
            self.renderer.render_map(self.map_surface, self.map)
            map_rect = self.map_surface.get_rect()
            map_rect.center = self.surf.get_rect().center
            self.renderer.render_outerline(self.surf, map_rect,
                                           self.map.outerline_thickness, self.map.outerline_color)

            self.surf.blit(self.map_surface, map_rect)

        self.renderer.render_ui(self.surf)

        surf.blit(self.surf, self.rect)