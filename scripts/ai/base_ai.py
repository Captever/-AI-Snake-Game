from abc import ABC, abstractmethod

class BaseAI(ABC):
    def __init__(self, game):
        self.game = game

    @abstractmethod
    def decide_direction(self):
        """Method for the AI to decide the next direction"""
        pass
