from typing import Tuple

def get_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]):
    return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])

def get_x_y_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]):
    return (pos_b[0] - pos_a[0], pos_b[1] - pos_a[1])

def get_relative_x_y_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int], grid_size: Tuple[int, int]):
    x, y = get_x_y_dist(pos_a, pos_b)
    relative_x = x / grid_size[0]
    relative_y = y / grid_size[1]
    return (relative_x, relative_y)