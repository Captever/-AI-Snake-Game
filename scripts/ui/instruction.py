import pygame

from constants import UI_INSTRUCTION

from scripts.ui.ui_components import RelativeRect, UILayout

from typing import List, Tuple

class Instruction:
    def __init__(self, rect: pygame.Rect, title: str, instruction_list: List[Tuple[str, str]], font_color, bg_color = UI_INSTRUCTION["default_color"]):
        self.rect = rect
        self.title = title
        self.instruction_list = instruction_list
        self.font_color = font_color
        self.bg_color = bg_color

        self.surf = pygame.Surface(rect.size, pygame.SRCALPHA)

        self.index = 0
        self.init_layout()
    
    def init_layout(self):
        layout_rect = RelativeRect().to_absolute_with_inner_padding(self.rect.size, UI_INSTRUCTION["inner_padding"])

        self.layout = UILayout((0, 0), layout_rect)

        # add title
        self.layout.add_textbox(RelativeRect(height=UI_INSTRUCTION["title_ratio"]), self.title, self.font_color, bold=True)

        # add content
        self.layout.add_layout("content", RelativeRect(y=1-UI_INSTRUCTION["content_ratio"], height=UI_INSTRUCTION["content_ratio"]))
        for key, act in self.instruction_list:
            self.add_instruction(key, act)

    def add_instruction(self, key: str, act: str):
        curr_y = self.index * (UI_INSTRUCTION["each_content_ratio"] + UI_INSTRUCTION["each_content_margin"])
        curr_instruction = f"{key} : {act}"

        self.layout.layouts["content"].add_textbox(RelativeRect(y=curr_y, height=UI_INSTRUCTION["each_content_ratio"]), curr_instruction, self.font_color)
        
        # shift to next index
        self.index += 1

        # accept change after adding new instruction
        self.accept_change()

    def accept_change(self):
        self.surf.fill(self.bg_color)

        self.layout.render(self.surf)

    def render(self, surf):
        surf.blit(self.surf, self.rect)