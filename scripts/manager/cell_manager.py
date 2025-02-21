from random import sample
from typing import Tuple, Set, List

class CellManager:
    """
    Manages grid size, available cells.
    """
    def __init__(self, grid_size: Tuple[int, int]):
        """
        Initialize the game state manager with the given grid size.

        Args:
            grid_size (Tuple[int, int]): Size of the grid as (width, height).
        """
        self.grid_size: Tuple[int, int] = grid_size
        self.available_cells: Set[Tuple[int, int]] = set(
            (x, y) for x in range(grid_size[0]) for y in range(grid_size[1])
        )
    
    def get_grid_size(self):
        return self.grid_size

    def mark_cell_used(self, coord: Tuple[int, int]) -> None:
        """
        Mark a cell as used and remove it from available cells.

        Args:
            coord (Tuple[int, int]): The coordinate of the cell to mark as used.
        """
        if coord in self.available_cells:
            self.available_cells.discard(coord)

    def mark_cell_free(self, coord: Tuple[int, int]) -> None:
        """
        Mark a cell as free and add it back to available cells.

        Args:
            coord (Tuple[int, int]): The coordinate of the cell to mark as free.
        """
        self.available_cells.add(coord)

    def is_cell_available(self, coord: Tuple[int, int]) -> bool:
        """
        Check if a given cell is available.

        Args:
            coord (Tuple[int, int]): The coordinate of the cell to check.

        Returns:
            bool: True if the cell is available, False otherwise.
        """
        return coord in self.available_cells
    
    def get_remaining_available_cells_num(self) -> int:
        """
        Get the number of remaining available cells

        Returns:
            int: Number of remaining available cells.
        """
        return len(self.available_cells)

    def get_random_available_cells(self, k: int) -> List[Tuple[int, int]]:
        """
        Get `k` random available cells from the grid.

        Args:
            k (int): The number of cells to be returned.

        Returns:
            List[Tuple[int, int]]: Coordinates of `k` available cells.
        """
        return sample(list(self.available_cells), k=min(k, len(self.available_cells)))

    def reset(self) -> None:
        """
        Reset all cells in the grid to available state.
        """
        self.available_cells = set(
            (x, y) for x in range(self.grid_size[0]) for y in range(self.grid_size[1])
        )