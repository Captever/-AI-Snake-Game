import pygame
import math

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

class Map:
    def __init__(self, game, side_length, grid_num, grid_color=(255, 255, 255, 128), outline_thickness=3, inline_thickness=1):
        self.game = game
        self.length = side_length
        self.grid_num = grid_num
        self.grid_color = grid_color
        self.outline_thickness = outline_thickness
        self.inline_thickness = inline_thickness

        self.cell_side_length = side_length // grid_num

    def render(self, surf, pos=(0, 0)):
        self.surf = pygame.Surface((self.length, self.length))

        head = self.game.bodies[0]
        dir_offset = DIR_OFFSET_DICT[self.game.direction]
        dir_render_pos = (head[0] + dir_offset[0], head[1] + dir_offset[1])
        for y in range(self.grid_num):
            for x in range(self.grid_num):
                curr_type = []
                if (x, y) in self.game.bodies:
                    curr_type = 'body'
                if (x, y) in self.game.feeds:
                    curr_type = 'feed'
                curr_cell = Cell(self.game, self.cell_side_length, curr_type, self.inline_thickness)

                if (x, y) == dir_render_pos:
                    curr_cell.render_dir(self.game.direction)
                offset = (x * self.cell_side_length, y * self.cell_side_length)
                curr_cell.render(self.surf, offset)
                
        # draw outline
        pygame.draw.rect(self.surf, self.grid_color[:3], self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, pos)

class Cell:
    def __init__(self, game, side_length, cell_type=[], outline_thickness=1, outline_color=(255, 255, 255, 128)):
        self.game = game
        self.length = side_length
        self.type = cell_type
        self.outline_thickness = outline_thickness
        self.outline_color = outline_color

        self.layer_dir = None

    def render(self, surf, pos=(0, 0)):
        self.surf = pygame.Surface((self.length, self.length), pygame.SRCALPHA)

        feature_outline_thickness = 7
        if self.type == 'body':
            pygame.draw.rect(self.surf, BODY_OUTLINE_COLOR, self.surf.get_rect())
            pygame.draw.rect(self.surf, BODY_COLOR, pygame.Rect(feature_outline_thickness, feature_outline_thickness, self.length - feature_outline_thickness * 2, self.length - feature_outline_thickness * 2))
        elif self.type == 'feed':
            pygame.draw.rect(self.surf, FEED_OUTLINE_COLOR, self.surf.get_rect())
            pygame.draw.rect(self.surf, FEED_COLOR, pygame.Rect(feature_outline_thickness, feature_outline_thickness, self.length - feature_outline_thickness * 2, self.length - feature_outline_thickness * 2))

        # draw outline
        if self.layer_dir is not None:
            self.surf.blit(self.layer_dir, (0, 0))
        pygame.draw.rect(self.surf, self.outline_color, self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, pos)
    
    # dir: type(str)
    def render_dir(self, dir):
        self.layer_dir = pygame.Surface((self.length, self.length), pygame.SRCALPHA)
        self.layer_dir.fill((0, 0, 0, 0))

        self.center_pos = self.layer_dir.get_rect().center

        curr_dir_offset = DIR_OFFSET[DIR_FILTER_DICT[dir]]
        dir_arrow_coord = [self.center_pos]
        for (offset_x, offset_y) in curr_dir_offset:
            dir_arrow_coord.append((self.center_pos[0] + offset_x, self.center_pos[1] + offset_y))
        pygame.draw.polygon(self.layer_dir, DIR_COLOR, dir_arrow_coord)