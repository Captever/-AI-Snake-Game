import pygame

import warnings

from constants import *

from typing import Tuple, Dict, List

class RelativeRect:
    def __init__(self, x: float = 0.0, y: float = 0.0, width: float = 1.0, height: float = 1.0):
        """
        Represents a rectangle using relative values (fractions of a parent surface).
        
        Args:
            x (float): Relative x-coordinate (0.0 to 1.0).
            y (float): Relative y-coordinate (0.0 to 1.0).
            width (float): Relative width (0.0 to 1.0).
            height (float): Relative height (0.0 to 1.0).
        """
        self.relative_x = x
        self.relative_y = y
        self.relative_width = width
        self.relative_height = height

    def to_absolute(self, parent_size: Tuple[int, int]) -> pygame.Rect:
        """
        Converts the relative rectangle to an absolute Pygame Rect.
        
        Args:
            parent_size (Tuple[int, int]): Size of the parent surface.

        Returns:
            pygame.Rect: Absolute rectangle.
        """
        abs_x = int(self.relative_x * parent_size[0])
        abs_y = int(self.relative_y * parent_size[1])
        abs_width = int(self.relative_width * parent_size[0])
        abs_height = int(self.relative_height * parent_size[1])
        return pygame.Rect(abs_x, abs_y, abs_width, abs_height)
    
    def to_absolute_with_inner_padding(self, parent_size: Tuple[int, int], relative_inner_padding: float) -> pygame.Rect:
        abs_x = int((self.relative_x + relative_inner_padding) * parent_size[0])
        abs_y = int((self.relative_y + relative_inner_padding) * parent_size[1])
        abs_width = int((self.relative_width - relative_inner_padding * 2) * parent_size[0])
        abs_height = int((self.relative_height - relative_inner_padding * 2) * parent_size[1])
        return pygame.Rect(abs_x, abs_y, abs_width, abs_height)

class Outerline:
    def __init__(self, size: Tuple[int, int], thickness: int = 1, color=(255, 255, 255)):
        self.thickness = thickness

        outer_rect = pygame.Rect(0, 0, size[0] + thickness * 2, size[1] + thickness * 2)

        self.surf = pygame.Surface((outer_rect.width, outer_rect.height), pygame.SRCALPHA)
        self.surf.fill((0, 0, 0, 0))

        pygame.draw.rect(self.surf, color, outer_rect, max(1, thickness)) # minimum value of width: 1

    def render(self, surf, offset=(0, 0)):
        adjusted_pos = (offset[0] - self.thickness, offset[1] - self.thickness)

        surf.blit(self.surf, adjusted_pos)

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

        self.outerline: Outerline = None

    def get_size(self):
        return self.rect.size
    
    def add_outerline(self, outline_thickness: int = 1, outline_color=(255, 255, 255)):
        self.outerline = Outerline(self.get_size(), outline_thickness, outline_color)

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

    def add_button(self, relative_rect: RelativeRect, text: str, callback=None, auto_lined_str: List[str]=None):
        """
        Add a button to the layout with its relative position.
        """
        button = Button(self.abs_pos, relative_rect.to_absolute(self.rect.size), text, callback, auto_lined_str)

        self.elements.append(button)

    def add_scrollbar(self, relative_rect: RelativeRect, text: str, min_val: int, max_val: int, default_val: int, val_step: int = 1):
        """
        Add a scroll bar to the layout with its relative position.
        """
        scrollbar = ScrollBar(self.abs_pos, relative_rect.to_absolute(self.rect.size), text, min_val, max_val, default_val, val_step)

        self.elements.append(scrollbar)
    
    def add_textbox(self, relative_rect: RelativeRect, text: str, font_color, bold: bool = False):
        """
        Add a text box to the layout with its relative position.
        """
        textbox = TextBox(relative_rect.to_absolute(self.rect.size), text, font_color, bold=bold)

        self.elements.append(textbox)
    
    def update_radio_selection(self, target_text: str):
        for element in self.elements:
            if isinstance(element, Button):
                if element.text == target_text:
                    element.set_selected()
                else:
                    element.set_selected(False)

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
                if isinstance(element, Button) or isinstance(element, ScrollBar):
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
        
        render_offset = self.rect.topleft
        surf.blit(layout_surf, render_offset)

        if self.outerline is not None:
            self.outerline.render(surf, render_offset)

class Button:
    def __init__(self, parent_abs_pos: Tuple[int, int], rect: pygame.Rect, text: str, callback=None, auto_lined_str: List[str]=None):
        self.rect: pygame.Rect = pygame.Rect(rect)
        self.abs_pos: Tuple[int, int] = tuple(parent_abs_pos[i] + rect.topleft[i] for i in [0, 1])
        self.text: str = text
        self.callback = callback
        self.auto_lined_str = auto_lined_str

        self.hovered: bool = False
        self.selected: bool = False
    
    def handle_event(self, event):
        if self.is_clicked(event) and not self.selected:
            if self.callback:
                self.callback()
    
    def set_selected(self, is_selected: bool = True):
        self.selected = is_selected
    
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

    def to_auto_lined_text(self, text: str, auto_lined_str: List[str]) -> str:
        for target in auto_lined_str:
            text = text.replace(target, '\n')

        return text

    def render(self, surf: pygame.Surface):
        """
        Render the button on the given surface at the specified rect.
        
        Args:
            surf (pygame.Surface): Surface to render on.
        """
        if self.auto_lined_str is not None:
            text = self.to_auto_lined_text(self.text, self.auto_lined_str)
        else:
            text = self.text

        pygame.draw.rect(surf, UI_BUTTON["selected_color"] if self.selected else (UI_BUTTON["hover_color"] if self.hovered else UI_BUTTON["default_color"]), self.rect)

        font_rect = self.rect.scale_by(UI_BUTTON["font_ratio"], UI_BUTTON["font_ratio"])
        TextBox(font_rect, text, BLACK).render(surf)

class ScrollBar:
    def __init__(self, parent_abs_pos: Tuple[int, int], rect: pygame.Rect, text: str, min_val: int, max_val: int, default_val: int, val_step: int = 1):
        # handling exception
        if (min_val > max_val) or (default_val < min_val) or (default_val > max_val):
            error_param = []

            if min_val > max_val:
                error_param.append("min_val > max_val")
            if default_val < min_val:
                error_param.append("default_val < min_val")
            if default_val > max_val:
                error_param.append("default_val > max_val")

            error_message = f"Scrollbar({text}) value error: {' / '.join(error_param)}"

            raise ValueError(error_message)

        # handling warning
        if (min_val % val_step) or (max_val % val_step) or (default_val % val_step):
            warn_param = []

            if min_val % val_step:
                min_val = (min_val // val_step) * val_step
                warn_param.append("min_val")
            if max_val % val_step:
                max_val = (max_val // val_step + 1) * val_step
                warn_param.append("max_val")
            if default_val % val_step:
                default_val = (default_val // val_step) * val_step
                warn_param.append("default_val")

            warn_message = f"Scrollbar({text}) value warning: items({', '.join(warn_param)}) does not align with the value step."
            
            warnings.warn(warn_message, UserWarning)

        self.rect: pygame.Rect = pygame.Rect(rect)
        self.abs_pos: Tuple[int, int] = tuple(parent_abs_pos[i] + rect.topleft[i] for i in [0, 1])
        self.text: str = text
        self.min_val: int = min_val
        self.max_val: int = max_val
        self.value: int = default_val
        self.val_step: int = val_step
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
            relative_x = event.pos[0] - self.abs_pos[0]
            percentile_val: float = relative_x / self.rect.width
            range_count = self.max_val - self.min_val
            step_count: int = round(percentile_val * range_count / self.val_step) * self.val_step // self.val_step
            self.value = max(self.min_val, min(self.max_val, step_count * self.val_step + self.min_val))
            self.update_handle()

    def render(self, surf: pygame.Surface):
        text = f"{self.text}: {int(self.value):,}"
        font_height = self.rect.height * UI_SCROLLBAR["font_ratio"]
        font_rect = pygame.Rect(self.rect.left, self.rect.top, self.rect.width, font_height)
        TextBox(font_rect, text, WHITE).render(surf)

        if self.hovered:
            pygame.draw.rect(surf, UI_SCROLLBAR["bar_hover_color"], self.bar_rect)
            pygame.draw.rect(surf, UI_SCROLLBAR["handle_hover_color"], self.handle_rect)
        else:
            pygame.draw.rect(surf, UI_SCROLLBAR["bar_default_color"], self.bar_rect)
            pygame.draw.rect(surf, UI_SCROLLBAR["handle_default_color"], self.handle_rect)

class Board:
    def __init__(self, rect: pygame.Rect, title, font_color, default: int=0, format: str=None, custom_ttf_file_path=None):
        self.rect = rect
        self.title = title
        self.surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        self.font_color = font_color
        self.format = format
        self.custom_ttf_file_path = custom_ttf_file_path

        self.default = default

        self.init_font()

    def init_font(self):
        font_area_rect = RelativeRect().to_absolute_with_inner_padding(self.rect.size, UI_BOARD["inner_padding"])

        title_rect_height = round(font_area_rect.height * UI_BOARD["title_ratio"])
        content_rect_height = round(font_area_rect.height * UI_BOARD["content_ratio"])

        title_rect = pygame.Rect(font_area_rect.x, font_area_rect.y, font_area_rect.width, title_rect_height)
        content_rect = pygame.Rect(font_area_rect.x, font_area_rect.y + font_area_rect.height - content_rect_height, font_area_rect.width, content_rect_height)

        if self.custom_ttf_file_path != None:
            self.title_textbox = TextBox(title_rect, self.title, self.font_color, ttf_file_path=self.custom_ttf_file_path, bold=True)
            self.content_textbox = TextBox(content_rect, "", self.font_color, ttf_file_path=self.custom_ttf_file_path)
        else:
            self.title_textbox = TextBox(title_rect, self.title, self.font_color, bold=True)
            self.content_textbox = TextBox(content_rect, "", self.font_color)
        
        self.update_content(self.default)
    
    def reset(self):
        self.update_content(self.default)
    
    def update_content(self, content):
        if self.format != None:
            content = self.format.format(content)
        else:
            content = str(content)
        self.content_textbox.update_content(content)

    def render(self, surf):
        self.surf.fill((0, 0, 0, 0))
        self.title_textbox.render(self.surf)
        self.content_textbox.render(self.surf)

        surf.blit(self.surf, self.rect)

class TextBox:
    def __init__(self, rect: pygame.Rect, content: str, font_color, ttf_file_path: str = "resources/fonts/NanumSquareB.ttf", bold: bool = False):
        self.rect = rect
        self.content = self.get_lined_content(content)
        self.font_color = font_color
        self.font_size = round(rect.height / len(self.content))
        self.font = pygame.font.Font(ttf_file_path, self.font_size)
        self.font.set_bold(bold)

    def get_lined_content(self, content: str):
        return content.split('\n')
    
    def update_content(self, content):
        self.content = self.get_lined_content(content)
    
    def render(self, surf: pygame.Surface):
        for idx, line in enumerate(self.content):
            font_surf = self.font.render(line, True, self.font_color)
            top = self.rect.top + (self.rect.height - (len(self.content) * self.font_size)) // 2 + idx * self.font_size
            font_rect = font_surf.get_rect(centerx=self.rect.centerx, top=top)
            surf.blit(font_surf, font_rect)