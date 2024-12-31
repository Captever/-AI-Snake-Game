import pygame

from scripts.cell import Cell

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