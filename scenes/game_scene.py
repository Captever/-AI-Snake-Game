import pygame

from scripts.scene_manager import Scene

class GameScene(Scene):
    def __init__(self, manager, game_instance):
        super().__init__(manager)
        # self.game = game_instance  # The existing Game instance should be integrated here.
        # game_instance.run()

    # def handle_events(self, events):
    #     for event in events:
    #         if event.type == pygame.KEYDOWN:
    #             self.game.handle_keydown(event.key)
    #         elif event.type == pygame.QUIT:
    #             pygame.quit()
    #             sys.exit()

    # def update(self):
    #     if self.game.is_active():
    #         self.game.player.move_sequence()
    #     self.game.countdown()

    # def render(self, screen):
    #     self.game.start_of_frame()
    #     self.game.end_of_frame()
