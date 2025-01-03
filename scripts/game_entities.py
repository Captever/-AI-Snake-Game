import random

from constants import *

from typing import Tuple


class Player:
    def __init__(self, game, initial_length):
        self.game = game
        self.length = initial_length
        
        rand_pos = (random.randint(0, GRID_NUM[0] - 1), random.randint(0, GRID_NUM[1] - 1))

        self.bodies = [rand_pos]
        self.direction = None
        self.move_accum = 0
        
        dirs = ['E', 'W', 'S', 'N']
        for _ in range(initial_length - 1):
            prev_body_pos = self.bodies[-1]
            dirs_copy = dirs.copy()
            while True:
                dir = dirs_copy[random.randint(0, len(dirs_copy) - 1)]
                dir_offset = DIR_OFFSET_DICT[dir]
                body_pos = (prev_body_pos[0] + dir_offset[0], prev_body_pos[1] + dir_offset[1])
                # validation
                if self.game.is_in_bound(body_pos) and body_pos not in self.bodies:
                    if self.direction == None:
                        if dir == 'E':
                            self.direction = 'W'
                        elif dir == 'W':
                            self.direction = 'E'
                        elif dir == 'S':
                            self.direction = 'N'
                        else:
                            self.direction = 'S'
                    self.bodies.append(body_pos)
                    break
                else:
                    dirs_copy.remove(dir)
    
    def set_direction(self, dir: str):
        if dir not in DIR_OFFSET_DICT:
            raise ValueError("parameter(dir) must be the one of [EWSN]")
        
        if self.validate_direction(dir):
            self.direction = dir
    
    def validate_direction(self, dir: str) -> bool:
        if dir not in DIR_OFFSET_DICT:
            raise ValueError("parameter(dir) must be the one of [EWSN]")
        
        dir_offset = DIR_OFFSET_DICT[dir]

        head = self.bodies[0]
        next_to_head = self.bodies[1]

        next_pos = (head[0] + dir_offset[0], head[1] + dir_offset[1])
        if not self.game.is_in_bound(next_pos) or next_pos == next_to_head:
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
        prev_head = self.bodies[0]
        dir_offset = DIR_OFFSET_DICT[self.direction]
        head = (prev_head[0] + dir_offset[0], prev_head[1] + dir_offset[1])

        collision = self.check_collision(head)
        # game over when colliding with walls or the player's own body
        if collision[0] in ['wall', 'body']:
            self.game.gameover()
            return
        # length increases when eat feed
        if collision[0] == 'feed':
            self.bodies.append(self.bodies[-1])
            curr_feed = collision[1]
            self.game.remove_feed(curr_feed.pos)

        updated_bodies = [head] + self.bodies[:-1]
        self.bodies = updated_bodies

class FeedSystem:
    def __init__(self, game):
        self.feeds = {}
        self.game = game
    
    def add_feed(self, pos: Tuple[int, int], feed_type: str = "normal"):
        self.feeds[pos] = Feed(pos=pos, feed_type=feed_type)
    
    def add_feed_random_pos(self, num: int, feed_type: str = "normal"):
        for _ in range(num):
            while True:
                rand_pos = (random.randint(0, GRID_NUM[0] - 1), random.randint(0, GRID_NUM[1] - 1))
                # validation
                if rand_pos not in self.game.player.bodies:
                    self.add_feed(pos=rand_pos, feed_type=feed_type)
                    break
    
    def remove_feed(self, pos: Tuple[int, int]):
        del self.feeds[pos]

class Feed:
    def __init__(self, pos, feed_type):
        self.pos = pos
        self.type = feed_type