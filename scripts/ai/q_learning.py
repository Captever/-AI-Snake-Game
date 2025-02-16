import random

from .base_ai import BaseAI

from constants import DIR_OFFSET_DICT
from scripts.plugin.custom_func import get_dist, get_relative_x_y_dist

from collections import defaultdict

from typing import Tuple
    
class QLearningAI(BaseAI):
    def __init__(self, alpha=0.1, gamma=0.9, epsilon=0.9):
        self.actions = list(DIR_OFFSET_DICT.keys())

        self.agent = QLearningAgent(self.actions, alpha, gamma, epsilon)

        self.dir_offset_list = list(DIR_OFFSET_DICT.values())

        self.last_state = None
        self.last_feed_dist = None
        self.last_score = None
        self.last_action = None

    def get_collision_values(self, head):
        collision_values = []

        for dir_offset in self.dir_offset_list:
            predicted_coord = (head[0] + dir_offset[0], head[1] + dir_offset[1])
            predicted_collision = self.game.check_collision(predicted_coord)[0]
            collision_values.append(predicted_collision)
        
        return collision_values
    
    def get_neck_dir(self, head, neck):
        neck_offset = (neck[0] - head[0], neck[1] - head[1])

        for dir, dir_offset in DIR_OFFSET_DICT.items():
            if neck_offset == dir_offset:
                return dir
    
    def get_dists_from_wall(self, head, grid_size):
        return [grid_size[0]-1 - head[0], grid_size[1]-1 - head[1], head[0], head[1]]

    def decide_direction(self):
        grid_size = self.game.grid_size

        bodies = self.game.player.bodies
        head = bodies[0]
        neck = bodies[1]
        tail = bodies[-1]
        feed = self.game.fs.get_nearest_feed(head)

        state = get_relative_x_y_dist(head, feed, grid_size) + \
                tuple(self.get_collision_values(head)) + \
                (self.get_neck_dir(head, neck), len(bodies)) + \
                tuple(self.get_dists_from_wall(head, grid_size))
        feed_dist = get_dist(head, feed)
        score = self.game.scores["score"]
        action = self.agent.choose_action(state)

        if self.last_state is not None:
            reward = score - self.last_score
            if reward == 0:
                # feedback based on distance
                reward = 0.1 if feed_dist < self.last_feed_dist else -0.1
            self.learn(reward, state)

        self.last_state = state
        self.last_feed_dist = feed_dist
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

        self.epsilon = max(0.01, self.epsilon * 0.995)  # gradually increase greedy behavior