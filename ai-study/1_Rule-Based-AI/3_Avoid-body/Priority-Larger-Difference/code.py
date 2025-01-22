from .base_ai import BaseAI

from sys import maxsize

from typing import Tuple, List

from constants import DIR_OFFSET_DICT

def get_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
    return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])

def get_nearest_feed_pos(head: Tuple[int, int], feed_list: List[Tuple[int, int]]) -> Tuple[int, int]:
    min_dist = maxsize
    ret = None

    for feed in feed_list:
        dist = get_dist(head, feed)

        if dist < min_dist:
            min_dist = dist
            ret = feed
    
    return ret

def get_neck_dir(head, neck) -> str:
    dir_offset = (neck[0] - head[0], neck[1] - head[1])

    for dir, offset in DIR_OFFSET_DICT.items():
        if dir_offset == offset:
            return dir

class RuleBasedAI(BaseAI):
    def decide_direction(self):
        head = self.game.player.bodies[0]
        neck = self.game.player.bodies[1]

        dir: str = None
        neck_dir = get_neck_dir(head, neck)
        valid_dirs = ['E', 'W', 'S', 'N']
        valid_dirs.remove(neck_dir)

        feed_list = list(self.game.fs.feeds.keys())
        if not feed_list:
            return None
        
        target = get_nearest_feed_pos(head, feed_list)

        dx, dy = target[0] - head[0], target[1] - head[1]

        if abs(dx) > abs(dy):
            dir = 'E' if dx > 0 else 'W'
        else:
            dir = 'S' if dy > 0 else 'N'
        
        # exclude directions with movement restrictions
        # - facing the neck
        # - direction out of bounds
        if dir not in valid_dirs:
            grid_size = self.game.grid_size

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
            if next_pos in self.game.player.bodies or not self.game.is_in_bound(next_pos):
                valid_dirs.remove(dir)
                if len(valid_dirs) == 0:
                    dir = "surrender"
                else:
                    dir = valid_dirs[0]
            else:
                break
        
        return dir
