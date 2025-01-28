from typing import Tuple

def get_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]):
    return abs(pos_b[0] - pos_a[0]) + abs(pos_b[1] - pos_a[1])