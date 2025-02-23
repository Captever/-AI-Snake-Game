from constants import *

from scripts.manager.game_manager import GameState

from typing import Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.game.base_game import BaseGame

class FeedSystem:
    def __init__(self, game: "BaseGame", feed_amount: int):
        """
        Initialize FeedSystem Class

        Args:
            game (BaseGame): Current Game object
            feed_amount (int): Amount of feeds
        """
        self.feeds: Dict[Tuple[int, int], Feed] = {}
        self.game = game
        self.feed_amount: int = feed_amount
    
    def is_feed_empty(self, feed_type: str = 'normal'):
        return not any(feed.type == feed_type for feed in self.feeds.values())
    
    def is_feed_exist(self, coord: Tuple[int, int]) -> bool:
        """
        Check if the given coordinates are currently in feeds list
        """
        return coord in self.feeds
    
    def get_feed(self, coord: Tuple[int, int]) -> 'Feed':
        return self.feeds[coord]

    def add_feed(self, coord: Tuple[int, int], feed_type: str = 'normal'):
        self.feeds[coord] = Feed(coord=coord, feed_type=feed_type)
        self.game.cell_manager.mark_cell_used(coord)
    
    def add_feed_random_coord(self, k: int, feed_type: str = 'normal'):
        if k < 1:
            return

        random_cell_coords = self.game.cell_manager.get_random_available_cells(k)

        if not len(random_cell_coords):
            self.game.set_state(GameState.CLEAR)
            return

        for rand_coord in random_cell_coords:
            self.add_feed(rand_coord, feed_type)

class Feed:
    def __init__(self, coord: Tuple[int, int], feed_type: str):
        self.coord = coord
        self.type = feed_type

    def to_list(self):
        return [list(self.coord), self.type]