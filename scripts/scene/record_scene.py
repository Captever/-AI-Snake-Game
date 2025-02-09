import pygame

from constants import *

from .base_scene import Scene
from scripts.ui.ui_components import UILayout, RelativeRect

from typing import Tuple

class RecordScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.replay_list_layout = self.create_replay_list_layout()
        self.playback_tool_layout = self.create_playback_tool_layout()
    
    def get_centered_rect(self, base_size: Tuple[int, int], offset_ratio: Tuple[float, float]) -> pygame.Rect:
        screen_center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        origin_pos = (screen_center[0] - base_size[0] // 2, screen_center[1] - base_size[1] // 2)

        offset = tuple(base_size[i] * offset_ratio[i] for i in [0, 1])
        return pygame.Rect((origin_pos[0] + offset[0], origin_pos[1] + offset[1]) + base_size)

    def create_replay_list_layout(self):
        layout_relative_rect: RelativeRect

        if IS_LANDSCAPE:
            layout_relative_rect = RelativeRect(0.05, 0.05, 0.25, 0.9)
        else:
            layout_relative_rect = RelativeRect(0.1, 0.5, 0.8, 0.25)

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_color = (50, 50, 50, 50)

        layout = UILayout((0, 0), layout_rect, bg_color)

        outerline_thickness = 1
        layout.add_outerline(outerline_thickness)
        
        # TODO: Add ScrollArea which is for showing replay list
        #     + Add replays as button into scrollArea & accept `set_selected_replay` function to button's callback

        return layout
    
    def create_playback_tool_layout(self):
        layout_relative_rect: RelativeRect

        if IS_LANDSCAPE:
            layout_relative_rect = RelativeRect(0.35, 0.8, 0.6, 0.15)
        else:
            layout_relative_rect = RelativeRect(0.05, 0.8, 0.9, 0.15)

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute((SCREEN_WIDTH, SCREEN_HEIGHT))
        bg_color = (50, 50, 50, 50)

        layout = UILayout((0, 0), layout_rect, bg_color)

        return layout
    
    def handle_events(self, events):
        super().handle_events(events)
        
        self.replay_list_layout.handle_events(events)
        self.playback_tool_layout.handle_events(events)

    def set_selected_replay(self, replay_list_layout: UILayout, replay_index: str):
        replay_list_layout.update_radio_selection(replay_index)
        self.target_ai_name = replay_index

    def render(self, surf):
        surf.fill((0, 0, 0))

        self.replay_list_layout.render(surf)
        self.playback_tool_layout.render(surf)