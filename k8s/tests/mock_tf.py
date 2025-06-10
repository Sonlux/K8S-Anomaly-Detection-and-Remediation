#!/usr/bin/env python
"""
Mock TensorFlow module for testing
This provides minimal mocks for TensorFlow objects
"""
import logging
import numpy as np

logger = logging.getLogger("mock-tensorflow")

class MockModel:
    """Mock TensorFlow Keras Model"""
    
    def __init__(self, name="mock_model"):
        self.name = name
    
    def predict(self, x, verbose=0):
        """Mock prediction function that always returns low anomaly scores"""
        logger.info(f"Mock TF model predicting on input shape: {x.shape if hasattr(x, 'shape') else 'unknown'}")
        # Always return 0.1 as anomaly score (below threshold)
        batch_size = x.shape[0] if hasattr(x, 'shape') and len(x.shape) > 0 else 1
        return np.array([[0.1]] * batch_size)
    
    def load_model(self, filepath):
        """Mock load_model function"""
        logger.info(f"Mock loading model from {filepath}")
        return self

# Create module structure
class KerasModels:
    """Mock for keras.models module"""
    
    def load_model(self, filepath):
        """Mock load_model function"""
        logger.info(f"Mock loading model from {filepath}")
        return MockModel()

# Mock for tensorflow.keras
class Keras:
    """Mock for keras module"""
    
    def __init__(self):
        self.models = KerasModels()

# Create module structure
class TensorFlow:
    """Mock for tensorflow module"""
    
    def __init__(self):
        self.keras = Keras()

# Global instance
keras = Keras()
tensorflow = TensorFlow() 