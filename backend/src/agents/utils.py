import logging
import pandas as pd
from typing import Dict, Any
from datetime import datetime

# Configure logger
logger = logging.getLogger("k8s-utils")

def generate_synthetic_metrics() -> Dict[str, Dict[str, Any]]:
    """Generate synthetic metrics for testing when no real data is available."""
    logger.info("Generating synthetic metrics data for testing")
    
    # Create synthetic data for a few pods
    pod_data = {}
    
    # Pod with crash loop issue
    pod_data["frontend-app-1"] = {
        'Pod Name': 'frontend-app-1',
        'namespace': 'default',
        'status': 'Running',
        'node': 'node-1',
        'Pod Restarts': 12,
        'Pod Status': '1/1',
        'Ready Containers': 1,
        'Total Containers': 1,
        'CPU Usage (%)': 5.2,
        'Memory Usage (%)': 35.7,
        'Memory Usage (MB)': 256.5,
        'Network Receive (B/s)': 1024.0,
        'Network Transmit (B/s)': 2048.0,
        'Network Receive Bytes': 1024.0,
        'Network Transmit Bytes': 2048.0,
        'Network Receive Packets Dropped (p/s)': 0.0,
        'Network Transmit Packets Dropped (p/s)': 0.0,
        'FS Reads Total (MB)': 1.5,
        'FS Writes Total (MB)': 0.5,
        'Event Reason': 'BackOff',
        'Event Message': 'Back-off restarting failed container',
        'Event Age (minutes)': 15,
        'Event Count': 8,
        'Pod Event Age': '15m'
    }
    
    # Pod with memory issue
    pod_data["backend-api-2"] = {
        'Pod Name': 'backend-api-2',
        'namespace': 'default',
        'status': 'Running',
        'node': 'node-2',
        'Pod Restarts': 3,
        'Pod Status': '1/1',
        'Ready Containers': 1,
        'Total Containers': 1,
        'CPU Usage (%)': 15.8,
        'Memory Usage (%)': 92.3,
        'Memory Usage (MB)': 768.2,
        'Network Receive (B/s)': 5120.0,
        'Network Transmit (B/s)': 1536.0,
        'Network Receive Bytes': 5120.0,
        'Network Transmit Bytes': 1536.0,
        'Network Receive Packets Dropped (p/s)': 0.0,
        'Network Transmit Packets Dropped (p/s)': 0.0,
        'FS Reads Total (MB)': 3.2,
        'FS Writes Total (MB)': 1.8,
        'Event Reason': 'OOMKilled',
        'Event Message': 'Container exceeded memory limit',
        'Event Age (minutes)': 45,
        'Event Count': 2,
        'Pod Event Age': '45m'
    }
    
    # Pod with network issue
    pod_data["cache-redis-3"] = {
        'Pod Name': 'cache-redis-3',
        'namespace': 'default',
        'status': 'Running',
        'node': 'node-1',
        'Pod Restarts': 1,
        'Pod Status': '1/1',
        'Ready Containers': 1,
        'Total Containers': 1,
        'CPU Usage (%)': 8.3,
        'Memory Usage (%)': 45.2,
        'Memory Usage (MB)': 128.7,
        'Network Receive (B/s)': 256.0,
        'Network Transmit (B/s)': 128.0,
        'Network Receive Bytes': 256.0,
        'Network Transmit Bytes': 128.0,
        'Network Receive Packets Dropped (p/s)': 12.5,
        'Network Transmit Packets Dropped (p/s)': 8.2,
        'FS Reads Total (MB)': 0.5,
        'FS Writes Total (MB)': 0.8,
        'Event Reason': 'NetworkNotReady',
        'Event Message': 'Network interface not ready',
        'Event Age (minutes)': 8,
        'Event Count': 1,
        'Pod Event Age': '8m'
    }
    
    # Pod with no issues
    pod_data["worker-job-4"] = {
        'Pod Name': 'worker-job-4',
        'namespace': 'default',
        'status': 'Running',
        'node': 'node-3',
        'Pod Restarts': 0,
        'Pod Status': '1/1',
        'Ready Containers': 1,
        'Total Containers': 1,
        'CPU Usage (%)': 22.5,
        'Memory Usage (%)': 48.7,
        'Memory Usage (MB)': 384.2,
        'Network Receive (B/s)': 3072.0,
        'Network Transmit (B/s)': 4096.0,
        'Network Receive Bytes': 3072.0,
        'Network Transmit Bytes': 4096.0,
        'Network Receive Packets Dropped (p/s)': 0.0,
        'Network Transmit Packets Dropped (p/s)': 0.0,
        'FS Reads Total (MB)': 2.8,
        'FS Writes Total (MB)': 3.2
    }
    
    return pod_data

def preprocess_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the metrics dataframe to prepare it for analysis.
    
    Args:
        df: Raw metrics dataframe
        
    Returns:
        Processed dataframe ready for anomaly detection
    """
    # Make a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Convert string columns to appropriate numeric types
    numeric_columns = [
        'CPU Usage (%)', 'Memory Usage (%)', 'Pod Restarts',
        'Network Traffic (B/s)', 'Network Receive (B/s)', 'Network Transmit (B/s)',
        'Network Receive Errors', 'Network Transmit Errors'
    ]
    
    for col in numeric_columns:
        if col in processed_df.columns:
            # Convert to float, handling any errors
            try:
                processed_df[col] = pd.to_numeric(processed_df[col], errors='coerce')
            except Exception as e:
                logger.warning(f"Error converting column {col}: {e}")
                processed_df[col] = 0.0
    
    # Extract Ready and Total containers as separate columns
    if 'Ready Containers' not in processed_df.columns and 'Total Containers' not in processed_df.columns:
        # Try to extract from status column if available
        if 'Pod Status' in processed_df.columns:
            try:
                # Format might be "1/1", "2/3", etc.
                status_parts = processed_df['Pod Status'].str.split('/')
                processed_df['Ready Containers'] = status_parts.str[0].astype(float)
                processed_df['Total Containers'] = status_parts.str[1].astype(float)
            except Exception as e:
                logger.warning(f"Could not extract container counts: {e}")
                processed_df['Ready Containers'] = 1
                processed_df['Total Containers'] = 1
    
    # Map required features for the prediction model
    feature_mapping = {
        'Network Receive (B/s)': 'Network Receive Bytes',
        'Network Transmit (B/s)': 'Network Transmit Bytes',
        'Network Receive Errors': 'Network Receive Packets Dropped (p/s)',
        'Network Transmit Errors': 'Network Transmit Packets Dropped (p/s)'
    }
    
    # Add mapped columns
    for source, target in feature_mapping.items():
        if source in processed_df.columns and target not in processed_df.columns:
            processed_df[target] = processed_df[source]
    
    # Add FS metrics if missing (required by model)
    if 'FS Reads Total (MB)' not in processed_df.columns:
        processed_df['FS Reads Total (MB)'] = 0.0
    if 'FS Writes Total (MB)' not in processed_df.columns:
        processed_df['FS Writes Total (MB)'] = 0.0
    
    # Ensure all required features exist
    required_features = [
        'CPU Usage (%)', 'Memory Usage (%)', 'Pod Restarts', 'Memory Usage (MB)',
        'Network Receive Bytes', 'Network Transmit Bytes', 'FS Reads Total (MB)', 
        'FS Writes Total (MB)', 'Network Receive Packets Dropped (p/s)', 
        'Network Transmit Packets Dropped (p/s)', 'Ready Containers'
    ]
    
    for feature in required_features:
        if feature not in processed_df.columns:
            processed_df[feature] = 0.0
    
    return processed_df

def parse_event_age(age_str: str) -> int:
    """
    Parse Kubernetes event age strings into minutes.
    Examples: "10m" -> 10, "2h" -> 120, "1d" -> 1440
    
    Args:
        age_str: Age string from Kubernetes event
        
    Returns:
        Age in minutes
    """
    try:
        if not age_str or pd.isna(age_str) or age_str == 'Unknown':
            return 0
            
        age_str = str(age_str).strip()
        if not age_str:
            return 0
        
        if age_str.endswith('s'):
            return int(age_str[:-1]) // 60  # seconds to minutes
        elif age_str.endswith('m'):
            return int(age_str[:-1])  # already in minutes
        elif age_str.endswith('h'):
            return int(age_str[:-1]) * 60  # hours to minutes
        elif age_str.endswith('d'):
            return int(age_str[:-1]) * 24 * 60  # days to minutes
        else:
            # Try to convert directly to int
            return int(age_str)
    except Exception as e:
        logger.warning(f"Could not parse age '{age_str}': {e}")
        return 0