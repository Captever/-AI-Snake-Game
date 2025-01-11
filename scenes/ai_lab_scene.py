import pygame

from constants import *

from scripts.scene_manager import Scene
from scripts.ui_components import UILayout, RelativeRect
from scripts.ai_manager import AIManager

from instances.game_instance import Game
from instances.ai_instance import AI

from typing import Tuple, Dict, List
from functools import partial

CONFIG, IN_GAME = "config", "in_game"

class AILabScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.game: Game = None

        self.ai_manager: AIManager = AIManager()
        self.ai: AI = None
        self.active_ai = None
        
        self.ui_state = CONFIG

        self.config_layout = self.create_config_layout()

    def create_config_layout(self):
        layout_pos: Tuple[int, int]
        layout_size: Tuple[int, int]

        if IS_LANDSCAPE:
            layout_pos = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 6)
            layout_size = (SCREEN_WIDTH // 1.5, SCREEN_HEIGHT // 1.5)
        else:
            layout_pos = (0, SCREEN_HEIGHT // 6)
            layout_size = (SCREEN_WIDTH, SCREEN_HEIGHT // 1.5)

        layout_rect: pygame.Rect = pygame.Rect(layout_pos + layout_size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout((0, 0), layout_rect, bg_color)

        self.add_game_init_layout(layout)
        self.add_ai_init_layout(layout)

        layout.add_button(RelativeRect(0.2, 0.75, 0.25, 0.1), "Start", self.start_game)
        layout.add_button(RelativeRect(0.55, 0.75, 0.25, 0.1), "Cancel", self.activate_main_scene)

        return layout

    def add_game_init_layout(self, parent_layout: UILayout):
        game_init_layout_name = "game_init"
        parent_layout.add_layout(game_init_layout_name, RelativeRect(0.05, 0.1, 0.5, 0.5), (0, 0, 0, 0))
        game_init_layout = parent_layout.layouts[game_init_layout_name]

        game_init_layout.add_scrollbar(RelativeRect(0, 0, 1, 0.2), "Player Speed", 1, 10, 9)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.4, 0.45, 0.2), "Grid Width", 5, 20, 5)
        game_init_layout.add_scrollbar(RelativeRect(0.55, 0.4, 0.45, 0.2), "Grid Height", 5, 20, 5)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.8, 1, 0.2), "Clear Goal (%)", 50, 100, 90)

    def add_ai_init_layout(self, parent_layout: UILayout):
        ai_init_layout_name = "ai_init"
        parent_layout.add_layout(ai_init_layout_name, RelativeRect(0.6, 0.1, 0.35, 0.5), (0, 0, 0, 0))
        ai_init_layout = parent_layout.layouts[ai_init_layout_name]

        ai_list: List[str] = self.ai_manager.get_ai_list()
        x_offset, y_offset, each_row_num = 0.4, 0.3, 3
        for idx, ai_name in enumerate(ai_list):
            ai_init_layout.add_button(RelativeRect((x_offset % each_row_num) * idx, (y_offset // each_row_num) * idx, 0.3, 0.2), ai_name, partial(self.set_active_ai, ai_name))

    def initialize_game(self, settings: Dict[str, any]):
        # Initialize the game with the given settings
        self.settings = settings
        self.player_speed: int = settings['Player Speed']
        self.grid_size: Tuple[int, int] = (settings['Grid Width'], settings['Grid Height'])
        self.clear_goal: float = settings['Clear Goal (%)'] / 100.0
        self.game = Game(self.player_speed, self.grid_size, self.clear_goal)

    def initialize_ai(self):
        # Initialize the ai with the given settings
        self.ai = AI(self.active_ai)

    def handle_events(self, events):
        super().handle_events(events)
        
        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            self.config_layout.handle_events(events)
        elif ui_state == IN_GAME:
            self.game.handle_events(events)
    
    def set_ui_state(self, state):
        if state not in [CONFIG, IN_GAME]:
            ValueError("invalid UI state")
        
        self.ui_state = state
    
    def get_ui_state(self):
        return self.ui_state

    def start_game(self):
        game_settings = self.config_layout.get_scrollbar_values()
        self.initialize_game(game_settings)
        self.initialize_ai()
        self.set_ui_state(IN_GAME)
    
    def set_active_ai(self, ai_name: str):
        self.active_ai = ai_name
    
    def activate_main_scene(self):
        self.manager.set_active_scene("MainScene")

    def update(self):
        ui_state = self.get_ui_state()
        if ui_state == IN_GAME:
            self.game.update()

    def render(self, surf):
        surf.fill((0, 0, 0))

        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            self.config_layout.render(surf)
        elif ui_state == IN_GAME:
            self.game.render(surf)
