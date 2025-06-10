import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load the data
df = pd.read_csv('dataSynthetic.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values('Timestamp')

# Define features for anomaly detection
features = [
    'CPU Usage (%)', 'Memory Usage (%)', 'Pod Restarts', 
    'Memory Usage (MB)', 'Network Receive Bytes', 'Network Transmit Bytes',
    'FS Reads Total (MB)', 'FS Writes Total (MB)'
]

# Create target variable (1 for anomaly, 0 for normal)
df['anomaly'] = 0
df.loc[df['Pod Status'] == 'CrashLoopBackOff', 'anomaly'] = 1
df.loc[df['Pod Status'] == 'Error', 'anomaly'] = 1
df.loc[df['Event Reason'] == 'OOMKilling', 'anomaly'] = 1
df.loc[df['Pod Status'] == 'Unknown', 'anomaly'] = 1
df.loc[df['Node Name'].str.contains('NodeNotReady', na=False), 'anomaly'] = 1

# Scale features
scaler = MinMaxScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)
df_scaled['anomaly'] = df['anomaly']
df_scaled['Timestamp'] = df['Timestamp']

# Now you can create sequences for LSTM
df_values = df_scaled.drop('Timestamp', axis=1).values

# Function to create sequences
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length, :-1])  # All columns except the last (anomaly)
        y.append(data[i+seq_length, -1])     # Only the anomaly column
    return np.array(X), np.array(y)

# Create sequences
sequence_length = 10
X, y = create_sequences(df_values, sequence_length)

print(f"Sequences created: X shape = {X.shape}, y shape = {y.shape}")
