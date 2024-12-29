import pygame

from scripts.cell import Cell

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

        for y in range(self.grid_num):
            for x in range(self.grid_num):
                curr_cell = Cell(self.game, self.cell_side_length, self.inline_thickness)
                offset = (x * self.cell_side_length, y * self.cell_side_length)
                curr_cell.render(self.surf, offset)
                
        # draw outline
        pygame.draw.rect(self.surf, self.grid_color[:3], self.surf.get_rect(), self.outline_thickness)

        surf.blit(self.surf, pos)