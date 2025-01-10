import pygame
import sys

from constants import *

from scripts.scene_manager import Scene
from scripts.ui_components import UILayout, RelativeRect

from typing import Tuple

MAIN_MENU, OPTIONS_MENU = "MainMenu", "OptionsMenu"

class InitScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.menu_layout = self.create_menu_layout()
        self.options_layout = self.create_options_layout()

        self.menu_state = MAIN_MENU
    
    def get_centered_rect(self, base_size: Tuple[int, int], offset_ratio: Tuple[float, float]) -> pygame.Rect:
        screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        origin_pos = (screen_center[0] - base_size[0] // 2, screen_center[1] - base_size[1] // 2)

        offset = tuple(base_size[i] * offset_ratio[i] for i in [0, 1])
        return pygame.Rect((origin_pos[0] + offset[0], origin_pos[1] + offset[1]) + base_size)

    def create_menu_layout(self):
        layout_pos: Tuple[int, int]
        layout_size: Tuple[int, int]

        if IS_LANDSCAPE:
            layout_pos = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6)
            layout_size = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
        else:
            layout_pos = (0, SCREEN_HEIGHT // 4)
            layout_size = (SCREEN_WIDTH, SCREEN_HEIGHT // 2)

        layout_rect: pygame.Rect = pygame.Rect(layout_pos + layout_size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout((0, 0), layout_rect, bg_color)

        layout.add_button(RelativeRect(0.25, 0.1, 0.5, 0.15), "Game Start", self.show_options_menu)
        layout.add_button(RelativeRect(0.25, 0.4, 0.5, 0.15), "AI Lab", self.open_ai_lab)
        layout.add_button(RelativeRect(0.25, 0.7, 0.5, 0.15), "Record", self.open_record)

        return layout

    def create_options_layout(self):
        layout_pos: Tuple[int, int]
        layout_size: Tuple[int, int]

        if IS_LANDSCAPE:
            layout_pos = (SCREEN_WIDTH // 4, SCREEN_HEIGHT // 6)
            layout_size = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 1.5)
        else:
            layout_pos = (0, SCREEN_HEIGHT // 4)
            layout_size = (SCREEN_WIDTH, SCREEN_HEIGHT // 2)

        layout_rect: pygame.Rect = pygame.Rect(layout_pos + layout_size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout((0, 0), layout_rect, bg_color)

        layout.add_scrollbar(RelativeRect(0.2, 0.1, 0.6, 0.1), "Player Speed", 1, 10, 9)
        layout.add_scrollbar(RelativeRect(0.2, 0.3, 0.6, 0.1), "Grid Size", 5, 20, 5)
        layout.add_scrollbar(RelativeRect(0.2, 0.5, 0.6, 0.1), "Clear Goal (%)", 50, 100, 90)

        layout.add_button(RelativeRect(0.2, 0.75, 0.25, 0.1), "Start", self.start_game)
        layout.add_button(RelativeRect(0.55, 0.75, 0.25, 0.1), "Cancel", self.show_main_menu)

        return layout

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
        if self.menu_state == MAIN_MENU:
            self.menu_layout.handle_events(events)
        elif self.menu_state == OPTIONS_MENU:
            self.options_layout.handle_events(events)

    def set_menu_state(self, state):
        if state not in [MAIN_MENU, OPTIONS_MENU]:
            raise ValueError("invalid menu state")
        
        self.menu_state = state
        
    def start_game(self):
        game_settings = self.options_layout.get_scrollbar_values()
        self.manager.set_active_scene("GameScene", settings=game_settings)
        
    def open_ai_lab(self):
        self.manager.set_active_scene("AILabScene")
        
    def open_record(self):
        self.manager.set_active_scene("RecordScene")
    
    def show_main_menu(self):
        self.set_menu_state(MAIN_MENU)
    
    def show_options_menu(self):
        self.set_menu_state(OPTIONS_MENU)

    def render(self, surf):
        surf.fill((0, 0, 0))

        if self.menu_state == MAIN_MENU:
            self.menu_layout.render(surf)
        elif self.menu_state == OPTIONS_MENU:
            self.options_layout.render(surf)