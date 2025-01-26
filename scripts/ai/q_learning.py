import random
from collections import defaultdict


class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.1):
        """
        Initialize Q-Learning Agent
        :param actions: list of possible actions (['N', 'E', 'S', 'W'])
        :param alpha: learning rate
        :param gamma: discount factor
        :param epsilon: exploration probability (ε-greedy)
        """
        self.q_table = defaultdict(float)  # Q-value storage table
        self.actions = actions
        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.choice(self.actions)  # exploration
        else:
            # exploitation
            q_values = [self.q_table[(state, action)] for action in self.actions]
            max_q = max(q_values)
            return random.choice([action for action, q in zip(self.actions, q_values) if q == max_q])

    def learn(self, state, action, reward, next_state):
        current_q = self.q_table[(state, action)]
        max_next_q = max([self.q_table[(next_state, a)] for a in self.actions])
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[(state, action)] = new_q