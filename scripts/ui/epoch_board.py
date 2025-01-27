import pygame

from typing import Tuple

class EpochBoard:
    def __init__(self, size: Tuple[int, int], font_weight: int, font_color, offset=(0, 0)):
        self.size = size
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.font_weight = font_weight
        self.font_color = font_color
        self.offset = offset

        self.epoch: int = 0

        self.init_font_surfs()

    def init_font_surfs(self):
        self.title_font = pygame.font.SysFont('consolas', round(self.font_weight * 1.25), bold=True)
        self.content_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.9))
        
        self.centered_origin = (self.size[0] * 0.5, self.size[1] * 0.5)

        self.title_surf = self.title_font.render("Epoch", True, self.font_color)
        self.title_rect = self.title_surf.get_rect(center = self.centered_origin)
        self.title_font_offset = self.title_rect.topleft
        self.update_epoch_font()
    
    def reset(self):
        self.epoch = 0
        self.update_epoch_font()
    
    def update_epoch(self, epoch: int):
        self.epoch = epoch
        self.update_epoch_font()
    
    def update_epoch_font(self):
        self.epoch_surf = self.content_font.render(str(self.epoch), True, self.font_color)
        self.epoch_rect = self.epoch_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1] + self.title_rect.height * 1.1)
        self.epoch_font_offset = self.epoch_rect.topleft

    def render(self, surf):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.title_surf, self.title_font_offset)
        self.surf.blit(self.epoch_surf, self.epoch_font_offset)

        surf.blit(self.surf, self.offset)