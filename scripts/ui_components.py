import pygame

from constants import *

from typing import Tuple

# UI Elements
class Button:
    def __init__(self, text: str, rect: pygame.Rect, font_size: int, color=WHITE, hover_color=LIGHT_GRAY):
        self.text: str = text
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.font = pygame.font.SysFont("arial", font_size)
        self.color = color
        self.hover_color = hover_color
        self.hovered: bool = False

    def render(self, surface):
        pygame.draw.rect(surface, self.hover_color if self.hovered else self.color, self.rect)
        text_surf = self.font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_hovered(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def is_clicked(self, event):
        return self.hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

class ScrollBar:
    def __init__(self, rect: pygame.Rect, min_val: int, max_val: int, initial_val: int):
        self.rect = pygame.Rect(rect)
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.value: int = initial_val
        self.handle_rect = pygame.Rect(0, 0, 20, self.rect.height)
        self.update_handle()

    def update_handle(self):
        handle_x = int(self.rect.x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.width)
        self.handle_rect.topleft = (handle_x - self.handle_rect.width // 2, self.rect.y)

    def render(self, surface):
        pygame.draw.rect(surface, GRAY, self.rect)
        pygame.draw.rect(surface, WHITE, self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.handle_rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and getattr(self, "dragging", False):
            rel_x = event.pos[0] - self.rect.x
            self.value = max(self.min_val, min(self.max_val, self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)))
            self.update_handle()