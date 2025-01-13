from .base_ai import BaseAI

from typing import Tuple, List

def get_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]) -> int:
    return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[0])

def get_nearest_feed_pos(head: Tuple[int, int], feed_list: List[Tuple[int, int]]) -> Tuple[int, int]:
    min_dist = int('inf')
    ret = None

    for feed in feed_list:
        dist = get_dist(head, feed)

        if dist < min_dist:
            min_dist = dist
            ret = feed
    
    return ret

class RuleBasedAI(BaseAI):
    def decide_direction(self):
        head = self.game.player.bodies[0]

        feed_list = list(self.game.fs.feeds.keys())
        if not feed_list:
            return None
        
        target = get_nearest_feed_pos(feed_list)

        dx, dy = target[0] - head[0], target[1] - head[1]

        if abs(dx) > abs(dy):
            return 'E' if dx > 0 else 'W'
        else:
            return 'S' if dy > 0 else 'N'