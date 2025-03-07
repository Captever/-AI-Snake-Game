import pygame

from constants import *

from .base_scene import BaseScene
from scripts.ui.ui_components import UILayout, RelativeRect

from typing import Tuple

class MainScene(BaseScene):
    def __init__(self, manager, rect: pygame.Rect):
        super().__init__(manager, rect)

        self.menu_layout = self.create_menu_layout()
    
    def get_centered_rect(self, base_size: Tuple[int, int], offset_ratio: Tuple[float, float]) -> pygame.Rect:
        screen_center = (self.size[0] // 2, self.size[1] // 2)
        origin_pos = (screen_center[0] - base_size[0] // 2, screen_center[1] - base_size[1] // 2)

        offset = tuple(base_size[i] * offset_ratio[i] for i in [0, 1])
        return pygame.Rect((origin_pos[0] + offset[0], origin_pos[1] + offset[1]) + base_size)

    def create_menu_layout(self):
        layout_relative_rect: RelativeRect

        if self.is_landscape:
            layout_relative_rect = RelativeRect(0.25, 0.16, 0.5, 0.68)
        else:
            layout_relative_rect = RelativeRect(0, 0.25, 1, 0.5)

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute(self.size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout(self.origin, layout_rect, bg_color)

        layout.add_button(RelativeRect(0.25, 0.1, 0.5, 0.15), "Game Start", self.activate_game_scene)
        layout.add_button(RelativeRect(0.25, 0.4, 0.5, 0.15), "AI Lab", self.activate_ai_lab_scene)
        layout.add_button(RelativeRect(0.25, 0.7, 0.5, 0.15), "Record", self.activate_record_scene)

        return layout


    def handle_events(self, events):
        super().handle_events(events)
        
        self.menu_layout.handle_events(events)
        
    def activate_game_scene(self):
        self.manager.set_active_scene("GameScene")
        
    def activate_ai_lab_scene(self):
        self.manager.set_active_scene("AILabScene")
        
    def activate_record_scene(self):
        self.manager.set_active_scene("RecordScene")

    def render(self, surf):
        super().render(surf)

        self.menu_layout.render(self.surf)

        surf.blit(self.surf, self.origin)