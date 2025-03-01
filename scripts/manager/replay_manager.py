import pygame
import json
import os
import shutil
import uuid
from datetime import datetime

from constants import REPLAY_DIRECTORY, REPLAY_CACHE_DIRECTORY, REPLAY_METADATA_FILE_PATH, REPLAY_PREFIX, REPLAY_EXTENSION

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
            feeds=[Feed(tuple(feed_coord), feed_type) for feed_coord, feed_type in data["feeds"]],
            scores=[tuple(score) for score in data["scores"]]
        )

class Replay:
    def __init__(self, title: str, grid_size: Tuple[int, int], score_info_list: List[Tuple[str, str, str]], timestamp: datetime = datetime.now(), game_version: str = "1.0.0", steps: List[Step] = None):
        self.title = title
        self.grid_size = grid_size
        self.score_info_list = score_info_list
        self.timestamp = timestamp
        self.game_version = game_version

        self.steps: List[Step] = steps if steps is not None else []
        
    def add_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List[Feed], scores: List[Tuple[str, any]]):
        self.steps.append(Step(player_bodies, player_direction, feeds, scores))

    def get_step_state(self, step: int):
        step_index: int = min(max(0, step - 1), len(self.steps))
        return self.steps[step_index]

class ReplayManager:
    def __init__(self, save_dir: str = REPLAY_DIRECTORY, cache_dir: str = REPLAY_CACHE_DIRECTORY, metadata_file_path: str = REPLAY_METADATA_FILE_PATH):
        self.save_dir = save_dir
        self.cache_dir = cache_dir
        self.metadata_file = metadata_file_path
        
        # Create a new directory if it does not exist
        os.makedirs(save_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)

        self.current_replay: Replay = None

        self.replay_cache_list: List[Tuple[str, str]] = []  # uuid filename, real filename

        self.metadata: Dict[str, list[str]] = None
        self._load_metadata()

    # about temporary data; metadata, cache
    def _load_metadata(self):
        """ Load existing metadata """
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as file:
                self.metadata = json.load(file)
        else:
            self.metadata = {"top_replay": None}

    def _save_metadata(self):
        """ Save the current top record replay information to a metadata file """
        with open(self.metadata_file, "w") as file:
            json.dump(self.metadata, file)

    def save_cache_replay(self, replay_data):
        """ Save the current top record replay as a cached file in the cache directory """
        temp_filename = f"top_replay_{uuid.uuid4().hex}.json"
        temp_path = os.path.join(self.cache_dir, temp_filename)

        with open(temp_path, "w") as file:
            file.write(replay_data)

        # delete previous cache file
        if self.metadata["top_replay"]:
            old_cache_path = os.path.join(self.cache_dir, self.metadata["top_replay"])
            if os.path.exists(old_cache_path):
                os.remove(old_cache_path)

        # save metadata for the cached top record replay
        self.metadata["top_replay"] = temp_filename
        self._save_metadata()
        print(f"New best replay cached: {temp_filename}")

    def confirm_save_best_replay(self):
        """ Move the cached top record replay file to the official storage """
        if not self.metadata["top_replay"]:
            print("No cached replay to save.")
            return

        cache_path = os.path.join(self.cache_dir, self.metadata["top_replay"])
        final_filename = f"replay_{uuid.uuid4().hex}.json"
        final_path = os.path.join(self.save_dir, final_filename)

        if os.path.exists(cache_path):
            shutil.move(cache_path, final_path)

            # initialize metadata
            self.metadata["top_replay"] = None
            self._save_metadata()
        else:
            raise FileExistsError("Cached replay file not found.")

    def discard_cached_replay(self):
        """ Discard the cached replay """
        if not self.metadata["top_replay"]:
            print("No cached replay to discard.")
            return

        cache_path = os.path.join(self.cache_dir, self.metadata["top_replay"])
        if os.path.exists(cache_path):
            os.remove(cache_path)

        # initialize metadata
        self.metadata["top_replay"] = None
        self._save_metadata()

        self.metadata: Dict[str, list[str]] = None
        self._load_metadata()

    # about temporary data; metadata, cache
    def _load_metadata(self):
        """ Load existing metadata """
        if os.path.exists(self.metadata_file):
            with open(self.metadata_file, "r") as file:
                self.metadata = json.load(file)
        else:
            self.metadata = {"top_replay": None}

    def _save_metadata(self):
        """ Save the current top record replay information to a metadata file """
        with open(self.metadata_file, "w") as file:
            json.dump(self.metadata, file)

    def save_cache_replay(self, replay_data):
        """ Save the current top record replay as a cached file in the cache directory """
        temp_filename = f"top_replay_{uuid.uuid4().hex}.json"
        temp_path = os.path.join(self.cache_dir, temp_filename)

        with open(temp_path, "w") as file:
            file.write(replay_data)

        # delete previous cache file
        if self.metadata["top_replay"]:
            old_cache_path = os.path.join(self.cache_dir, self.metadata["top_replay"])
            if os.path.exists(old_cache_path):
                os.remove(old_cache_path)

        # save metadata for the cached top record replay
        self.metadata["top_replay"] = temp_filename
        self._save_metadata()
        print(f"New best replay cached: {temp_filename}")

    def confirm_save_best_replay(self):
        """ Move the cached top record replay file to the official storage """
        if not self.metadata["top_replay"]:
            print("No cached replay to save.")
            return

        cache_path = os.path.join(self.cache_dir, self.metadata["top_replay"])
        final_filename = f"replay_{uuid.uuid4().hex}.json"
        final_path = os.path.join(self.save_dir, final_filename)

        if os.path.exists(cache_path):
            shutil.move(cache_path, final_path)

            # initialize metadata
            self.metadata["top_replay"] = None
            self._save_metadata()
        else:
            raise FileExistsError("Cached replay file not found.")

    def discard_cached_replay(self):
        """ Discard the cached replay """
        if not self.metadata["top_replay"]:
            print("No cached replay to discard.")
            return

        cache_path = os.path.join(self.cache_dir, self.metadata["top_replay"])
        if os.path.exists(cache_path):
            os.remove(cache_path)

        # initialize metadata
        self.metadata["top_replay"] = None
        self._save_metadata()

        self.replay_cache_list: List[Tuple[str, str]] = []  # uuid filename, real filename


    # about filename
    def wrap_filename(self, filename):
        return REPLAY_PREFIX + filename + REPLAY_EXTENSION

    def unwrap_filename(self, filename):
        start_idx = len(REPLAY_PREFIX)
        end_idx = len(REPLAY_EXTENSION)
        return filename[start_idx:][:-end_idx]


    # about recording
    def start_to_record(self, replay_title: str, grid_size: Tuple[int, int], score_info_list: List[Tuple[int, int]]):
        self.current_replay = Replay(replay_title, grid_size, score_info_list)

    def add_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List[Feed], scores: Dict[str, any]):
        self.current_replay.add_step(player_bodies, player_direction, feeds, scores)

    def finish_to_record(self, is_saved: bool):
        if is_saved:
            self.save_replay()
        else:
            self.current_replay = None


    # about replay management
    def update_replay_list(self):
        """
        Update the replay file list
        """
        self.replay_file_list = [
            self.unwrap_filename(f) for f in os.listdir(self.save_dir)
            if f.startswith(REPLAY_PREFIX) and f.endswith(REPLAY_EXTENSION)
        ]
    
    def get_replay_list(self):
        """
        Get the replay file list
        """
        self.update_replay_list()

        return self.replay_file_list
    
    def get_real_filename_from_uuid(self, uuid_filename):
        for uuid, real in self.replay_cache_list:
            if uuid == uuid_filename:
                return real
        return None
    
    def save_replay_as_cache(self) -> str:
        """
        Temporarily saved the current replay

        Returns:
            str: name of the cached file where the replay was saved
        """
        uuid_filename = uuid.uuid4().hex
        
        formatted_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        real_filname: str = self.wrap_filename('_'.join([formatted_date, self.current_replay.name]))

        # Create directory if it does not exist
        os.makedirs(REPLAY_CACHE_DIRECTORY, exist_ok=True)

        file_path = REPLAY_CACHE_DIRECTORY + '/' + uuid_filename
        data = self.convert_to_json(self.current_replay)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        # Saved file as a valid cache and added it to the cache list
        self.replay_cache_list.append((uuid_filename, real_filname))

        return uuid_filename

    def save_replay_from_cache(self, uuid_filename):
        old_path = os.path.join(REPLAY_CACHE_DIRECTORY, uuid_filename)
        new_filename = self.get_real_filename_from_uuid(uuid_filename)
        new_path = os.path.join(REPLAY_DIRECTORY, new_filename)

        # Create directory if it does not exist
        os.makedirs(REPLAY_DIRECTORY, exist_ok=True)

        try:
            shutil.move(old_path, new_path)  # move file
            print(f"Replay saved as {new_filename} in {REPLAY_DIRECTORY}")
            return new_path
        except FileNotFoundError:
            print("Error: The file does not exist.")
        except Exception as e:
            print(f"Error: {e}")

    def save_replay(self):
        """
        Saved replay using the cached game replay file
        """
        formatted_date = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename: str = self.wrap_filename('_'.join([formatted_date, self.current_replay.title]))

        file_path = self.save_dir + '/' + filename
        data = self.convert_to_json(self.current_replay)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

    def load_replay(self, index: int):
        """
        Load a specific replay
        """
        filename = self.wrap_filename(self.replay_file_list[index])

        file_path = self.save_dir + '/' + filename

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.current_replay = self.convert_from_json(data)
        except FileNotFoundError:
            print(f"File({filename}) not found")

    def get_replay_game(self, replay_index: int, rect: pygame.Rect) -> ReplayGame:
        """
        Show the loaded replay
        """
        self.load_replay(replay_index)

        return ReplayGame(rect, self.current_replay)
    

    # about JSON converting
    def convert_to_json(self, replay: Replay):
        return {
            "title": replay.title,
            "timestamp": replay.timestamp,
            "grid_size": list(replay.grid_size),
            "score_info_list": [list(score_info) for score_info in replay.score_info_list],
            "game_version": replay.game_version,
            "steps": [step.to_json_dict() for step in replay.steps]
        }

    def convert_from_json(self, data: any) -> Replay:
        title = data["title"]
        timestamp = data["timestamp"]
        grid_size = data["grid_size"]
        score_info_list = data["score_info_list"]
        game_version = data["game_version"]
        steps = [Step.from_json_dict(step) for step in data["steps"]]

        return Replay(title, grid_size, score_info_list, timestamp=timestamp, game_version=game_version, steps=steps)