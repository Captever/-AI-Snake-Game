from .base_ai import BaseAI

class RuleBasedAI(BaseAI):
    def decide_direction(self):
        # decide the direction using simple rules (e.g., move toward the food)
        head = self.game.player.bodies[0]
        feeds = list(self.game.fs.feeds.keys())
        if not feeds:
            return None
        target = feeds[0]
        dx, dy = target[0] - head[0], target[1] - head[1]

        if abs(dx) > abs(dy):
            return 'E' if dx > 0 else 'W'
        else:
            return 'S' if dy > 0 else 'N'
