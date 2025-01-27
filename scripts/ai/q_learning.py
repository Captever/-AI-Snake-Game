import random

from .base_ai import BaseAI

from constants import DIR_OFFSET_DICT

from collections import defaultdict

from typing import Tuple

def get_x_y_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]):
    return (pos_b[0] - pos_a[0], pos_b[1] - pos_a[1])

def get_dist(pos_a: Tuple[int, int], pos_b: Tuple[int, int]):
    x_diff, y_diff = get_x_y_dist(pos_a, pos_b)
    return abs(x_diff) + abs(y_diff)

def get_nearest_feed(head, feeds):
    return min(feeds, key=lambda food: get_dist(head, food))
    
class QLearningAI(BaseAI):
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.1):
        self.actions = list(DIR_OFFSET_DICT.keys())

        self.agent = QLearningAgent(self.actions, alpha, gamma, epsilon)

        self.last_state = None
        self.last_score = None
        self.last_action = None

    def get_state(self, head, feeds):
        target_feed = get_nearest_feed(head, feeds)
        dist_to_target = get_x_y_dist(head, target_feed)
        return dist_to_target

    def decide_direction(self):
        head = self.game.player.bodies[0]
        feeds = self.game.fs.feeds

        state = self.get_state(head, feeds)
        score = self.game.sm.get_score()
        action = self.agent.choose_action(state)

        if self.last_state is not None:
            reward = score - self.last_score
            if reward == 0:
                reward = -0.1 # movement penalty
            self.learn(reward, state)

        self.last_state = state
        self.last_score = score
        self.last_action = action

        return action
    
    def learn(self, reward, next_state):
        self.agent.learn(self.last_state, self.last_action, reward, next_state)

class QLearningAgent:
    def __init__(self, actions, alpha, gamma, epsilon):
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

    def choose_action(self, state: Tuple[int, int]) -> str:
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