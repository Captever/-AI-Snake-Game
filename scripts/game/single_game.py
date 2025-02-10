import pygame

from scripts.game.base_game import BaseGame

from constants import *

from scripts.ui.ui_components import UILayout, RelativeRect

from typing import Tuple

class SingleGame(BaseGame):
    def __init__(self, scene, player_move_delay: int, grid_size: Tuple[int, int], feed_amount: int, clear_goal: float):
        super().__init__(scene, player_move_delay, grid_size, feed_amount, clear_goal)

        self.start_game()

    def init_board_list(self):
        self.board_list = [ # key, title, content format
            ("score", "Score", "{:,}")
        ]
    
    def init_instruction_list(self):
        self.instruction_list = [ # key, act
            ("W", "Up"),
            ("A", "Left"),
            ("S", "Down"),
            ("D", "Right"),
            ("P", "Pause")
        ]
    
    def init_paused_layout(self, rect):
        layout: UILayout = UILayout((0, 0), rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "PAUSED", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.3, 0, 0.4, 1), "New", self.scene.restart_new_game)

        self.set_paused_layout(layout)
    
    def init_gameover_layout(self, rect):
        layout: UILayout = UILayout((0, 0), rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "GAME OVER", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.1, 0, 0.35, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.55, 0, 0.35, 1), "Save")

        self.set_gameover_layout(layout)
    
    def init_clear_layout(self, rect):
        layout: UILayout = UILayout((0, 0), rect, (0, 0, 0, 0))

        layout.add_textbox(RelativeRect(0, 0, 1, 0.6), "CLEAR", WHITE)

        button_layout_name = "button_layout"
        layout.add_layout(button_layout_name, RelativeRect(0.25, 0.7, 0.5, 0.3), (0, 0, 0, 0))
        layout.layouts[button_layout_name].add_button(RelativeRect(0.1, 0, 0.35, 1), "New", self.scene.restart_new_game)
        layout.layouts[button_layout_name].add_button(RelativeRect(0.55, 0, 0.35, 1), "Save")

        self.set_clear_layout(layout)


    def is_on_move(self) -> bool:
        return self.move_accum >= self.player_move_delay


    def start_game(self):
        super().start_game()

        self.start_countdown(3000)

    def update(self):
        super().update()

        if self.is_state_countdown():
            self.countdown()

    
    def handle_events(self, events):
        super().handle_events(events)

        for event in events:
            if event.type == pygame.KEYDOWN:
                self.handle_keydown(event.key)
    
    def handle_keydown(self, key):
        if key == pygame.K_p:
            self.flip_game_pause()

        elif self.is_active() or self.is_state_countdown():
            self.handle_movement_keydown(key)
    
    def handle_movement_keydown(self, key):
        if key == pygame.K_UP:
            self.next_direction = 'N'
        elif key == pygame.K_DOWN:
            self.next_direction = 'S'
        elif key == pygame.K_LEFT:
            self.next_direction = 'W'
        elif key == pygame.K_RIGHT:
            self.next_direction = 'E'
        self.player.set_direction(self.next_direction)