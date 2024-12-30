import pygame

# define type
NONE = 0
BODY = 1
FEED = 2

class Cell:
    def __init__(self, game, side_length, cell_type='none', outline_thickness=1, outline_color=(255, 255, 255, 128)):
        self.game = game
        self.length = side_length
        self.type = cell_type
        self.outline_thickness = outline_thickness
        self.outline_color = outline_color

    def render(self, surf, pos=(0, 0)):
        self.surf = pygame.Surface((self.length, self.length), pygame.SRCALPHA)

        if self.type == 'body':
            pygame.draw.rect(self.surf, (30, 255, 30), self.surf.get_rect())
        elif self.type == 'feed':
            pygame.draw.rect(self.surf, (255, 255, 30), self.surf.get_rect())

        # draw outline
        pygame.draw.rect(self.surf, self.outline_color, self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, pos)