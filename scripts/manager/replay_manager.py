import pygame
import json
import os
from datetime import datetime

from constants import REPLAY_DIRECTORY, REPLAY_PREFIX, REPLAY_EXTENSION

from scripts.entity.feed_system import Feed

from scripts.game.replay_game import ReplayGame

from typing import List, Tuple, Dict

class Step:
    def __init__(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List[Feed], scores: List[Tuple[str, any]]):
        self.player_bodies = player_bodies
        self.player_direction = player_direction
        self.feeds = feeds
        self.scores = scores
    
    def to_json_dict(self):
        return {
            "player_bodies": [list(body) for body in self.player_bodies],
            "player_direction": self.player_direction,
            "feeds": [feed.to_list() for feed in self.feeds],
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
    def __init__(self, name: str, grid_size: Tuple[int, int], score_info_list: List[Tuple[str, str, str]], game_version: str = "1.0.0", steps: List[Step] = None):
        self.name = name
        self.grid_size = grid_size
        self.score_info_list = score_info_list
        self.game_version = game_version

        self.steps: List[Step] = steps if steps is not None else []
        
    def add_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List[Feed], scores: List[Tuple[str, any]]):
        self.steps.append(Step(player_bodies, player_direction, feeds, scores))

    def get_step_state(self, step: int):
        step_index: int = min(max(0, step - 1), len(self.steps))
        return self.steps[step_index]

class ReplayBuffer:
    def __init__(self):
        """
        A buffer that manages the input and output of replays.
        """

    def save_to_file(self, replay: Replay, filename: str):
        file_path = REPLAY_DIRECTORY + '/' + filename
        data = self.convert_to_json(replay)

        if not os.path.exists(REPLAY_DIRECTORY):
            os.makedirs(REPLAY_DIRECTORY)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def convert_to_json(self, replay: Replay):
        return {
            "grid_size": list(replay.grid_size),
            "score_info_list": [list(score_info) for score_info in replay.score_info_list],
            "game_version": replay.game_version,
            "steps": [step.to_json_dict() for step in replay.steps]
        }

    def load_from_file(self, filename: str) -> Replay:
        file_path = REPLAY_DIRECTORY + '/' + filename

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            return self.convert_from_json(data)
        except FileNotFoundError:
            print(f"File({filename}) not found")
            return None

    def convert_from_json(self, data: any) -> Replay:
        grid_size = data["grid_size"]
        score_info_list = data["score_info_list"]
        game_version = data["game_version"]
        steps = [Step.from_json_dict(step) for step in data["steps"]]

        return Replay('', grid_size, score_info_list, game_version, steps)

class ReplayManager:
    def __init__(self):
        self.buffer = ReplayBuffer()

        self.current_replay: Replay = None

        self.replay_file_list: List[str] = None

    def wrap_filename(self, filename):
        return REPLAY_PREFIX + filename + REPLAY_EXTENSION

    def unwrap_filename(self, filename):
        start_idx = len(REPLAY_PREFIX)
        end_idx = len(REPLAY_EXTENSION)
        return filename[start_idx:][:-end_idx]

    def start_to_record(self, replay_name: str, grid_size: Tuple[int, int], score_info_list: List[Tuple[int, int]]):
        self.current_replay = Replay(replay_name, grid_size, score_info_list)

    def add_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List[Feed], scores: Dict[str, any]):
        self.current_replay.add_step(player_bodies, player_direction, feeds, scores)

    def finish_to_record(self, is_saved: bool):
        if is_saved:
            self.save_replay()
        else:
            self.current_replay = None

    def update_replay_list(self):
        """
        Update the replay file list
        """
        self.replay_file_list = [
            self.unwrap_filename(f) for f in os.listdir(REPLAY_DIRECTORY)
            if f.startswith(REPLAY_PREFIX) and f.endswith(REPLAY_EXTENSION)
        ]
    
    def get_replay_list(self):
        """
        Get the replay file list
        """
        self.update_replay_list()

        return self.replay_file_list

    def save_replay(self):
        """
        Save the current game as a replay
        """
        formatted_date = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename: str = self.wrap_filename('_'.join([formatted_date, self.current_replay.name]))

        self.buffer.save_to_file(self.current_replay, filename)

    def load_replay(self, index: int):
        """
        Load a specific replay
        """
        filename = self.wrap_filename(self.replay_file_list[index])

        self.current_replay = self.buffer.load_from_file(filename)

    def get_replay_game(self, replay_index: int, rect: pygame.Rect) -> ReplayGame:
        """
        Show the loaded replay
        """
        self.load_replay(replay_index)

        return ReplayGame(rect, self.current_replay)