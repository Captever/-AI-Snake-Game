from .base_ai import BaseAI

from constants import DIR_OFFSET_DICT

class GreedyAI(BaseAI):
    def decide_direction(self):
        # explore the optimal direction from all possible directions
        head = self.game.player.bodies[0]
        possible_directions = ['E', 'W', 'N', 'S']
        best_direction = None
        min_distance = float('inf')

        for direction in possible_directions:
            offset = DIR_OFFSET_DICT[direction]
            next_position = (head[0] + offset[0], head[1] + offset[1])
            if not self.game.is_in_bound(next_position):
                continue

            for feed in self.game.fs.feeds:
                distance = abs(next_position[0] - feed[0]) + abs(next_position[1] - feed[1])
                if distance < min_distance:
                    min_distance = distance
                    best_direction = direction
        return best_direction
