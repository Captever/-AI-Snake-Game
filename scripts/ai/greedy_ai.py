from sys import maxsize

from .base_ai import BaseAI

from constants import DIR_OFFSET_DICT

from typing import Tuple
from queue import PriorityQueue

def is_in_bound(coord: Tuple[int, int], grid_size):
    x, y = coord
    return (0 <= x < grid_size[0]) and (0 <= y < grid_size[1])

def is_safe(coord: Tuple[int, int], p_body, grid_size):
    return is_in_bound(coord, grid_size) and (coord not in p_body)

def flood_fill_safety_check(coord: Tuple[int, int], p_body, grid_size):
    visited = set()
    queue = [coord]
    count = 0

    while queue:
        x, y = queue.pop(0)
        if (x, y) in visited or not is_safe((x, y), p_body, grid_size):
            continue
        visited.add((x, y))
        count += 1
        # 4-directional search
        for dx, dy in DIR_OFFSET_DICT.values():
            queue.append((x + dx, y + dy))

    return count

def a_star_with_safety_check(goal: Tuple[int, int], start: Tuple[int, int], p_body, grid_size):
    def heuristic(pos_a: Tuple[int, int], pos_b: Tuple[int, int]):
        return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])
    
    open_set = PriorityQueue()
    open_set.put((0, start))
    came_from = {}
    g_score = {start: 0}

    while not open_set.empty():
        _, current = open_set.get()
        if current == goal:
            # return optimal path
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.reverse()

            return path
    
        # 4-directional search
        for dx, dy in DIR_OFFSET_DICT.values():
            neighbor = (current[0] + dx, current[1] + dy)
            if not is_safe(neighbor, p_body, grid_size):
                continue

            # calculate g_score
            tentative_g_score = g_score[current] + 1
            safety_score = flood_fill_safety_check(neighbor, p_body, grid_size)

            safety_penalty = grid_size[0] * grid_size[1] - safety_score
            f_score = tentative_g_score + heuristic(neighbor, goal) + safety_penalty

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                open_set.put((f_score, neighbor))
    
    return None

class GreedyAI(BaseAI):
    def decide_direction(self):
        # explore the optimal direction from all possible directions
        bodies = self.game.player.bodies
        head = bodies[0]
        grid_size = self.game.grid_size

        best_direction = None
        min_distance = maxsize

        for direction, offset in DIR_OFFSET_DICT.items():
            next_position = (head[0] + offset[0], head[1] + offset[1])
            if (not self.game.is_in_bound(next_position)) or (next_position in bodies):
                continue

            for feed in self.game.fs.feeds:
                distance = abs(next_position[0] - feed[0]) + abs(next_position[1] - feed[1])
                if distance < min_distance:
                    min_distance = distance
                    best_direction = direction
        
        return best_direction if best_direction is not None else "surrender"
