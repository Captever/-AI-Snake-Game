import pygame, sys
from abc import ABC, abstractmethod

from typing import Tuple

class Scene(ABC):
    def __init__(self, manager, size: Tuple[int, int]):
        self.manager = manager
        self.size = size

        self.is_landscape: bool = self.size[0] >= self.size[1]

    @abstractmethod
    def handle_events(self, events):
        """Handle input events."""
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    @abstractmethod
    def render(self, screen):
        """Render the scene."""
        pass

    def update(self):
        """Update game logic."""
        pass