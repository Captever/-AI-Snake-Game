from .base_ai import BaseAI

from sys import maxsize

from typing import Tuple, List

from constants import DIR_OFFSET_DICT

def get_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
    return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])

def get_neck_dir(head, neck) -> str:
    dir_offset = (neck[0] - head[0], neck[1] - head[1])

    for dir, offset in DIR_OFFSET_DICT.items():
        if dir_offset == offset:
            return dir

def is_even(num: int) -> bool:
    return num % 2 == 0

class RuleBasedAI(BaseAI):
    def __init__(self, method: str):
        super().__init__()
        self.method = method

    def decide_direction(self):
        head = self.game.player.get_head()
        grid_size = self.game.grid_size
        
        dir: str = None

        if self.method != "maximalism":
            neck = self.game.player.get_neck()

            neck_dir = get_neck_dir(head, neck)
            valid_dirs = ['E', 'W', 'S', 'N']
            valid_dirs.remove(neck_dir)

            target = self.game.fs.get_nearest_feed_coord(head)

            dx, dy = target[0] - head[0], target[1] - head[1]

            if self.method == "priority-larger":
                if abs(dx) > abs(dy):
                    dir = 'E' if dx > 0 else 'W'
                else:
                    dir = 'S' if dy > 0 else 'N'
            elif self.method == "priority-smaller":
                if dx == 0:
                    dir = 'S' if dy > 0 else 'N'
                elif dy == 0:
                    dir = 'E' if dx > 0 else 'W'

                if dir is None:
                    if abs(dx) < abs(dy):
                        dir = 'E' if dx > 0 else 'W'
                    else:
                        dir = 'S' if dy > 0 else 'N'
            
            # exclude directions with movement restrictions
            # - facing the neck
            # - direction out of bounds
            if dir not in valid_dirs:
                if dir in ['S', 'N']:
                    dir = 'E' if dx > 0 else 'W'

                    if head[0] == 0:
                        valid_dirs.remove('W')
                        dir = 'E'
                    elif head[0] == grid_size[0] - 1:
                        valid_dirs.remove('E')
                        dir = 'W'
                else:
                    dir = 'S' if dy > 0 else 'N'

                    if head[1] == 0:
                        valid_dirs.remove('N')
                        dir = 'S'
                    elif head[1] == grid_size[1] - 1:
                        valid_dirs.remove('S')
                        dir = 'N'
            
            # avoid the player's body
            for _ in range(len(valid_dirs)):
                next_pos = tuple(head[i] + DIR_OFFSET_DICT[dir][i] for i in [0, 1])
                if next_pos in self.game.player.get_bodies() or not self.game.is_in_bound(next_pos):
                    valid_dirs.remove(dir)
                    if len(valid_dirs) == 0:
                        dir = "surrender"
                    else:
                        dir = valid_dirs[0]
                else:
                    break
        else: # method: maximalism
            is_width_even, is_height_even = tuple(is_even(grid_size[i]) for i in [0, 1])

            if is_width_even:
                if head[0] < grid_size[0] - 1 and head[1] == grid_size[1] - 1:
                    dir = 'E'
                elif head[0] == 0 and head[1] < grid_size[1] - 1:
                    dir = 'S'
                elif head[0] == grid_size[0] - 1 and head[1] > 0:
                    dir = 'N'
                elif (not is_even(head[0]) and head[1] == 0) \
                     or (is_even(head[0]) and head[1] == grid_size[1] - 2):
                    dir = 'W'
                elif is_even(head[0]) and head[1] < grid_size[1] - 2:
                    dir = 'S'
                else:
                    dir = 'N'

            elif is_height_even:
                if head[0] < grid_size[0] - 1 and head[1] == grid_size[1] - 1:
                    dir = 'E'
                elif head[0] == 0 and head[1] < grid_size[1] - 1:
                    dir = 'S'
                elif head[1] == 0:
                    dir = 'W'
                elif (head[0] == grid_size[0] - 1 and not is_even(head[1])) \
                     or (head[0] == 1 and is_even(head[1])):
                    dir = 'N'
                elif head[0] > 1 and is_even(head[1]):
                    dir = 'W'
                else:
                    dir = 'E'

            else:
                # There will inevitably be empty spaces.
                # Causes too much deliberation, so it's put on hold.
                pass

        return dir
