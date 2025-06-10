"""
Anomaly Prediction Model

This module provides functions for predicting anomalies in Kubernetes pods.
It can operate in two modes:
1. TensorFlow-based prediction (when TensorFlow is available)
2. Rule-based fallback prediction (when TensorFlow is not available)
"""

import os
import sys
import logging
import pandas as pd
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("anomaly-prediction")

# Try to import TensorFlow, but provide a robust fallback if it fails
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model
    HAS_TENSORFLOW = True
    logger.info("TensorFlow successfully imported")
except ImportError as e:
    HAS_TENSORFLOW = False
    logger.warning(f"TensorFlow import failed: {e}")
    logger.info("Using rule-based fallback prediction instead")

# Path to the saved model
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                         "model_artifacts", "anomaly_model.h5")

# Load the model if TensorFlow is available
model = None
if HAS_TENSORFLOW and os.path.exists(MODEL_PATH):
    try:
        model = load_model(MODEL_PATH)
        logger.info(f"Loaded model from {MODEL_PATH}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        model = None

def rule_based_prediction(pod_metrics):
    """
    Fallback prediction function using simple rules when TensorFlow is unavailable
    
    Args:
        pod_metrics: Dictionary containing pod metrics
        
    Returns:
        Dictionary with prediction results
    """
    # Extract relevant metrics with safe defaults
    cpu_usage = pod_metrics.get('CPU Usage (%)', 0)
    memory_usage = pod_metrics.get('Memory Usage (%)', 0)
    pod_restarts = pod_metrics.get('Pod Restarts', 0)
    ready_containers = pod_metrics.get('Ready Containers', 0)
    total_containers = pod_metrics.get('Total Containers', 1)
    
    # Default result
    result = {
        'predicted_anomaly': 0,
        'anomaly_probability': 0.1,
        'anomaly_type': 'unknown'
    }
    
    # Simple rule-based detection
    if pod_restarts > 5:
        result['predicted_anomaly'] = 1
        result['anomaly_probability'] = min(0.5 + (pod_restarts * 0.05), 0.95)
        result['anomaly_type'] = 'crash_loop'
    elif cpu_usage > 90:
        result['predicted_anomaly'] = 1
        result['anomaly_probability'] = min(cpu_usage / 100, 0.95)
        result['anomaly_type'] = 'resource_exhaustion'
    elif memory_usage > 90:
        result['predicted_anomaly'] = 1
        result['anomaly_probability'] = min(memory_usage / 100, 0.95)
        result['anomaly_type'] = 'oom_risk'
    elif ready_containers < total_containers:
        result['predicted_anomaly'] = 1
        result['anomaly_probability'] = 0.8
        result['anomaly_type'] = 'pod_failure'
    
    return result

def predict_anomalies(pod_metrics):
    """
    Predict anomalies in a Kubernetes pod based on its metrics
    
    Args:
        pod_metrics: Dictionary containing pod metrics
        
    Returns:
        Dictionary with prediction results
    """
    if not HAS_TENSORFLOW or model is None:
        # Use rule-based prediction as fallback
        return rule_based_prediction(pod_metrics)
    
    try:
        # Convert metrics to model input format
        # This would need to match your model's expected input format
        input_features = [
            pod_metrics.get('CPU Usage (%)', 0),
            pod_metrics.get('Memory Usage (%)', 0),
            pod_metrics.get('Pod Restarts', 0),
            pod_metrics.get('Memory Usage (MB)', 0),
            pod_metrics.get('Network Receive Bytes', 0),
            pod_metrics.get('Network Transmit Bytes', 0),
            pod_metrics.get('Network Receive Packets Dropped (p/s)', 0),
            pod_metrics.get('Network Transmit Packets Dropped (p/s)', 0),
            pod_metrics.get('Ready Containers', 0)
        ]
        
        # Reshape for model input (assuming time series model)
        X = np.array([input_features]).reshape(1, 1, len(input_features))
        
        # Make prediction
        prediction = model.predict(X)[0]
        
        # Process prediction output
        is_anomaly = prediction[0] > 0.5
        anomaly_type = 'unknown'
        
        # Map prediction to anomaly type (adjust based on your model output)
        if is_anomaly:
            if pod_metrics.get('Pod Restarts', 0) > 5:
                anomaly_type = 'crash_loop'
            elif pod_metrics.get('CPU Usage (%)', 0) > 80:
                anomaly_type = 'resource_exhaustion'
            elif pod_metrics.get('Memory Usage (%)', 0) > 80:
                anomaly_type = 'oom_risk'
            else:
                anomaly_type = 'pod_failure'
        
        return {
            'predicted_anomaly': 1 if is_anomaly else 0,
            'anomaly_probability': float(prediction[0]),
            'anomaly_type': anomaly_type
        }
    except Exception as e:
        logger.error(f"Error in TensorFlow prediction: {e}")
        # Fallback to rule-based prediction on error
        return rule_based_prediction(pod_metrics)

# Test function to verify the module works
def test_prediction():
    """Test the prediction function with sample data"""
    sample_metrics = {
        'CPU Usage (%)': 50.0,
        'Memory Usage (%)': 60.0,
        'Pod Restarts': 0,
        'Memory Usage (MB)': 500.0,
        'Network Receive Bytes': 1000.0,
        'Network Transmit Bytes': 1000.0,
        'Network Receive Packets Dropped (p/s)': 0.0,
        'Network Transmit Packets Dropped (p/s)': 0.0,
        'Ready Containers': 1.0,
        'Total Containers': 1.0
    }
    
    result = predict_anomalies(sample_metrics)
    logger.info(f"Test prediction result: {result}")
    return result

# Run test if executed directly
if __name__ == "__main__":
    test_prediction()