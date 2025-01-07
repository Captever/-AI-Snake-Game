import pygame
import sys

from constants import *

from scripts.scene_manager import Scene
from scripts.ui_components import Button, ScrollBar

from typing import Tuple

MAIN_MENU, OPTIONS_MENU = "MainMenu", "OptionsMenu"

class InitScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.menu_buttons = [
            Button("Game Start", self.get_centered_rect((BUTTON_WIDTH, BUTTON_HEIGHT), (0, -BUTTON_OFFSET_RATIO)), BUTTON_FONT_SIZE),
            Button("AI Lab", self.get_centered_rect((BUTTON_WIDTH, BUTTON_HEIGHT), (0, 0)), BUTTON_FONT_SIZE),
            Button("Record", self.get_centered_rect((BUTTON_WIDTH, BUTTON_HEIGHT), (0, BUTTON_OFFSET_RATIO)), BUTTON_FONT_SIZE),
        ]
        
        self.options_buttons = [
            Button("Start", self.get_centered_rect((BUTTON_WIDTH // 2.5, BUTTON_HEIGHT), (-BUTTON_OFFSET_RATIO * 0.5, BUTTON_OFFSET_RATIO * 2)), BUTTON_FONT_SIZE),
            Button("Cancel", self.get_centered_rect((BUTTON_WIDTH // 2.5, BUTTON_HEIGHT), (BUTTON_OFFSET_RATIO * 0.5, BUTTON_OFFSET_RATIO * 2)), BUTTON_FONT_SIZE)
        ]
        self.options_scrollbars = {
            "Player Speed": ScrollBar(self.get_centered_rect((SCROLL_BAR_WIDTH, SCROLL_BAR_HEIGHT), (0, -SCROLL_BAR_OFFSET_RATIO)), SCROLL_BAR_FONT_SIZE, 1, 10, 5),
            "Grid Size": ScrollBar(self.get_centered_rect((SCROLL_BAR_WIDTH, SCROLL_BAR_HEIGHT), (0, 0)), SCROLL_BAR_FONT_SIZE, 5, 20, 10),
            "Clear Goal (%)": ScrollBar(self.get_centered_rect((SCROLL_BAR_WIDTH, SCROLL_BAR_HEIGHT), (0, SCROLL_BAR_OFFSET_RATIO)), SCROLL_BAR_FONT_SIZE, 50, 100, 70),
        }

        self.menu_state = MAIN_MENU
    
    def get_centered_rect(self, base_size: Tuple[int, int], offset_ratio: Tuple[float, float]) -> pygame.Rect:
        screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        origin_pos = (screen_center[0] - base_size[0] // 2, screen_center[1] - base_size[1] // 2)

        offset = tuple(base_size[i] * offset_ratio[i] for i in [0, 1])
        return pygame.Rect((origin_pos[0] + offset[0], origin_pos[1] + offset[1]) + base_size)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if self.menu_state == MAIN_MENU:
                for button in self.menu_buttons:
                    if button.is_hovered(pygame.mouse.get_pos()) and button.is_clicked(event):
                        if button.text == "Game Start":
                            self.menu_state = OPTIONS_MENU
                        elif button.text == "AI Lab":
                            self.manager.set_active_scene("AILabScene")
                        elif button.text == "Record":
                            self.manager.set_active_scene("RecordScene")
            elif self.menu_state == OPTIONS_MENU:
                for scrollbar in self.options_scrollbars.values():
                    scrollbar.handle_event(event)
                for button in self.options_buttons:
                    if button.is_hovered(pygame.mouse.get_pos()) and button.is_clicked(event):
                        if button.text == "Start":
                            self.manager.set_active_scene("GameScene")
                        elif button.text == "Cancel":
                            self.menu_state = MAIN_MENU
                            

    def render(self, screen):
        screen.fill((0, 0, 0))

        if self.menu_state == MAIN_MENU:
            for button in self.menu_buttons:
                button.is_hovered(pygame.mouse.get_pos())
                button.render(screen)

        elif self.menu_state == OPTIONS_MENU:
            for name, scrollbar in self.options_scrollbars.items():
                scrollbar.render(screen, name)
            for button in self.options_buttons:
                button.is_hovered(pygame.mouse.get_pos())
                button.render(screen)