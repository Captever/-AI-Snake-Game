import pygame

from constants import *

from typing import Tuple, List

LAYOUT_DEFAULT_BG_COLOR = (50, 50, 50, 150)
BUTTON_DEFAULT_COLOR = WHITE
BUTTON_DEFAULT_HOVER_COLOR = LIGHT_GRAY

class RelativeRect:
    def __init__(self, x: float, y: float, width: float, height: float):
        """
        Represents a rectangle using relative values (fractions of a parent surface).
        
        Args:
            x (float): Relative x-coordinate (0.0 to 1.0).
            y (float): Relative y-coordinate (0.0 to 1.0).
            width (float): Relative width (0.0 to 1.0).
            height (float): Relative height (0.0 to 1.0).
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def to_absolute(self, parent_size: Tuple[int, int]) -> pygame.Rect:
        """
        Converts the relative rectangle to an absolute Pygame Rect.
        
        Args:
            parent_size (Tuple[int, int]): Size of the parent surface.

        Returns:
            pygame.Rect: Absolute rectangle.
        """
        abs_x = int(self.x * parent_size[0])
        abs_y = int(self.y * parent_size[1])
        abs_width = int(self.width * parent_size[0])
        abs_height = int(self.height * parent_size[1])
        return pygame.Rect(abs_x, abs_y, abs_width, abs_height)

class UILayout:
    def __init__(self, rect: pygame.Rect, bg_color=LAYOUT_DEFAULT_BG_COLOR):
        """
        A layout for managing UI elements relative to the surface size.
        
        Args:
            rect (pygame.Rect): Position and size
            bg_color (Tuple[int, int, int]): Background color of the surface.
        """
        self.rect = rect
        self.bg_color = bg_color
        self.elements = []

    def add_layout(self, relative_rect: RelativeRect, bg_color=LAYOUT_DEFAULT_BG_COLOR):
        """
        Add a layout to the layout with its relative position.
        
        Args:
            relative_rect (pygame.Rect): Relative position and size as a fraction of the layout size.
            bg_color (Tuple[int, int, int]): Background color of the layout surface.
        """
        layout = UILayout(relative_rect.to_absolute(self.rect.size), bg_color)

        self.elements.append(layout)

    def add_button(self, relative_rect: RelativeRect, text: str, color=BUTTON_DEFAULT_COLOR, hover_color=BUTTON_DEFAULT_HOVER_COLOR):
        """
        Add a button to the layout with its relative position.
        """
        button = Button(relative_rect.to_absolute(self.rect.size), text, color, hover_color)

        self.elements.append(button)

    def add_scrollbar(self, relative_rect: RelativeRect, text: str, min_val: int, max_val: int, initial_val: int):
        """
        Add a scroll bar to the layout with its relative position.
        """
        scrollbar = ScrollBar(relative_rect.to_absolute(self.rect.size), text, min_val, max_val, initial_val)

        self.elements.append(scrollbar)

    def render(self, surf: pygame.Surface):
        """
        Render all elements on the layout's surface.
        
        Args:
            surf (pygame.Surface): Surface to render on.
        """
        layout_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        layout_surf.fill(self.bg_color)
        
        for element in self.elements:
            element.render(layout_surf)
        
        layout_rect = layout_surf.get_rect(center=self.rect.center)
        surf.blit(layout_surf, layout_rect)

    def get_surface(self):
        return self.surf

class Button:
    def __init__(self, rect: pygame.Rect, text: str, color=BUTTON_DEFAULT_COLOR, hover_color=BUTTON_DEFAULT_HOVER_COLOR):
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.text: str = text
        self.color = color
        self.hover_color = hover_color
        self.hovered: bool = False

    def render(self, surf: pygame.Surface):
        """
        Render the button on the given surface at the specified rect.
        
        Args:
            surf (pygame.Surface): Surface to render on.
        """
        pygame.draw.rect(surf, self.hover_color if self.hovered else self.color, self.rect)
        font = pygame.font.SysFont("arial", round(self.rect.height * UI_BUTTON["font_ratio"]))
        text_surf = font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surf.blit(text_surf, text_rect)

    def is_hovered(self, pos: Tuple[int, int]):
        """
        Check if the button is hovered based on the mouse position.
        
        Args:
            pos (Tuple[int, int]): Mouse position.
        """
        self.hovered = self.rect.collidepoint(pos)
        return self.hovered

    def is_clicked(self, event):
        return self.hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

class ScrollBar:
    def __init__(self, rect: pygame.Rect, text: str, min_val: int, max_val: int, initial_val: int):
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.text: str = text
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.value: int = initial_val
        self.handle_rect = pygame.Rect(0, 0, self.rect.width * 0.05, self.rect.height)
        self.update_handle()

    def update_handle(self):
        handle_x = int(self.rect.x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.rect.width)
        self.handle_rect.topleft = (handle_x - self.handle_rect.width // 2, self.rect.y)

    def render(self, surf: pygame.Surface):
        font = pygame.font.SysFont("arial", round(self.rect.height * UI_SCROLLBAR["font_ratio"]))
        text_surf = font.render(f"{self.text}: {int(self.value)}", True, WHITE)
        surf.blit(text_surf, (self.rect.topleft[0], self.rect.topleft[1] - self.rect.height * 5))
        pygame.draw.rect(surf, GRAY, self.rect)
        pygame.draw.rect(surf, WHITE, self.handle_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.handle_rect.collidepoint(event.pos):
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and getattr(self, "dragging", False):
            rel_x = event.pos[0] - self.rect.x
            self.value = max(self.min_val, min(self.max_val, self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)))
            self.update_handle()