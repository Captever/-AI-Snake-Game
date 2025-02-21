import pygame

from constants import DIR_ANGLE_DICT

from scripts.ui.ui_components import Outerline

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.entity.feed_system import Feed
    from scripts.ui.map_structure import Map

class Renderer:
    def render_player(self, surf, bodies: List[Tuple[int, int]]):
        pass

    def render_feeds(self, surf, feeds: List["Feed"]):
        pass

    def render_direction(self, surf, pos: Tuple[int, int], direction: str):
        pass

    def render_map(self, surf: pygame.Surface, map: "Map"):
        grid_size = map.grid_size
        arrow_pos = map.arrow_pos

        map_rect = map.rect
        map_outerline_thickness = map.outerline_thickness
        map_outerline_color = map.outerline_color

        grid_rect = map.grid_rect
        grid_origin = grid_rect.topleft
        grid_outerline_thickness = map.grid_outerline_thickness
        grid_outerline_color = map.grid_outerline_color

        cell_side_len: int = map.cell_side_len
        cell_outerline_thickness = map.grid_thickness
        cell_outerline_color = map.grid_color

        for y_coord in range(grid_size[1]):
            for x_coord in range(grid_size[0]):
                cell_origin = (grid_origin[0] + cell_side_len * x_coord, grid_origin[1] + cell_side_len * y_coord)
                cell_rect = pygame.Rect(cell_origin, (cell_side_len, cell_side_len))
                self.render_outerline(surf, cell_rect, cell_outerline_thickness, cell_outerline_color)

        self.render_outerline(surf, grid_rect, grid_outerline_thickness, grid_outerline_color)

        self.render_outerline(surf, map_rect, map_outerline_thickness, map_outerline_color)
    
    def render_outerline(self, surf, rect: pygame.Rect, thickness: int = 1, color = (255, 255, 255, 255)):
        Outerline(rect, thickness, color).render(surf)

    def render_instruction(self, surf):
        pass

    def render_board(self, surf):
        pass