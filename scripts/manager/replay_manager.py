import pygame
import json
import os
import uuid
import sqlite3
from datetime import datetime

from constants import REPLAY_DIRECTORY, TIMESTAMP_FORMAT

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
    def __init__(self, title: str, grid_size: Tuple[int, int], score_info_list: List[Tuple[str, str, str]], timestamp: datetime = None, game_version: str = "1.0.0", steps: List[Step] = None):
        self.title = title
        self.grid_size = grid_size
        self.score_info_list = score_info_list
        self.timestamp = datetime.now() if timestamp is None else timestamp
        self.game_version = game_version

        self.steps: List[Step] = steps if steps is not None else []
        
    def add_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List[Feed], scores: List[Tuple[str, any]]):
        self.steps.append(Step(player_bodies, player_direction, feeds, scores))

    def get_step_state(self, step: int):
        step_index: int = min(max(0, step - 1), len(self.steps))
        return self.steps[step_index]
    
    def get_final_score_and_epoch(self) -> Tuple[int, int]:
        final_scores = self.steps[-1].scores.copy()

        final_score: int = None
        epoch_count: int = None

        for key, score in final_scores:
            if key == "score":
                final_score = score
            elif key == "epoch":
                epoch_count = score

        return (final_score, epoch_count)

class ReplayManager:
    def __init__(self, save_dir: str = REPLAY_DIRECTORY):
        self.save_dir = save_dir
        self.db_path = os.path.join(save_dir, "metadata.db")
        # Create a new directory if it does not exist
        os.makedirs(save_dir, exist_ok=True)
        
        self.replay_file_list: List[Tuple] = None  # uuid, title, timestamp, steps_num, score

        self.current_replay: Replay = None

        self.initialize_db()

    def initialize_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # create table 'replays' to db if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS replays (
                uuid TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                steps_num INTEGER NOT NULL,
                final_score INTEGER NOT NULL
            )
        """)
        
        conn.commit()
        conn.close()


    # about recording
    def start_to_record(self, replay_title: str, grid_size: Tuple[int, int], score_info_list: List[Tuple[int, int]]):
        self.current_replay = Replay(replay_title, grid_size, score_info_list)

    def add_step(self, player_bodies: List[Tuple[int, int]], player_direction: str, feeds: List[Feed], scores: List[Tuple[str, any]]):
        self.current_replay.add_step(player_bodies, player_direction, feeds, scores)

    def finish_to_record(self, is_saved: bool):
        if is_saved:
            self.save_replay()
        self.current_replay = None


    # about replay management
    def update_replay_list(self):
        """
        Update the replay file list
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT uuid, title, timestamp, steps_num, final_score FROM replays ORDER BY timestamp DESC")
        self.replay_file_list = cursor.fetchall()

        conn.close()
    
    def get_replay_list(self):
        """
        Get the replay file list
        """
        self.update_replay_list()

        return self.replay_file_list

    def save_replay(self):
        """
        Saved replay using the cached game replay file
        """
        current_uuid = uuid.uuid4().hex
        filename = f"{current_uuid}.json"
        file_path = os.path.join(self.save_dir, filename)

        data = self.convert_to_json(self.current_replay)

        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)

        # add replay info to metadata
        title = self.current_replay.title
        timestamp = self.current_replay.timestamp.strftime(TIMESTAMP_FORMAT)
        steps_num = len(self.current_replay.steps)
        final_score = self.current_replay.get_final_score_and_epoch()[0]

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
    
        try:
            cursor.execute("INSERT INTO replays (uuid, title, timestamp, steps_num, final_score) VALUES (?, ?, ?, ?, ?)", (current_uuid, title, timestamp, steps_num, final_score))
            conn.commit()
        except sqlite3.IntegrityError as e:  # prevent duplicate
            print(f"sqlite3 IntegrityError Occured: {e}")
        finally:
            conn.close()

    def load_replay(self, replay_uuid: str):
        """
        Load a specific replay
        """

        filename = f"{replay_uuid}.json"
        file_path = os.path.join(self.save_dir, filename)

        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            self.current_replay = self.convert_from_json(data)
        except FileNotFoundError:
            print(f"File({filename}) not found")

    def delete_replay(self, replay_uuid: str):
        """
        Delete a specific replay file
        """
        try:
            # Connect to the SQLite database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Retrieve the filename before deleting from the database
            cursor.execute("SELECT uuid FROM replays WHERE uuid = ?", (replay_uuid,))
            result = cursor.fetchone()

            if result is None:
                print(f"No matching record found in the database for UUID: {replay_uuid}")
            else:
                filename = f"{replay_uuid}.json"
                file_path = os.path.join(self.save_dir, filename)

                # Check if the file exists before attempting to delete it
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"Replay deleted successfully: {file_path}")
                else:
                    print(f"Replay does not exist: {file_path}")

                # Delete the corresponding entry in the database
                cursor.execute("DELETE FROM replays WHERE uuid = ?", (replay_uuid,))
                conn.commit()
                print(f"Database record deleted for UUID: {replay_uuid}")

            # Close the database connection
            conn.close()
        except PermissionError:
            print(f"Failed to delete file: Permission denied. ({file_path})")
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def get_replay_game(self, replay_uuid: str, rect: pygame.Rect) -> ReplayGame:
        """
        Show the loaded replay
        """
        self.load_replay(replay_uuid)

        return ReplayGame(rect, self.current_replay)
    

    # about JSON converting
    def convert_to_json(self, replay: Replay):
        return {
            "title": replay.title,
            "timestamp": replay.timestamp.strftime(TIMESTAMP_FORMAT),
            "grid_size": list(replay.grid_size),
            "score_info_list": [list(score_info) for score_info in replay.score_info_list],
            "game_version": replay.game_version,
            "steps": [step.to_json_dict() for step in replay.steps]
        }

    def convert_from_json(self, data: any) -> Replay:
        title = data["title"]
        timestamp = datetime.strptime(data["timestamp"], TIMESTAMP_FORMAT)
        grid_size = data["grid_size"]
        score_info_list = data["score_info_list"]
        game_version = data["game_version"]
        steps = [Step.from_json_dict(step) for step in data["steps"]]

        return Replay(title, grid_size, score_info_list, timestamp=timestamp, game_version=game_version, steps=steps)