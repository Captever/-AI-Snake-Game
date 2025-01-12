from abc import ABC, abstractmethod

class BaseAI(ABC):
    def __init__(self):
        self.game = None

    def set_current_game(self, game):
        self.game = game

    @abstractmethod
    def decide_direction(self):
        """Method for the AI to decide the next direction"""
        pass
