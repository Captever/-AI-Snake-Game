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
        self.option_layout = self.create_option_layout()

        self.menu_state = MAIN_MENU
        self.menu_state = OPTIONS_MENU
    
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

        layout = UILayout(layout_rect, bg_color)

        layout.add_button(RelativeRect(0.25, 0.1, 0.5, 0.15), "Game Start")
        layout.add_button(RelativeRect(0.25, 0.4, 0.5, 0.15), "AI Lab")
        layout.add_button(RelativeRect(0.25, 0.7, 0.5, 0.15), "Record")

        return layout

    def create_option_layout(self):
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

        layout = UILayout(layout_rect, bg_color)

        layout.add_scrollbar(RelativeRect(0.2, 0.1, 0.6, 0.1), "Player Speed", 1, 10, 5)
        layout.add_scrollbar(RelativeRect(0.2, 0.3, 0.6, 0.1), "Grid Size", 5, 20, 10)
        layout.add_scrollbar(RelativeRect(0.2, 0.5, 0.6, 0.1), "Clear Goal (%)", 50, 100, 70)

        layout.add_button(RelativeRect(0.2, 0.75, 0.25, 0.1), "Start")
        layout.add_button(RelativeRect(0.55, 0.75, 0.25, 0.1), "Cancel")

        return layout

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # if self.menu_state == MAIN_MENU:
            #     for button in self.menu_buttons:
            #         if button.is_hovered(pygame.mouse.get_pos()) and button.is_clicked(event):
            #             if button.text == "Game Start":
            #                 self.menu_state = OPTIONS_MENU
            #             elif button.text == "AI Lab":
            #                 self.manager.set_active_scene("AILabScene")
            #             elif button.text == "Record":
            #                 self.manager.set_active_scene("RecordScene")
            # elif self.menu_state == OPTIONS_MENU:
            #     for scrollbar in self.options_scrollbars.values():
            #         scrollbar.handle_event(event)
            #     for button in self.options_buttons:
            #         if button.is_hovered(pygame.mouse.get_pos()) and button.is_clicked(event):
            #             if button.text == "Start":
            #                 self.manager.set_active_scene("GameScene")
            #             elif button.text == "Cancel":
            #                 self.menu_state = MAIN_MENU
                            

    def render(self, surf):
        surf.fill((0, 0, 0))

        if self.menu_state == MAIN_MENU:
            self.menu_layout.render(surf)
            # for button in self.menu_buttons:
            #     button.is_hovered(pygame.mouse.get_pos())
            #     button.render(surf)

        elif self.menu_state == OPTIONS_MENU:
            self.option_layout.render(surf)
            # for name, scrollbar in self.options_scrollbars.items():
            #     scrollbar.render(screen, name)
            # for button in self.options_buttons:
            #     button.is_hovered(pygame.mouse.get_pos())
            #     button.render(surf)