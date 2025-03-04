import pygame

from constants import *

from .base_scene import BaseScene
from scripts.ui.ui_components import UILayout, RelativeRect, ScrollBar, ScrollArea
from scripts.manager.state_manager import ReplayState

from scripts.game.replay_game import ReplayGame

from typing import Tuple

from functools import partial

class RecordScene(BaseScene):
    def __init__(self, manager, rect: pygame.Rect):
        super().__init__(manager, rect)

        self.replay_list_area: UILayout = None
        self.playback_tool_layout: UILayout = None

        self.replay_game: ReplayGame = None
        self.progress_scrollbar: ScrollBar = None

        self.state: ReplayState = ReplayState.PAUSE  # Start in a paused state

        self.step_delay: int = 16  # Ensure that 2x, 4x, 8x, and 16x speeds all divide evenly
        self.step_weight: int = 1
        self.step_accum: int = 0  # accumulate value for stepping


    # about creation ui object
    def create_replay_list_area(self):
        area_relative_rect: RelativeRect

        if self.is_landscape:
            area_relative_rect = RelativeRect(0.05, 0.05, 0.25, 0.9)
            replay_button_relative_y_offset, replay_button_relative_height = 0.07, 0.06
        else:
            area_relative_rect = RelativeRect(0.15, 0.45, 0.7, 0.3)
            replay_button_relative_y_offset, replay_button_relative_height = 0.15, 0.13

        replay_list = self.manager.get_replay_list()  # uuid, title, timestamp, steps_num, final_score
        replay_num = len(replay_list)

        scroll_area_rect: pygame.Rect = area_relative_rect.to_absolute(self.size)
        scroll_area_content_height = replay_button_relative_y_offset * replay_num * scroll_area_rect.height
        scroll_area_content_size: Tuple[int, int] = (self.size[0], scroll_area_content_height)
        bg_color = (50, 50, 50, 50)

        scroll_area = ScrollArea(self.origin, scroll_area_rect, scroll_area_content_size, bg_color)

        outerline_thickness = 1
        scroll_area.add_outerline(outerline_thickness)

        for idx, (_, title, timestamp, steps_num, final_score) in enumerate(replay_list):
            scroll_area.add_replay_button(RelativeRect(0, replay_button_relative_y_offset * idx, 1, replay_button_relative_height), title, timestamp, int(steps_num), int(final_score), partial(self.set_selected_replay, scroll_area, idx))

        return scroll_area
    
    def create_replay_game_rect(self) -> pygame.Rect:
        game_relative_rect: RelativeRect

        if self.is_landscape:
            game_relative_rect = RelativeRect(0.35, 0.05, 0.6, 0.6)
        else:
            game_relative_rect = RelativeRect(0.05, 0.025, 0.9, 0.375)
        
        game_rect: pygame.Rect = game_relative_rect.to_absolute(self.size)

        return game_rect

    def create_playback_tool_layout(self):
        layout_relative_rect: RelativeRect

        if self.is_landscape:
            layout_relative_rect = RelativeRect(0.35, 0.72, 0.6, 0.18)
            progress_layout_relative_rect = RelativeRect(0, 0, 1, 0.35)
            tool_layout_relative_rect = RelativeRect(0.25, 0.55, 0.5, 0.45)

            progress_scrollbar_relative_rect = RelativeRect(0.06, 0.2, 0.88, 0.6)
            prev_step_button_relative_rect = RelativeRect(0, 0.5, 0.03, 0.5)
            next_step_button_relative_rect = RelativeRect(0.97, 0.5, 0.03, 0.5)
        else:
            layout_relative_rect = RelativeRect(0.05, 0.8, 0.9, 0.15)
            progress_layout_relative_rect = RelativeRect(0, 0, 1, 0.4)
            tool_layout_relative_rect = RelativeRect(0.1, 0.65, 0.8, 0.35)

            progress_scrollbar_relative_rect = RelativeRect(0.1, 0.2, 0.8, 0.6)
            prev_step_button_relative_rect = RelativeRect(0, 0.5, 0.08, 0.5)
            next_step_button_relative_rect = RelativeRect(0.92, 0.5, 0.08, 0.5)

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute(self.size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout(self.origin, layout_rect, bg_color)

        if self.replay_game is None:
            raise ValueError("`self.replay_game` is None")
        min_step, max_step = self.replay_game.min_step, self.replay_game.max_step
        progress_layout = layout.add_layout("progress", progress_layout_relative_rect, (20,20,20,255))
        self.progress_scrollbar = progress_layout.add_scrollbar(progress_scrollbar_relative_rect, "Step", min_step, max_step, 1, callback=self.update_step_by_scrollbar, show_max_val=True)
        progress_layout.add_button(prev_step_button_relative_rect, "◀", self.go_to_prev_step)
        progress_layout.add_button(next_step_button_relative_rect, "▶", self.go_to_next_step)

        tool_layout = layout.add_layout("tool", tool_layout_relative_rect, (20,20,20,255))
        tool_list = [  # showing text, callback function
            ("I◀", self.go_to_first_step),
            ("◀◀", self.rewind),
            ("▶/II", self.flip_replay_pause),
            ("▶▶", self.fastforward),
            ("▶I", self.go_to_last_step)]
        for idx, (text, callback) in enumerate(tool_list):
            tool_layout.add_button(RelativeRect(idx * 0.2125, 0, 0.15, 1), title=text, callback=callback)

        return layout


    # about setter
    def set_state(self, state: ReplayState):
        if state not in ReplayState:
            raise ValueError(f"Invalid ReplayState on `set_state()`: {state}")
        
        self.state = state
        self.on_state_change() # hooking

    def on_state_change(self):
        if self.is_state(ReplayState.PAUSE):
            self.step_weight = 1  # Reset playback speed to 1x immediately after transitioning to pause state


    # about getter
    def is_state(self, state: ReplayState) -> bool:
        if state not in ReplayState:
            raise ValueError(f"Invalid ReplayState on `is_state()`: {state}")
        
        return self.state == state

    def is_on_step(self) -> bool:
        is_on_delay: bool = self.step_accum >= abs(self.step_delay / self.step_weight)
        return is_on_delay


    # flip
    def flip_replay_pause(self):
        if self.is_state(ReplayState.PAUSE):
            self.set_state(ReplayState.PLAY)
        else:
            self.set_state(ReplayState.PAUSE)


    # about replay system
    def update_step_by_scrollbar(self, step):
        self.replay_game.go_to_step(step)

    def refresh_replay_list_layout(self):
        self.replay_list_area = self.create_replay_list_area()
        self.clear_replay_state()

    def set_selected_replay(self, replay_list_area: ScrollArea, replay_index: int):
        replay_list_area.update_radio_selection(replay_index)
        self.replay_game = self.manager.get_replay_game(replay_index, self.create_replay_game_rect())

        self.playback_tool_layout = self.create_playback_tool_layout()

        self.set_state(ReplayState.PLAY)  # Switch to PLAY state when a replay is selected

    def go_to_step(self, step: int):
        self.progress_scrollbar.update_value(step)
        self.replay_game.go_to_step(step)

    def go_to_first_step(self):
        """
        Move to the first step
        """
        self.go_to_step(self.replay_game.min_step)

    def go_to_last_step(self):
        """
        Move to the last step
        """
        self.go_to_step(self.replay_game.max_step)

    def go_to_next_step(self):
        """
        Move to the next step
        """
        curr_step = self.replay_game.step
        next_step = min(curr_step + 1, self.replay_game.max_step)

        self.go_to_step(next_step)

    def go_to_prev_step(self):
        """
        Move to the previous step
        """
        curr_step = self.replay_game.step
        prev_step = max(curr_step - 1, self.replay_game.min_step)

        self.go_to_step(prev_step)

    def rewind(self):
        if self.step_weight <= -16:
            return

        if self.step_weight == 1:
            self.set_state(ReplayState.REWIND)  # transition state when changing to reverse speed
            self.step_weight = -1
        elif self.step_weight < 0:
            self.step_weight *= 2
        else:
            self.step_weight //= 2

            if self.step_weight == 1:  # transition state when changing to 1x speed
                self.set_state(ReplayState.PLAY)

    def fastforward(self):
        if self.step_weight >= 16:
            return

        if self.step_weight == -1:
            self.set_state(ReplayState.PLAY)  # transition state when changing to 1x speed
            self.step_weight = 1
        elif self.step_weight < 0:
            self.step_weight //= 2
        else:
            self.step_weight *= 2

            if self.step_weight == 2:  # transition state when changing to 2x speed
                self.set_state(ReplayState.FASTFORWARD)

    
    # about progress
    def return_to_main_scene(self):
        self.manager.set_active_scene("MainScene")
        self.clear_replay_state()

    def clear_replay_state(self):
        self.replay_game = None
        self.playback_tool_layout = None

    def on_scene_changed(self):
        self.refresh_replay_list_layout()


    # functions to update every frame
    def update(self):
        if not self.is_state(ReplayState.PAUSE) and self.replay_game is not None:
            self.step_sequence()

    def step_sequence(self):
        to_reverse: bool = self.step_weight < 0
        if self.replay_game.is_stepable(to_reverse=to_reverse):
            if self.is_on_step():
                self.step_accum = 0
                if to_reverse:
                    self.go_to_prev_step()
                else:
                    self.go_to_next_step()
            self.step_accum += 1
        elif not self.is_state(ReplayState.PAUSE):
            self.set_state(ReplayState.PAUSE)
    

    # about every frame routine
    def handle_events(self, events):
        super().handle_events(events)
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
                
        self.replay_list_area.handle_events(events)
        if self.replay_game is not None:
            self.playback_tool_layout.handle_events(events)
    
    def handle_keydown(self, key):
        if key == pygame.K_ESCAPE:
            # back to main scene
            self.return_to_main_scene()
        elif key == pygame.K_SPACE or key == pygame.K_k:
            # flip play/pause
            self.flip_replay_pause()
        elif key == pygame.K_j:
            # prev step
            self.go_to_prev_step()
        elif key == pygame.K_l:
            # next step
            self.go_to_next_step()
        elif key == pygame.K_LEFTBRACKET:
            # rewind
            self.rewind()
        elif key == pygame.K_RIGHTBRACKET:
            # fast forward
            self.fastforward()

    def render(self, surf):
        super().render(surf)

        self.replay_list_area.render(self.surf)
        if self.replay_game is not None:
            self.replay_game.render(self.surf)
            self.playback_tool_layout.render(self.surf)

        surf.blit(self.surf, self.origin)