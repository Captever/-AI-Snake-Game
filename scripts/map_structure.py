import pygame

from constants import *

from typing import Tuple, List

class Outerline:
    def __init__(self, size: Tuple[int, int], thickness: int = 1, color=(255, 255, 255)):
        self.thickness = thickness

        outer_rect = pygame.Rect(0, 0, size[0] + thickness * 2, size[1] + thickness * 2)

        self.surf = pygame.Surface((outer_rect.width, outer_rect.height), pygame.SRCALPHA)
        self.surf.fill((0, 0, 0, 0))

        pygame.draw.rect(self.surf, color, outer_rect, max(1, thickness)) # minimum value of width: 1

    def render(self, surf, pos=(0, 0)):
        adjusted_pos = (pos[0] - self.thickness, pos[1] - self.thickness)

        surf.blit(self.surf, adjusted_pos)

class Map:
    def __init__(self, game, size: Tuple[int, int], grid_num: Tuple[int, int], grid_thickness: int = 1, grid_color=(255, 255, 255, 128)):
        self.game = game
        self.size = size
        self.grid_num = grid_num
        self.grid_color = grid_color
        self.grid_thickness = grid_thickness

        self.outerline = None

        self.cell_size = (size[0] // grid_num[0], size[1] // grid_num[1])
    
    def add_outerline(self, outline_thickness: int = 3, outline_color=(255, 255, 255)):
        self.outerline = Outerline(self.size, outline_thickness, outline_color)

    def render(self, surf, pos=(0, 0)):
        self.surf = pygame.Surface(self.size)

        head = self.game.player.bodies[0]
        dir_offset = DIR_OFFSET_DICT[self.game.player.direction]
        dir_render_pos = (head[0] + dir_offset[0], head[1] + dir_offset[1])

        for y in range(self.grid_num[0]):
            for x in range(self.grid_num[1]):
                curr_pos = (x, y)
                curr_object = self.game.check_collision(curr_pos)
                curr_cell = Cell(self.game, self.cell_size, OBJECT_DICT[curr_object[0]], self.grid_thickness, self.grid_color)

                if curr_pos == dir_render_pos:
                    curr_cell.render_dir(self.game.player.direction)
                offset = (x * self.cell_size[0], y * self.cell_size[1])
                curr_cell.render(self.surf, offset)

        surf.blit(self.surf, pos)
        if self.outerline is not None:
            self.outerline.render(surf, pos)
    
    def is_inside(self, pos) -> bool:
        is_in_x = 0 <= pos[0] < self.grid_num[0]
        is_in_y = 0 <= pos[1] < self.grid_num[1]
        return is_in_x and is_in_y

class Cell:
    def __init__(self, game, size: Tuple[int, int], cell_type: int = OBJECT_DICT['none'], outline_thickness: int = 1, outline_color=(255, 255, 255, 128)):
        self.game = game
        self.size = size
        self.type = cell_type
        self.outline_thickness = outline_thickness
        self.outline_color = outline_color

        self.layer_dir = None

    def render(self, surf, pos=(0, 0)):
        self.surf = pygame.Surface(self.size, pygame.SRCALPHA)

        feature_outline_thickness = 7
        if self.type == OBJECT_DICT['body']:
            pygame.draw.rect(self.surf, BODY_OUTLINE_COLOR, self.surf.get_rect())
            pygame.draw.rect(self.surf, BODY_COLOR, pygame.Rect(feature_outline_thickness, feature_outline_thickness, self.size[0] - feature_outline_thickness * 2, self.size[1] - feature_outline_thickness * 2))
        elif self.type == OBJECT_DICT['feed']:
            pygame.draw.rect(self.surf, FEED_OUTLINE_COLOR, self.surf.get_rect())
            pygame.draw.rect(self.surf, FEED_COLOR, pygame.Rect(feature_outline_thickness, feature_outline_thickness, self.size[0] - feature_outline_thickness * 2, self.size[1] - feature_outline_thickness * 2))

        # draw outline
        if self.layer_dir is not None:
            self.surf.blit(self.layer_dir, (0, 0))
        pygame.draw.rect(self.surf, self.outline_color, self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, pos)
    
    def render_dir(self, dir: str):
        self.layer_dir = pygame.Surface(self.size, pygame.SRCALPHA)
        self.layer_dir.fill((0, 0, 0, 0))

        self.center_pos = self.layer_dir.get_rect().center

        dir_arrow_vertexes = DIR_ARROW_VERTEX_DICT[dir]
        dir_arrow_coord = [self.center_pos]
        for (offset_x, offset_y) in dir_arrow_vertexes:
            dir_arrow_coord.append((self.center_pos[0] + offset_x, self.center_pos[1] + offset_y))
        pygame.draw.polygon(self.layer_dir, DIR_COLOR, dir_arrow_coord)