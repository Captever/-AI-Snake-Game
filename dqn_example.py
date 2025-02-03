import numpy as np
import random
import torch
import torch.nn as nn
import torch.optim as optim
import gym
import pickle
from collections import deque

# Hyperparameters
GRID_SIZE = 10
NUM_FOOD = 3  # Number of food items
EPISODES = 10000
BATCH_SIZE = 64
GAMMA = 0.9
EPSILON = 1.0
EPSILON_DECAY = 0.995
EPSILON_MIN = 0.01
LEARNING_RATE = 0.001
MEMORY_SIZE = 10000
TARGET_UPDATE = 10  # Update target network every 10 episodes
BUFFER_FILE = "replay_buffer.pkl"  # File to store Replay Buffer

# Replay Buffer (Stores past experiences)
class ReplayBuffer:
    def __init__(self, max_size=MEMORY_SIZE):
        self.buffer = self.load_replay_buffer()  # Load buffer if exists, else create new
        self.max_size = max_size

    def add(self, experience):
        self.buffer.append(experience)
        self.save_replay_buffer()  # Save buffer after each addition

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def size(self):
        return len(self.buffer)

    def save_replay_buffer(self):
        """Save the Replay Buffer to a file using pickle."""
        with open(BUFFER_FILE, "wb") as f:
            pickle.dump(self.buffer, f)

    def load_replay_buffer(self):
        """Load Replay Buffer from a file if it exists."""
        try:
            with open(BUFFER_FILE, "rb") as f:
                return deque(pickle.load(f), maxlen=self.max_size)
        except FileNotFoundError:
            return deque(maxlen=self.max_size)

# DQN Neural Network
class DQN(nn.Module):
    def __init__(self, state_size, action_size):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(state_size, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, action_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)  # Output Q-values for all actions

# Snake Agent (Handles learning and action selection)
class SnakeAgent:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.q_network = DQN(STATE_SIZE, ACTION_SIZE).to(self.device)  # Main Q-network
        self.target_network = DQN(STATE_SIZE, ACTION_SIZE).to(self.device)  # Target network
        self.target_network.load_state_dict(self.q_network.state_dict())  # Sync initially
        self.target_network.eval()  # Target network does not train

        self.optimizer = optim.Adam(self.q_network.parameters(), lr=LEARNING_RATE)
        self.memory = ReplayBuffer()  # Load saved replay buffer
        self.epsilon = EPSILON

    def choose_action(self, state):
        """Select an action using epsilon-greedy policy."""
        if random.random() < self.epsilon:
            return random.randint(0, ACTION_SIZE - 1)  # Random action (exploration)
        else:
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            with torch.no_grad():
                q_values = self.q_network(state_tensor)
            return torch.argmax(q_values).item()  # Best action (exploitation)

    def update(self):
        """Update the Q-network using experience replay."""
        if self.memory.size() < BATCH_SIZE:
            return  # Wait until enough samples are available

        batch = self.memory.sample(BATCH_SIZE)
        states, actions, rewards, next_states, dones = zip(*batch)

        states = torch.FloatTensor(states).to(self.device)
        actions = torch.LongTensor(actions).to(self.device)
        rewards = torch.FloatTensor(rewards).to(self.device)
        next_states = torch.FloatTensor(next_states).to(self.device)
        dones = torch.FloatTensor(dones).to(self.device)

        q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (1 - dones) * GAMMA * next_q_values

        loss = nn.MSELoss()(q_values, target_q_values)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

    def update_target_network(self):
        """Update the target network with the latest Q-network parameters."""
        self.target_network.load_state_dict(self.q_network.state_dict())

# Training Loop
def train_snake():
    env = gym.make('gym_snake:snake-v0', grid_size=GRID_SIZE, num_food=NUM_FOOD)
    agent = SnakeAgent()
    
    for episode in range(EPISODES):
        state = env.reset()
        state = extract_features(state)  # Convert state to feature vector
        done = False
        total_reward = 0
        
        while not done:
            action = agent.choose_action(state)
            next_state, reward, done, _ = env.step(action)
            next_state = extract_features(next_state)
            agent.memory.add((state, action, reward, next_state, done))
            agent.update()
            state = next_state
            total_reward += reward

        agent.epsilon = max(EPSILON_MIN, agent.epsilon * EPSILON_DECAY)  # Decay epsilon

        if episode % TARGET_UPDATE == 0:
            agent.update_target_network()

        if episode % 100 == 0:
            print(f"Episode: {episode}, Score: {total_reward}, Epsilon: {agent.epsilon}")

    env.close()

# State Processing Function
def extract_features(state):
    """Extracts relevant features from the game state."""
    snake_head = state['snake'][0]  # Get snake head position
    food_positions = state['food']
    collisions = state['collisions']

    features = []
    
    # Encode relative food positions (x, y)
    for food in food_positions:
        features.append(food[0] - snake_head[0])
        features.append(food[1] - snake_head[1])

    # Add collision information (N, S, E, W)
    features.extend(collisions)

    return np.array(features, dtype=np.float32)

# Run Training
train_snake()