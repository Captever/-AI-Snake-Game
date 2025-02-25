from constants import *

from typing import Tuple, Dict, List

class FeedSystem:
    def __init__(self):
        """
        Create FeedSystem Class
        """
        self._feeds: Dict[Tuple[int, int], Feed] = {}
    
    def is_feed_empty(self, feed_type: str = 'normal'):
        return not any(feed._type == feed_type for feed in self._feeds.values())
    
    def is_feed_exist(self, coord: Tuple[int, int]) -> bool:
        """
        Check if the given coordinates are currently in feeds list
        """
        return coord in self._feeds
    
    def get_feeds(self) -> List["Feed"]:
        return list(self._feeds.keys())
    
    def get_feed(self, coord: Tuple[int, int]) -> 'Feed':
        return self._feeds[coord]

    def add_feed(self, coord: Tuple[int, int], feed_type: str = 'normal'):
        if coord in self._feeds.keys():
            raise ValueError("Feed already exists at the inserted coordinates")

        self._feeds[coord] = Feed(coord=coord, type=feed_type)

    def remove_feed(self, coord: Tuple[int, int]):
        if coord not in self._feeds.keys():
            raise ValueError("No feed exists at the inserted coordinates")

        del self._feeds[coord]

class Feed:
    def __init__(self, coord: Tuple[int, int], type: str):
        self._coord = coord
        self._type = type

    def get_coord(self) -> Tuple[int, int]:
        return self._coord
    
    def get_type(self) -> str:
        return self._type

    def to_list(self):
        return [list(self._coord), self._type]