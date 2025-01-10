from scripts.scene_manager import Scene

from typing import Tuple, Dict

from game import Game

class GameScene(Scene):
    def __init__(self, manager):
        super().__init__(manager)
        self.game = None

    def initialize(self, settings: Dict[str, any]):
        self.settings = settings
        self.player_speed: int = settings['Player Speed']
        self.grid_size: Tuple[int, int] = (settings['Grid Width'], settings['Grid Height'])
        self.clear_goal: float = settings['Clear Goal (%)'] / 100.0
        self.initial_game()
    
    def initial_game(self):
        # Initialize the game with the given settings
        self.game = Game(self.player_speed, self.grid_size, self.clear_goal)

    def handle_events(self, events):
        super().handle_events(events)
        
        self.game.handle_events(events)

    def update(self):
        self.game.update()

    def render(self, surf):
        self.game.render(surf)
