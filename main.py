import pygame
import sys

from constants import *

from scripts.scene_manager import SceneManager
from scenes.init_scene import InitScene
from scenes.game_scene import GameScene

from game import Game

class Main:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption("Snake")

        self.screen: pygame.Surface = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

        self.init_scenes()

        self.running: bool = False

    def init_scenes(self):
        self.scene_manager = SceneManager()
        game_instance = Game()

        init_scene = InitScene(self.scene_manager)
        self.scene_manager.add_scene("InitScene", init_scene)
        game_scene = GameScene(self.scene_manager, game_instance)
        self.scene_manager.add_scene("GameScene", game_scene)
        
        self.scene_manager.set_active_scene("InitScene")

    def run(self):
        self.running = True
        while self.running:
            self.scene_manager.update()

            self.scene_manager.handle_events(pygame.event.get())

            self.end_of_frame()

        self.end_of_game()
    
    def end_of_frame(self):
        self.scene_manager.render(self.screen)

        pygame.display.flip()

    def end_of_game(self):
        pygame.quit()
        sys.exit()
    
Main().run()