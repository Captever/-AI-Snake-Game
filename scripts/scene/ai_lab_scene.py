import pygame

from constants import *

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from .base_scene import BaseScene
from scripts.ui.ui_components import UILayout, RelativeRect
from scripts.manager.ai_manager import AIManager

from scripts.game.ai_pilot_game import AIPilotGame

from typing import Tuple, Dict, List
from functools import partial

# UI state
CONFIG = "config"
IN_GAME = "in_game"

class AILabScene(BaseScene):
    def __init__(self, manager, rect: pygame.Rect):
        super().__init__(manager, rect)

        self.game: AIPilotGame = None

        self.ai_manager: AIManager = AIManager()
        self.ai = None
        self.target_ai_name = None
        
        self.ui_state = CONFIG

        self.fig, self.ax = None, None

        self.config_layout = self.create_config_layout()

    def create_config_layout(self):
        layout_relative_rect: RelativeRect

        if self.is_landscape:
            layout_relative_rect = RelativeRect(0.16, 0.16, 0.68, 0.68)
        else:
            layout_relative_rect = RelativeRect(0, 0.16, 1, 0.68)

        layout_rect: pygame.Rect = layout_relative_rect.to_absolute(self.size)
        bg_color = (50, 50, 50, 50)

        layout = UILayout(self.origin, layout_rect, bg_color)

        self.add_game_init_layout(layout)
        self.add_ai_init_layout(layout)

        layout.add_button(RelativeRect(0.2, 0.75, 0.25, 0.1), "Start", self.start_game)
        layout.add_button(RelativeRect(0.55, 0.75, 0.25, 0.1), "Cancel", self.return_to_main_scene)

        return layout

    def add_game_init_layout(self, parent_layout: UILayout):
        game_init_layout_name = "game_init"
        parent_layout.add_layout(game_init_layout_name, RelativeRect(0.1, 0.1, 0.4, 0.5), (0, 0, 0, 0))
        game_init_layout = parent_layout.layouts[game_init_layout_name]

        game_init_layout.add_scrollbar(RelativeRect(0, 0, 0.45, 0.15), "Grid Width", 5, 20, 10)
        game_init_layout.add_scrollbar(RelativeRect(0.55, 0, 0.45, 0.15), "Grid Height", 5, 20, 10)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.28, 0.45, 0.15), "Player Speed", 1, 5, 5)
        game_init_layout.add_scrollbar(RelativeRect(0.55, 0.28, 0.45, 0.15), "Feed Amount", 1, 5, 3)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.56, 1, 0.15), "Clear Goal (%)", 50, 100, 75, 5)
        game_init_layout.add_scrollbar(RelativeRect(0, 0.85, 1, 0.15), "number of POTG", 0, 10, 3)

    def add_ai_init_layout(self, parent_layout: UILayout):
        ai_init_layout_name = "ai_init"
        parent_layout.add_layout(ai_init_layout_name, RelativeRect(0.55, 0.1, 0.35, 0.5), (0, 0, 0, 0))
        ai_init_layout = parent_layout.layouts[ai_init_layout_name]

        ai_list: List[str] = self.ai_manager.get_ai_list()
        x_offset, y_offset, each_row_num = 0.35, 0.35, 3
        for idx, ai_name in enumerate(ai_list):
            ai_init_layout.add_button(RelativeRect(x_offset * (idx % each_row_num), y_offset * (idx // each_row_num), 0.3, 0.3), ai_name, partial(self.set_selected_ai, ai_init_layout, ai_name, idx), ['-'])
            if idx == 0:
                self.set_selected_ai(ai_init_layout, ai_name, idx)

    def initialize_ai(self):
        # Initialize the ai with the given settings
        self.ai = self.ai_manager.get_ai(self.target_ai_name)

    def initialize_game(self, settings: Dict[str, any]):
        # Initialize the game with the given settings
        self.settings = settings
        grid_size: Tuple[int, int] = (int(settings['Grid Width']), int(settings['Grid Height']))
        player_speed: int = int(settings['Player Speed'])
        self.player_move_delay = MOVE_DELAY * (11 - player_speed * 2) # min: 1, max: 9
        feed_amount: int = int(settings['Feed Amount'])
        clear_goal: float = settings['Clear Goal (%)'] / 100.0
        potg_num: int = int(settings['number of POTG'])
        game_rect = pygame.Rect(self.rect)
        self.game = AIPilotGame(self, game_rect, self.ai, self.target_ai_name, self.player_move_delay, grid_size, feed_amount, clear_goal, potg_num)
        self.ai.set_current_game(self.game)

    def init_plt(self):
        self.fig, self.ax = plt.subplots()
        self.epochs = []
        self.scores = []
        self.average_score_last_100 = []
        self.overall_average_score = []

        self.plot_scores, = self.ax.plot([], [], label="Scores", marker='o', color='skyblue')
        self.plot_average_scores_last_100, = self.ax.plot([], [], label="Average Score(Last 100)", linestyle='--', color='red')
        self.plot_overall_average_scores, = self.ax.plot([], [], label="Overall Average Score", color='moccasin')

        self.ax.set_xlabel("Epochs")
        self.ax.set_ylabel("Score")

        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.tick_params(axis='x', which='minor', bottom=False)
        self.ax.legend()

        self.fig.canvas.draw()
        self.fig.show()

    def handle_events(self, events):
        super().handle_events(events)
        
        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        # back to main scene
                        self.return_to_main_scene()
            self.config_layout.handle_events(events)
        elif ui_state == IN_GAME:
            self.game.handle_events(events)
    
    def set_ui_state(self, state):
        if state not in [CONFIG, IN_GAME]:
            ValueError("invalid UI state")
        
        if state == CONFIG and self.fig is not None:
            plt.close(self.fig)

        self.ui_state = state
    
    def get_ui_state(self):
        return self.ui_state

    def start_game(self):
        game_settings = self.config_layout.get_scrollbar_values()
        self.initialize_ai()
        self.initialize_game(game_settings)
        self.init_plt()
        self.set_ui_state(IN_GAME)
    
    def restart_new_game(self):
        self.set_ui_state(CONFIG)
        self.manager.finish_to_record()
        self.game = None
        self.ai = None
    
    def set_selected_ai(self, ai_layout: UILayout, ai_name: str, ai_idx: int):
        ai_layout.update_radio_selection(ai_idx)
        self.target_ai_name = ai_name
    
    def return_to_main_scene(self):
        self.manager.set_active_scene("MainScene")
    
    def add_score_to_figure(self, epoch: int, score: int):
        self.epochs.append(epoch)
        self.scores.append(score)
        last_data_num = min(len(self.scores), 100)
        self.average_score_last_100.append(sum(self.scores[-last_data_num:]) / last_data_num)
        self.overall_average_score.append(self.get_average_score())

        self.plot_scores.set_data(self.epochs[-last_data_num:], self.scores[-last_data_num:])
        self.plot_average_scores_last_100.set_data(self.epochs[-last_data_num:], self.average_score_last_100[-last_data_num:])
        self.plot_overall_average_scores.set_data(self.epochs[-last_data_num:], self.overall_average_score[-last_data_num:])

        self.ax.relim()
        self.ax.autoscale_view()

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
    
    def get_average_score(self):
        return sum(self.scores) / len(self.scores)

    def get_last_average_score_last_100(self):
        return self.average_score_last_100[-1]

    def update(self):
        ui_state = self.get_ui_state()
        if ui_state == IN_GAME:
            self.game.update()

    def render(self, surf):
        super().render(surf)

        ui_state = self.get_ui_state()
        if ui_state == CONFIG:
            self.config_layout.render(self.surf)
        elif ui_state == IN_GAME:
            self.game.render(self.surf)
        
        surf.blit(self.surf, self.origin)