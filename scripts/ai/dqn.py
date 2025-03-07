import random
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque

from .base_ai import BaseAI
from constants import DIR_OFFSET_DICT
from scripts.plugin.custom_func import get_dist, get_relative_x_y_dist

from typing import Tuple


# Define Neural Network (DQN Model)
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)  # Return Q-values


# Experience Replay Buffer
class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)

    def push(self, state, action, reward, next_state, done):
        self.buffer.append((state, action, reward, next_state, done))

    def sample(self, batch_size):
        indices = np.arange(len(self.buffer))  # Assign weight to the latest data
        
        # Apply log weighting for better balance between old and new data
        probs = np.log(indices + 1)
        probs /= probs.sum()  # Normalize to probabilities
        
        sampled_indices = np.random.choice(indices, batch_size, p=probs)
        batch = [self.buffer[i] for i in sampled_indices]
        
        states, actions, rewards, next_states, dones = zip(*batch)
        return np.array(states), actions, np.array(rewards), np.array(next_states), np.array(dones)

    def __len__(self):
        return len(self.buffer)


# DQN Agent Definition
class DQNAgent:
    def __init__(self, state_size, action_size, lr=0.001, gamma=0.9, epsilon=0.9, epsilon_min=0.01, epsilon_decay=0.995, epsilon_update_period=1000, tar_net_update_period=500, buffer_size=10000, batch_size=32):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma  # Discount factor
        self.epsilon = epsilon  # Exploration probability
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.epsilon_update_period = epsilon_update_period
        self.tar_net_update_period = tar_net_update_period
        self.batch_size = batch_size

        # Policy Network (Current training network)
        self.policy_net = DQN(state_size, action_size)
        # Target Network (For stable learning)
        self.target_net = DQN(state_size, action_size)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()  # Target network does not train

        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)
        self.criterion = nn.MSELoss()

        self.memory = ReplayBuffer(buffer_size)
        self.update_target_counter = 0

    def choose_action(self, state):
        if random.uniform(0, 1) < self.epsilon:
            return random.randint(0, self.action_size - 1)  # Exploration
        else:
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            with torch.no_grad():
                q_values = self.policy_net(state_tensor)
            return torch.argmax(q_values).item()  # Select action with max Q-value

    def learn(self):
        if len(self.memory) < self.batch_size:
            return  # Do not train if not enough data

        states, actions, rewards, next_states, dones = self.memory.sample(self.batch_size)

        states = torch.tensor(states, dtype=torch.float32)
        actions = torch.tensor(actions, dtype=torch.int64).unsqueeze(1)
        rewards = torch.tensor(rewards, dtype=torch.float32)
        next_states = torch.tensor(next_states, dtype=torch.float32)
        dones = torch.tensor(dones, dtype=torch.float32)

        # Compute Q(s, a)
        q_values = self.policy_net(states).gather(1, actions).squeeze(1)

        # Compute Q_target(s', a') using target network
        with torch.no_grad():
            max_next_q_values = self.target_net(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * max_next_q_values

        loss = self.criterion(q_values, target_q_values)

        # Update neural network
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        self.update_target_counter += 1

        # Decrease epsilon every epsilon_update_period (Reduce exploration)
        if self.epsilon > self.epsilon_min and self.update_target_counter % self.epsilon_update_period == 0:
            prev_epsilon = self.epsilon
            self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
            print(f"epsilon decrease: {prev_epsilon} -> {self.epsilon}")

        # Update target network periodically
        if self.update_target_counter % self.tar_net_update_period == 0:
            self.target_net.load_state_dict(self.policy_net.state_dict())


# DQN-based Snake AI
class DQNAI(BaseAI):
    def __init__(self):
        self.actions = list(DIR_OFFSET_DICT.keys())  # ['E', 'W', 'S', 'N']
        self.action_size = len(self.actions)
        self.state_size = 11
        
        self.agent = DQNAgent(self.state_size, self.action_size)

        self.dir_offset_list = list(DIR_OFFSET_DICT.values())

        self.last_state = None
        self.last_feed_dist = None
        self.last_score = None
        self.last_action = None

    def get_collision_mapping_values(self, head, mapping_dict):
        collision_values = []

        for dir_offset in self.dir_offset_list:
            predicted_coord = (head[0] + dir_offset[0], head[1] + dir_offset[1])
            predicted_collision = self.game.check_collision(predicted_coord)[0]
            collision_values.append(mapping_dict[predicted_collision])
        
        return collision_values
    
    def get_dists_from_wall(self, head, grid_size):
        return [grid_size[0]-1 - head[0], grid_size[1]-1 - head[1], head[0], head[1]]

    def decide_direction(self):
        grid_size = self.game.grid_size

        bodies = self.game.player.get_bodies()
        head = bodies[0]
        feed = self.game.fs.get_nearest_feed_coord(head)

        collision_mapping = {'none': 0, 'wall': 1, 'body': 2, 'feed': 3}
        # Define current state
        state = get_relative_x_y_dist(head, feed, grid_size) + \
                tuple(self.get_collision_mapping_values(head, collision_mapping),) + \
                (len(bodies),) + \
                tuple(self.get_dists_from_wall(head, grid_size))
        
        feed_dist = get_dist(head, feed)
        score = self.game.scores["score"]

        action_index = self.agent.choose_action(state)

        if self.last_state is not None:
            reward = score - self.last_score
            if reward == 0:
                # If moving towards the food, increase reward; if moving away, decrease reward
                reward = 0.5 if feed_dist < self.last_feed_dist else -0.5

                # Additional reward: Encouraging survival
                reward += 0.1  # Small reward for staying alive each turn
            self.learn(reward, state, False)

        self.last_state = state
        self.last_feed_dist = feed_dist
        self.last_score = score
        self.last_action = action_index

        return self.actions[action_index]
    
    def learn(self, reward, next_state, done: bool):
        # If game over, set next_state as a zero vector (same shape as state)
        if done or next_state is None:
            next_state = np.zeros_like(self.last_state)  # Zero vector with same shape

        self.agent.memory.push(self.last_state, self.last_action, reward, next_state, done)
        self.agent.learn()