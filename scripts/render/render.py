import pygame

from constants import DIR_ANGLE_DICT, OBJECT_OUTLINE_RATIO, BODY_OUTLINE_COLOR, BODY_COLOR, FEED_OUTLINE_COLOR, FEED_COLOR

from scripts.ui.ui_components import Outerline

from typing import List, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.entity.feed_system import Feed
    from scripts.ui.map_structure import Map

class Renderer:
    def __init__(self, cell_side_len: int, grid_origin: Tuple[int, int]):
        self.cell_side_len = cell_side_len
        self.grid_origin = grid_origin

    def render_player(self, surf, bodies: List[Tuple[int, int]]):
        for coord_x, coord_y in bodies:
            outline_thickness = round(self.cell_side_len * OBJECT_OUTLINE_RATIO)
            outline_rect = pygame.Rect(self.grid_origin[0] + coord_x * self.cell_side_len, self.grid_origin[1] + coord_y * self.cell_side_len,
                                      self.cell_side_len, self.cell_side_len)
            fill_rect = pygame.Rect(outline_rect.x + outline_thickness, outline_rect.y + outline_thickness,
                                     outline_rect.width - outline_thickness * 2, outline_rect.height - outline_thickness * 2)
            pygame.draw.rect(surf, BODY_OUTLINE_COLOR, outline_rect)
            pygame.draw.rect(surf, BODY_COLOR, fill_rect)

    def render_feeds(self, surf, feeds: List["Feed"]):
        for feed in feeds:
            coord_x, coord_y = feed.coord
            type = feed.type

            if type == 'normal':
                outline_thickness = round(self.cell_side_len * OBJECT_OUTLINE_RATIO)
                outline_rect = pygame.Rect(self.grid_origin[0] + coord_x * self.cell_side_len, self.grid_origin[1] + coord_y * self.cell_side_len,
                                        self.cell_side_len, self.cell_side_len)
                fill_rect = pygame.Rect(outline_rect.x + outline_thickness, outline_rect.y + outline_thickness,
                                        outline_rect.width - outline_thickness * 2, outline_rect.height - outline_thickness * 2)
                pygame.draw.rect(surf, FEED_OUTLINE_COLOR, outline_rect)
                pygame.draw.rect(surf, FEED_COLOR, fill_rect)

    def render_direction(self, surf, coord: Tuple[int, int], direction: str):
        pass

    def render_map(self, surf: pygame.Surface, map: "Map"):
        grid_size = map.grid_size
        arrow_pos = map.arrow_pos

        grid_rect = map.grid_rect
        grid_outerline_thickness = map.grid_outerline_thickness
        grid_outerline_color = map.grid_outerline_color

        cell_outerline_thickness = map.grid_thickness
        cell_outerline_color = map.grid_color

        for y_coord in range(grid_size[1]):
            for x_coord in range(grid_size[0]):
                cell_origin = (self.grid_origin[0] + self.cell_side_len * x_coord, self.grid_origin[1] + self.cell_side_len * y_coord)
                cell_rect = pygame.Rect(cell_origin, (self.cell_side_len, self.cell_side_len))
                # render outerline of cell
                self.render_outerline(surf, cell_rect, cell_outerline_thickness, cell_outerline_color)

        # render outerline of grid
        self.render_outerline(surf, grid_rect, grid_outerline_thickness, grid_outerline_color)
    
    def render_outerline(self, surf, rect: pygame.Rect, thickness: int = 1, color = (255, 255, 255, 255)):
        Outerline(rect, thickness, color).render(surf)

    def render_instruction(self, surf):
        pass

    def render_board(self, surf):
        pass