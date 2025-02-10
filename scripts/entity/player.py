import pygame

import random

from constants import *

from scripts.entity.feed_system import Feed

from typing import List, Tuple

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
        grid_num = self.game.cell_manager.get_grid_num()
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

    def move(self):
        head, tail = self.bodies[0], self.bodies[-1]
        dir_offset = DIR_OFFSET_DICT[self.direction]
        new_head = (head[0] + dir_offset[0], head[1] + dir_offset[1])

        collision = self.check_collision(new_head)
        # game over when colliding with walls or the player's own body
        if collision[0] in ['wall', 'body']:
            self.game.set_state_gameover()
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
    
    def render(self):
        for body_coord in self.bodies:
            self.game.map.get_cells()[body_coord].put_surf(self.body_surf)

        head = self.bodies[0]
        dir_offset = DIR_OFFSET_DICT[self.direction]

        arrow_coord = (head[0] + dir_offset[0], head[1] + dir_offset[1])
        self.game.map.set_arrow(arrow_coord, DIR_ANGLE_DICT[self.direction])