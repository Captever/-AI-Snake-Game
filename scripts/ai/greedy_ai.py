from sys import maxsize

from .base_ai import BaseAI

from constants import DIR_OFFSET_DICT, SAFETY_CRITERIA

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
        """Determine the optimal direction with A* and Flood Fill for safety."""
        bodies = self.game.player.bodies
        head = bodies[0]
        grid_size = self.game.grid_size

        # step 1: calculate the minimum distance to all feeds using A*
        best_feed = None
        best_path = None
        shortest_distance = maxsize

        for feed in self.game.fs.feeds:
            # use the A* algorithm to search for paths
            path = self.a_star_with_safety(head, feed, bodies, grid_size)
            if path is not None and len(path) < shortest_distance:
                shortest_distance = len(path)
                best_feed = feed
                best_path = path

        # step 2: decide movement direction based on the nearest feed
        if best_path is None or len(best_path) == 0:
            return "surrender"  # If no path exists, surrender
        next_position = best_path[0]

        # step 3: determine movement direction
        for direction, offset in DIR_OFFSET_DICT.items():
            if (head[0] + offset[0], head[1] + offset[1]) == next_position:
                return direction

        return "surrender"

    def a_star_with_safety(self, start, goal, snake_body, grid_size):
        """use the A* algorithm to search for the shortest path while checking for safety"""
        def heuristic(pos1, pos2):
            # calculate Manhattan distance
            return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

        def is_safe(position, snake_body):
            """use Flood Fill to ensure the remaining area is sufficiently safe"""
            visited = set()
            queue = [position]
            count = 0

            while queue:
                x, y = queue.pop(0)
                if (x, y) in visited or not self.game.is_in_bound((x, y)) or (x, y) in snake_body:
                    continue
                visited.add((x, y))
                count += 1

                # perform four-directional search
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    queue.append((x + dx, y + dy))

            return count > SAFETY_CRITERIA  # safety assessment criteria

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

            # perform four-directional search
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                neighbor = (current[0] + dx, current[1] + dy)

                if (not self.game.is_in_bound(neighbor)) or (neighbor in snake_body):
                    continue

                # confirm safety using Flood Fill
                if not is_safe(neighbor, snake_body):
                    continue

                tentative_g_score = g_score[current] + 1
                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score = tentative_g_score + heuristic(neighbor, goal)
                    open_set.put((f_score, neighbor))

        return None  # there is no path
