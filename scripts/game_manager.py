import pygame
from enum import Enum
from random import sample
from typing import Tuple, Set, List

class GameState(Enum):
    # IN GAME
    ACTIVE = 100
    COUNTDOWN = 101
    PAUSED = 102
    SURRENDER = 103
    GAMEOVER = 110
    CLEAR = 109

class GameStateManager:
    """
    Centralized data manager for the game's state.
    Manages grid size, available cells, and provides utility methods for coordinate management.
    """
    def __init__(self, grid_num: Tuple[int, int]):
        """
        Initialize the game state manager with the given grid size.

        Args:
            grid_size (Tuple[int, int]): Size of the grid as (width, height).
        """
        self.grid_num: Tuple[int, int] = grid_num
        self.available_cells: Set[Tuple[int, int]] = set(
            (x, y) for x in range(grid_num[0]) for y in range(grid_num[1])
        )
    
    def get_grid_num(self):
        return self.grid_num

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

        Raises:
            ValueError: If there are not enough available cells remain.
        """
        if not self.available_cells:
            raise ValueError("There are not enough available cells in the grid.")
        return sample(list(self.available_cells), k=k)

    def reset(self) -> None:
        """
        Reset all cells in the grid to available state.
        """
        self.available_cells = set(
            (x, y) for x in range(self.grid_num[0]) for y in range(self.grid_num[1])
        )

class ScoreManager:
    def __init__(self, game, size: Tuple[int, int], font_weight: int, font_color):
        self.game = game
        self.size = size
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.font_weight = font_weight
        self.font_color = font_color

        self.score: int = 0
        self.clear_condition: int = None

        self.init_font_surfs()

    def init_font_surfs(self):
        self.title_font = pygame.font.SysFont('consolas', round(self.font_weight * 1.25), bold=True)
        self.score_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.9))
        
        self.centered_origin = (self.size[0] * 0.5, self.size[1] * 0.1)

        self.title_surf = self.title_font.render("Score", True, self.font_color)
        self.title_rect = self.title_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1])
        self.title_font_offset = self.title_rect.topleft
        self.update_score_font()
    
    def set_clear_condition(self, score: int):
        self.clear_condition = score
    
    def update_score(self, amount: int):
        self.score += amount
        self.update_score_font()
        if self.clear_condition is not None and self.score >= self.clear_condition:
            self.game.set_state(GameState.CLEAR)
    
    def update_score_font(self):
        self.score_surf = self.score_font.render(str(self.score), True, self.font_color)
        self.score_rect = self.score_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1] + self.title_rect.height * 1.1)
        self.score_font_offset = self.score_rect.topleft

    def render(self, surf, offset: Tuple[int, int] = (0, 0)):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.title_surf, self.title_font_offset)
        self.surf.blit(self.score_surf, self.score_font_offset)

        surf.blit(self.surf, offset)