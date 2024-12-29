import pygame

class Map:
    def __init__(self, side_length, grid_num, grid_color=(255, 255, 255), outline_thickness=3, inline_thickness=1):
        self.length = side_length
        self.grid_num = grid_num
        self.inline_thickness = inline_thickness

        self.surf = pygame.Surface((side_length, side_length))
        
        self.rect = self.surf.get_rect()
        pygame.draw.rect(self.surf, grid_color, self.rect, outline_thickness)
    
    def draw_by_center(self, surf, center_pos=(0, 0)):
        self.rect.center = center_pos
        surf.blit(self.surf, self.rect.topleft)
