import pygame

from constants import *

import matplotlib.pyplot as plt

from scripts.scene_manager import Scene
from scripts.ui_components import UILayout, RelativeRect
from scripts.ai_manager import AIManager

from instances.ai_pilot_game_instance import AI_Pilot_Game

from typing import Tuple, Dict, List
from functools import partial

CONFIG, IN_GAME = "config", "in_game"

class AILabScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)

        self.game: AI_Pilot_Game = None

        self.ai_manager: AIManager = AIManager()
        self.ai = None
        self.target_ai_name = None

        self.fig, self.ax = plt.subplots()
        self.scores = []
        
        self.ui_state = CONFIG

        self.config_layout = self.create_config_layout()

    def create_config_layout(self):
        layout_pos: Tuple[int, int]
        layout_size: Tuple[int, int]

        if IS_LANDSCAPE:
            layout_pos = (SCREEN_WIDTH // 6, SCREEN_HEIGHT // 6)
            layout_size = (SCREEN_WIDTH // 1.5, SCREEN_HEIGHT // 1.5)
        else:
            layout_pos = (0, SCREEN_HEIGHT // 6)
            layout_size = (SCREEN_WIDTH, SCREEN_HEIGHT // 1.5)

        layout_rect: pygame.Rect = pygame.Rect(layout_pos + layout_size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout((0, 0), layout_rect, bg_color)

        self.add_game_init_layout(layout)
        self.add_ai_init_layout(layout)

        layout.add_button(RelativeRect(0.2, 0.75, 0.25, 0.1), "Start", self.start_game)
        layout.add_button(RelativeRect(0.55, 0.75, 0.25, 0.1), "Cancel", self.activate_main_scene)

        return layout

    def add_game_init_layout(self, parent_layout: UILayout):
        game_init_layout_name = "game_init"
        parent_layout.add_layout(game_init_layout_name, RelativeRect(0.1, 0.1, 0.4, 0.5), (0, 0, 0, 0))
        game_init_layout = parent_layout.layouts[game_init_layout_name]

        game_init_layout.add_scrollbar(RelativeRect(0, 0, 0.45, 0.15), "Grid Width", 5, 20, 5)
        game_init_layout.add_scrollbar(RelativeRect(0.55, 0, 0.45, 0.15), "Grid Height", 5, 20, 5)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.28, 0.45, 0.15), "Player Speed", 1, 10, 9)
        game_init_layout.add_scrollbar(RelativeRect(0.55, 0.28, 0.45, 0.15), "Feed Amount", 1, 5, 3)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.56, 1, 0.15), "Clear Goal (%)", 50, 100, 90)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.84, 1, 0.15), "Epoch", 1, 30, 10)

    def add_ai_init_layout(self, parent_layout: UILayout):
        ai_init_layout_name = "ai_init"
        parent_layout.add_layout(ai_init_layout_name, RelativeRect(0.55, 0.1, 0.35, 0.5), (0, 0, 0, 0))
        ai_init_layout = parent_layout.layouts[ai_init_layout_name]

        ai_list: List[str] = self.ai_manager.get_ai_list()
        x_offset, y_offset, each_row_num = 0.55, 0.4, 2
        for idx, ai_name in enumerate(ai_list):
            ai_init_layout.add_button(RelativeRect(x_offset * (idx % each_row_num), y_offset * (idx // each_row_num), 0.45, 0.3), ai_name, partial(self.set_selected_ai, ai_init_layout, ai_name), ['-'])
            if idx == 0:
                self.set_selected_ai(ai_init_layout, ai_name)

    def initialize_ai(self):
        # Initialize the ai with the given settings
        self.ai = self.ai_manager.get_ai(self.target_ai_name)

    def initialize_game(self, settings: Dict[str, any]):
        # Initialize the game with the given settings
        self.settings = settings
        grid_size: Tuple[int, int] = (int(settings['Grid Width']), int(settings['Grid Height']))
        player_speed: int = int(settings['Player Speed'])
        self.player_move_delay = MOVE_DELAY * (10 - player_speed + 1) # min: 1, max: 10
        feed_amount: int = int(settings['Feed Amount'])
        clear_goal: float = settings['Clear Goal (%)'] / 100.0
        self.epoch_num: int = settings['Epoch']
        self.game = AI_Pilot_Game(self, self.ai, self.player_move_delay, grid_size, feed_amount, clear_goal, self.epoch_num)
        self.ai.set_current_game(self.game)

    def handle_events(self, events):
        super().handle_events(events)
        
        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            self.config_layout.handle_events(events)
        elif ui_state == IN_GAME:
            self.game.handle_events(events)
    
    def set_ui_state(self, state):
        if state not in [CONFIG, IN_GAME]:
            ValueError("invalid UI state")
        
        self.ui_state = state
    
    def get_ui_state(self):
        return self.ui_state

    def start_game(self):
        game_settings = self.config_layout.get_scrollbar_values()
        self.initialize_ai()
        self.initialize_game(game_settings)
        self.set_ui_state(IN_GAME)
    
    def restart_new_game(self):
        self.set_ui_state(CONFIG)
        self.game = None
        self.ai = None
    
    def set_selected_ai(self, ai_layout: UILayout, ai_name: str):
        ai_layout.update_radio_selection(ai_name)
        self.target_ai_name = ai_name
    
    def activate_main_scene(self):
        self.manager.set_active_scene("MainScene")
    
    def add_score_to_statistics(self, score: int):
        self.scores.append(score)
    
    def plot_scores(self):
        epochs, average_scores = [], []

        for i in range(len(self.scores)):
            epochs.append(i + 1)
            average_scores.append(sum(self.scores[:i+1]) / (i + 1))

        self.ax.plot(epochs, self.scores, label="Scores", marker='o')
        self.ax.plot(epochs, average_scores, label="Average score", marker='--')

        self.ax.set_xlabel("Epochs")
        self.ax.set_ylabel("Score")

        plt.show()

    def update(self):
        ui_state = self.get_ui_state()
        if ui_state == IN_GAME:
            self.game.update()

    def render(self, surf):
        surf.fill((0, 0, 0))

        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            self.config_layout.render(surf)
        elif ui_state == IN_GAME:
            self.game.render(surf)
