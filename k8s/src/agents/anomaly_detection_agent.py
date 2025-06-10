import os
import sys
import time
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import json
import tempfile
import shutil
import portalocker
import subprocess
from typing import Dict, List, Any, Tuple, Optional

# Configure logger first to avoid duplicate handlers
logger = logging.getLogger("anomaly-detection-agent")
# Check if handlers are already configured to avoid duplicates
if not logger.handlers:
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Add console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler with absolute path
    log_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'logs'))
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, 'anomaly_detection_agent.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    logger.setLevel(logging.INFO)
    logger.info(f"Logging configured to file: {log_file}")

# Check for required packages
try:
    import portalocker
except ImportError:
    logger.error("portalocker module not found. Please install with: pip install portalocker")
    sys.exit(1)

# Import the anomaly prediction model with robust error handling
# Use absolute path to the models directory
models_path = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../models'))
sys.path.insert(0, models_path)  # Insert at beginning of path for priority

try:
    from anomaly_prediction import predict_anomalies
    logger.info(f"Successfully imported anomaly_prediction from {models_path}")
except ImportError as e:
    logger.warning(f"Could not import anomaly_prediction module: {e}")
    
    # As a fallback, try direct import if the file exists
    model_file = os.path.join(models_path, 'anomaly_prediction.py')
    if os.path.exists(model_file):
        logger.info(f"Found model file at {model_file}, loading directly")
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("anomaly_prediction", model_file)
            model_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(model_module)
            predict_anomalies = model_module.predict_anomalies
            logger.info("Successfully loaded predict_anomalies function")
        except Exception as imp_err:
            logger.error(f"Failed to import the model module: {imp_err}")
            # Define a stub function for testing
            def predict_anomalies(data):
                logger.warning("Using stub prediction function due to import failure")
                return pd.DataFrame({
                    'predicted_anomaly': [0],
                    'anomaly_probability': [0.1],
                    'anomaly_type': ['unknown']
                })
    else:
        # Define a stub function for testing
        logger.error(f"Model file not found at {model_file}, using stub function")
        def predict_anomalies(data):
            logger.warning("Using stub prediction function due to missing model file")
            return pd.DataFrame({
                'predicted_anomaly': [0],
                'anomaly_probability': [0.1],
                'anomaly_type': ['unknown']
            })

# Import NVIDIA LLM if available
try:
    nvidia_llm_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nvidia_llm.py')
    if os.path.exists(nvidia_llm_path):
        import importlib.util
        spec = importlib.util.spec_from_file_location("nvidia_llm", nvidia_llm_path)
        nvidia_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(nvidia_module)
        NvidiaLLM = nvidia_module.NvidiaLLM
        logger.info(f"Successfully imported NvidiaLLM from {nvidia_llm_path}")
    else:
        logger.warning(f"NVIDIA LLM module not found at {nvidia_llm_path}")
        NvidiaLLM = None
except Exception as e:
    logger.warning(f"Could not import NVIDIA LLM module: {e}")
    NvidiaLLM = None

class FileLocker:
    """Class to handle file locking for safe concurrent access"""
    
    @staticmethod
    def acquire_lock(file_path, timeout=10):
        """
        Acquire a lock on a file
        
        Args:
            file_path: Path to the file to lock
            timeout: Maximum time to wait for lock in seconds
            
        Returns:
            File handle that holds the lock
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
            # Create lock file if it doesn't exist
            lock_file = file_path + ".lock"
            if not os.path.exists(lock_file):
                with open(lock_file, 'w') as f:
                    pass
                
            # Acquire lock with timeout
            lock_handle = open(lock_file, 'r+')
            
            # Use portalocker for Windows compatibility
            start_time = time.time()
            while True:
                try:
                    portalocker.lock(lock_handle, portalocker.LOCK_EX | portalocker.LOCK_NB)
                    return lock_handle
                except (portalocker.LockException, IOError):
                    if time.time() - start_time > timeout:
                        logger.error(f"Timeout waiting for lock on {file_path}")
                        lock_handle.close()
                        return None
                    time.sleep(0.1)
                    
        except Exception as e:
            logger.error(f"Error acquiring lock for {file_path}: {e}")
            return None
    
    @staticmethod
    def release_lock(lock_handle):
        """
        Release a lock on a file
        
        Args:
            lock_handle: File handle that holds the lock
        """
        if lock_handle:
            try:
                portalocker.unlock(lock_handle)
                lock_handle.close()
            except Exception as e:
                logger.error(f"Error releasing lock: {e}")

# Update requirements.txt to add portalocker
try:
    requirements_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r') as f:
            requirements = f.read()
        
        if 'portalocker' not in requirements:
            with open(requirements_path, 'a') as f:
                f.write('\nportalocker>=2.7.0\n')
            logger.info("Added portalocker to requirements.txt")
except Exception as e:
    logger.error(f"Could not update requirements.txt: {e}")

class AnomalyDetectionAgent:
    """Agent for detecting anomalies in Kubernetes metrics data"""
    
    def __init__(self, 
                 alert_threshold: float = 0.7,
                 history_window: int = 60,
                 data_dir: str = None,
                 use_nvidia_llm: bool = False):
        """
        Initialize the anomaly detection agent.
        
        Args:
            alert_threshold: Probability threshold for anomaly alerts
            history_window: Number of minutes of history to maintain
            data_dir: Directory to store data files (defaults to project root)
            use_nvidia_llm: Whether to use NVIDIA LLM for enhanced analysis
        """
        self.alert_threshold = alert_threshold
        self.history_window = history_window
        self.use_nvidia_llm = use_nvidia_llm
        
        # Initialize NVIDIA LLM if requested
        self.nvidia_llm = None
        if use_nvidia_llm:
            if NvidiaLLM is not None:
                try:
                    self.nvidia_llm = NvidiaLLM()
                    logger.info("NVIDIA LLM client initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize NVIDIA LLM: {e}")
            else:
                logger.error("NVIDIA LLM module not available")
                
        # Setup data directory
        if data_dir:
            self.data_dir = os.path.abspath(data_dir)
        else:
            self.data_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..', 'data'))
        
        # Create data directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize data structures
        self.pod_metrics = {}  # Store latest metrics for each pod
        self.anomaly_history = {}  # Store anomaly history for each pod
        
        logger.info(f"Initialized AnomalyDetectionAgent with "
                   f"alert_threshold={alert_threshold}, "
                   f"data_dir={self.data_dir}")
        
        # Check model availability
        try:
            # Create a simple test dataframe
            test_df = pd.DataFrame({
                'CPU Usage (%)': [0.5],
                'Memory Usage (%)': [0.5],
                'Pod Restarts': [0],
                'Memory Usage (MB)': [100],
                'Network Receive Bytes': [100],
                'Network Transmit Bytes': [100],
                'FS Reads Total (MB)': [0.1],
                'FS Writes Total (MB)': [0.1],
                'Network Receive Packets Dropped (p/s)': [0],
                'Network Transmit Packets Dropped (p/s)': [0],
                'Ready Containers': [1],
                'Pod Name': ['test-pod']  # Add required column
            })
            
            # Test the model
            result = predict_anomalies(test_df)
            logger.info(f"Model test successful: {result.iloc[0].to_dict()}")
        except Exception as e:
            logger.error(f"Model test failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    def detect_anomalies(self, pod_history: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
        """
        Run anomaly detection on pod history data.
        
        Args:
            pod_history: Dictionary mapping pod names to lists of metric dictionaries
            
        Returns:
            Dictionary of pod names to anomaly results
        """
        results = {}
        
        if not pod_history:
            logger.warning("Empty pod history provided, skipping anomaly detection")
            return results
            
        for pod_name, history in pod_history.items():
            # Skip if no history
            if not history:
                continue
                
            # Store the latest metrics for reference
            self.pod_metrics[pod_name] = history[-1] if history else {}
            
            try:
                # Create a dataframe from pod history
                pod_df = pd.DataFrame(history)
                
                # Validate required columns
                required_columns = ['Pod Name', 'CPU Usage (%)', 'Memory Usage (%)']
                missing_columns = [col for col in required_columns if col not in pod_df.columns]
                if missing_columns:
                    logger.warning(f"Pod {pod_name} missing required columns: {missing_columns}, skipping")
                    continue
                
                # Run anomaly detection
                try:
                    prediction_df = predict_anomalies(pod_df)
                    prediction = prediction_df.iloc[0].to_dict()
                    
                    # Add timestamp and pod name
                    prediction['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    prediction['pod_name'] = pod_name
                    
                    # Add to results
                    results[pod_name] = prediction
                    
                    # Update anomaly history
                    if pod_name not in self.anomaly_history:
                        self.anomaly_history[pod_name] = []
                    self.anomaly_history[pod_name].append(prediction)
                    
                    # Trim anomaly history to keep only recent entries
                    if len(self.anomaly_history[pod_name]) > 100:
                        self.anomaly_history[pod_name] = self.anomaly_history[pod_name][-100:]
                    
                    # Log anomalies
                    if prediction['predicted_anomaly']:
                        logger.warning(
                            f"Anomaly detected in pod {pod_name}: "
                            f"type={prediction['anomaly_type']}, "
                            f"probability={prediction['anomaly_probability']:.4f}"
                        )
                    
                except Exception as e:
                    logger.error(f"Error in prediction for pod {pod_name}: {e}")
                    import traceback
                    logger.error(traceback.format_exc())
                
            except Exception as e:
                logger.error(f"Error processing history for pod {pod_name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        return results
    
    def generate_insights(self, anomalies: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate insights based on detected anomalies.
        
        Args:
            anomalies: Dictionary of pod names to anomaly results
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        if not anomalies:
            return insights
            
        # Process each anomaly
        for pod_name, prediction in anomalies.items():
            try:
                # Skip non-anomalies below threshold
                if not prediction['predicted_anomaly'] and prediction['anomaly_probability'] < self.alert_threshold:
                    continue
                    
                # Get pod metrics
                metrics = self.pod_metrics.get(pod_name, {})
                
                # Generate insight based on anomaly type and metrics
                insight = {
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'pod_name': pod_name,
                    'is_anomaly': bool(prediction['predicted_anomaly']),
                    'anomaly_type': prediction['anomaly_type'],
                    'anomaly_probability': float(prediction['anomaly_probability']),
                    'severity': self._calculate_severity(prediction, metrics),
                    'recommendation': self._generate_recommendation(prediction, metrics)
                }
                
                # Add insight metadata
                if 'Node Name' in metrics:
                    insight['node_name'] = metrics['Node Name']
                if 'Pod Status' in metrics:
                    insight['pod_status'] = metrics['Pod Status']
                if 'Pod Restarts' in metrics:
                    insight['pod_restarts'] = metrics['Pod Restarts']
                if 'Pod Event Reason' in metrics:
                    insight['event_reason'] = metrics['Pod Event Reason']
                if 'Pod Event Age' in metrics:
                    insight['event_age'] = metrics['Pod Event Age']
                
                # Use NVIDIA LLM for enhanced analysis if available
                if self.nvidia_llm and self.use_nvidia_llm:
                    try:
                        logger.info(f"Generating enhanced analysis using NVIDIA LLM for pod {pod_name}")
                        metrics_str = json.dumps(metrics, indent=2)
                        prediction_str = json.dumps(prediction, indent=2)
                        enhanced_analysis = self.nvidia_llm.analyze_k8s_metrics(metrics_str, prediction_str)
                        
                        # Add enhanced analysis to insight
                        insight['enhanced_analysis'] = enhanced_analysis
                        insight['ai_generated'] = True
                        
                        # Extract specific recommendations from enhanced analysis
                        recommendation_section = self._extract_recommendations(enhanced_analysis)
                        if recommendation_section:
                            insight['enhanced_recommendation'] = recommendation_section
                            
                        logger.info(f"Enhanced analysis generated for pod {pod_name}")
                    except Exception as e:
                        logger.error(f"Error generating enhanced analysis for pod {pod_name}: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                
                insights.append(insight)
                
                # Log the insight
                if insight['is_anomaly']:
                    logger.warning(
                        f"Insight for {pod_name}: {insight['anomaly_type']} anomaly, "
                        f"severity={insight['severity']}, "
                        f"recommendation: {insight['recommendation']}"
                    )
                elif insight['anomaly_probability'] >= self.alert_threshold:
                    logger.info(
                        f"Potential issue for {pod_name}: probability={insight['anomaly_probability']:.4f}, "
                        f"recommendation: {insight['recommendation']}"
                    )
            except Exception as e:
                logger.error(f"Error generating insight for pod {pod_name}: {e}")
                import traceback
                logger.error(traceback.format_exc())
        
        return insights
    
    def _calculate_severity(self, prediction: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """
        Calculate severity level based on anomaly prediction and metrics.
        
        Args:
            prediction: Anomaly prediction dictionary
            metrics: Pod metrics dictionary
            
        Returns:
            Severity level (Critical, High, Medium, Low)
        """
        # Start with default severity
        if not prediction['predicted_anomaly']:
            return 'Low'
            
        # Base severity on anomaly probability
        prob = float(prediction['anomaly_probability'])
        if prob >= 0.9:
            severity = 'Critical'
        elif prob >= 0.8:
            severity = 'High'
        elif prob >= 0.6:
            severity = 'Medium'
        else:
            severity = 'Low'
            
        # Safely get metrics values with defaults
        restarts = float(metrics.get('Pod Restarts', 0)) if metrics.get('Pod Restarts') is not None else 0
        cpu_usage = float(metrics.get('CPU Usage (%)', 0)) if metrics.get('CPU Usage (%)') is not None else 0
            
        # Adjust based on anomaly type
        anomaly_type = prediction['anomaly_type']
        if anomaly_type == 'crash_loop' and restarts > 10:
            severity = 'Critical'
        elif anomaly_type == 'oom_kill':
            severity = 'High'
        elif anomaly_type == 'resource_exhaustion' and cpu_usage > 95:
            severity = 'High'
            
        # Adjust based on event age
        event_age_minutes = 0
        if 'Event Age (minutes)' in metrics:
            event_age_minutes = float(metrics['Event Age (minutes)'])
        elif 'Pod Event Age' in metrics:
            # Try to parse from string (e.g., "5m" -> 5)
            try:
                age_str = str(metrics['Pod Event Age'])
                if age_str.endswith('m'):
                    event_age_minutes = int(age_str[:-1])
                elif age_str.endswith('h'):
                    event_age_minutes = int(age_str[:-1]) * 60
                elif age_str.endswith('d'):
                    event_age_minutes = int(age_str[:-1]) * 24 * 60
            except Exception:
                pass
        
        # Recent events are more concerning
        if event_age_minutes < 5 and severity != 'Critical':
            severity = 'High'  # Elevate recent events
        elif event_age_minutes > 120 and severity == 'Critical':
            severity = 'High'  # Long-standing issues may be less urgent
            
        return severity
    
    def _generate_recommendation(self, prediction: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """
        Generate a recommendation based on the anomaly prediction and pod metrics.
        
        Args:
            prediction: Anomaly prediction dictionary
            metrics: Pod metrics dictionary
            
        Returns:
            Recommendation string
        """
        anomaly_type = prediction['anomaly_type']
        recommendations = []
        
        # Generate recommendations based on anomaly type
        if anomaly_type == 'crash_loop':
            recommendations.append("Check container logs for application errors")
            recommendations.append("Verify that container image and startup commands are correct")
            recommendations.append("Ensure the pod has sufficient resources to start")
            if metrics.get('Pod Restarts', 0) > 20:
                recommendations.append("Consider setting appropriate liveness/readiness probes")
                
        elif anomaly_type == 'oom_kill':
            recommendations.append("Increase memory limits in pod specification")
            recommendations.append("Check for memory leaks in the application")
            recommendations.append("Optimize memory usage in the container")
            
        elif anomaly_type == 'resource_exhaustion':
            recommendations.append("Scale the deployment horizontally with more replicas")
            recommendations.append("Increase CPU limits/requests for the pod")
            recommendations.append("Check for potential CPU-intensive operations or loops")
            
        elif anomaly_type == 'network_issue':
            recommendations.append("Check network policies and ensure proper connectivity")
            recommendations.append("Verify DNS resolution within the cluster")
            recommendations.append("Check for network congestion or bandwidth issues")
            
        elif anomaly_type == 'partial_failure':
            recommendations.append("Check if init containers are completing successfully")
            recommendations.append("Verify all required container volumes and configmaps exist")
            recommendations.append("Check if service dependencies are available")
            
        elif anomaly_type == 'io_issue':
            recommendations.append("Check disk space and inode usage on the node")
            recommendations.append("Verify persistent volume claims are bound correctly")
            recommendations.append("Consider optimizing I/O operations in the application")
            
        else:
            # Generic recommendations
            recommendations.append("Check pod logs for error messages")
            recommendations.append("Verify pod configuration and dependencies")
            recommendations.append("Check node health and resource availability")
        
        # Get event-specific recommendations
        event_reason = metrics.get('Pod Event Reason', '')
        if event_reason:
            if event_reason == 'BackOff':
                recommendations.append("Check container logs for application errors causing restarts")
            elif event_reason == 'Failed':
                recommendations.append("Verify node resources and pod resource requirements")
            elif event_reason == 'Unhealthy':
                recommendations.append("Check readiness/liveness probe configuration")
            elif event_reason == 'FailedScheduling':
                recommendations.append("Check for resource constraints or node affinity issues")
        
        # Select top 3 most relevant recommendations
        if len(recommendations) > 3:
            recommendations = recommendations[:3]
        
        return "; ".join(recommendations)
    
    def _extract_recommendations(self, analysis_text: str) -> str:
        """Extract recommendation section from LLM analysis text.
        
        Args:
            analysis_text: Full text of the LLM analysis
            
        Returns:
            Extracted recommendation section or empty string if not found
        """
        try:
            # Try to find recommendations section
            lower_text = analysis_text.lower()
            
            # Look for common section markers
            markers = [
                "recommendations:", "recommended actions:", "actionable steps:",
                "3. specific, actionable recommendations", "to resolve the issue:"
            ]
            
            for marker in markers:
                if marker in lower_text:
                    start_idx = lower_text.find(marker) + len(marker)
                    # Find the next section header (number followed by period or newline)
                    next_section = None
                    for idx in range(start_idx, len(lower_text)):
                        if idx + 2 < len(lower_text) and lower_text[idx].isdigit() and lower_text[idx+1] == '.' and (lower_text[idx+2].isspace() or lower_text[idx+2] == '\n'):
                            next_section = idx
                            break
                    
                    if next_section:
                        return analysis_text[start_idx:next_section].strip()
                    else:
                        # If no next section found, take the rest of the text
                        return analysis_text[start_idx:].strip()
            
            # If no section found, return the last paragraph which often contains recommendations
            paragraphs = analysis_text.split('\n\n')
            if paragraphs:
                return paragraphs[-1].strip()
                
            return ""
        except Exception as e:
            logger.error(f"Error extracting recommendations: {e}")
            return ""
    
    def output_insights(self, insights: List[Dict[str, Any]], output_file: str = None) -> None:
        """
        Output insights to a JSON file with proper file locking.
        
        Args:
            insights: List of insight dictionaries
            output_file: Path to the output file (absolute or relative to data_dir)
        """
        if not insights:
            return
        
        # Resolve output file path
        if not output_file:
            output_file = os.path.join(self.data_dir, 'pod_insights.json')
        elif not os.path.isabs(output_file):
            output_file = os.path.join(self.data_dir, output_file)
            
        # Ensure directory exists
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
            
        # Acquire lock
        lock_handle = FileLocker.acquire_lock(output_file)
        if not lock_handle:
            logger.error(f"Could not acquire lock on {output_file}, skipping write")
            return
            
        try:
            # Use a temporary file to avoid corruption
            with tempfile.NamedTemporaryFile('w', delete=False) as temp_file:
                # Read existing insights
                existing_insights = []
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    try:
                        with open(output_file, 'r') as f:
                            existing_insights = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning(f"Could not parse existing insights file {output_file}, creating new file")
                
                # Add new insights
                all_insights = existing_insights + insights
                
                # Keep only the latest 100 insights
                if len(all_insights) > 100:
                    all_insights = all_insights[-100:]
                
                # Write to temporary file
                json.dump(all_insights, temp_file, indent=2)
                temp_file_path = temp_file.name
                
            # Replace the original file with the temporary file
            shutil.move(temp_file_path, output_file)
                
            logger.info(f"Wrote {len(insights)} new insights to {output_file}")
                
        except Exception as e:
            logger.error(f"Error writing insights to {output_file}: {e}")
            import traceback
            logger.error(traceback.format_exc())
        finally:
            # Release lock
            FileLocker.release_lock(lock_handle)
    
    def process_metrics_file(self, input_file: str, output_file: str = None) -> None:
        """
        Process a metrics file and generate insights.
        
        Args:
            input_file: Path to the input CSV file
            output_file: Path to the output JSON file
        """
        # Resolve input file path
        if not os.path.isabs(input_file):
            input_file = os.path.join(self.data_dir, input_file)
            
        try:
            # Check if file exists
            if not os.path.exists(input_file):
                logger.error(f"Input file {input_file} does not exist")
                return
                
            # Read the file
            df = pd.read_csv(input_file)
            logger.info(f"Loaded {len(df)} rows from {input_file}")
            
            if df.empty:
                logger.warning(f"No data in {input_file}")
                return
                
            # Check for required column
            if 'Pod Name' not in df.columns:
                logger.error(f"Required column 'Pod Name' not found in {input_file}")
                return
                
            # Group by pod name
            pod_history = {}
            for pod_name, pod_df in df.groupby('Pod Name'):
                pod_history[pod_name] = pod_df.to_dict('records')
                
            # Detect anomalies
            anomalies = self.detect_anomalies(pod_history)
            
            # Generate insights
            insights = self.generate_insights(anomalies)
            
            # Output insights
            self.output_insights(insights, output_file)
            
        except Exception as e:
            logger.error(f"Error processing metrics file {input_file}: {e}")
            import traceback
            logger.error(traceback.format_exc())

def run_dataset_generator(prometheus_url=None, namespace=None, output_file=None, interval=None):
    """
    Run the dataset-generator.py script as a subprocess.
    
    Args:
        prometheus_url: URL of the Prometheus server
        namespace: Kubernetes namespace to monitor
        output_file: Output file path for metrics
        interval: Collection interval in seconds
        
    Returns:
        Subprocess object for the running generator
    """
    try:
        # Find the dataset-generator.py script
        project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
        generator_script = os.path.join(project_root, 'dataset-generator.py')
        
        if not os.path.exists(generator_script):
            logger.error(f"Could not find dataset-generator.py at {generator_script}")
            return None
            
        # Build command arguments
        cmd = [sys.executable, generator_script]
        
        if prometheus_url:
            cmd.extend(['--prometheus-url', prometheus_url])
            
        if namespace:
            cmd.extend(['--namespace', namespace])
            
        if output_file:
            cmd.extend(['--output-file', output_file])
            
        if interval:
            cmd.extend(['--interval', str(interval)])
            
        # Environment variables for the generator
        env = os.environ.copy()
        if prometheus_url:
            env['PROMETHEUS_URL'] = prometheus_url
        if namespace:
            env['NAMESPACE'] = namespace
        if output_file:
            env['OUTPUT_FILE'] = output_file
        if interval:
            env['SLEEP_INTERVAL'] = str(interval)
            
        # Start the generator process
        logger.info(f"Starting dataset generator with command: {' '.join(cmd)}")
        process = subprocess.Popen(
            cmd, 
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Start a thread to log the generator output
        import threading
        def log_output(process):
            for line in process.stdout:
                logger.info(f"Generator: {line.strip()}")
                
        thread = threading.Thread(target=log_output, args=(process,))
        thread.daemon = True
        thread.start()
        
        return process
        
    except Exception as e:
        logger.error(f"Error starting dataset generator: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Add a main function for standalone testing
def main():
    """Run the anomaly detection agent as a standalone script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run anomaly detection agent on pod metrics',
        epilog='Example: python anomaly_detection_agent.py --input-file ../../pod_metrics.csv --use-nvidia-llm'
    )
    parser.add_argument('--input-file', type=str, default='pod_metrics.csv',
                        help='Input metrics CSV file (absolute path or relative to data directory)')
    parser.add_argument('--output-file', type=str, default='pod_insights.json',
                        help='Output insights JSON file (absolute path or relative to data directory)')
    parser.add_argument('--alert-threshold', type=float, default=0.7,
                        help='Probability threshold for anomaly alerts (default: 0.7)')
    parser.add_argument('--data-dir', type=str, default=None,
                        help='Directory for data files (default: K8S/data)')
    parser.add_argument('--test', action='store_true',
                        help='Run a quick test of the agent without processing any files')
    parser.add_argument('--run-generator', action='store_true',
                        help='Run the dataset-generator.py script to collect metrics')
    parser.add_argument('--prometheus-url', type=str, default='http://localhost:8082',
                        help='Prometheus URL for data collection (default: http://localhost:8082)')
    parser.add_argument('--namespace', type=str, default='monitoring',
                        help='Kubernetes namespace to monitor (default: monitoring)')
    parser.add_argument('--generator-interval', type=int, default=5,
                        help='Interval in seconds for metrics collection (default: 5)')
    parser.add_argument('--watch', action='store_true',
                        help='Watch for file changes and continuously process new data')
    parser.add_argument('--watch-interval', type=int, default=10,
                        help='Interval in seconds between file checks when watching (default: 10)')
    parser.add_argument('--use-nvidia-llm', action='store_true',
                        help='Use NVIDIA LLM API for enhanced anomaly analysis')
    
    args = parser.parse_args()
    
    try:
        # Create the agent with NVIDIA LLM if requested
        agent = AnomalyDetectionAgent(
            alert_threshold=args.alert_threshold,
            data_dir=args.data_dir,
            use_nvidia_llm=args.use_nvidia_llm
        )
        
        # If test mode, just exit
        if args.test:
            logger.info("Test mode: agent initialized successfully")
            return
            
        # Run dataset generator if requested
        generator_process = None
        if args.run_generator:
            logger.info("Starting dataset generator to collect metrics")
            generator_process = run_dataset_generator(
                prometheus_url=args.prometheus_url,
                namespace=args.namespace,
                output_file=args.input_file,
                interval=args.generator_interval
            )
            
            if generator_process:
                logger.info("Dataset generator started successfully")
                # Give it some time to collect initial data
                logger.info("Waiting 10 seconds for initial data collection...")
                time.sleep(10)
            else:
                logger.error("Failed to start dataset generator")
                
        # Check for project root pod_metrics.csv if no file is specified
        if args.input_file == 'pod_metrics.csv' and not os.path.exists(args.input_file):
            project_root_file = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../pod_metrics.csv'))
            if os.path.exists(project_root_file):
                logger.info(f"Using project root pod_metrics.csv: {project_root_file}")
                args.input_file = project_root_file
        
        # Ensure input file exists
        input_file = args.input_file
        if not os.path.isabs(input_file):
            input_file = os.path.join(agent.data_dir, input_file)
            
        if not args.run_generator and not os.path.exists(input_file):
            logger.error(f"Input file not found: {input_file}")
            logger.error("Please specify a valid input file with --input-file")
            logger.error("You can run with --test to verify the agent is working correctly")
            logger.error("Or use --run-generator to collect metrics automatically")
            sys.exit(1)
            
        if args.watch:
            logger.info(f"Watching for changes to {input_file} every {args.watch_interval} seconds")
            last_mtime = 0
            last_position = 0
            
            try:
                while True:
                    if os.path.exists(input_file):
                        current_mtime = os.path.getmtime(input_file)
                        if current_mtime > last_mtime:
                            logger.info(f"File {input_file} has been updated, processing...")
                            last_mtime = current_mtime
                            
                            # Process only the new data
                            try:
                                df = pd.read_csv(input_file)
                                if len(df) > last_position:
                                    new_df = df.iloc[last_position:]
                                    last_position = len(df)
                                    
                                    logger.info(f"Processing {len(new_df)} new rows")
                                    
                                    # Group by pod name
                                    pod_history = {}
                                    for pod_name, pod_df in new_df.groupby('Pod Name'):
                                        pod_history[pod_name] = pod_df.to_dict('records')
                                        
                                    # Detect anomalies
                                    anomalies = agent.detect_anomalies(pod_history)
                                    
                                    # Generate insights
                                    insights = agent.generate_insights(anomalies)
                                    
                                    # Output insights
                                    agent.output_insights(insights, args.output_file)
                                else:
                                    logger.debug("No new rows to process")
                            except Exception as e:
                                logger.error(f"Error processing file: {e}")
                                import traceback
                                logger.error(traceback.format_exc())
                    
                    time.sleep(args.watch_interval)
                    
            except KeyboardInterrupt:
                logger.info("Watch mode stopped by user")
            finally:
                # Clean up the generator process if it's running
                if generator_process and generator_process.poll() is None:
                    logger.info("Stopping dataset generator...")
                    generator_process.terminate()
                    generator_process.wait(timeout=5)
                    logger.info("Dataset generator stopped")
        else:
            # Process the metrics file once
            logger.info(f"Processing {input_file}")
            agent.process_metrics_file(args.input_file, args.output_file)
            
            # Clean up the generator if it was started
            if generator_process and generator_process.poll() is None:
                logger.info("Stopping dataset generator...")
                generator_process.terminate()
                generator_process.wait(timeout=5)
                logger.info("Dataset generator stopped")
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 