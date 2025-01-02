import pygame
import random

DIR_OFFSET_DICT = {
    'E': (1, 0),
    'W': (-1, 0),
    'S': (0, 1),
    'N': (0, -1),
}

class Player:
    def __init__(self, game, initial_length):
        self.game = game
        self.length = initial_length
        
        rand_pos = (random.randint(0, self.game.grid_num[0] - 1), random.randint(0, self.game.grid_num[1] - 1))

        self.bodies = []
        
        self.bodies.append(rand_pos)
        
        pos_possibilities = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for _ in range(initial_length - 1):
            prev_body_pos = self.bodies[-1]
            while True:
                possibilities = pos_possibilities.copy()
                curr_poss = possibilities[random.randint(0, len(possibilities) - 1)]
                curr_body_pos = (prev_body_pos[0] + curr_poss[0], prev_body_pos[1] + curr_poss[1])
                # validation
                if self.game.is_in_bound(curr_body_pos) and curr_body_pos not in self.bodies:
                    self.bodies.append(curr_body_pos)
                    break
                else:
                    possibilities.remove(curr_poss)
    
    def set_direction(self, dir):
        if dir not in ['E', 'W', 'S', 'N']:
            raise ValueError("dir must be the one of EWSN")
        
    def check_collision(self, target) -> int:
        return self.game.check_entity(target)
        
    def move(self):
        prev_head = self.bodies[0]
        dir_offset = DIR_OFFSET_DICT[self.game.direction]
        head = (prev_head[0] + dir_offset[0], prev_head[1] + dir_offset[1])

        collision = self.check_collision(head)
        # game over when colliding with walls or the player's own body
        if collision == 99 or collision == 0:
            self.game.gameover()
            return
        # length increases when eat feed
        if collision == 1:
            self.bodies.append(self.bodies[-1])
            # TODO: remove feed

        updated_bodies = []
        updated_bodies.append(head)

        for idx in range(1, len(self.bodies)):
            updated_bodies.append(self.bodies[idx - 1])
        
        self.bodies = updated_bodies

class Feed:
    def __init__(self, game):
        self.game = game

        self.pos = ()
        self.type = ''

        # generate randomly
        while True:
            rand_pos = (random.randint(0, self.game.grid_num[0]), random.randint(0, self.game.grid_num[1]))
            # validation
            if 0 <= rand_pos[0] < self.game.grid_num[0] and 0 <= rand_pos[1] < self.game.grid_num[1] and rand_pos not in self.game.player.bodies:
                self.pos = rand_pos
                self.type = 'normal'
                break