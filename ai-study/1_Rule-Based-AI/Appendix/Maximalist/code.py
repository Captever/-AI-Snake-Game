from .base_ai import BaseAI

def is_even(num: int) -> bool:
    return num % 2 == 0

class RuleBasedAI(BaseAI):
    def __init__(self, method: str):
        super().__init__()
        self.method = method

    def decide_direction(self):
        head = self.game.player.bodies[0]
        grid_size = self.game.grid_size
        
        dir: str = None

        is_width_even, is_height_even = tuple(is_even(grid_size[i]) for i in [0, 1])

        if is_width_even:
            if head[0] < grid_size[0] - 1 and head[1] == grid_size[1] - 1:
                dir = 'E'
            elif head[0] == 0 and head[1] < grid_size[1] - 1:
                dir = 'S'
            elif head[0] == grid_size[0] - 1 and head[1] > 0:
                dir = 'N'
            elif (not is_even(head[0]) and head[1] == 0) \
                    or (is_even(head[0]) and head[1] == grid_size[1] - 2):
                dir = 'W'
            elif is_even(head[0]) and head[1] < grid_size[1] - 2:
                dir = 'S'
            else:
                dir = 'N'

        elif is_height_even:
            if head[0] < grid_size[0] - 1 and head[1] == grid_size[1] - 1:
                dir = 'E'
            elif head[0] == 0 and head[1] < grid_size[1] - 1:
                dir = 'S'
            elif head[1] == 0:
                dir = 'W'
            elif (head[0] == grid_size[0] - 1 and not is_even(head[1])) \
                    or (head[0] == 1 and is_even(head[1])):
                dir = 'N'
            elif head[0] > 1 and is_even(head[1]):
                dir = 'W'
            else:
                dir = 'E'

        else:
            # There will inevitably be empty spaces.
            # Causes too much deliberation, so it's put on hold.
            pass

        return dir
