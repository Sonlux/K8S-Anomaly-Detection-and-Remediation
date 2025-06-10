#!/usr/bin/env python
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import time
import importlib.util
import mock_k8s
import mock_utils

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("test-remediation")

# Path to metrics file
OUTPUT_FILE = 'pod_metrics.csv'
os.environ['OUTPUT_FILE'] = OUTPUT_FILE

# Patch the kubernetes module with our mocks
import sys
import types
try:
    # Mock the kubernetes module
    k8s_module = types.ModuleType('kubernetes')
    k8s_module.client = types.ModuleType('client')
    k8s_module.client.CoreV1Api = mock_k8s.CoreV1Api
    k8s_module.client.AppsV1Api = mock_k8s.AppsV1Api
    k8s_module.client.V1Pod = mock_k8s.V1Pod
    k8s_module.client.V1Container = mock_k8s.V1Container
    k8s_module.client.V1ResourceRequirements = mock_k8s.V1ResourceRequirements
    k8s_module.watch = types.ModuleType('watch')
    k8s_module.watch.Watch = mock_k8s.Watch
    k8s_module.client.rest = types.ModuleType('rest')
    k8s_module.client.rest.ApiException = Exception
    
    # Add mock module to sys.modules
    sys.modules['kubernetes'] = k8s_module
    sys.modules['kubernetes.client'] = k8s_module.client
    sys.modules['kubernetes.watch'] = k8s_module.watch
    
    # Mock the utils module
    utils_module = types.ModuleType('utils')
    utils_module.setup_k8s_client = mock_utils.setup_k8s_client
    utils_module.safe_api_call = mock_utils.safe_api_call
    utils_module.parse_resource_value = mock_utils.parse_resource_value
    utils_module.logger = mock_utils.logger
    
    # Add mock module to sys.modules
    sys.modules['utils'] = utils_module
    
    logger.info("Successfully patched kubernetes and utils modules with mocks")
except Exception as e:
    logger.error(f"Failed to patch modules: {e}")
    import traceback
    traceback.print_exc()

def create_test_metrics_file():
    """Create a test metrics file with some anomalous pods"""
    logger.info(f"Creating test metrics file: {OUTPUT_FILE}")
    
    # Create a DataFrame with sample pod metrics
    data = []
    
    # Normal pod
    data.append({
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Pod Name': 'normal-pod',
        'Namespace': 'default',
        'Pod Status': 'Running',
        'CPU Usage (%)': 30.0,
        'Memory Usage (%)': 40.0,
        'Pod Restarts': 0,
        'Memory Usage (MB)': 200.0,
        'Network Receive (B/s)': 1000.0,
        'Network Transmit (B/s)': 1000.0,
        'Network Receive Errors': 0,
        'Network Transmit Errors': 0,
        'Ready Containers': 1,
        'Total Containers': 1
    })
    
    # Pod with high CPU (resource exhaustion)
    data.append({
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Pod Name': 'cpu-exhausted-pod',
        'Namespace': 'default',
        'Pod Status': 'Running',
        'CPU Usage (%)': 95.0,
        'Memory Usage (%)': 60.0,
        'Pod Restarts': 0,
        'Memory Usage (MB)': 400.0,
        'Network Receive (B/s)': 1000.0,
        'Network Transmit (B/s)': 1000.0,
        'Network Receive Errors': 0,
        'Network Transmit Errors': 0,
        'Ready Containers': 1,
        'Total Containers': 1
    })
    
    # Pod with high memory (OOM risk)
    data.append({
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Pod Name': 'oom-risk-pod',
        'Namespace': 'default',
        'Pod Status': 'Running',
        'CPU Usage (%)': 40.0,
        'Memory Usage (%)': 90.0,
        'Pod Restarts': 0,
        'Memory Usage (MB)': 900.0,
        'Network Receive (B/s)': 1000.0,
        'Network Transmit (B/s)': 1000.0,
        'Network Receive Errors': 0,
        'Network Transmit Errors': 0,
        'Ready Containers': 1,
        'Total Containers': 1
    })
    
    # Pod with restart issues (crash loop)
    data.append({
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Pod Name': 'crash-loop-pod',
        'Namespace': 'default',
        'Pod Status': 'Running',
        'CPU Usage (%)': 30.0,
        'Memory Usage (%)': 40.0,
        'Pod Restarts': 8,
        'Memory Usage (MB)': 200.0,
        'Network Receive (B/s)': 1000.0,
        'Network Transmit (B/s)': 1000.0,
        'Network Receive Errors': 0,
        'Network Transmit Errors': 0,
        'Ready Containers': 1,
        'Total Containers': 1
    })
    
    # Pod with network issues
    data.append({
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'Pod Name': 'network-issue-pod',
        'Namespace': 'default',
        'Pod Status': 'Running',
        'CPU Usage (%)': 30.0,
        'Memory Usage (%)': 40.0,
        'Pod Restarts': 0,
        'Memory Usage (MB)': 200.0,
        'Network Receive (B/s)': 100000.0,
        'Network Transmit (B/s)': 100000.0,
        'Network Receive Errors': 50,
        'Network Transmit Errors': 50,
        'Ready Containers': 1,
        'Total Containers': 1
    })
    
    # Create DataFrame and save to CSV
    df = pd.DataFrame(data)
    
    # Add duplicate rows to simulate sequence data (for LSTM)
    df_copy = df.copy()
    df_copy['Timestamp'] = (datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
    df = pd.concat([df, df_copy], ignore_index=True)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    logger.info(f"Created test metrics file with {len(df)} rows")
    
    return df

def test_fetch_pod_metrics():
    """Test importing metrics collection function"""
    logger.info("Testing get_pod_metrics_from_file function...")
    
    try:
        # Import the function
        import remediation_logic
        
        # Test with a pod that exists
        metrics = remediation_logic.get_pod_metrics_from_file('cpu-exhausted-pod', 'default')
        logger.info(f"Metrics for cpu-exhausted-pod: {metrics}")
        
        # Test with a pod that doesn't exist
        metrics = remediation_logic.get_pod_metrics_from_file('nonexistent-pod', 'default')
        logger.info(f"Metrics for nonexistent-pod: {metrics}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing fetch_pod_metrics: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_remediate_pod():
    """Test pod remediation function"""
    logger.info("Testing pod remediation function...")
    
    try:
        # Import remediation_logic
        import remediation_logic
        
        # Create a remediation instance
        remediation = remediation_logic.K8sRemediation(
            cooldown_period=10,  # Short cooldown for testing
            confidence_threshold=0.5  # Lower threshold for testing
        )
        
        # Create prediction for a resource exhaustion issue
        prediction = {
            'resource_type': 'pod',
            'resource_name': 'cpu-exhausted-pod',
            'namespace': 'default',
            'issue_type': 'resource_exhaustion',
            'confidence': 0.9,
            'metrics': {
                'CPU Usage (%)': 95.0,
                'Memory Usage (%)': 60.0,
                'Pod Restarts': 0,
                'Memory Usage (MB)': 400.0,
                'Network Receive Bytes': 1000.0,
                'Network Transmit Bytes': 1000.0,
                'FS Reads Total (MB)': 0.0,
                'FS Writes Total (MB)': 0.0,
                'Network Receive Packets Dropped (p/s)': 0.0,
                'Network Transmit Packets Dropped (p/s)': 0.0,
                'Ready Containers': 1.0
            }
        }
        
        # Test remediation
        result = remediation.remediate_issue(prediction)
        logger.info(f"Remediation result: {result}")
        
        # Now test with a pod from the CSV file
        logger.info("Testing with a pod from CSV file")
        pod = mock_k8s.V1Pod(name="cpu-exhausted-pod", namespace="default")
        metrics = remediation._fetch_pod_metrics(pod)
        logger.info(f"Fetched metrics: {metrics}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing remediate_pod: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_monitor_cluster():
    """Test monitor_cluster function with mock K8s API"""
    logger.info("Testing monitor_cluster function...")
    
    try:
        # Import remediation_logic
        import remediation_logic
        
        # Create a remediation instance
        remediation = remediation_logic.K8sRemediation(
            cooldown_period=10,  # Short cooldown for testing
            confidence_threshold=0.5  # Lower threshold for testing
        )
        
        # Add our test pods to the mock K8s API
        for pod_name in ['cpu-exhausted-pod', 'oom-risk-pod', 'crash-loop-pod', 'network-issue-pod']:
            pod = mock_k8s.V1Pod(name=pod_name, namespace="default")
            remediation.k8s_api.pods[f"default/{pod_name}"] = pod
        
        # Set sequence_length to 1 for quicker testing
        remediation_logic.sequence_length = 1
        
        # Run monitor_cluster in a separate thread to avoid blocking
        import threading
        def run_monitor():
            try:
                remediation.monitor_cluster(interval=1)
            except Exception as e:
                logger.error(f"Error in monitor_cluster: {e}")
                import traceback
                traceback.print_exc()
        
        thread = threading.Thread(target=run_monitor)
        thread.daemon = True
        thread.start()
        
        # Give it a moment to process
        time.sleep(3)
        
        logger.info("Monitor cluster test completed")
        return True
    except Exception as e:
        logger.error(f"Error testing monitor_cluster: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    logger.info("Starting remediation logic test")
    
    # Create test metrics file
    try:
        create_test_metrics_file()
    except Exception as e:
        logger.error(f"Error creating test metrics file: {str(e)}")
        return False
    
    # Test fetch_pod_metrics
    if not test_fetch_pod_metrics():
        logger.error("Failed to test fetch_pod_metrics")
        return False
    
    # Test remediate_pod
    if not test_remediate_pod():
        logger.error("Failed to test remediate_pod")
        return False
    
    # Test monitor_cluster
    if not test_monitor_cluster():
        logger.error("Failed to test monitor_cluster")
        return False
    
    logger.info("All tests completed successfully")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 