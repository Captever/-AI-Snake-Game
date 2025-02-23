import pygame

from constants import *

from typing import Tuple

class Map:
    def __init__(self, rect: pygame.Rect, grid_size: Tuple[int, int], outerline_thickness: int = 3, outerline_color=(255, 255, 255, 255), grid_outerline_thickness: int = 1, grid_outerline_color=(255, 255, 255, 255), grid_thickness: int = 1, grid_color=(255, 255, 255, 128)):
        self.rect = rect
        self.side_len: int = rect.width
        self.origin = rect.topleft
        self.grid_size = grid_size

        # about outerline
        self.outerline_thickness = outerline_thickness
        self.outerline_color = outerline_color
        self.grid_outerline_thickness = grid_outerline_thickness
        self.grid_outerline_color = grid_outerline_color
        self.grid_thickness = grid_thickness
        self.grid_color = grid_color

        # divide by grid height for vertical rect, grid width for horizontal rect
        grid_diff = self.grid_size[0] - self.grid_size[1]
        self.cell_side_len = self.side_len // (self.grid_size[0] if grid_diff > 0 else self.grid_size[1])
        
        # about calculating grid
        grid_width, grid_height = tuple(self.cell_side_len * self.grid_size[i] for i in [0, 1])
        grid_origin = (self.origin[0] + (self.side_len - grid_width) // 2, self.origin[1] + (self.side_len - grid_height) // 2)
        self.grid_rect = pygame.Rect(grid_origin, (grid_width, grid_height))

    def is_inside(self, coord) -> bool:
        is_in_x = 0 <= coord[0] < self.grid_size[0]
        is_in_y = 0 <= coord[1] < self.grid_size[1]
        return is_in_x and is_in_y

    def get_size(self) -> Tuple[int, int]:
        return (self.side_len, self.side_len)

    def get_cell_size(self) -> Tuple[int, int]:
        return (self.cell_side_len, self.cell_side_len)