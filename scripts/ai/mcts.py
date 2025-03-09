import math

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = {}
        self.visits = 0
        self.value = 0.0  # Expected reward

    def is_fully_expanded(self, action_size):
        return len(self.children) == action_size

    def best_child(self, exploration_weight=1.0):
        """Select the best child node based on UCT (Upper Confidence Bound) formula."""
        return max(
            self.children.values(),
            key=lambda child: child.value / (child.visits + 1e-6) + exploration_weight * math.sqrt(math.log(self.visits + 1) / (child.visits + 1e-6))
        )

    def select(self, action_size):
        """Select a child node to explore."""
        if not self.is_fully_expanded(action_size):
            return self.expand(action_size)
        return self.best_child()

    def expand(self, action_size):
        """Expand a new child node with an unexplored action."""
        for action in range(action_size):
            if action not in self.children:
                new_state = self.state  # Replace with actual state transition logic
                self.children[action] = MCTSNode(new_state, parent=self)
                return self.children[action]
        return self  # Return itself if already fully expanded

    def backpropagate(self, reward):
        """Backpropagate reward to parent nodes."""
        self.visits += 1
        self.value += reward
        if self.parent:
            self.parent.backpropagate(reward)