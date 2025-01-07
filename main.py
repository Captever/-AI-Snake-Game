import pygame
import sys

from constants import *

from scripts.scene_manager import SceneManager
from scenes.init_scene import InitScene
from scenes.game_scene import GameScene

from game import Game

pygame.init()

pygame.display.set_caption("Snake")

game_instance = Game()

standard_font_size: int = round(max(SCREEN_WIDTH, SCREEN_HEIGHT) * FONT_SIZE_RATIO)
scene_manager = SceneManager(standard_font_size)
init_scene = InitScene(scene_manager)
game_scene = GameScene(scene_manager, game_instance)

scene_manager.add_scene("InitScene", init_scene)
scene_manager.add_scene("GameScene", game_scene)

scene_manager.set_active_scene("InitScene")