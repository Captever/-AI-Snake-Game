import pygame

import random

from constants import *

from scripts.entity.feed_system import Feed
from scripts.manager.game_manager import GameState

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.game.base_game import BaseGame
    from scripts.ui.map_structure import Map

class Player:
    def __init__(self, game: "BaseGame", initial_length):
        """
        Initialize Player Class

        Args:
            game (BaseGame): Current Game object
            initial_length (int): initial length of the player
        """
        self.game = game
        self.length: int = initial_length

        self.bodies: List[Tuple[int, int]] = self.make_bodies()

    def get_head_coord(self) -> Tuple[int, int]:
        return self.bodies[0]
    
    def make_bodies(self):
        grid_num = self.game.cell_manager.get_grid_size()
        rand_coord = (random.randint(0, grid_num[0] - 1), random.randint(0, grid_num[1] - 1))
        ret = [rand_coord]
        self.game.cell_manager.mark_cell_used(rand_coord)
        
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
                    self.game.cell_manager.mark_cell_used(body_coord)

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

    def set_direction(self, dir: str, with_validate: bool = True):
        if dir not in DIR_OFFSET_DICT:
            raise ValueError("parameter(dir) must be the one of [EWSN]")
        
        if with_validate and not self.validate_direction(dir):
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
    
    def get_bodies_as_list(self):
        return [list(body) for body in self.bodies]

    def move(self, direction: str):
        head, tail = self.bodies[0], self.bodies[-1]
        dir_offset = DIR_OFFSET_DICT[direction]
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
            self.game.cell_manager.mark_cell_free(tail)
        self.game.cell_manager.mark_cell_used(new_head)

        self.bodies = [new_head] + self.bodies[:-1]
    
    def eat_feed(self, tail_coord: Tuple[int, int], feed: Feed):
        self.bodies.append(tail_coord)
        self.game.remove_feed(feed.coord)

        self.game.update_score(1)