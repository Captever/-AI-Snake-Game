import pygame, sys
from abc import ABC, abstractmethod

class Scene(ABC):
    def __init__(self, manager):
        self.manager = manager

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