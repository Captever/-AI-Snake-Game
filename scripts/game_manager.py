import pygame

from typing import Tuple

class ScoreManager:
    def __init__(self, game, size: Tuple[int, int], font_weight: int, font_color):
        self.game = game
        self.size = size
        self.surf = pygame.Surface(size, pygame.SRCALPHA)
        self.font_weight = font_weight
        self.font_color = font_color

        self.title_font = pygame.font.SysFont('consolas', round(font_weight * 1.25))
        pygame.font.Font.set_bold(self.title_font, True)
        self.score_font = pygame.font.SysFont('consolas', round(font_weight * 0.9))

        self.score: int = 0
        self.clear_condition: int = None
    
    def set_clear_condition(self, score: int):
        self.clear_condition = score
    
    def update_score(self, amount: int):
        self.score += amount
        if self.clear_condition is not None and self.score >= self.clear_condition:
            self.game.clear()

    def render(self, surf, offset: Tuple[int, int] = (0, 0)):
        self.surf.fill((0, 0, 0, 0))
        title_surf = self.title_font.render("Score", True, self.font_color)
        score_surf = self.score_font.render(str(self.score), True, self.font_color)
        centered_origin = (self.size[0] * 0.5, self.size[1] * 0.1)
        title_rect = title_surf.get_rect(centerx = centered_origin[0], y = centered_origin[1])
        score_rect = score_surf.get_rect(centerx = centered_origin[0], y = centered_origin[1] + title_rect.height * 1.1)
        title_offset = title_rect.topleft
        score_offset = score_rect.topleft
        self.surf.blit(title_surf, title_offset)
        self.surf.blit(score_surf, score_offset)

        surf.blit(self.surf, offset)