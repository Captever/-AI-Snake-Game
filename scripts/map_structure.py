import pygame
from random import sample

from constants import *

from queue import Queue
from typing import Tuple, Dict, List

class Map:
    def __init__(self, game, map_side_length: Tuple[int, int], grid_num: Tuple[int, int], grid_thickness: int = 1, grid_color=(255, 255, 255, 128)):
        self.game = game
        self.side_length = map_side_length
        self.grid_num = grid_num

        self.outerline = None
        self.available_cells = set((x, y) for x in range(grid_num[0]) for y in range(grid_num[1]))

        # divide by grid height for vertical rect, grid width for horizontal rect
        grid_diff = grid_num[0] - grid_num[1]
        grid_coord_diff = abs(grid_diff) // 2
        if grid_diff > 0:
            self.cell_side_length = map_side_length // grid_num[0]
            self.grid_offset = (0, self.cell_side_length * grid_coord_diff)
        else:
            self.cell_side_length = map_side_length // grid_num[1]
            self.grid_offset = (self.cell_side_length * grid_coord_diff, 0)
        
        self.arrow = Arrow(self.get_cell_size())
        self.arrow_pos = None

        self.grid = Grid(self.cell_side_length, grid_num, grid_thickness, grid_color)
        self.grid.add_outerline(GRID_OUTERLINE_THICKNESS, WHITE)
    
    def add_outerline(self, outline_thickness: int = 3, outline_color=(255, 255, 255)):
        self.outerline = Outerline(self.get_size(), outline_thickness, outline_color)
    
    def set_arrow(self, coord: Tuple[int, int], angle: float):
        self.arrow.set_angle(angle)
        self.arrow_pos = tuple(coord[i] * self.cell_side_length for i in [0, 1])

    # remove coordinate currently in use
    def mark_cell_used(self, coord: Tuple[int, int]):
        self.available_cells.discard(coord)
    
    # restore coordinate no longer in use
    def mark_cell_free(self, coord: Tuple[int, int]):
        self.available_cells.add(coord)
    
    def is_inside(self, coord) -> bool:
        is_in_x = 0 <= coord[0] < self.grid_num[0]
        is_in_y = 0 <= coord[1] < self.grid_num[1]
        return is_in_x and is_in_y
    
    def get_remaining_cell_num(self):
        return len(self.available_cells)

    def get_available_cell_coords(self, num: int = 1) -> List[Tuple[int, int]]:
        remaining_cell_num = self.get_remaining_cell_num()
        return sample(list(self.available_cells), k=min(remaining_cell_num, num))

    def get_cells(self):
        return self.grid.cells

    def get_size(self) -> Tuple[int, int]:
        return (self.side_length, self.side_length)

    def get_cell_size(self) -> Tuple[int, int]:
        return (self.cell_side_length, self.cell_side_length)

    def render(self, surf, offset=(0, 0)):
        self.surf = pygame.Surface(self.get_size())

        self.grid.render(self.surf, self.grid_offset)

        surf.blit(self.surf, offset)
        if self.outerline is not None:
            self.outerline.render(surf, offset)
        
        abs_arrow_pos = tuple(offset[i] + self.grid_offset[i] + self.arrow_pos[i] for i in [0, 1])
        surf.blit(self.arrow.surf, abs_arrow_pos)

class Grid:
    def __init__(self, cell_side_length: int, grid_num: Tuple[int, int], cell_outline_thickness: int = 1, cell_outline_color=WHITE):
        self.cell_side_length = cell_side_length
        self.size = tuple(cell_side_length * grid_num[i] for i in [0, 1])
        self.grid_num = grid_num

        self.outerline = None

        self.cells: Dict[Tuple[int, int], Cell] = {}

        for y in range(self.grid_num[1]):
            for x in range(self.grid_num[0]):
                curr_coord = (x, y)
                curr_cell = Cell(cell_side_length, cell_outline_thickness, cell_outline_color)

                self.cells[curr_coord] = curr_cell
    
    def add_outerline(self, outline_thickness: int = 3, outline_color=(255, 255, 255)):
        self.outerline = Outerline(self.size, outline_thickness, outline_color)
    
    def render(self, surf, offset=(0, 0)):
        self.surf = pygame.Surface(self.size)

        for coord, cell in self.cells.items():
            x, y = coord
            cell_pos = (x * self.cell_side_length, y * self.cell_side_length)
            cell.render(self.surf, cell_pos)

        surf.blit(self.surf, offset)
        if self.outerline is not None:
            self.outerline.render(surf, offset)

class Cell:
    def __init__(self, cell_side_length: int, outline_thickness: int = 1, outline_color=(255, 255, 255, 128)):
        self.side_length = cell_side_length
        self.outline_thickness = outline_thickness
        self.outline_color = outline_color

        self.surfs: Queue[Tuple[pygame.Surface, Tuple[int, int]]] = Queue()
    
    def put_surf(self, surf: pygame.Surface, offset: Tuple[int, int] = (0, 0)):
        self.surfs.put((surf, offset))

    def render(self, surf, offset=(0, 0)):
        self.surf = pygame.Surface(self.get_size(), pygame.SRCALPHA)

        while not self.surfs.empty():
            target_surf, target_offset = self.surfs.get()
            self.surf.blit(target_surf, target_offset)

        # draw outline
        pygame.draw.rect(self.surf, self.outline_color, self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, offset)
    
    def get_size(self) -> Tuple[int, int]:
        return (self.side_length, self.side_length)

class Outerline:
    def __init__(self, size: Tuple[int, int], thickness: int = 1, color=(255, 255, 255)):
        self.thickness = thickness

        outer_rect = pygame.Rect(0, 0, size[0] + thickness * 2, size[1] + thickness * 2)

        self.surf = pygame.Surface((outer_rect.width, outer_rect.height), pygame.SRCALPHA)
        self.surf.fill((0, 0, 0, 0))

        pygame.draw.rect(self.surf, color, outer_rect, max(1, thickness)) # minimum value of width: 1

    def render(self, surf, offset=(0, 0)):
        adjusted_pos = (offset[0] - self.thickness, offset[1] - self.thickness)

        surf.blit(self.surf, adjusted_pos)
        
class Arrow:
    def __init__(self, cell_size: Tuple[int, int], color=WHITE, width=0):
        self.surf = pygame.Surface(cell_size, pygame.SRCALPHA)
        self.surf.fill((0, 0, 0, 0))
        self.angle: float = 0

        arrow_size = (cell_size[0] * DIR_ARROW_RATIO, cell_size[1] * DIR_ARROW_RATIO)
        arrow_pos = (cell_size[0] * (1 - DIR_ARROW_RATIO) // 2, cell_size[1] * (1 - DIR_ARROW_RATIO) // 2)
        arrow_surf = pygame.Surface(arrow_size, pygame.SRCALPHA)
        arrow_surf.fill((0, 0, 0, 0))

        points = ((0, 0), (0, arrow_size[1]), (arrow_size[0] / 2, arrow_size[1] / 2))
        pygame.draw.polygon(arrow_surf, color, points, width=width)

        self.surf.blit(arrow_surf, arrow_pos)

    def set_angle(self, angle: float):
        self.surf = pygame.transform.rotate(self.surf, angle - self.angle)
        self.angle = angle