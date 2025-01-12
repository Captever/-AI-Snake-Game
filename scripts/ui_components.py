import pygame

from constants import *

from typing import Tuple, Dict

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
    def __init__(self, parent_abs_pos: Tuple[int, int], rect: pygame.Rect, bg_color=UI_LAYOUT["default_color"]):
        """
        A layout for managing UI elements relative to the surface size.
        
        Args:
            parent_abs_pos (Tuple[int, int]): Absolute position of the parent element
            rect (pygame.Rect): Position and size
            bg_color (Tuple[int, int, int]): Background color of the surface.
        """
        self.rect: pygame.Rect = rect
        self.abs_pos: Tuple[int, int] = tuple(parent_abs_pos[i] + rect.topleft[i] for i in [0, 1])
        self.bg_color = bg_color
        self.elements = []
        self.layouts: Dict[str, UILayout] = {} # sub layout

    def add_layout(self, name: str, relative_rect: RelativeRect, bg_color=UI_LAYOUT["default_color"]):
        """
        Add a layout to the layout with its relative position.
        
        Args:
            relative_rect (pygame.Rect): Relative position and size as a fraction of the layout size.
            bg_color (Tuple[int, int, int]): Background color of the layout surface.
        """
        if name in self.layouts:
            ValueError(f"Layout name[{name}] already exists")
            return

        layout = UILayout(self.abs_pos, relative_rect.to_absolute(self.rect.size), bg_color)
        
        self.layouts[name] = layout

    def add_button(self, relative_rect: RelativeRect, text: str, callback=None):
        """
        Add a button to the layout with its relative position.
        """
        button = Button(self.abs_pos, relative_rect.to_absolute(self.rect.size), text, callback)

        self.elements.append(button)

    def add_scrollbar(self, relative_rect: RelativeRect, text: str, min_val: int, max_val: int, initial_val: int):
        """
        Add a scroll bar to the layout with its relative position.
        """
        scrollbar = ScrollBar(self.abs_pos, relative_rect.to_absolute(self.rect.size), text, min_val, max_val, initial_val)

        self.elements.append(scrollbar)

    def get_surface(self):
        return self.surf

    def get_scrollbar_values(self) -> Dict[str, any]:
        scrollbar_values = {}
        for element in self.elements:
            if isinstance(element, ScrollBar):
                scrollbar_values[element.text] = element.value
        
        for layout in self.layouts.values():
            scrollbar_values.update(layout.get_scrollbar_values())

        return scrollbar_values
    
    def handle_events(self, events):
        for event in events:
            for element in self.elements:
                element.handle_event(event)
            
        for layout in self.layouts.values():
            layout.handle_events(events)

    def render(self, surf: pygame.Surface):
        """
        Render all elements on the layout's surface.
        
        Args:
            surf (pygame.Surface): Surface to render on.
        """
        layout_surf = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        layout_surf.fill(self.bg_color)
        
        for layout in self.layouts.values():
            layout.render(layout_surf)

        for element in self.elements:
            if isinstance(element, Button) or isinstance(element, ScrollBar):
                element.is_hovered(pygame.mouse.get_pos())
            element.render(layout_surf)
        
        surf.blit(layout_surf, self.rect.topleft)

class Button:
    def __init__(self, parent_abs_pos: Tuple[int, int], rect: pygame.Rect, text: str, callback=None):
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.abs_pos: Tuple[int, int] = tuple(parent_abs_pos[i] + rect.topleft[i] for i in [0, 1])
        self.text: str = text
        self.callback = callback
        self.hovered: bool = False
        self.disable: bool = False
    
    def handle_event(self, event):
        if self.is_clicked(event):
            if self.callback:
                self.callback()
    
    def get_abs_rect(self) -> pygame.Rect:
        return pygame.Rect(self.abs_pos + self.rect.size)

    def is_hovered(self, m_pos: Tuple[int, int]):
        """
        Check if the button is hovered based on the mouse position.
        
        Args:
            pos (Tuple[int, int]): Mouse position.
        """
        self.hovered = self.get_abs_rect().collidepoint(m_pos)
        return self.hovered

    def is_clicked(self, event):
        return self.hovered and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1

    def render(self, surf: pygame.Surface):
        """
        Render the button on the given surface at the specified rect.
        
        Args:
            surf (pygame.Surface): Surface to render on.
        """
        lined_text = self.text.split('\n')
        line_num = len(lined_text)

        pygame.draw.rect(surf, UI_BUTTON["hover_color"] if self.hovered else (UI_BUTTON["disable_color"] if self.disable else UI_BUTTON["default_color"]), self.rect)
        font_size = round(self.rect.height * UI_BUTTON["font_ratio"] / line_num)
        font = pygame.font.SysFont("arial", font_size)

        if line_num == 1:
            text_surf = font.render(self.text, True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            surf.blit(text_surf, text_rect)
        else:
            for idx, line in enumerate(lined_text):
                text_surf = font.render(line, True, BLACK)
                text_rect = text_surf.get_rect(centerx=self.rect.centerx, y=(self.rect.size[1] - (line_num * font_size)) // 2 + idx * font_size)
                surf.blit(text_surf, text_rect)

class ScrollBar:
    def __init__(self, parent_abs_pos: Tuple[int, int], rect: pygame.Rect, text: str, min_val: int, max_val: int, initial_val: int):
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.abs_pos: Tuple[int, int] = tuple(parent_abs_pos[i] + rect.topleft[i] for i in [0, 1])
        self.text: str = text
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.value: int = initial_val
        self.bar_rect = pygame.Rect(self.rect.x, self.rect.y + self.rect.height * (1.0 - UI_SCROLLBAR["bar_ratio"]), self.rect.width, self.rect.height * UI_SCROLLBAR["bar_ratio"])
        self.handle_rect = pygame.Rect((self.bar_rect.topleft) + (self.bar_rect.width * 0.05, self.bar_rect.height))
        self.update_handle()

    def update_handle(self):
        handle_x = int(self.bar_rect.x + ((self.value - self.min_val) / (self.max_val - self.min_val)) * self.bar_rect.width)
        self.handle_rect.topleft = (handle_x - self.handle_rect.width // 2, self.bar_rect.y)
    
    def get_abs_bar_rect(self) -> pygame.Rect:
        return pygame.Rect(
            tuple(self.abs_pos[i] + self.bar_rect.topleft[i] - self.rect.topleft[i] for i in [0, 1])
              + self.bar_rect.size)

    def is_hovered(self, m_pos: Tuple[int, int]):
        """
        Check if the scrollbar is hovered based on the mouse position.
        
        Args:
            pos (Tuple[int, int]): Mouse position.
        """
        self.hovered = self.get_abs_bar_rect().collidepoint(m_pos)
        return self.hovered

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.hovered:
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and getattr(self, "dragging", False):
            rel_x = event.pos[0] - self.abs_pos[0]
            self.value = max(self.min_val, min(self.max_val, round(self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val))))
            self.update_handle()

    def render(self, surf: pygame.Surface):
        font = pygame.font.SysFont("arial", round(self.rect.height * UI_SCROLLBAR["font_ratio"]))
        text_surf = font.render(f"{self.text}: {int(self.value)}", True, WHITE)
        surf.blit(text_surf, self.rect.topleft)
        if self.hovered:
            pygame.draw.rect(surf, UI_SCROLLBAR["bar_hover_color"], self.bar_rect)
            pygame.draw.rect(surf, UI_SCROLLBAR["handle_hover_color"], self.handle_rect)
        else:
            pygame.draw.rect(surf, UI_SCROLLBAR["bar_default_color"], self.bar_rect)
            pygame.draw.rect(surf, UI_SCROLLBAR["handle_default_color"], self.handle_rect)