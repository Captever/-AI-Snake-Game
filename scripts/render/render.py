import pygame

from constants import DIR_OFFSET_DICT, DIR_COLOR, DIR_ARROW_RATIO, OBJECT_OUTLINE_RATIO, BODY_OUTLINE_COLOR, BODY_COLOR, FEED_OUTLINE_COLOR, FEED_COLOR

from scripts.ui.ui_components import Outerline

from typing import List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.entity.feed_system import Feed
    from scripts.ui.map_structure import Map
    from scripts.ui.ui_components import Board
    from scripts.ui.instruction import Instruction

class GameRenderer:
    def __init__(self):
        self.cell_side_len: int = None
        self.grid_origin: Tuple[int, int] = None
        self.boards: Dict[str, "Board"] = None
        self.instruction: Instruction = None

    def set_cell_side_len(self, cell_side_len: int):
        self.cell_side_len = cell_side_len
    
    def set_grid_origin(self, grid_origin: Tuple[int, int]):
        self.grid_origin = grid_origin

    def set_boards(self, boards: Dict[str, "Board"]):
        self.boards = boards

    def set_instruction(self, instruction: "Instruction"):
        self.instruction = instruction

    def render_player(self, surf: pygame.Surface, bodies: List[Tuple[int, int]]):
        for coord_x, coord_y in bodies:
            outline_thickness = round(self.cell_side_len * OBJECT_OUTLINE_RATIO)
            outline_rect = pygame.Rect(self.grid_origin[0] + coord_x * self.cell_side_len, self.grid_origin[1] + coord_y * self.cell_side_len,
                                      self.cell_side_len, self.cell_side_len)
            fill_rect = pygame.Rect(outline_rect.x + outline_thickness, outline_rect.y + outline_thickness,
                                     outline_rect.width - outline_thickness * 2, outline_rect.height - outline_thickness * 2)
            pygame.draw.rect(surf, BODY_OUTLINE_COLOR, outline_rect)
            pygame.draw.rect(surf, BODY_COLOR, fill_rect)

    def render_feeds(self, surf: pygame.Surface, feeds: List["Feed"]):
        for feed in feeds:
            coord_x, coord_y = feed.get_coord()
            type = feed.get_type()

            if type == 'normal':
                outline_thickness = round(self.cell_side_len * OBJECT_OUTLINE_RATIO)
                outline_rect = pygame.Rect(self.grid_origin[0] + coord_x * self.cell_side_len, self.grid_origin[1] + coord_y * self.cell_side_len,
                                        self.cell_side_len, self.cell_side_len)
                fill_rect = pygame.Rect(outline_rect.x + outline_thickness, outline_rect.y + outline_thickness,
                                        outline_rect.width - outline_thickness * 2, outline_rect.height - outline_thickness * 2)
                pygame.draw.rect(surf, FEED_OUTLINE_COLOR, outline_rect)
                pygame.draw.rect(surf, FEED_COLOR, fill_rect)

    def render_direction_arrow(self, surf: pygame.Surface, head_coord: Tuple[int, int], direction: str):
        dir_offset = DIR_OFFSET_DICT[direction]
        arrow_coord = tuple(head_coord[i] + dir_offset[i] for i in [0, 1])
        cell_mid_dist = self.cell_side_len // 2
        center_x, center_y = tuple(self.grid_origin[i] + arrow_coord[i] * self.cell_side_len + cell_mid_dist for i in [0, 1])

        arrow_size = self.cell_side_len * DIR_ARROW_RATIO

        points = self.get_arrow_points(center_x, center_y, arrow_size, direction)
        pygame.draw.polygon(surf, DIR_COLOR, points)

    def get_arrow_points(self, center_x: int, center_y: int, size: int, direction: str) -> List[Tuple[int, int]]:
        point_offset = size * 4 // 5  # size * 0.8

        if direction == 'E':
            return [(center_x - size, center_y + point_offset), (center_x - size, center_y - point_offset), (center_x, center_y)]
        elif direction == 'W':
            return [(center_x + size, center_y + point_offset), (center_x + size, center_y - point_offset), (center_x, center_y)]
        elif direction == 'S':
            return [(center_x + point_offset, center_y - size), (center_x - point_offset, center_y - size), (center_x, center_y)]
        else:
            return [(center_x + point_offset, center_y + size), (center_x - point_offset, center_y + size), (center_x, center_y)]

    def render_map(self, surf: pygame.Surface, map: "Map"):
        grid_size = map.grid_size

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
    
    def render_outerline(self, surf: pygame.Surface, rect: pygame.Rect, thickness: int = 1, color = (255, 255, 255, 255)):
        Outerline(rect, thickness, color).render(surf)

    def render_ui(self, surf: pygame.Surface):
        if self.boards is not None:
            for board in self.boards.values():
                board.render(surf)
        if self.instruction is not None:
            self.instruction.render(surf)
    
    def update_board_content(self, key: str, value: any):
        self.boards[key].update_content(value)

    def reset_board_content(self, key: str):
        self.boards[key].reset()