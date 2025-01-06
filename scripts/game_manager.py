import pygame

from typing import Tuple

class ScoreManager:
    def __init__(self, game, size: Tuple[int, int], font_weight: int, font_color):
        self.game = game
        self.size = size
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.font_weight = font_weight
        self.font_color = font_color

        self.score: int = 0
        self.clear_condition: int = None

        self.init_font_surfs()

    def init_font_surfs(self):
        self.title_font = pygame.font.SysFont('consolas', round(self.font_weight * 1.25), bold=True)
        self.score_font = pygame.font.SysFont('consolas', round(self.font_weight * 0.9))
        
        self.centered_origin = (self.size[0] * 0.5, self.size[1] * 0.1)

        self.title_surf = self.title_font.render("Score", True, self.font_color)
        self.title_rect = self.title_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1])
        self.title_font_offset = self.title_rect.topleft
        self.update_score_font()
    
    def set_clear_condition(self, score: int):
        self.clear_condition = score
    
    def update_score(self, amount: int):
        self.score += amount
        self.update_score_font()
        if self.clear_condition is not None and self.score >= self.clear_condition:
            self.game.clear()
    
    def update_score_font(self):
        self.score_surf = self.score_font.render(str(self.score), True, self.font_color)
        self.score_rect = self.score_surf.get_rect(centerx = self.centered_origin[0], y = self.centered_origin[1] + self.title_rect.height * 1.1)
        self.score_font_offset = self.score_rect.topleft

    def render(self, surf, offset: Tuple[int, int] = (0, 0)):
        self.surf.fill((0, 0, 0, 0))
        self.surf.blit(self.title_surf, self.title_font_offset)
        self.surf.blit(self.score_surf, self.score_font_offset)

        surf.blit(self.surf, offset)