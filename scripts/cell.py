import pygame

class Cell:
    def __init__(self, side_length, outline_thickness, outline_color=(255, 255, 255, 128)):
        self.length = side_length

        self.surf = pygame.Surface((side_length, side_length), pygame.SRCALPHA)

        pygame.draw.rect(self.surf, outline_color, self.surf.get_rect(), outline_thickness)

    def render(self, surf, pos=(0, 0)):
        surf.blit(self.surf, pos)