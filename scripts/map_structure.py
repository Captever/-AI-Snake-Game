import pygame

from constants import *

from queue import Queue
from typing import Tuple, Dict, List

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

class Map:
    def __init__(self, game, size: Tuple[int, int], grid_num: Tuple[int, int], grid_thickness: int = 1, grid_color=(255, 255, 255, 128)):
        self.game = game
        self.size = size
        self.grid_num = grid_num
        self.grid_color = grid_color
        self.grid_thickness = grid_thickness

        self.outerline = None
        self.cell_size = (size[0] // grid_num[0], size[1] // grid_num[1])
        self.arrow = Arrow(self.cell_size)
        self.arrow_pos = None

        self.cells: Dict[Tuple[int, int], Cell] = {}

        for y in range(self.grid_num[1]):
            for x in range(self.grid_num[0]):
                curr_coord = (x, y)
                curr_cell = Cell(self.game, self.cell_size, self.grid_thickness, self.grid_color)

                self.cells[curr_coord] = curr_cell
    
    def add_outerline(self, outline_thickness: int = 3, outline_color=(255, 255, 255)):
        self.outerline = Outerline(self.size, outline_thickness, outline_color)
    
    def set_arrow(self, coord: Tuple[int, int], angle: float):
        self.arrow.set_angle(angle)
        self.arrow_pos = tuple(coord[i] * self.cell_size[i] for i in [0, 1])

    def render(self, surf, offset=(0, 0)):
        self.surf = pygame.Surface(self.size)

        for coord, cell in self.cells.items():
            x, y = coord
            cell_pos = (x * cell.size[0], y * cell.size[1])
            cell.render(self.surf, cell_pos)

        surf.blit(self.surf, offset)
        if self.outerline is not None:
            self.outerline.render(surf, offset)
        
        abs_arrow_pos = tuple(offset[i] + self.arrow_pos[i] for i in [0, 1])
        surf.blit(self.arrow.surf, abs_arrow_pos)
    
    def is_inside(self, coord) -> bool:
        is_in_x = 0 <= coord[0] < self.grid_num[0]
        is_in_y = 0 <= coord[1] < self.grid_num[1]
        return is_in_x and is_in_y

class Cell:
    def __init__(self, game, size: Tuple[int, int], outline_thickness: int = 1, outline_color=(255, 255, 255, 128)):
        self.game = game
        self.size = size
        self.outline_thickness = outline_thickness
        self.outline_color = outline_color

        self.surfs: Queue[Tuple[pygame.Surface, Tuple[int, int]]] = Queue()
    
    def put_surf(self, surf: pygame.Surface, offset: Tuple[int, int] = (0, 0)):
        self.surfs.put((surf, offset))

    def render(self, surf, offset=(0, 0)):
        self.surf = pygame.Surface(self.size, pygame.SRCALPHA)

        while not self.surfs.empty():
            target_surf, target_offset = self.surfs.get()
            self.surf.blit(target_surf, target_offset)

        # draw outline
        pygame.draw.rect(self.surf, self.outline_color, self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, offset)