import pygame
import sys

# define color
WHITE = (255, 255, 255)
GRAY = (127, 127, 127)
BLACK = (0, 0, 0)

class Game:
    def __init__(self):
        # initialize Pygame
        pygame.init()

        # initialize screen
        pygame.display.set_caption("Snake")
        self.screen = pygame.display.set_mode((1280, 720))
        self.screen.fill(BLACK)

        # initialize map
        self.mapLength = self.screen.get_width() // 2
        self.map = pygame.Surface((self.mapLength, self.mapLength))
        mapRect = pygame.Rect(0, 0, self.mapLength, self.mapLength)
        pygame.draw.rect(self.map, WHITE, mapRect, 3)

        self.screen.blit(self.map, ((self.screen.get_width() - self.mapLength) // 2, (self.screen.get_height() - self.mapLength) // 2))

        # initialize clock
        self.clock = pygame.time.Clock()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
            pygame.display.update()
            self.clock.tick(60)

        # end of program
        pygame.quit()
        sys.exit()

Game().run()