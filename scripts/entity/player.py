from constants import DIR_OFFSET_DICT

from typing import List, Tuple

class Player:
    def __init__(self, bodies: List[Tuple[int, int]]):
        """
        Initialize Player Class

        Args:
            bodies (List[Tuple[int, int]]): initial bodies of the player
        """
        self._bodies = bodies

    def get_head(self) -> Tuple[int, int]:
        """
        Get player's second first coord
        """
        return self._bodies[0]
    
    def get_neck(self) -> Tuple[int, int]:
        """
        Get player's second body coord
        """
        return self._bodies[1]
    
    def get_tail(self) -> Tuple[int, int]:
        """
        Get player's second last coord
        """
        return self._bodies[-1]
    
    def get_next_head(self, dir: str):
        head = self.get_head()
        dir_offset = DIR_OFFSET_DICT[dir]

        next_head = tuple(head[i] + dir_offset[i] for i in [0, 1])

        return next_head
    
    def get_bodies(self, start_index: int = 0) -> List[Tuple[int, int]]:
        return self._bodies[start_index:]
    
    def get_bodies_without_tail(self) -> List[Tuple[int, int]]:
        return self._bodies[:-1]
    
    def add_head(self, coord):
        self._bodies.insert(0, coord)

    def add_tail(self, coord):
        self._bodies.append(coord)

    def remove_tail(self, num: int = 1):
        for _ in range(num):
            self._bodies.pop()