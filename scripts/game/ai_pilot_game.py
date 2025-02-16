import pygame

from scripts.game.base_game import BaseGame
from scripts.ai.base_ai import BaseAI

from constants import *

from scripts.ui.ui_components import UILayout, RelativeRect

from scripts.manager.game_manager import GameState

from typing import Tuple

from scripts.ai.q_learning import QLearningAI

class AIPilotGame(BaseGame):
    def __init__(self, scene, rect: pygame.Rect, pilot_ai: BaseAI, player_move_delay: int, grid_size: Tuple[int, int], feed_amount: int, clear_goal: float):
        super().__init__(scene, rect, player_move_delay, grid_size, feed_amount, clear_goal)
        self.pilot_ai = pilot_ai

        self.final_epoch_flag: bool = False # If true, terminate at the current epoch
        self.enable_speed_limit_flag: bool = False # If true, enable speed restriction
        
        self.curr_direction: str = None

        self.start_game()

    def init_score_info_list(self):
        self.score_info_list = [ # key, title, content format, default value
            ("top_score", "TOP", "{:,}", 0),
            ("score", "Score", "{:,}", 0),
            ("epoch", "Epoch", "{:,}", 0),
            ("avg_score_last_100", "Average Last 100", "{:,.3f}", 0.0),
            ("overall_avg_score", "Overall Average", "{:,.3f}", 0.0)
        ]
    
    def init_instruction_list(self):
        self.instruction_list = [ # key, act
            ("P", "Pause"),
            ("E", "Set as final epoch"),
            ("Q", "Enable speed limit")
        ]

    def init_paused_layout(self, rect):
        layout: UILayout = UILayout(self.origin, rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "PAUSED", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.3, 0, 0.4, 1), "New", self.scene.restart_new_game)

        self.set_paused_layout(layout)
    
    def init_gameover_layout(self, rect):
        layout: UILayout = UILayout(self.origin, rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "GAME OVER", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.025, 0, 0.3, 1), "Continue", self.restart_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.35, 0, 0.3, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.675, 0, 0.3, 1), "Save")

        self.set_gameover_layout(layout)
    
    def init_clear_layout(self, rect):
        layout: UILayout = UILayout(self.origin, rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "CLEAR", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.025, 0, 0.3, 1), "Continue", self.restart_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.35, 0, 0.3, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.675, 0, 0.3, 1), "Save")

        self.set_clear_layout(layout)


    def on_state_change(self):
        if self.is_state(GameState.GAMEOVER):
            if isinstance(self.pilot_ai, QLearningAI):
                self.pilot_ai.learn(-1, None)
            self.handle_game_end()

        elif self.is_state(GameState.CLEAR):
            self.handle_game_end()

    
    def is_on_move_delay(self) -> bool:
        # If enable_speed_limit_flag is true, enable speed restriction
        return not self.enable_speed_limit_flag or self.move_accum >= self.player_move_delay
    
    def is_decided_next_direction(self) -> bool:
        return self.next_direction is not None

    def is_on_move(self) -> bool:
        return self.is_on_move_delay() and self.is_decided_next_direction()
    
    def is_ended_process(self) -> bool:
        # If final_epoch_flag is true, terminate at the current epoch
        return self.final_epoch_flag
    
    
    def start_game(self):
        super().start_game()

        self.scores["epoch"] += 1
        self.boards["epoch"].update_content(self.scores["epoch"])

        self.final_epoch_flag = False
        
        self.set_state(GameState.ACTIVE)
    
    def restart_game(self):
        self.scores["score"] = 0
        self.boards["score"].reset()
        self.start_game()
    
    def update(self):
        super().update()

        if self.player is not None and self.is_state(GameState.ACTIVE) and self.next_direction is None:
            self.next_direction = self.pilot_ai.decide_direction()
            if self.next_direction == "surrender": # Maintain previous movement upon surrender
                self.next_direction = self.curr_direction
            else: # No need to reset when maintaining the same direction
                self.curr_direction = self.next_direction
                self.player.set_direction(self.next_direction, False)
    

    def flip_final_epoch_flag(self):
        self.final_epoch_flag = not self.final_epoch_flag

    def flip_speed_limit_flag(self):
        self.enable_speed_limit_flag = not self.enable_speed_limit_flag

    
    def update_score(self, amount = 1):
        super().update_score(amount)

        if self.scores["score"] > self.scores["top_score"]:
            self.scores["top_score"] = self.scores["score"]
            self.boards["top_score"].update_content(self.scores["top_score"])
    

    def handle_game_end(self):
        self.scene.add_score_to_figure(self.scores["epoch"], self.scores["score"])

        self.scores["avg_score_last_100"] = self.scene.get_last_average_score_last_100()
        self.scores["overall_avg_score"] = self.scene.get_average_score()

        self.boards["avg_score_last_100"].update_content(self.scores["avg_score_last_100"])
        self.boards["overall_avg_score"].update_content(self.scores["overall_avg_score"])

        if not self.is_ended_process():
            self.restart_game()
    
    def handle_events(self, events):
        super().handle_events(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
    
    def handle_keydown(self, key):
        if self.is_state(GameState.PAUSED) or self.is_state(GameState.ACTIVE):
            if key == pygame.K_p:
                self.flip_game_pause()
            if key == pygame.K_e:
                self.flip_final_epoch_flag()
            if key == pygame.K_q:
                self.flip_speed_limit_flag()