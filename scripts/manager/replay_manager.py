import json

from scripts.entity.feed_system import Feed

from scripts.game.replay_game import ReplayGame

from typing import List, Tuple, Dict

class Step:
    def __init__(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: Dict[Tuple[int, int], Feed], scores: List[Tuple[str, any]]):
        self.player_bodies = player_bodies
        self.player_direction = player_direction
        self.feeds = feeds
        self.scores = scores
    
    def to_json_dict(self):
        return {
            "player_bodies": [list(body) for body in self.player_bodies],
            "player_direction": self.player_direction,
            "feeds": [[list(feed_coord), feed.to_list()] for feed_coord, feed in self.feeds.items()],
            "scores": [list(score) for score in self.scores]
        }
    
    @classmethod
    def from_json_dict(cls, data):
        return cls(
            player_bodies=[tuple(body) for body in data["player_bodies"]],
            player_direction=data["player_direction"],
            feeds={tuple(feed_coord): Feed(tuple(feed[0]), feed[1]) for feed_coord, feed in data["feeds"]},
            scores=[tuple(score) for score in data["scores"]]
        )

class Replay:
    def __init__(self, grid_size: Tuple[int, int], game_version: str = "1.0.0"):
        self.grid_size = grid_size
        self.game_version = game_version

        self.steps: List[Step] = []

    @classmethod
    def with_steps(self, grid_size: Tuple[int, int], steps: List[Step], game_version: str = "1.0.0"):
        self.grid_size = grid_size
        self.game_version = game_version

        self.steps: List[Step] = steps
        
    def add_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: Dict[Tuple[int, int], Feed], scores: List[Tuple[str, any]]):
        self.steps.append(Step(player_bodies, player_direction, feeds, scores))

    def get_step_state(self, step: int):
        step_index: int = min(max(0, step - 1), len(self.steps))
        return self.steps[step_index]

class ReplayBuffer:
    def __init__(self):
        """
        A buffer that manages the input and output of replays.
        """

    def save_to_file(self, replay: Replay):
        filename: str = None
        data = self.convert_to_json(replay)

        with open(filename, "w") as f:
            json.dump(data, f, indent=4)

    def convert_to_json(self, replay: Replay):
        return {
            "grid_size": replay.grid_size,
            "game_version": replay.game_version,
            "steps": [step.to_json_dict() for step in replay.steps]
        }

    def load_from_file(self, filename: str) -> Replay:
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            
            return self.convert_from_json(data)
        except FileNotFoundError:
            print(f"File({filename}) not found")
            return None

    def convert_from_json(self, data: any) -> Replay:
        grid_size = data["grid_size"]
        game_version = data["game_version"]
        steps = [Step.from_json_dict(step) for step in data["steps"]]

        return Replay.with_steps(grid_size, steps, game_version)

class ReplayManager:
    def __init__(self):
        pass
        
    def show_replay(self):
        pass

    def go_to_step(self):
        pass

    def go_to_next_step(self):
        pass

    def go_to_prev_step(self):
        pass

    def save_replay(self):
        pass

    def load_replay(self):
        pass

