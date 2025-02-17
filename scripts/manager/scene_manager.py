from scripts.scene.base_scene import BaseScene

from scripts.manager.replay_manager import ReplayManager

from typing import Dict, Tuple, List

class SceneManager:
    def __init__(self):
        self.scenes: Dict[str, BaseScene] = {}
        self.active_scene: BaseScene = None
        self.replay_manager = ReplayManager()

    def add_scene(self, name, scene):
        """Add a scene to the manager."""
        self.scenes[name] = scene

    def set_active_scene(self, name):
        """Set the active scene by name."""
        self.active_scene = self.scenes[name]


    # about replay manager
    def start_to_record(self, replay_name: str, grid_size: Tuple[int, int]):
        self.replay_manager.start_to_record(replay_name, grid_size)

    def finish_to_record(self, is_saved: bool = False):
        self.replay_manager.finish_to_record(is_saved)

    def add_replay_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List['Feed'], scores: List[Tuple[str, any]]):
        self.replay_manager.add_step(player_bodies, player_direction, feeds, scores)
        
    def get_replay_list(self):
        return self.replay_manager.get_replay_list()

    def load_replay(self, replay_index: int):
        self.replay_manager.load_replay(replay_index)


    # functions to update every frame
    def handle_events(self, events):
        if self.active_scene:
            self.active_scene.handle_events(events)

    def update(self):
        if self.active_scene:
            self.active_scene.update()

    def render(self, screen):
        if self.active_scene:
            self.active_scene.render(screen)