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