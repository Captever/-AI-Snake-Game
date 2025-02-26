import pygame

from constants import *

from .base_scene import BaseScene
from scripts.ui.ui_components import UILayout, RelativeRect

from typing import Tuple, Dict

from scripts.game.single_game import SingleGame

# UI state
CONFIG = "config"
IN_GAME = "in_game"

class SingleGameScene(BaseScene):
    def __init__(self, manager, rect: pygame.Rect):
        super().__init__(manager, rect)
        self.game: SingleGame = None
        
        self.ui_state = CONFIG

        self.config_layout = self.create_config_layout()

    def create_config_layout(self):
        layout_relative_rect: RelativeRect

        if self.is_landscape:
            layout_relative_rect = RelativeRect(0.25, 0.16, 0.5, 0.68)
        else:
            layout_relative_rect = RelativeRect(0, 0.25, 1, 0.5)

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute(self.size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout(self.origin, layout_rect, bg_color)

        game_init_layout_name = "game_init"
        layout.add_layout(game_init_layout_name, RelativeRect(0.2, 0.1, 0.6, 0.5), (0, 0, 0, 0))
        game_init_layout = layout.layouts[game_init_layout_name]

        game_init_layout.add_scrollbar(RelativeRect(0, 0, 0.45, 0.15), "Grid Width", 5, 20, 5)
        game_init_layout.add_scrollbar(RelativeRect(0.55, 0, 0.45, 0.15), "Grid Height", 5, 20, 5)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.28, 1, 0.15), "Player Speed", 1, 8, 5)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.56, 1, 0.15), "Feed Amount", 1, 5, 3)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.84, 1, 0.15), "Clear Goal (%)", 50, 100, 90)

        layout.add_button(RelativeRect(0.2, 0.75, 0.25, 0.1), "Start", self.start_game)
        layout.add_button(RelativeRect(0.55, 0.75, 0.25, 0.1), "Cancel", self.return_to_main_scene)

        return layout

    def initialize_game(self, settings: Dict[str, any]):
        # Initialize the game with the given settings
        self.settings = settings
        grid_size: Tuple[int, int] = (int(settings['Grid Width']), int(settings['Grid Height']))
        player_speed: int = int(settings['Player Speed'])
        move_delay = MOVE_DELAY * (10 - player_speed) # min: 2, max: 9
        feed_amount: int = int(settings['Feed Amount'])
        clear_goal: float = settings['Clear Goal (%)'] / 100.0
        game_rect = pygame.Rect(self.rect)
        self.game = SingleGame(self, game_rect, move_delay, grid_size, feed_amount, clear_goal)

    def handle_events(self, events):
        super().handle_events(events)
        
        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # back to main scene
                        self.return_to_main_scene()
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
        self.set_ui_state(IN_GAME)
    
    def restart_new_game(self):
        self.set_ui_state(CONFIG)
        self.manager.finish_to_record() # discard replay
        self.game = None
    
    def return_to_main_scene(self):
        self.manager.set_active_scene("MainScene")

    def update(self):
        ui_state = self.get_ui_state()
        if ui_state == IN_GAME:
            self.game.update()

    def render(self, surf):
        super().render(surf)
        
        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            self.config_layout.render(self.surf)
        elif ui_state == IN_GAME:
            self.game.render(self.surf)

        surf.blit(self.surf, self.origin)
