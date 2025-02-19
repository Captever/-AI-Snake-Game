import pygame

from constants import *
from scripts.plugin.custom_func import get_dist

from scripts.manager.game_manager import GameState

from typing import Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.game.base_game import BaseGame
    from scripts.ui.map_structure import Map

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
        
        self.feed_surf: pygame.Surface = self.create_feed_surface()

    def create_feed_surface(self) -> pygame.Surface:
        size = self.game.map.get_cell_size()
        outline_thickness = round(size[0] * OBJECT_OUTLINE_RATIO)
        feed_surface = pygame.Surface(size)
        pygame.draw.rect(feed_surface, FEED_OUTLINE_COLOR, feed_surface.get_rect())
        pygame.draw.rect(feed_surface, FEED_COLOR, pygame.Rect(outline_thickness, outline_thickness, size[0] - outline_thickness * 2, size[1] - outline_thickness * 2))
        return feed_surface
    
    def is_feed_empty(self, feed_type: str = 'normal'):
        return not any(feed.type == feed_type for feed in self.feeds.values())
    
    def is_feed_exist(self, coord: Tuple[int, int]) -> bool:
        """
        Check if the given coordinates are currently in feeds list
        """
        return coord in self.feeds
    
    def get_feed(self, coord: Tuple[int, int]) -> 'Feed':
        return self.feeds[coord]

    def get_nearest_feed(self, target: Tuple[int, int]):
        return min(self.feeds, key=lambda feed: get_dist(feed, target))

    def get_feeds_as_list(self):
        return [[list(feed_pos), feed.to_list()] for feed_pos, feed in self.feeds.items()]

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
    
    def remove_feed(self, coord: Tuple[int, int]):
        target_type = self.feeds[coord].type
        del self.feeds[coord]
        
        # if there is no same type feed, add new feeds
        if self.is_feed_empty(target_type):
            self.add_feed_random_coord(self.feed_amount, feed_type=target_type)

        self.game.cell_manager.mark_cell_free(coord)
    
    def render(self, map: "Map"):
        for feed_coord, feed in self.feeds.items():
            map.get_cells()[feed_coord].put_surf(self.feed_surf)

class Feed:
    def __init__(self, coord: Tuple[int, int], feed_type: str):
        self.coord = coord
        self.type = feed_type

    def to_list(self):
        return [list(self.coord), self.type]