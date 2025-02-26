import pygame, sys
from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from scripts.manager.scene_manager import SceneManager

class BaseScene(ABC):
    def __init__(self, manager: "SceneManager", rect: pygame.Rect):
        self.manager = manager
        self.rect = rect
        self.size = rect.size
        self.origin = rect.topleft

        self.surf = pygame.Surface(self.size)

        self.is_landscape: bool = self.size[0] >= self.size[1]

    def on_scene_changed(self):
        """Methods to be overridden in subclasses"""
        pass

    @abstractmethod
    def handle_events(self, events):
        """Handle input events."""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    @abstractmethod
    def render(self, surf):
        """Render the scene."""
        self.surf.fill((0, 0, 0))

    def update(self):
        """Update game logic."""
        pass