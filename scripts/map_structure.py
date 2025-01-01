import pygame
import math

from typing import Tuple, List

# define type
NONE = 0
BODY = 1
FEED = 2

# define color
BODY_OUTLINE_COLOR = (59, 92, 70)
BODY_COLOR = (7, 255, 82)
FEED_OUTLINE_COLOR = (187, 113, 40)
FEED_COLOR = (255, 255, 15)
DIR_COLOR = (255, 255, 255)

# define direction
DIR_ARROW_HEIGHT = 10
DIR_FILTER_DICT = {
    'E': 0,
    'W': 1,
    'S': 2,
    'N': 3,
}
# E / W / S / N
DIR_OFFSET = (
    ((-DIR_ARROW_HEIGHT, DIR_ARROW_HEIGHT / math.sqrt(3)), (-DIR_ARROW_HEIGHT, -DIR_ARROW_HEIGHT / math.sqrt(3))),
    ((DIR_ARROW_HEIGHT, DIR_ARROW_HEIGHT / math.sqrt(3)), (DIR_ARROW_HEIGHT, -DIR_ARROW_HEIGHT / math.sqrt(3))),
    ((DIR_ARROW_HEIGHT / math.sqrt(3), -DIR_ARROW_HEIGHT), (-DIR_ARROW_HEIGHT / math.sqrt(3), -DIR_ARROW_HEIGHT)),
    ((DIR_ARROW_HEIGHT / math.sqrt(3), DIR_ARROW_HEIGHT), (-DIR_ARROW_HEIGHT / math.sqrt(3), DIR_ARROW_HEIGHT)),
)

DIR_OFFSET_DICT = {
    'E': (1, 0),
    'W': (-1, 0),
    'S': (0, 1),
    'N': (0, -1),
}

class Outerline:
    def __init__(self, size: Tuple[int, int], thickness: int = 1, color=(255, 255, 255)):
        self.thickness = thickness

        outer_rect = pygame.Rect(0, 0, size[0], size[1]).inflate(thickness * 2, thickness * 2)

        self.surf = pygame.Surface((outer_rect.width, outer_rect.height))
        pygame.draw.rect(self.surf, color, outer_rect, max(1, thickness)) # minimum value of width: 1

    def render(self, surf, pos=(0, 0)):
        adjusted_pos = (pos[0] - self.thickness, pos[1] - self.thickness)

        surf.blit(self.surf, adjusted_pos)

class Map:
    def __init__(self, game, size: Tuple[int, int], grid_num: Tuple[int, int], grid_color=(255, 255, 255, 128), grid_thickness: int = 1):
        self.game = game
        self.size = size
        self.grid_num = grid_num
        self.grid_color = grid_color
        self.grid_thickness = grid_thickness

        self.cell_size = (size[0] // grid_num[0], size[1] // grid_num[1])

    def render(self, surf, pos=(0, 0)):
        self.surf = pygame.Surface(self.size)

        head = self.game.player.bodies[0]
        dir_offset = DIR_OFFSET_DICT[self.game.direction]
        dir_render_pos = (head[0] + dir_offset[0], head[1] + dir_offset[1])
        for y in range(self.grid_num[0]):
            for x in range(self.grid_num[1]):
                curr_type = []
                curr_pos = (x, y)
                if curr_pos in self.game.player.bodies:
                    curr_type = 'body'
                for feed in self.game.feeds:
                    if curr_pos == feed.pos:
                        curr_type = 'feed'
                        break
                curr_cell = Cell(self.game, self.cell_size, curr_type, self.grid_thickness)

                if curr_pos == dir_render_pos:
                    curr_cell.render_dir(self.game.direction)
                offset = (x * self.cell_size[0], y * self.cell_size[1])
                curr_cell.render(self.surf, offset)

        surf.blit(self.surf, pos)

class Cell:
    def __init__(self, game, size: Tuple[int, int], cell_type: List[str] = [], outline_thickness: int = 1, outline_color=(255, 255, 255, 128)):
        self.game = game
        self.size = size
        self.type = cell_type
        self.outline_thickness = outline_thickness
        self.outline_color = outline_color

        self.layer_dir = None

    def render(self, surf, pos=(0, 0)):
        self.surf = pygame.Surface(self.size, pygame.SRCALPHA)

        feature_outline_thickness = 7
        if self.type == 'body':
            pygame.draw.rect(self.surf, BODY_OUTLINE_COLOR, self.surf.get_rect())
            pygame.draw.rect(self.surf, BODY_COLOR, pygame.Rect(feature_outline_thickness, feature_outline_thickness, self.size[0] - feature_outline_thickness * 2, self.size[1] - feature_outline_thickness * 2))
        elif self.type == 'feed':
            pygame.draw.rect(self.surf, FEED_OUTLINE_COLOR, self.surf.get_rect())
            pygame.draw.rect(self.surf, FEED_COLOR, pygame.Rect(feature_outline_thickness, feature_outline_thickness, self.size[0] - feature_outline_thickness * 2, self.size[1] - feature_outline_thickness * 2))

        # draw outline
        if self.layer_dir is not None:
            self.surf.blit(self.layer_dir, (0, 0))
        pygame.draw.rect(self.surf, self.outline_color, self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, pos)
    
    # dir: type(str)
    def render_dir(self, dir):
        self.layer_dir = pygame.Surface(self.size, pygame.SRCALPHA)
        self.layer_dir.fill((0, 0, 0, 0))

        self.center_pos = self.layer_dir.get_rect().center

        curr_dir_offset = DIR_OFFSET[DIR_FILTER_DICT[dir]]
        dir_arrow_coord = [self.center_pos]
        for (offset_x, offset_y) in curr_dir_offset:
            dir_arrow_coord.append((self.center_pos[0] + offset_x, self.center_pos[1] + offset_y))
        pygame.draw.polygon(self.layer_dir, DIR_COLOR, dir_arrow_coord)