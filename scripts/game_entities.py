import pygame
import random

from constants import *

from typing import Tuple, Dict


class Player:
    def __init__(self, game, initial_length):
        self.game = game
        self.length = initial_length
        self.direction = None
        self.move_accum = 0

        self.body_surf: pygame.Surface = self.make_surf()
        self.bodies = self.make_bodies()
    
    def make_bodies(self):
        rand_coord = (random.randint(0, GRID_NUM[0] - 1), random.randint(0, GRID_NUM[1] - 1))
        ret = [rand_coord]
        self.game.map.mark_cell_used(rand_coord)
        
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
                    self.game.map.mark_cell_used(body_coord)

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

    def make_surf(self) -> pygame.Surface:
        size = self.game.map.get_cell_size()
        outline_thickness = round(size[0] * OBJECT_OUTLINE_RATIO)
        ret = pygame.Surface(size)
        pygame.draw.rect(ret, BODY_OUTLINE_COLOR, ret.get_rect())
        pygame.draw.rect(ret, BODY_COLOR, pygame.Rect(outline_thickness, outline_thickness, size[0] - outline_thickness * 2, size[1] - outline_thickness * 2))
        return ret

    def set_direction(self, dir: str):
        if dir not in DIR_OFFSET_DICT:
            raise ValueError("parameter(dir) must be the one of [EWSN]")
        
        if not self.validate_direction(dir):
            return
        
        self.direction = dir
    
    def validate_direction(self, dir: str) -> bool:
        if dir not in DIR_OFFSET_DICT:
            raise ValueError("parameter(dir) must be the one of [EWSN]")
        
        dir_offset = DIR_OFFSET_DICT[dir]

        head = self.bodies[0]
        next_to_head = self.bodies[1]

        next_coord = (head[0] + dir_offset[0], head[1] + dir_offset[1])
        if not self.game.is_in_bound(next_coord) or next_coord == next_to_head:
            return False

        return True
        
    def check_collision(self, target) -> int:
        return self.game.check_collision(target)
        
    def move_sequence(self):
        if self.move_accum >= MOVE_DELAY:
            self.move_accum = 0
            self.move()
        else:
            self.move_accum += 1

    def move(self):
        head, tail = self.bodies[0], self.bodies[-1]
        dir_offset = DIR_OFFSET_DICT[self.direction]
        new_head = (head[0] + dir_offset[0], head[1] + dir_offset[1])

        self.bodies = [new_head] + self.bodies[:-1]

        collision = self.check_collision(new_head)
        # game over when colliding with walls or the player's own body
        if collision[0] in ['wall', 'body']:
            self.game.gameover()
            return
        # length increases when eat feed
        if collision[0] == 'feed':
            curr_feed = collision[1]
            self.eat_feed(tail, curr_feed)
        else:
            self.game.map.mark_cell_free(tail)
        self.game.map.mark_cell_used(new_head)
    
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
    def __init__(self, game):
        self.feeds: Dict[Tuple[int, int], Feed] = {}
        self.game = game
        
        self.feed_surf: pygame.Surface = self.make_surf()

    def make_surf(self) -> pygame.Surface:
        size = self.game.map.get_cell_size()
        outline_thickness = round(size[0] * OBJECT_OUTLINE_RATIO)
        ret = pygame.Surface(size)
        pygame.draw.rect(ret, FEED_OUTLINE_COLOR, ret.get_rect())
        pygame.draw.rect(ret, FEED_COLOR, pygame.Rect(outline_thickness, outline_thickness, size[0] - outline_thickness * 2, size[1] - outline_thickness * 2))
        return ret
    
    def is_feed_empty(self, feed_type: str = 'normal'):
        for feed in self.feeds.values():
            if feed.type == feed_type:
                return False
        return True
    
    def add_feed(self, coord: Tuple[int, int], feed_type: str = 'normal'):
        self.feeds[coord] = Feed(coord=coord, feed_type=feed_type)
        self.game.map.mark_cell_used(coord)
    
    def add_feed_random_coord(self, num: int, feed_type: str = 'normal'):
        random_cell_coords = self.game.map.get_available_cell_coords(num)

        if not len(random_cell_coords):
            self.game.clear()

        for rand_coord in random_cell_coords:
            self.add_feed(rand_coord, feed_type)
    
    def remove_feed(self, coord: Tuple[int, int]):
        target_type = self.feeds[coord].type
        del self.feeds[coord]
        
        # if there is no same type feed, add new feeds
        if self.is_feed_empty(target_type):
            self.add_feed_random_coord(FEED_NUM, feed_type=target_type)

        self.game.map.mark_cell_free(coord)
    
    def render(self):
        for feed_coord, feed in self.feeds.items():
            self.game.map.get_cells()[feed_coord].put_surf(self.feed_surf)

class Feed:
    def __init__(self, coord, feed_type):
        self.coord = coord
        self.type = feed_type