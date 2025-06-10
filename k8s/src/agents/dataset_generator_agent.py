import os
import sys
import time
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
import argparse
import json
from typing import Dict, List, Any, Tuple, Optional

# Import the anomaly detection agent
anomaly_agent_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'anomaly_detection_agent.py')
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("anomaly_detection_agent", anomaly_agent_path)
    anomaly_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(anomaly_module)
    AnomalyDetectionAgent = anomaly_module.AnomalyDetectionAgent
    print(f"Successfully imported AnomalyDetectionAgent from {anomaly_agent_path}")
except ImportError as e:
    print(f"Warning: Could not import AnomalyDetectionAgent: {e}")
    # We'll handle this case later

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('dataset_generator_agent.log')
    ]
)
logger = logging.getLogger("dataset-generator-agent")

class DatasetGeneratorAgent:
    """Agent for monitoring and analyzing Kubernetes metrics data"""
    
    def __init__(self, 
                 input_file: str = 'pod_metrics.csv',
                 watch_interval: int = 10,
                 alert_threshold: float = 0.7,
                 history_window: int = 60):
        """
        Initialize the dataset generator agent.
        
        Args:
            input_file: Path to the CSV file to monitor
            watch_interval: Interval in seconds between checks
            alert_threshold: Probability threshold for anomaly alerts
            history_window: Number of minutes of history to maintain
        """
        # Resolve input file path
        if input_file == 'pod_metrics.csv' and not os.path.isabs(input_file):
            # First check the current directory
            if os.path.exists(input_file):
                self.input_file = os.path.abspath(input_file)
            else:
                # Try the project root
                project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
                project_root_file = os.path.join(project_root, input_file)
                
                if os.path.exists(project_root_file):
                    logger.info(f"Found input file in project root: {project_root_file}")
                    self.input_file = project_root_file
                else:
                    # Try data directory in project root
                    data_dir = os.path.join(project_root, 'data')
                    data_file = os.path.join(data_dir, input_file)
                    
                    if os.path.exists(data_file):
                        logger.info(f"Found input file in data directory: {data_file}")
                        self.input_file = data_file
                    else:
                        # Use the original path, which will generate warnings if not found
                        logger.warning(f"Could not locate input file {input_file} in common locations")
                        self.input_file = input_file
        else:
            self.input_file = input_file
            
        self.watch_interval = watch_interval
        self.alert_threshold = alert_threshold
        self.history_window = history_window
        
        # Initialize data structures
        self.pod_metrics = {}  # Store latest metrics for each pod
        self.pod_history = {}  # Store historical metrics for each pod
        self.last_file_position = 0
        self.last_read_time = 0
        
        # Initialize the anomaly detection agent
        try:
            self.anomaly_agent = AnomalyDetectionAgent(alert_threshold=alert_threshold)
            logger.info("Successfully initialized AnomalyDetectionAgent")
        except NameError:
            logger.error("AnomalyDetectionAgent could not be initialized, anomaly detection will not be available")
            self.anomaly_agent = None
        
        logger.info(f"Initialized DatasetGeneratorAgent with input_file={self.input_file}, "
                   f"watch_interval={watch_interval}s, alert_threshold={alert_threshold}")
    
    def preprocess_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
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
        
        # Calculate derived metrics
        if 'Network Receive (B/s)' in processed_df.columns and 'Network Transmit (B/s)' in processed_df.columns:
            # Total network traffic
            processed_df['Network Traffic (B/s)'] = (
                processed_df['Network Receive (B/s)'] + processed_df['Network Transmit (B/s)']
            )
        
        # Convert memory usage to MB if needed
        if 'Memory Usage (MB)' not in processed_df.columns and 'Memory Usage (%)' in processed_df.columns:
            # Estimate memory in MB based on percentage (assuming 16GB node)
            processed_df['Memory Usage (MB)'] = processed_df['Memory Usage (%)'] * 160
        
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
        
        # Extract event age and convert to minutes
        if 'Pod Event Age' in processed_df.columns:
            processed_df['Event Age (minutes)'] = self._parse_event_age(processed_df['Pod Event Age'])
        
        # Add event count if missing
        if 'Event Count' not in processed_df.columns:
            processed_df['Event Count'] = 1
        
        return processed_df
    
    def _parse_event_age(self, age_series: pd.Series) -> pd.Series:
        """
        Parse Kubernetes event age strings into minutes.
        Examples: "10m" -> 10, "2h" -> 120, "1d" -> 1440
        
        Args:
            age_series: Series containing age strings
            
        Returns:
            Series containing age in minutes
        """
        minutes = pd.Series(0, index=age_series.index)
        
        for i, age in enumerate(age_series):
            try:
                if pd.isna(age) or age == 'Unknown':
                    minutes.iloc[i] = 0
                    continue
                    
                age = str(age).strip()
                if not age:
                    minutes.iloc[i] = 0
                    continue
                
                if age.endswith('s'):
                    minutes.iloc[i] = int(age[:-1]) / 60  # seconds to minutes
                elif age.endswith('m'):
                    minutes.iloc[i] = int(age[:-1])  # already in minutes
                elif age.endswith('h'):
                    minutes.iloc[i] = int(age[:-1]) * 60  # hours to minutes
                elif age.endswith('d'):
                    minutes.iloc[i] = int(age[:-1]) * 24 * 60  # days to minutes
                else:
                    # Try to convert directly to int
                    minutes.iloc[i] = int(age)
            except Exception as e:
                logger.warning(f"Could not parse age '{age}': {e}")
                minutes.iloc[i] = 0
                
        return minutes
    
    def read_new_data(self) -> pd.DataFrame:
        """
        Read new data from the metrics file.
        
        Returns:
            DataFrame containing new data, or empty DataFrame if no new data
        """
        try:
            if not os.path.exists(self.input_file):
                logger.warning(f"Input file {self.input_file} does not exist")
                return pd.DataFrame()
                
            # Check if file was modified since last read
            current_mtime = os.path.getmtime(self.input_file)
            if current_mtime <= self.last_read_time:
                logger.debug("No new data in file since last read")
                return pd.DataFrame()
                
            # Read the entire file but only process new rows
            df = pd.read_csv(self.input_file)
            self.last_read_time = current_mtime
            
            if len(df) <= self.last_file_position:
                logger.debug(f"No new rows (file has {len(df)} rows, last read position: {self.last_file_position})")
                return pd.DataFrame()
                
            # Extract new rows
            new_rows = df.iloc[self.last_file_position:]
            self.last_file_position = len(df)
            logger.info(f"Read {len(new_rows)} new rows from {self.input_file}")
            
            return new_rows
        except Exception as e:
            logger.error(f"Error reading data from {self.input_file}: {e}")
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def update_pod_metrics(self, df: pd.DataFrame) -> None:
        """
        Update pod metrics with new data.
        
        Args:
            df: DataFrame containing new metrics data
        """
        if df.empty:
            return
            
        # Preprocess metrics
        processed_df = self.preprocess_metrics(df)
        
        # Update metrics for each pod
        for _, row in processed_df.iterrows():
            # Skip rows without pod name
            if 'Pod Name' not in row or pd.isna(row['Pod Name']):
                continue
                
            pod_name = row['Pod Name']
            
            # Convert row to dictionary for easier manipulation
            pod_data = row.to_dict()
            
            # Add timestamp if not present
            if 'Timestamp' not in pod_data or pd.isna(pod_data['Timestamp']):
                pod_data['Timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Update latest metrics
            self.pod_metrics[pod_name] = pod_data
            
            # Update history
            if pod_name not in self.pod_history:
                self.pod_history[pod_name] = []
            self.pod_history[pod_name].append(pod_data)
            
            # Trim history to keep only recent data
            self._trim_pod_history(pod_name)
    
    def _trim_pod_history(self, pod_name: str) -> None:
        """
        Trim pod history to keep only recent data.
        
        Args:
            pod_name: Name of the pod to trim history for
        """
        if pod_name not in self.pod_history:
            return
            
        # Keep data within the history window
        cutoff_time = datetime.now() - timedelta(minutes=self.history_window)
        
        filtered_history = []
        for entry in self.pod_history[pod_name]:
            try:
                timestamp = entry.get('Timestamp')
                if timestamp:
                    entry_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                    if entry_time >= cutoff_time:
                        filtered_history.append(entry)
                else:
                    # If no timestamp, keep only recent entries
                    if len(filtered_history) < 100:  # Keep last 100 entries with no timestamp
                        filtered_history.append(entry)
            except Exception as e:
                logger.warning(f"Error parsing timestamp {timestamp}: {e}")
                # Keep entry if parsing fails
                filtered_history.append(entry)
        
        self.pod_history[pod_name] = filtered_history
    
    def detect_anomalies(self) -> Dict[str, Dict[str, Any]]:
        """
        Run anomaly detection on all pods using the separate anomaly detection agent.
        
        Returns:
            Dictionary of pod names to anomaly results
        """
        if self.anomaly_agent is None:
            logger.warning("Anomaly detection agent not available, skipping anomaly detection")
            return {}
        
        try:
            # Use the separate anomaly detection agent
            anomalies = self.anomaly_agent.detect_anomalies(self.pod_history)
            return anomalies
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def generate_insights(self, anomalies: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Generate insights based on detected anomalies using the separate anomaly detection agent.
        
        Args:
            anomalies: Dictionary of pod names to anomaly results
            
        Returns:
            List of insight dictionaries
        """
        if self.anomaly_agent is None:
            logger.warning("Anomaly detection agent not available, skipping insight generation")
            return []
        
        try:
            # Use the separate anomaly detection agent
            insights = self.anomaly_agent.generate_insights(anomalies)
            return insights
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def run(self) -> None:
        """Run the agent in a continuous loop"""
        logger.info(f"Starting dataset generator agent, monitoring {self.input_file}")
        
        try:
            while True:
                # Read new data
                new_data = self.read_new_data()
                if not new_data.empty:
                    # Update metrics
                    self.update_pod_metrics(new_data)
                    
                    # Detect anomalies
                    anomalies = self.detect_anomalies()
                    
                    # Generate insights
                    insights = self.generate_insights(anomalies)
                    
                    # Output insights
                    if insights and self.anomaly_agent:
                        self.anomaly_agent.output_insights(insights)
                
                # Sleep before next check
                time.sleep(self.watch_interval)
                
        except KeyboardInterrupt:
            logger.info("Dataset generator agent stopped by user")
        except Exception as e:
            logger.error(f"Error in dataset generator agent: {e}")
            import traceback
            traceback.print_exc()
    
    def _output_insights(self, insights: List[Dict[str, Any]], output_file: str = 'pod_insights.json') -> None:
        """
        Output insights to a JSON file.
        
        Args:
            insights: List of insight dictionaries
            output_file: Path to the output file
        """
        if self.anomaly_agent:
            # Delegate to the anomaly detection agent
            self.anomaly_agent.output_insights(insights, output_file)
        else:
            # Fallback if anomaly agent is not available
            try:
                if not insights:
                    return
                    
                # Read existing insights
                existing_insights = []
                if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                    with open(output_file, 'r') as f:
                        try:
                            existing_insights = json.load(f)
                        except json.JSONDecodeError:
                            logger.warning(f"Could not parse existing insights file {output_file}, creating new file")
                
                # Add new insights
                all_insights = existing_insights + insights
                
                # Keep only the latest 100 insights
                if len(all_insights) > 100:
                    all_insights = all_insights[-100:]
                
                # Write back to file
                with open(output_file, 'w') as f:
                    json.dump(all_insights, f, indent=2)
                    
                logger.info(f"Wrote {len(insights)} new insights to {output_file}")
                
            except Exception as e:
                logger.error(f"Error writing insights to {output_file}: {e}")
                import traceback
                traceback.print_exc()

def main():
    """Run the dataset generator agent as a standalone script"""
    parser = argparse.ArgumentParser(
        description='Monitor pod metrics and detect anomalies',
        epilog='Example: python dataset_generator_agent.py --input-file ../../pod_metrics.csv'
    )
    parser.add_argument('--input-file', type=str, default='pod_metrics.csv',
                        help='Input metrics CSV file (default: pod_metrics.csv)')
    parser.add_argument('--watch-interval', type=int, default=10,
                        help='Interval in seconds between checks (default: 10)')
    parser.add_argument('--alert-threshold', type=float, default=0.7,
                        help='Probability threshold for anomaly alerts (default: 0.7)')
    parser.add_argument('--test', action='store_true',
                        help='Test agent setup without running the main loop')
    
    args = parser.parse_args()
    
    try:
        # Create the agent
        agent = DatasetGeneratorAgent(
            input_file=args.input_file,
            watch_interval=args.watch_interval,
            alert_threshold=args.alert_threshold
        )
        
        # If test mode, just check if the input file exists
        if args.test:
            logger.info("Test mode: checking configuration")
            if not os.path.exists(agent.input_file):
                logger.error(f"Input file not found: {agent.input_file}")
                project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
                logger.error(f"Make sure the file exists or specify the full path with --input-file")
                logger.error(f"Project root directory is: {project_root}")
                sys.exit(1)
            else:
                logger.info(f"Input file found: {agent.input_file}")
                logger.info("Agent is correctly configured and ready to run")
                # Try to read the first few lines to verify file structure
                try:
                    df = pd.read_csv(agent.input_file, nrows=5)
                    if 'Pod Name' in df.columns:
                        logger.info(f"File structure looks good. Found {len(df)} rows with Pod Name column.")
                    else:
                        logger.warning("File is missing 'Pod Name' column which is required")
                    logger.info(f"Available columns: {', '.join(df.columns)}")
                except Exception as e:
                    logger.error(f"Error reading input file: {e}")
                    
                # Exit after test
                return
                
        # Run the agent in continuous mode
        agent.run()
        
    except KeyboardInterrupt:
        logger.info("Dataset generator agent stopped by user")
    except Exception as e:
        logger.error(f"Error in dataset generator agent: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 