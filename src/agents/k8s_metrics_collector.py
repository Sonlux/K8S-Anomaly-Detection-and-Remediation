import pandas as pd
import logging
import subprocess
import json
import time
import datetime
from typing import Dict, Any, Optional, List
# Import our anomaly detection agent
from anomaly_detection_agent import AnomalyDetectionAgent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("k8s_metrics_collector")

# Initialize the anomaly detection agent
anomaly_agent = AnomalyDetectionAgent()

# Create a wrapper function to match the expected interface
def process_metrics(metrics_dict):
    """Process metrics using the anomaly detection agent."""
    # Create a pod history with a single entry
    pod_name = metrics_dict.get('Pod Name', 'unknown-pod')
    pod_history = {pod_name: [metrics_dict]}
    
    # Detect anomalies
    anomalies = anomaly_agent.detect_anomalies(pod_history)
    
    # Generate insights
    insights = anomaly_agent.generate_insights(anomalies)
    
    # Convert insights to message objects
    class Message:
        def __init__(self, content):
            self.content = content
    
    messages = []
    if pod_name in insights:
        for insight in insights[pod_name]:
            messages.append(Message(insight))
    
    # If no insights, add a default message
    if not messages:
        messages.append(Message("No anomalies detected"))
    
    return messages

def run_kubectl_command(command: List[str]) -> Optional[str]:
    """Run a kubectl command and return the output."""
    try:
        # Join the command parts
        full_command = ["kubectl"] + command
        logger.debug(f"Running command: {' '.join(full_command)}")
        
        # Execute the command
        result = subprocess.run(
            full_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running kubectl command: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None

def get_pod_metrics(namespace: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get metrics for all pods in the specified namespace."""
    cmd = ["top", "pods"]
    if namespace:
        cmd.extend(["-n", namespace])
    
    # Remove the -o json flag as it's not supported by kubectl top
    output = run_kubectl_command(cmd)
    if not output:
        logger.warning("No pod metrics retrieved")
        return []
    
    try:
        # Parse the text output manually
        lines = output.strip().split('\n')
        if len(lines) <= 1:  # Only header or empty
            return []
            
        # Skip the header line
        header = lines[0].split()
        metrics = []
        
        for line in lines[1:]:
            parts = line.split()
            if len(parts) >= 3:  # Name, CPU, Memory at minimum
                pod_name = parts[0]
                cpu = parts[1]
                memory = parts[2]
                
                # Convert CPU string (e.g., "15m") to number
                cpu_value = 0
                if cpu.endswith("m"):
                    cpu_value = float(cpu[:-1]) / 1000  # Convert millicores to cores
                else:
                    try:
                        cpu_value = float(cpu)
                    except ValueError:
                        cpu_value = 0
                
                # Convert memory string (e.g., "15Mi") to number
                memory_value = 0
                if memory.endswith("Ki"):
                    memory_value = float(memory[:-2]) * 1024
                elif memory.endswith("Mi"):
                    memory_value = float(memory[:-2]) * 1024 * 1024
                elif memory.endswith("Gi"):
                    memory_value = float(memory[:-2]) * 1024 * 1024 * 1024
                
                metrics.append({
                    "metadata": {"name": pod_name},
                    "containers": [{
                        "usage": {
                            "cpu": cpu,
                            "memory": memory
                        }
                    }]
                })
        
        return metrics
    except Exception as e:
        logger.error(f"Error parsing kubectl top output: {e}")
        return []
    cmd.extend(["-o", "json"])
    
    output = run_kubectl_command(cmd)
    if not output:
        logger.warning("No pod metrics retrieved")
        return []
    
    try:
        data = json.loads(output)
        return data.get("items", [])
    except json.JSONDecodeError:
        logger.error(f"Error parsing JSON from kubectl output")
        return []

def get_pod_info(namespace: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get detailed information about pods."""
    cmd = ["get", "pods"]
    if namespace:
        cmd.extend(["-n", namespace])
    cmd.extend(["-o", "json"])
    
    output = run_kubectl_command(cmd)
    if not output:
        logger.warning("No pod information retrieved")
        return []
    
    try:
        data = json.loads(output)
        return data.get("items", [])
    except json.JSONDecodeError:
        logger.error(f"Error parsing JSON from kubectl output")
        return []

def get_pod_events(namespace: Optional[str] = None, pod_name: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get events for pods in the specified namespace."""
    cmd = ["get", "events"]
    if namespace:
        cmd.extend(["-n", namespace])
    cmd.extend(["-o", "json"])
    
    output = run_kubectl_command(cmd)
    if not output:
        logger.warning("No events retrieved")
        return []
    
    try:
        data = json.loads(output)
        events = data.get("items", [])
        
        # Filter events related to specific pod if specified
        if pod_name:
            pod_events = []
            for event in events:
                involved_object = event.get("involvedObject", {})
                if involved_object.get("kind") == "Pod" and involved_object.get("name") == pod_name:
                    pod_events.append(event)
            return pod_events
        
        # Return only Pod events if no specific pod requested
        pod_events = []
        for event in events:
            if event.get("involvedObject", {}).get("kind") == "Pod":
                pod_events.append(event)
        return pod_events
        
    except json.JSONDecodeError:
        logger.error(f"Error parsing JSON from kubectl output")
        return []

def parse_event_age(age_str: str) -> int:
    """Parse Kubernetes event age string (like '5m', '2h', '3d') to minutes."""
    if not age_str:
        return 0
    
    try:
        if age_str.endswith('s'):
            return int(float(age_str[:-1]) / 60)  # seconds to minutes
        elif age_str.endswith('m'):
            return int(age_str[:-1])  # already in minutes
        elif age_str.endswith('h'):
            return int(age_str[:-1]) * 60  # hours to minutes
        elif age_str.endswith('d'):
            return int(age_str[:-1]) * 24 * 60  # days to minutes
        else:
            return 0
    except ValueError:
        return 0

def parse_k8s_timestamp(timestamp_str: str) -> Optional[datetime.datetime]:
    """Parse Kubernetes timestamp to Python datetime."""
    if not timestamp_str:
        return None
    
    try:
        # K8s timestamps are in RFC3339 format
        dt = datetime.datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt
    except (ValueError, TypeError):
        return None

def calculate_event_age_minutes(event: Dict[str, Any]) -> int:
    """Calculate event age in minutes from timestamp or age field."""
    # Try to get from firstTimestamp
    first_timestamp = event.get("firstTimestamp")
    if first_timestamp:
        dt = parse_k8s_timestamp(first_timestamp)
        if dt:
            now = datetime.datetime.now(dt.tzinfo)
            delta = now - dt
            return int(delta.total_seconds() / 60)
    
    # Fall back to lastTimestamp
    last_timestamp = event.get("lastTimestamp")
    if last_timestamp:
        dt = parse_k8s_timestamp(last_timestamp)
        if dt:
            now = datetime.datetime.now(dt.tzinfo)
            delta = now - dt
            return int(delta.total_seconds() / 60)
    
    # If no timestamps, try to parse from age field (if present in the event)
    age = event.get("age")
    if age:
        return parse_event_age(age)
    
    return 0

def extract_pod_metrics(pod_metrics: List[Dict[str, Any]], pod_info: List[Dict[str, Any]], 
                      pod_events: List[Dict[str, Any]]) -> pd.DataFrame:
    """Extract and transform pod metrics into a format for anomaly detection."""
    if not pod_metrics or not pod_info:
        return pd.DataFrame()
    
    metrics_rows = []
    
    # Create a lookup for pod info by name
    pod_info_lookup = {pod.get("metadata", {}).get("name"): pod for pod in pod_info}
    
    # Create a lookup for pod events by name
    pod_events_lookup = {}
    for event in pod_events:
        pod_name = event.get("involvedObject", {}).get("name")
        if pod_name:
            if pod_name not in pod_events_lookup:
                pod_events_lookup[pod_name] = []
            pod_events_lookup[pod_name].append(event)
    
    for pod in pod_metrics:
        pod_name = pod.get("metadata", {}).get("name")
        if not pod_name:
            continue
            
        # Get pod status info
        pod_status = pod_info_lookup.get(pod_name, {}).get("status", {})
        
        # Extract containers info
        total_containers = len(pod.get("containers", []))
        ready_containers = sum(1 for container in pod_status.get("containerStatuses", []) 
                               if container.get("ready", False))
        
        # Extract restart counts
        restart_count = sum(container.get("restartCount", 0) 
                           for container in pod_status.get("containerStatuses", []))
        
        # Get CPU and memory metrics
        cpu_usage = 0
        memory_usage_bytes = 0
        memory_usage_percent = 0
        
        for container in pod.get("containers", []):
            cpu = container.get("usage", {}).get("cpu", "0")
            memory = container.get("usage", {}).get("memory", "0")
            
            # Convert CPU string (e.g., "15m") to number
            if cpu.endswith("m"):
                cpu_usage += float(cpu[:-1]) / 1000  # Convert millicores to cores
            else:
                cpu_usage += float(cpu)
                
            # Convert memory string (e.g., "15Mi") to number
            if memory.endswith("Ki"):
                memory_usage_bytes += float(memory[:-2]) * 1024
            elif memory.endswith("Mi"):
                memory_usage_bytes += float(memory[:-2]) * 1024 * 1024
            elif memory.endswith("Gi"):
                memory_usage_bytes += float(memory[:-2]) * 1024 * 1024 * 1024
                
        # Convert to MB
        memory_usage_mb = memory_usage_bytes / (1024 * 1024)
        
        # Calculate percentages (assuming pod requests/limits are set)
        cpu_usage_percent = cpu_usage * 100  # Assuming 1 core = 100%
        
        # Basic network and filesystem metrics (would need to be collected from other sources)
        # For this example, setting placeholder values
        network_receive_bytes = 0
        network_transmit_bytes = 0
        fs_reads_mb = 0
        fs_writes_mb = 0
        network_rx_dropped = 0
        network_tx_dropped = 0
        
        # Get pod status
        pod_phase = pod_status.get("phase", "Unknown")
        pod_conditions = pod_status.get("conditions", [])
        pod_ready = any(cond.get("type") == "Ready" and cond.get("status") == "True" 
                       for cond in pod_conditions)
        
        # Get event information
        pod_event_list = pod_events_lookup.get(pod_name, [])
        
        # Find the most recent event
        latest_event = None
        latest_event_age = 0
        event_reason = ""
        event_message = ""
        event_count = 0
        
        if pod_event_list:
            # Sort events by time (newest first)
            sorted_events = sorted(
                pod_event_list, 
                key=lambda e: parse_k8s_timestamp(e.get("lastTimestamp", "")) or datetime.datetime.min,
                reverse=True
            )
            
            if sorted_events:
                latest_event = sorted_events[0]
                latest_event_age = calculate_event_age_minutes(latest_event)
                event_reason = latest_event.get("reason", "")
                event_message = latest_event.get("message", "")
                event_count = latest_event.get("count", 1)
        
        metrics_row = {
            'Pod Name': pod_name,
            'Pod Status': pod_phase,
            'CPU Usage (%)': cpu_usage_percent,
            'Memory Usage (%)': memory_usage_percent,
            'Memory Usage (MB)': memory_usage_mb,
            'Pod Restarts': restart_count,
            'Network Receive Bytes': network_receive_bytes,
            'Network Transmit Bytes': network_transmit_bytes,
            'FS Reads Total (MB)': fs_reads_mb,
            'FS Writes Total (MB)': fs_writes_mb,
            'Network Receive Packets Dropped (p/s)': network_rx_dropped,
            'Network Transmit Packets Dropped (p/s)': network_tx_dropped,
            'Ready Containers': ready_containers,
            'Total Containers': total_containers,
            'Event Reason': event_reason,
            'Event Message': event_message,
            'Event Age (minutes)': latest_event_age,
            'Event Count': event_count,
            'Node Name': pod_status.get("hostIP", "")
        }
        
        metrics_rows.append(metrics_row)
    
    return pd.DataFrame(metrics_rows)

def monitor_cluster(namespace: Optional[str] = None, interval_seconds: int = 60):
    """Continuously monitor the cluster and analyze metrics."""
    logger.info(f"Starting K8s monitoring for namespace: {namespace or 'all'}")
    
    while True:
        logger.info(f"Collecting metrics...")
        
        # Get metrics
        pod_metrics = get_pod_metrics(namespace)
        pod_info = get_pod_info(namespace)
        pod_events = get_pod_events(namespace)
        
        if not pod_metrics or not pod_info:
            logger.warning("No metrics or pod info available, retrying...")
            time.sleep(interval_seconds)
            continue
            
        # Transform metrics
        metrics_df = extract_pod_metrics(pod_metrics, pod_info, pod_events)
        
        if metrics_df.empty:
            logger.warning("No valid metrics extracted, retrying...")
            time.sleep(interval_seconds)
            continue
            
        logger.info(f"Collected metrics for {len(metrics_df)} pods")
        
        # Process each pod's metrics through the anomaly agent
        for _, pod_metrics_row in metrics_df.iterrows():
            pod_name = pod_metrics_row['Pod Name']
            logger.info(f"Analyzing pod: {pod_name}")
            
            # Convert Series to dict
            metrics_dict = pod_metrics_row.to_dict()
            
            # Process metrics through the agent
            messages = process_metrics(metrics_dict)
            
            # Print the analysis
            print(f"\n--- Analysis for pod {pod_name} ---")
            print(f"Status: {pod_metrics_row['Pod Status']}")
            if pod_metrics_row['Event Reason']:
                print(f"Latest Event: {pod_metrics_row['Event Reason']} (Age: {pod_metrics_row['Event Age (minutes)']} min, Count: {pod_metrics_row['Event Count']})")
                if pod_metrics_row['Event Message']:
                    print(f"Event Message: {pod_metrics_row['Event Message']}")
            
            for msg in messages:
                if hasattr(msg, 'content'):
                    print(f"> {msg.content}")
            
        # Wait before next collection
        logger.info(f"Waiting {interval_seconds} seconds before next collection...")
        time.sleep(interval_seconds)

if __name__ == "__main__":
    # Example usage
    try:
        monitor_cluster(namespace="default", interval_seconds=300)  # Check every 5 minutes
    except KeyboardInterrupt:
        logger.info("Monitoring stopped by user")
    except Exception as e:
        logger.error(f"Error in monitoring: {e}")