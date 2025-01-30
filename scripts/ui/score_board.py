import pygame

from typing import Tuple

class ScoreBoard:
    def __init__(self, size: Tuple[int, int], text, font_weight: int, font_color, offset=(0, 0)):
        self.size = size
        self.text = text
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.font_weight = font_weight
        self.font_color = font_color
        self.offset = offset

        self.score: int = 0

        self.init_font_surfs()

    def init_font_surfs(self):
        self.title_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.8), bold=True)
        self.content_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.6))
        
        self.centered_origin = (self.size[0] * 0.5, self.size[1] * 0.5)

        self.title_surf = self.title_font.render(self.text, True, self.font_color)
        self.title_rect = self.title_surf.get_rect(center = self.centered_origin)
        self.title_font_offset = self.title_rect.topleft
        self.update_score_font()
    
    def reset(self):
        self.score = 0
        self.update_score_font()
    
    def update_score(self, score: int):
        self.score = score
        self.update_score_font()
    
    def update_score_font(self):
        self.score_surf = self.content_font.render(str(self.score), True, self.font_color)
        self.score_rect = self.score_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1] + self.title_rect.height * 1.1)
        self.score_font_offset = self.score_rect.topleft

    def render(self, surf):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.title_surf, self.title_font_offset)
        self.surf.blit(self.score_surf, self.score_font_offset)

        surf.blit(self.surf, self.offset)
    
class TopScoreBoard:
    def __init__(self, size: Tuple[int, int], text, font_weight: int, font_color, offset=(0, 0)):
        self.size = size
        self.text = text
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.font_weight = font_weight
        self.font_color = font_color
        self.offset = offset

        self.top_score: int = 0

        self.init_font_surfs()

    def init_font_surfs(self):
        self.title_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.8), bold=True)
        self.content_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.6))
        
        self.centered_origin = (self.size[0] * 0.5, self.size[1] * 0.5)

        self.title_surf = self.title_font.render(self.text, True, self.font_color)
        self.title_rect = self.title_surf.get_rect(center = self.centered_origin)
        self.title_font_offset = self.title_rect.topleft
        self.update_score_font()
    
    def reset(self):
        self.top_score = 0
        self.update_score_font()
    
    def update_score(self, score: int):
        if score > self.top_score:
            self.top_score = score
            self.update_score_font()
    
    def update_score_font(self):
        self.score_surf = self.content_font.render(str(self.top_score), True, self.font_color)
        self.score_rect = self.score_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1] + self.title_rect.height * 1.1)
        self.score_font_offset = self.score_rect.topleft

    def render(self, surf):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.title_surf, self.title_font_offset)
        self.surf.blit(self.score_surf, self.score_font_offset)

        surf.blit(self.surf, self.offset)

class AvgScoreBoard:
    def __init__(self, size: Tuple[int, int], text, font_weight: int, font_color, offset=(0, 0)):
        self.size = size
        self.text = text
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.font_weight = font_weight
        self.font_color = font_color
        self.offset = offset

        self.avg_score: float = 0.0

        self.init_font_surfs()

    def init_font_surfs(self):
        self.title_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.8), bold=True)
        self.content_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.6))

        self.title_surf = self.title_font.render(self.text, True, self.font_color)
        self.centered_origin = (self.size[0] * 0.5, self.size[1] * 0.5)
        self.title_rect = self.title_surf.get_rect(center = self.centered_origin)
        self.title_font_offset = self.title_rect.topleft
        self.update_avg_score_font()
    
    def reset(self):
        self.avg_score = 0
        self.update_avg_score_font()
    
    def update_avg_score(self, avg_score: float):
        self.avg_score = avg_score
        self.update_avg_score_font()
    
    def update_avg_score_font(self):
        self.avg_score_surf = self.content_font.render(str(self.avg_score), True, self.font_color)
        self.avg_score_rect = self.avg_score_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1] + self.title_rect.height * 1.1)
        self.avg_score_font_offset = self.avg_score_rect.topleft

    def render(self, surf):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.title_surf, self.title_font_offset)
        self.surf.blit(self.avg_score_surf, self.avg_score_font_offset)

        surf.blit(self.surf, self.offset)