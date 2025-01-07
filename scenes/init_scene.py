import pygame
import sys

from scripts.scene_manager import Scene
from scripts.menu_system import Button

class InitScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        font_size = manager.get_standard_font_size()
        self.buttons = [
            Button("Game Start", (300, 200, 200, 50), font_size),
            Button("Options", (300, 300, 200, 50), font_size),
            Button("Exit", (300, 400, 200, 50), font_size),
        ]

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if button.is_hovered(pygame.mouse.get_pos()) and button.is_clicked(event):
                        if button.text == "Game Start":
                            self.manager.set_active_scene("GameScene")
                        elif button.text == "Options":
                            self.manager.set_active_scene("OptionsScene")
                        elif button.text == "Exit":
                            pygame.quit()
                            sys.exit()

    def render(self, screen):
        screen.fill((0, 0, 0))
        for button in self.buttons:
            button.is_hovered(pygame.mouse.get_pos())
            button.render(screen)
