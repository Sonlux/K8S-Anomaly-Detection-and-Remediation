import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from tensorflow.keras.models import load_model, Sequential
from tensorflow.keras.layers import Dense, Input, Concatenate
from tensorflow.keras.optimizers import Adam
import logging
import random
from collections import deque
import os
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ai_agent_prediction")

# Load the pre-trained LSTM model and related components
model_path = 'lstm_anomaly_model.h5'
scaler_path = 'scaler.pkl'
threshold_path = 'anomaly_threshold.pkl'

# Check if files exist
if not all(os.path.exists(path) for path in [model_path, scaler_path, threshold_path]):
    logger.error("Required model files not found. Please ensure lstm_anomaly_model.h5, scaler.pkl, and anomaly_threshold.pkl exist.")
    raise FileNotFoundError("Required model files not found")

# Load the models and components
lstm_model = load_model(model_path)
scaler = joblib.load(scaler_path)
threshold = joblib.load(threshold_path)
logger.info(f"Loaded LSTM model, scaler, and threshold: {threshold:.4f}")

# Define features to match the trained model
features = [
    'CPU Usage (%)', 'Memory Usage (%)', 'Pod Restarts',
    'Memory Usage (MB)', 'Network Receive Bytes', 'Network Transmit Bytes',
    'FS Reads Total (MB)', 'FS Writes Total (MB)',
    'Network Receive Packets Dropped (p/s)', 'Network Transmit Packets Dropped (p/s)',
    'Ready Containers'
]

# Define possible actions the agent can take
ACTIONS = {
    0: "no_action",
    1: "restart_pod",
    2: "scale_up_resources",
    3: "scale_down_resources",
    4: "check_network",
    5: "check_storage"
}

# Define the AI Agent class
class AIAgent:
    def __init__(self, state_size, action_size, learning_rate=0.001, gamma=0.95, epsilon=1.0, 
                 epsilon_min=0.01, epsilon_decay=0.995, memory_size=2000):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=memory_size)
        self.gamma = gamma  # discount rate
        self.epsilon = epsilon  # exploration rate
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.learning_rate = learning_rate
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model()
        logger.info("AI Agent initialized")
        
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        model.add(Dense(64, input_dim=self.state_size, activation='relu'))
        model.add(Dense(64, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=self.learning_rate))
        return model
    
    def update_target_model(self):
        # copy weights from model to target_model
        self.target_model.set_weights(self.model.get_weights())
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    
    def act(self, state):
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
        act_values = self.model.predict(state, verbose=0)
        return np.argmax(act_values[0])
    
    def replay(self, batch_size):
        if len(self.memory) < batch_size:
            return
        
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                target = reward + self.gamma * np.amax(self.target_model.predict(next_state, verbose=0)[0])
            target_f = self.model.predict(state, verbose=0)
            target_f[0][action] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def load(self, name):
        self.model.load_weights(name)
    
    def save(self, name):
        self.model.save_weights(name)

# Define the environment class
class K8sEnvironment:
    def __init__(self, initial_data=None):
        self.initial_data = initial_data
        self.current_step = 0
        self.history = []
        self.action_history = []
        self.reward_history = []
        logger.info("K8s Environment initialized")
    
    def reset(self, data=None):
        if data is not None:
            self.initial_data = data
        self.current_step = 0
        self.history = []
        self.action_history = []
        self.reward_history = []
        return self._get_state()
    
    def _get_state(self):
        if self.initial_data is None:
            # Create a default state if no data is provided
            state = np.zeros(len(features))
        else:
            # Use the provided data
            if isinstance(self.initial_data, pd.DataFrame):
                if len(self.initial_data) > self.current_step:
                    state = self.initial_data.iloc[self.current_step][features].values
                else:
                    state = self.initial_data.iloc[-1][features].values
            else:
                state = self.initial_data
        
        # Scale the state using the same scaler as the LSTM model
        scaled_state = scaler.transform(state.reshape(1, -1))[0]
        return scaled_state.reshape(1, -1)
    
    def step(self, action):
        # Get the current state
        current_state = self._get_state()
        
        # Get prediction from LSTM model
        lstm_prediction = lstm_model.predict(current_state.reshape(1, 10, len(features)), verbose=0)
        anomaly_score = lstm_prediction[0][0]
        is_anomaly = anomaly_score > threshold
        
        # Determine reward based on action and prediction
        reward = self._calculate_reward(action, is_anomaly, anomaly_score)
        
        # Move to next step
        self.current_step += 1
        next_state = self._get_state()
        
        # Check if episode is done
        done = self.current_step >= 100  # Arbitrary episode length
        
        # Store history
        self.history.append(current_state)
        self.action_history.append(action)
        self.reward_history.append(reward)
        
        return next_state, reward, done, {}
    
    def _calculate_reward(self, action, is_anomaly, anomaly_score):
        # Define reward logic based on action and prediction
        if is_anomaly:
            # If anomaly is detected, taking an action is good
            if action > 0:  # Any action except no_action
                return 1.0
            else:
                return -1.0  # Penalty for not taking action when anomaly is detected
        else:
            # If no anomaly, taking no action is good
            if action == 0:  # no_action
                return 0.5
            else:
                return -0.5  # Small penalty for taking unnecessary action
    
    def get_action_description(self, action):
        return ACTIONS.get(action, "unknown_action")

# Function to prepare data for prediction
def prepare_data(data, sequence_length=10):
    missing_cols = [col for col in features if col not in data.columns]
    if missing_cols:
        logger.warning(f"Missing columns {missing_cols}, filling with zeros")
        for col in missing_cols:
            data[col] = 0
    
    data = data[features].copy()
    
    if len(data) < sequence_length:
        padded_data = np.zeros((sequence_length - len(data), len(features)))
        scaled_data = scaler.transform(np.vstack((padded_data, data)))
    else:
        scaled_data = scaler.transform(data.tail(sequence_length))
    
    return scaled_data

# Function to predict and take action
def predict_and_act(data, agent, env, sequence_length=10):
    # Prepare data
    scaled_data = prepare_data(data, sequence_length)
    
    # Get LSTM prediction
    X = scaled_data.reshape(1, sequence_length, len(features))
    lstm_prediction = lstm_model.predict(X, verbose=0)
    anomaly_score = lstm_prediction[0][0]
    is_anomaly = anomaly_score > threshold
    
    # Get current state for the agent
    current_state = env._get_state()
    
    # Agent decides on action
    action = agent.act(current_state)
    action_description = env.get_action_description(action)
    
    # Take action and get reward
    next_state, reward, done, _ = env.step(action)
    
    # Store experience in agent's memory
    agent.remember(current_state, action, reward, next_state, done)
    
    # Train the agent
    agent.replay(32)  # Replay with batch size of 32
    
    # Determine anomaly type
    anomaly_type = 'unknown'
    if is_anomaly:
        last_row = data.iloc[-1] if isinstance(data, pd.DataFrame) else data
        if last_row['Pod Restarts'] > 5:
            anomaly_type = 'crash_loop'
        elif last_row['Memory Usage (MB)'] > 500:
            anomaly_type = 'oom_kill'
        elif last_row['CPU Usage (%)'] > 90:
            anomaly_type = 'resource_exhaustion'
        elif (last_row['Network Receive Packets Dropped (p/s)'] > 0 or 
              last_row['Network Transmit Packets Dropped (p/s)'] > 0 or 
              last_row['Network Transmit Bytes'] > 10000):
            anomaly_type = 'network_issue'
        elif last_row['Ready Containers'] < last_row.get('Total Containers', 1):
            anomaly_type = 'partial_failure'
        elif last_row['FS Reads Total (MB)'] > 10 or last_row['FS Writes Total (MB)'] > 10:
            anomaly_type = 'io_issue'
    
    # Prepare result
    result = {
        'predicted_anomaly': 1 if is_anomaly else 0,
        'anomaly_probability': float(anomaly_score),
        'anomaly_type': anomaly_type,
        'recommended_action': action_description,
        'action_id': action,
        'reward': float(reward)
    }
    
    logger.info(f"Prediction: Anomaly={is_anomaly}, Score={anomaly_score:.4f}, Action={action_description}")
    return result

# Main function to run the AI agent
def run_ai_agent(data, episodes=10, batch_size=32):
    # Initialize environment and agent
    env = K8sEnvironment(data)
    state_size = len(features)
    action_size = len(ACTIONS)
    agent = AIAgent(state_size, action_size)
    
    # Training loop
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        done = False
        
        logger.info(f"Starting episode {episode+1}/{episodes}")
        
        while not done:
            # Agent decides on action
            action = agent.act(state)
            
            # Take action and get reward
            next_state, reward, done, _ = env.step(action)
            
            # Store experience in agent's memory
            agent.remember(state, action, reward, next_state, done)
            
            # Update state
            state = next_state
            total_reward += reward
            
            # Train the agent
            agent.replay(batch_size)
        
        # Update target model every episode
        agent.update_target_model()
        
        logger.info(f"Episode {episode+1}/{episodes} completed with total reward: {total_reward:.2f}")
    
    # Save the trained agent
    agent.save('ai_agent_model.h5')
    logger.info("AI Agent model saved as 'ai_agent_model.h5'")
    
    return agent, env

# Example usage
if __name__ == "__main__":
    # Sample data for testing
    sample_data = pd.DataFrame({
        'CPU Usage (%)': [0.012098631],
        'Memory Usage (%)': [4.747099786],
        'Pod Restarts': [370],
        'Memory Usage (MB)': [18.47939985],
        'Network Receive Bytes': [0.014544437],
        'Network Transmit Bytes': [0.122316709],
        'FS Reads Total (MB)': [0.000586664],
        'FS Writes Total (MB)': [0.000836434],
        'Network Receive Packets Dropped (p/s)': [0],
        'Network Transmit Packets Dropped (p/s)': [0],
        'Ready Containers': [0]
    })
    
    # Initialize environment and agent
    env = K8sEnvironment(sample_data)
    state_size = len(features)
    action_size = len(ACTIONS)
    agent = AIAgent(state_size, action_size)
    
    # Make a prediction and get an action
    result = predict_and_act(sample_data, agent, env)
    
    # Print the result
    logger.info("\nFinal Prediction and Action:")
    for key, value in result.items():
        logger.info(f"{key}: {value}")
