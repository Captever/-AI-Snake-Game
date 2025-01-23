import pygame
import random

from scripts.game_manager import GameState
from constants import *

from typing import Tuple, Dict, List

class Player:
    def __init__(self, game, initial_length):
        """
        Initialize Player Class

        Args:
            game (Game): Current Game object
            initial_length (int): initial length of the player
        """
        self.game = game
        self.length: int = initial_length
        self.direction: str = None

        self.body_surf: pygame.Surface = self.create_body_surface()
        self.bodies: List[Tuple[int, int]] = self.make_bodies()
    
    def make_bodies(self):
        grid_num = self.game.state_manager.get_grid_num()
        rand_coord = (random.randint(0, grid_num[0] - 1), random.randint(0, grid_num[1] - 1))
        ret = [rand_coord]
        self.game.state_manager.mark_cell_used(rand_coord)
        
        dirs = ['E', 'W', 'S', 'N']
        for _ in range(self.length - 1):
            prev_body_coord = ret[-1]
            dirs_copy = dirs.copy()
            while True:
                dir = dirs_copy[random.randint(0, len(dirs_copy) - 1)]
                dir_offset = DIR_OFFSET_DICT[dir]
                body_coord = (prev_body_coord[0] + dir_offset[0], prev_body_coord[1] + dir_offset[1])
                # validation
                if self.game.is_in_bound(body_coord) and body_coord not in ret:
                    ret.append(body_coord)
                    self.game.state_manager.mark_cell_used(body_coord)

                    # set the player's initial direction to
                    #  the opposite direction of the second body part
                    if self.direction == None:
                        if dir == 'E':
                            self.direction = 'W'
                        elif dir == 'W':
                            self.direction = 'E'
                        elif dir == 'S':
                            self.direction = 'N'
                        else:
                            self.direction = 'S'

                    break
                else:
                    dirs_copy.remove(dir)
        
        return ret

    def create_body_surface(self) -> pygame.Surface:
        """
        Create body surface

        Returns:
            pygame.Surface: Surface object to render the body
        """
        size = self.game.map.get_cell_size()
        outline_thickness = round(size[0] * OBJECT_OUTLINE_RATIO)
        body_surface = pygame.Surface(size)
        pygame.draw.rect(body_surface, BODY_OUTLINE_COLOR, body_surface.get_rect())
        pygame.draw.rect(body_surface, BODY_COLOR, pygame.Rect(outline_thickness, outline_thickness, size[0] - outline_thickness * 2, size[1] - outline_thickness * 2))
        return body_surface

    def set_direction(self, dir: str):
        if dir not in DIR_OFFSET_DICT:
            raise ValueError("parameter(dir) must be the one of [EWSN]")
        
        if not self.validate_direction(dir):
            return
        
        self.direction = dir
    
    def validate_direction(self, dir: str) -> bool:
        dir_offset = DIR_OFFSET_DICT[dir]
        head = self.bodies[0]
        neck = (head[0] + dir_offset[0], head[1] + dir_offset[1])

        # restrict movement towards walls or the neck direction
        return self.game.is_in_bound(neck) and neck != self.bodies[1]
        
    def check_collision(self, target):
        return self.game.check_collision(target)
    
    def is_body_collision(self, coord: Tuple[int, int]) -> bool:
        """
        Check if the given coordinate collides with the player's body
        (excluding the tail).
        """
        return coord in self.bodies[:-1]

    def move(self):
        head, tail = self.bodies[0], self.bodies[-1]
        dir_offset = DIR_OFFSET_DICT[self.direction]
        new_head = (head[0] + dir_offset[0], head[1] + dir_offset[1])

        collision = self.check_collision(new_head)
        # game over when colliding with walls or the player's own body
        if collision[0] in ['wall', 'body']:
            self.game.set_state(GameState.GAMEOVER)
            return
        
        # length increases when eat feed
        if collision[0] == 'feed':
            curr_feed = collision[1]
            self.eat_feed(tail, curr_feed)
        else:
            self.game.state_manager.mark_cell_free(tail)
        self.game.state_manager.mark_cell_used(new_head)

        self.bodies = [new_head] + self.bodies[:-1]
    
    def eat_feed(self, tail_coord: Tuple[int, int], feed: 'Feed'):
        self.game.update_score(1)
        self.bodies.append(tail_coord)
        self.game.remove_feed(feed.coord)
    
    def render(self):
        for body_coord in self.bodies:
            self.game.map.get_cells()[body_coord].put_surf(self.body_surf)

        head = self.bodies[0]
        dir_offset = DIR_OFFSET_DICT[self.direction]

        arrow_coord = (head[0] + dir_offset[0], head[1] + dir_offset[1])
        self.game.map.set_arrow(arrow_coord, DIR_ANGLE_DICT[self.direction])

class FeedSystem:
    def __init__(self, game, feed_amount: int):
        """
        Initialize FeedSystem Class

        Args:
            game (Game): Current Game object
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

    def add_feed(self, coord: Tuple[int, int], feed_type: str = 'normal'):
        self.feeds[coord] = Feed(coord=coord, feed_type=feed_type)
        self.game.state_manager.mark_cell_used(coord)
    
    def add_feed_random_coord(self, k: int, feed_type: str = 'normal'):
        if k < 1:
            return

        random_cell_coords = self.game.state_manager.get_random_available_cells(k)

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

        self.game.state_manager.mark_cell_free(coord)
    
    def render(self):
        for feed_coord, feed in self.feeds.items():
            self.game.map.get_cells()[feed_coord].put_surf(self.feed_surf)

class Feed:
    def __init__(self, coord, feed_type):
        self.coord = coord
        self.type = feed_type