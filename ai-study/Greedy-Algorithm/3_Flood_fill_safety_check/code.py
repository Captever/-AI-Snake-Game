from sys import maxsize

from .base_ai import BaseAI

from constants import DIR_OFFSET_DICT

from typing import Tuple

def is_in_bound(coord: Tuple[int, int], grid_size):
    x, y = coord
    return (0 <= x < grid_size[0]) and (0 <= y < grid_size[1])

def is_safe(coord: Tuple[int, int], p_bodies, grid_size):
    return is_in_bound(coord, grid_size) and (coord not in p_bodies)

def get_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]):
    return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])

def flood_fill_safety_check(coord: Tuple[int, int], p_bodies, grid_size):
    visited = set()
    queue = [coord]
    count = 0

    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited or not is_safe((x, y), p_bodies, grid_size):
            continue
        visited.add((x, y))
        count += 1
        # 4-directional search
        for dx, dy in DIR_OFFSET_DICT.values():
            queue.append((x + dx, y + dy))

    return count

def get_closest_dist_with_feed(coord: Tuple[int, int], feeds):
    closest_feed = None
    min_dist = maxsize

    for feed in feeds:
        dist = get_dist(coord, feed)

        if dist < min_dist:
            closest_feed = feed
            min_dist = dist
    
    return (min_dist, closest_feed)

class GreedyAI(BaseAI):
    def decide_direction(self):
        bodies = self.game.player.bodies
        head = bodies[0]
        grid_size = self.game.grid_size
        feeds = self.game.fs.feeds

        closest_feed_list_by_dir = []
        
        for dir, (offset_x, offset_y) in DIR_OFFSET_DICT.items():
            next_coord = (head[0] + offset_x, head[1] + offset_y)
            if not is_safe(next_coord, bodies, grid_size):
                continue
            
            closest_feed_list_by_dir.append((dir, get_closest_dist_with_feed(next_coord, feeds)))
        
        if len(closest_feed_list_by_dir) == 0:
            return "surrender"

        closest_sorted_feeds = sorted(closest_feed_list_by_dir, key=lambda x: x[1][0]) # compare with distance

        for target_dir, _ in closest_sorted_feeds:
            offset_x, offset_y = DIR_OFFSET_DICT[target_dir]
            target_coord = (head[0] + offset_x, head[1] + offset_y)

            if flood_fill_safety_check(target_coord, bodies, grid_size) > len(bodies):
                return target_dir
            
        return "surrender"