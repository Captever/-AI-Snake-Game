import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np

from .base_ai import BaseAI
from constants import DIR_OFFSET_DICT
from scripts.plugin.custom_func import get_dist, get_relative_x_y_dist

def check_for_nan(model, optimizer):
    for name, param in model.named_parameters():
        if torch.isnan(param).any():
            print(f"⚠️ NaN detected in {name}, reducing learning rate...", end=' ')
            for param_group in optimizer.param_groups:
                param_group['lr'] *= 0.5  # Reduce learning rate by half
            return True
    return False

# Policy Network (Neural Network for Policy Gradient)
class PolicyNetwork(nn.Module):
    def __init__(self, state_size, action_size):
        super(PolicyNetwork, self).__init__()
        self.fc1 = nn.Linear(state_size, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return torch.softmax(self.fc3(x), dim=-1)  # Probability distribution over actions


# Policy Gradient Agent
class PolicyGradientAgent:
    def __init__(self, state_size, action_size, lr=0.001, gamma=0.99):
        self.state_size = state_size
        self.action_size = action_size
        self.gamma = gamma  # Discount factor

        self.policy_net = PolicyNetwork(state_size, action_size)
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=lr)

        self.memory = []  # Store (state, action, reward, done)
        
    def choose_action(self, state):
        state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)

        with torch.no_grad():  # Disable gradient calculation for efficiency
            action_probs = self.policy_net(state_tensor).squeeze(0)

        # Ensure probabilities are valid
        action_probs = action_probs.clamp(min=1e-5)  # Prevent zero probability
        action_probs /= action_probs.sum()  # Normalize to sum to 1

        action_probs = action_probs.numpy()  # Convert to NumPy array

        # If NaN still exists, replace with uniform probability
        if np.isnan(action_probs).any():
            action_probs = np.ones(self.action_size) / self.action_size  # Assign equal probability to all actions

        return np.random.choice(self.action_size, p=action_probs)  # Sample action from probability distribution

    def store_transition(self, state, action, reward, done):
        self.memory.append((state, action, reward, done))

    def learn(self):
        if not self.memory:
            return  # No data to learn from

        # Check for NaN in model weights before training
        if check_for_nan(self.policy_net, self.optimizer):
            print(": occured on PolicyGradientAgent.learn()")
            return
        
        # Compute discounted rewards
        R = 0
        rewards = []
        for reward, done in reversed([(r, d) for _, _, r, d in self.memory]):
            if done:
                R = 0  # Reset reward at game over
            R = reward + self.gamma * R
            rewards.insert(0, R)  # Discounted rewards

        rewards = torch.tensor(rewards, dtype=torch.float32)
        rewards = (rewards - rewards.mean()) / (rewards.std() + 1e-9)  # Normalize rewards

        # Compute policy loss
        policy_loss = []
        for (state, action, reward, _), Gt in zip(self.memory, rewards):
            state_tensor = torch.tensor(state, dtype=torch.float32).unsqueeze(0)
            action_tensor = torch.tensor(action, dtype=torch.int64)

            action_probs = self.policy_net(state_tensor)
            action_log_prob = torch.log(action_probs.squeeze(0)[action_tensor].clamp(min=1e-5))
            policy_loss.append(-action_log_prob * Gt)  # Gradient ascent

        # Optimize policy network
        self.optimizer.zero_grad()
        loss = torch.stack(policy_loss).sum()
        loss.backward()

        # Apply Gradient Clipping
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), max_norm=1.0)

        self.optimizer.step()

        # Clear memory after learning
        self.memory = []


# Policy Gradient-based Snake AI
class PolicyGradientAI(BaseAI):
    def __init__(self):
        self.actions = list(DIR_OFFSET_DICT.keys())  # ['E', 'W', 'S', 'N']
        self.action_size = len(self.actions)
        self.state_size = 11

        self.agent = PolicyGradientAgent(self.state_size, self.action_size)

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
        return [grid_size[0] - 1 - head[0], grid_size[1] - 1 - head[1], head[0], head[1]]
    
    def get_current_state_and_feed_dist(self):
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
        
        return state, feed_dist

    def decide_direction(self):
        state, feed_dist = self.get_current_state_and_feed_dist()
        
        score = self.game.scores["score"]

        action_index = self.agent.choose_action(state)

        if self.last_state is not None:
            reward = score - self.last_score
            if reward == 0:
                # If moving towards the food, increase reward; if moving away, decrease reward
                reward = 0.2 if feed_dist < self.last_feed_dist else -0.2

                # Additional reward: Encouraging survival
                reward += 0.25  # Small reward for staying alive each turn
            self.learn(reward, False)

        self.last_state = state
        self.last_feed_dist = feed_dist
        self.last_score = score
        self.last_action = action_index

        return self.actions[action_index]
    
    def learn(self, reward, done: bool):
        self.agent.store_transition(self.last_state, self.last_action, reward, done)
        if done:
            self.agent.learn()

            self.last_state = None
            self.last_feed_dist = None
            self.last_score = None
            self.last_action = None