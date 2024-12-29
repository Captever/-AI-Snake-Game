import pygame

from scripts.cell import Cell

class Map:
    def __init__(self, side_length, grid_num, grid_color=(255, 255, 255, 128), outline_thickness=3, inline_thickness=1):
        self.surf = pygame.Surface((side_length, side_length))
        
        self.rect = self.surf.get_rect()

        # initialize cells
        slot_side_length = side_length // grid_num
        print("slot side length = ", slot_side_length)
        coord_range = range(0, side_length, slot_side_length)
        for y in coord_range:
            for x in coord_range:
                curr_slot = Cell(slot_side_length, inline_thickness)
                pos = (x, y)
                curr_slot.render(self.surf, pos)

        # draw outline
        pygame.draw.rect(self.surf, grid_color[:3], self.rect, outline_thickness)

    
    def render_by_center(self, surf, center_pos=(0, 0)):
        self.rect.center = center_pos
        surf.blit(self.surf, self.rect.topleft)
