import pygame

from constants import *

from .base_scene import BaseScene
from scripts.ui.ui_components import UILayout, RelativeRect, ScrollBar

from scripts.game.replay_game import ReplayGame

from typing import Tuple
from functools import partial

class RecordScene(BaseScene):
    def __init__(self, manager, rect: pygame.Rect):
        super().__init__(manager, rect)

        self.replay_game: ReplayGame = None
        self.progress_scrollbar: ScrollBar = None

        self.replay_game_rect = self.create_replay_game_rect()
        self.replay_list_layout = self.create_replay_list_layout()
        self.playback_tool_layout = self.create_playback_tool_layout()
    
    def get_centered_rect(self, base_size: Tuple[int, int], offset_ratio: Tuple[float, float]) -> pygame.Rect:
        screen_center = (self.size[0] // 2, self.size[1] // 2)
        origin_pos = (screen_center[0] - base_size[0] // 2, screen_center[1] - base_size[1] // 2)

        offset = tuple(base_size[i] * offset_ratio[i] for i in [0, 1])
        return pygame.Rect((origin_pos[0] + offset[0], origin_pos[1] + offset[1]) + base_size)

    def create_replay_game_rect(self) -> pygame.Rect:
        game_relative_rect: RelativeRect

        if self.is_landscape:
            game_relative_rect = RelativeRect(0.35, 0.05, 0.6, 0.6)
        else:
            game_relative_rect = RelativeRect(0.05, 0.025, 0.9, 0.375)
        
        game_rect: pygame.Rect = game_relative_rect.to_absolute(self.size)

        return game_rect

    def create_replay_list_layout(self):
        layout_relative_rect: RelativeRect

        if self.is_landscape:
            layout_relative_rect = RelativeRect(0.05, 0.05, 0.25, 0.9)
            replay_button_relative_y_offset, replay_button_relative_height = 0.07, 0.06
        else:
            layout_relative_rect = RelativeRect(0.15, 0.45, 0.7, 0.3)
            replay_button_relative_y_offset, replay_button_relative_height = 0.15, 0.13

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute(self.size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout(self.origin, layout_rect, bg_color)

        outerline_thickness = 1
        layout.add_outerline(outerline_thickness)

        replay_list = self.manager.get_replay_list()

        for idx, replay_name in enumerate(replay_list):
            layout.add_button(RelativeRect(0, replay_button_relative_y_offset * idx, 1, replay_button_relative_height), replay_name, partial(self.set_selected_replay, layout, idx))
        
        # TODO: Add ScrollArea which is for showing replay list
        #     + Add replays as button into scrollArea & accept `set_selected_replay` function to button's callback

        return layout
    
    def create_playback_tool_layout(self):
        layout_relative_rect: RelativeRect

        if self.is_landscape:
            layout_relative_rect = RelativeRect(0.35, 0.72, 0.6, 0.18)
            progress_layout_relative_rect = RelativeRect(0, 0, 1, 0.35)
            tool_layout_relative_rect = RelativeRect(0.25, 0.55, 0.5, 0.45)
        else:
            layout_relative_rect = RelativeRect(0.05, 0.8, 0.9, 0.15)
            progress_layout_relative_rect = RelativeRect(0, 0, 1, 0.4)
            tool_layout_relative_rect = RelativeRect(0.1, 0.65, 0.8, 0.35)

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute(self.size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout(self.origin, layout_rect, bg_color)

        progress_layout = layout.add_layout("progress", progress_layout_relative_rect, (20,20,20,255))
        if self.is_landscape:
            self.progress_scrollbar = progress_layout.add_scrollbar(RelativeRect(0.06, 0.2, 0.88, 0.6), "Step", 1, 99, 1, show_max_val=True)
            progress_layout.add_button(RelativeRect(0, 0.5, 0.03, 0.5), "◀")
            progress_layout.add_button(RelativeRect(0.97, 0.5, 0.03, 0.5), "▶")
        else:
            self.progress_scrollbar = progress_layout.add_scrollbar(RelativeRect(0.1, 0.2, 0.8, 0.6), "Step", 1, 99, 1, show_max_val=True)
            progress_layout.add_button(RelativeRect(0, 0.5, 0.08, 0.5), "◀")
            progress_layout.add_button(RelativeRect(0.92, 0.5, 0.08, 0.5), "▶")

        tool_layout = layout.add_layout("tool", tool_layout_relative_rect, (20,20,20,255))
        tool_text_list = ["I◀", "◀◀", "▶/II", "▶▶", "▶I"]
        for idx, text in enumerate(tool_text_list):
            tool_layout.add_button(RelativeRect(idx * 0.2125, 0, 0.15, 1), text=text)

        return layout
    
    def handle_events(self, events):
        super().handle_events(events)
        
        if self.replay_game is not None:
            self.replay_game.handle_events(events)
        self.replay_list_layout.handle_events(events)
        self.playback_tool_layout.handle_events(events)

    def set_selected_replay(self, replay_list_layout: UILayout, replay_index: int):
        replay_list_layout.update_radio_selection(replay_index)
        self.replay_game = self.manager.get_replay_game(replay_index, self.replay_game_rect)

    def render(self, surf):
        super().render(surf)

        if self.replay_game is not None:
            self.replay_game.render(self.surf)
        self.replay_list_layout.render(self.surf)
        self.playback_tool_layout.render(self.surf)

        surf.blit(self.surf, self.origin)