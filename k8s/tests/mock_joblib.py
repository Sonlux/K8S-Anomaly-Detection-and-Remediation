#!/usr/bin/env python
"""
Mock joblib module for testing
"""
import logging
import numpy as np

logger = logging.getLogger("mock-joblib")

class MockScaler:
    """Mock scaler similar to MinMaxScaler"""
    
    def transform(self, X):
        """Mock transform that returns values between 0 and 1"""
        logger.info(f"Mock scaler transforming data with shape: {X.shape if hasattr(X, 'shape') else 'unknown'}")
        if isinstance(X, np.ndarray):
            # Simply normalize by dividing by 100 (assuming typical metric values)
            return X / 100.0
        else:
            # Convert to numpy array first
            try:
                X_arr = np.array(X)
                return X_arr / 100.0
            except:
                logger.warning("Could not convert input to numpy array, returning zeros")
                return np.zeros((1, 1))

def load(filepath):
    """Mock joblib.load function"""
    logger.info(f"Mock loading from {filepath}")
    
    if 'scaler' in filepath:
        return MockScaler()
    elif 'threshold' in filepath:
        return 0.8  # Return a threshold value
    else:
        return None 