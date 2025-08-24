import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import joblib

# Load the data
# Example: If dataSynthetic.csv is in the same folder as the script
df = pd.read_csv('dataSynthetic.csv')
df['Timestamp'] = pd.to_datetime(df['Timestamp'])
df = df.sort_values('Timestamp')

# Define features present in the dataset
features = [
    'CPU Usage (%)', 'Memory Usage (%)', 'Pod Restarts',
    'Memory Usage (MB)', 'Network Receive Bytes', 'Network Transmit Bytes',
    'FS Reads Total (MB)', 'FS Writes Total (MB)',
    'Network Receive Packets Dropped (p/s)', 'Network Transmit Packets Dropped (p/s)',
    'Ready Containers'
]

# Handle missing or zero values
df[features] = df[features].fillna(0)  # Replace NaN with 0
df.loc[df['Pod Restarts'].isna(), 'Pod Restarts'] = 0  # Ensure restarts are numeric

# Define anomaly target with refined conditions
df['anomaly'] = 0
df.loc[df['Pod Status'].isin(['CrashLoopBackOff', 'Error', 'Unknown']), 'anomaly'] = 1
df.loc[df['Event Reason'] == 'OOMKilling', 'anomaly'] = 1
df.loc[df['Node Name'].str.contains('NodeNotReady', na=False), 'anomaly'] = 1
df.loc[df['Network Receive Packets Dropped (p/s)'] > 0, 'anomaly'] = 1
df.loc[df['Ready Containers'] < df['Total Containers'], 'anomaly'] = 1

# Scale features
scaler = MinMaxScaler()
df_scaled = pd.DataFrame(scaler.fit_transform(df[features]), columns=features)
df_scaled['anomaly'] = df['anomaly']

# Save the scaler
joblib.dump(scaler, 'scaler.pkl')
print("Scaler saved as 'scaler.pkl'")

# Create sequences for LSTM
def create_sequences(data, seq_length):
    X, y = [], []
    for i in range(len(data) - seq_length):
        X.append(data[i:i+seq_length, :-1])  # All features except anomaly
        y.append(data[i+seq_length, -1])     # Anomaly label
    return np.array(X), np.array(y)

# Prepare data
sequence_length = 10
df_values = df_scaled.values
X, y = create_sequences(df_values, sequence_length)

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build the LSTM model
model = Sequential()
model.add(LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])))
model.add(Dropout(0.2))
model.add(LSTM(64))
model.add(Dropout(0.2))
model.add(Dense(32, activation='relu'))
model.add(Dense(1, activation='sigmoid'))

# Compile model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train model
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2, verbose=1)

# Evaluate model
loss, accuracy = model.evaluate(X_test, y_test)
print(f"Test Loss: {loss:.4f}, Test Accuracy: {accuracy:.4f}")

# Predict anomaly scores on test set for threshold calculation
y_pred = model.predict(X_test)
threshold = np.percentile(y_pred, 95)  # Dynamic threshold at 95th percentile
print(f"Dynamic Anomaly Threshold: {threshold:.4f}")

# Save the model and threshold
model.save('lstm_anomaly_model.h5')
joblib.dump(threshold, 'anomaly_threshold.pkl')
print("Model saved as 'lstm_anomaly_model.h5'")
print("Threshold saved as 'anomaly_threshold.pkl'")