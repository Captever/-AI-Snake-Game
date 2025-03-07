from pygame import Rect

from scripts.scene.base_scene import BaseScene

from scripts.manager.replay_manager import ReplayManager

from typing import Dict, Tuple, List, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.entity.feed_system import Feed

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
        self.active_scene.on_scene_changed()


    # about replay manager
    def start_to_record(self, replay_title: str, grid_size: Tuple[int, int], score_info_list: List[Tuple[int, int]]):
        self.replay_manager.start_to_record(replay_title, grid_size, score_info_list)

    def finish_to_record(self, is_saved: bool = False):
        self.replay_manager.finish_to_record(is_saved)
    
    def delete_replay(self, replay_uuid: str):
        self.replay_manager.delete_replay(replay_uuid)

    def add_replay_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List["Feed"], scores: List[Tuple[str, any]]):
        self.replay_manager.add_step(player_bodies, player_direction, feeds, scores)
        
    def get_replay_list(self):
        return self.replay_manager.get_replay_list()

    def get_replay_game(self, replay_uuid: str, rect: Rect):
        return self.replay_manager.get_replay_game(replay_uuid, rect)


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