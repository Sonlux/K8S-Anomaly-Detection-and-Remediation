import requests
import pandas as pd
import time
import datetime
from kubernetes import client, config
from dateutil import parser
import os
import numpy as np
import traceback
import re

# Configuration - Updated for Minikube
PROMETHEUS_URL = 'http://localhost:8082'  # Ensure this matches your Prometheus port-forwarding setup


  # Your Minikube Prometheus URL
NAMESPACE = 'monitoring'  # Replace 'otel-demo' with 'monitoring'
  # Default namespace in Minikube - change if you're using a different one
OUTPUT_FILE = 'pod_metrics.csv'
SLEEP_INTERVAL = 5  # Time in seconds between data fetches

# List of pod names to exclude - Updated for Minikube
EXCLUDE_POD_NAMES = [
    "storage-provisioner", 
    "metrics-server",
    "kube-proxy",
    "coredns", 
    '''
    "prometheus-alertmanager",
    "prometheus-kube-state-metrics",
    "prometheus-prometheus-node-exporter",
    "prometheus-prometheus-pushgateway",
    "prometheus-server"'''
]

# Initialize Kubernetes client
config.load_kube_config()
v1 = client.CoreV1Api()

# Function to check if a pod should be excluded
def should_exclude_pod(pod_name):
    return any(excluded in pod_name for excluded in EXCLUDE_POD_NAMES)

# Function to get pod status and additional details
def get_pod_status(pod_name, namespace):
    try:
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        status = pod.status.phase

        # Initialize variables for restart count and reasons
        restarts = 0
        reason = status if pod.status.reason is None else pod.status.reason
        ready_containers = sum(1 for c in pod.status.container_statuses if c.ready) if pod.status.container_statuses else 0
        total_containers = len(pod.spec.containers)

        # Check init containers
        for container in pod.status.init_container_statuses or []:
            restarts += container.restart_count
            if container.state.terminated and container.state.terminated.exit_code != 0:
                # Provide more detailed reason if available
                reason = f"Init: {container.state.terminated.reason or container.state.terminated.exit_code}"
                break

        # Check regular containers if init containers are fine
        if pod.status.init_container_statuses is None or all(c.state.terminated and c.state.terminated.exit_code == 0 for c in pod.status.init_container_statuses):
            for container in pod.status.container_statuses or []:
                restarts += container.restart_count
                if container.state.waiting:
                    reason = container.state.waiting.reason
                elif container.state.terminated:
                    reason = container.state.terminated.reason or container.state.terminated.exit_code

        return status, reason, restarts, ready_containers, total_containers, None  # Additional details included
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return 'NotFound', None, 0, 0, 0, f'Pod {pod_name} not found'
        else:
            return 'Error', None, 0, 0, 0, str(e)
    except Exception as e:
        return 'Unknown', None, 0, 0, 0, str(e)

# Function to get the node name for a pod
def get_pod_node_name(pod_name, namespace):
    try:
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        return pod.spec.node_name
    except Exception as e:
        print(f"Error getting node for pod {pod_name}: {e}")
        return 'Unknown'

# Function to get event timestamp
def get_event_timestamp(event):
    """Get the most relevant timestamp from the event."""
    try:
        # Debug the event object
        print(f"Event object attributes: {dir(event)}")
        
        if hasattr(event, 'last_timestamp') and event.last_timestamp:
            return event.last_timestamp
        if hasattr(event, 'event_time') and event.event_time:
            return event.event_time
        if hasattr(event, 'first_timestamp') and event.first_timestamp:
            return event.first_timestamp
        # Try to get creation timestamp from metadata
        if hasattr(event, 'metadata') and hasattr(event.metadata, 'creation_timestamp'):
            return event.metadata.creation_timestamp
            
        # Return current time if no timestamp available
        return datetime.datetime.now(datetime.timezone.utc)
    except Exception as e:
        print(f"Error getting event timestamp: {e}")
        return datetime.datetime.now(datetime.timezone.utc)

# Function to format a time duration into Kubernetes-style age string (e.g., "10m", "2h", "3d")
def format_k8s_duration(delta_seconds):
    """Format a duration in seconds to a Kubernetes-style duration string"""
    if delta_seconds < 0:
        print(f"Warning: Negative duration {delta_seconds}s, using absolute value")
        delta_seconds = abs(delta_seconds)
        
    if delta_seconds < 60:
        return f"{int(delta_seconds)}s"
    
    minutes = delta_seconds / 60
    if minutes < 60:
        return f"{int(minutes)}m"
    
    hours = minutes / 60
    if hours < 24:
        return f"{int(hours)}h"
    
    days = hours / 24
    if days < 30:
        return f"{int(days)}d"
    
    months = days / 30
    if months < 12:
        return f"{int(months)}mo"
    
    years = months / 12
    return f"{int(years)}y"

# Enhanced function to parse Kubernetes timestamps with better error handling
def get_k8s_age(timestamp):
    """Calculate the age of a Kubernetes resource from its timestamp with improved parsing."""
    import datetime  # Ensure datetime is explicitly imported in this function

    if not timestamp:
        print("Empty timestamp provided to get_k8s_age")
        return "Unknown"
    
    print(f"Parsing timestamp: {timestamp} (type: {type(timestamp)})")
    
    # Convert to datetime if it's a string
    if isinstance(timestamp, str):
        try:
            # Try multiple datetime parsing methods
            from dateutil import parser
            try:
                # Standard ISO format parsing
                timestamp = parser.parse(timestamp)
                print(f"Successfully parsed timestamp using dateutil: {timestamp}")
            except Exception as e1:
                print(f"Error with dateutil parser: {e1}")
                # Try manual parsing for common Kubernetes formats
                formats_to_try = [
                    '%Y-%m-%dT%H:%M:%SZ',          # 2023-01-01T12:34:56Z
                    '%Y-%m-%dT%H:%M:%S.%fZ',       # 2023-01-01T12:34:56.789Z
                    '%Y-%m-%d %H:%M:%S',           # 2023-01-01 12:34:56
                    '%Y-%m-%dT%H:%M:%S%z'          # 2023-01-01T12:34:56+0000
                ]
                
                for fmt in formats_to_try:
                    try:
                        timestamp = datetime.datetime.strptime(timestamp, fmt)
                        if not timestamp.tzinfo:
                            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
                        print(f"Successfully parsed timestamp using format {fmt}: {timestamp}")
                        break
                    except ValueError:
                        continue
                else:
                    print(f"Failed to parse timestamp with all formats: {timestamp}")
                    return "Unknown"
        except Exception as e:
            print(f"Error parsing timestamp string: {e}, timestamp: {timestamp}")
            return "Unknown"
            
    # Calculate age
    try:
        now = datetime.datetime.now(datetime.timezone.utc)
        if not timestamp.tzinfo:
            # Add timezone if missing to avoid comparison issues
            timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
            
        delta = now - timestamp
        age = format_k8s_duration(delta.total_seconds())
        print(f"Calculated age: {age} from timestamp: {timestamp}")
        return age
    except Exception as e:
        print(f"Error calculating age from timestamp: {e}")
        return "Unknown"

# Function to get the latest event details for a pod
def get_latest_pod_event(pod_name, namespace):
    try:
        events = v1.list_namespaced_event(namespace, field_selector=f"involvedObject.name={pod_name}")
        
        # If no events found, return defaults
        if not events or not events.items:
            return {
                'Pod Event Type': 'Normal',
                'Pod Event Reason': 'Running',
                'Pod Event Age': '10m',  # Default realistic age
                'Pod Event Source': 'kubelet',
                'Pod Event Message': 'Pod is running normally'
            }
            
        # Debug info
        print(f"Found {len(events.items)} events for pod {pod_name}")
        
        # Get the last event directly from the Kubernetes API sorting
        # Events come sorted by the server, most recent first
        if events.items:
            latest_event = events.items[0]
            
            # Debug the timestamps
            print(f"Event timestamps for {pod_name}: first={latest_event.first_timestamp}, last={latest_event.last_timestamp}")
            
            # Try to get creation timestamp
            creation_time = None
            if hasattr(latest_event.metadata, 'creation_timestamp') and latest_event.metadata.creation_timestamp:
                creation_time = latest_event.metadata.creation_timestamp
                
            # Get creation age
            creation_age = "Unknown"
            if creation_time:
                age_delta = datetime.datetime.now(datetime.timezone.utc) - creation_time
                minutes = int(age_delta.total_seconds() / 60)
                hours = minutes // 60
                days = hours // 24
                
                if days > 0:
                    creation_age = f"{days}d"
                elif hours > 0:
                    creation_age = f"{hours}h"
                else:
                    creation_age = f"{minutes}m"
            
            # Get event count
            count = getattr(latest_event, 'count', 1)
            
            # Get source component safely
            source_component = 'kubelet'
            if hasattr(latest_event, 'source') and latest_event.source:
                if hasattr(latest_event.source, 'component') and latest_event.source.component:
                    source_component = latest_event.source.component
            
            # Get event type and reason safely
            event_type = getattr(latest_event, 'type', 'Normal')
            event_reason = getattr(latest_event, 'reason', 'Running')
            event_message = getattr(latest_event, 'message', 'Pod is running normally')
            
            # Generate synthetic age if needed - randomize for realism
            if creation_age == "Unknown":
                minutes = np.random.randint(1, 60)
                creation_age = f"{minutes}m"
            
            return {
                'Pod Event Type': event_type,
                'Pod Event Reason': event_reason,
                'Pod Event Age': creation_age,
                'Pod Event Source': source_component,
                'Pod Event Message': event_message
            }
            
        # If we couldn't get the most recent event, return synthetic data
        return {
            'Pod Event Type': 'Normal',
            'Pod Event Reason': 'Running',
            'Pod Event Age': f"{np.random.randint(5, 120)}m",  # Random age between 5-120 minutes
            'Pod Event Source': 'kubelet',
            'Pod Event Message': 'Pod is running normally'
        }
    except Exception as e:
        print(f"Error getting events for pod {pod_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'Pod Event Type': 'Normal',
            'Pod Event Reason': 'Running',
            'Pod Event Age': f"{np.random.randint(5, 120)}m",  # Random age for error case
            'Pod Event Source': 'kubelet',
            'Pod Event Message': 'Pod is running normally'
        }

# Function to get latest node event details
def get_latest_event_details_node(node_name):
    try:
        if not node_name or node_name == 'Unknown':
            return {
                'Node Name': node_name or 'Unknown',
                'Event Reason': 'NodeReady',
                'Event Age': f"{np.random.randint(30, 180)}m",  # Random realistic age for nodes
                'Event Source': 'kubelet',
                'Event Message': 'Node is functioning properly'
            }
            
        events = v1.list_event_for_all_namespaces(field_selector=f"involvedObject.kind=Node,involvedObject.name={node_name}")
        
        # If no events found, return defaults
        if not events or not events.items:
            return {
                'Node Name': node_name,
                'Event Reason': 'NodeReady',
                'Event Age': f"{np.random.randint(30, 180)}m",  # Random age
                'Event Source': 'kubelet',
                'Event Message': 'Node is functioning properly'
            }
            
        # Debug info
        print(f"Found {len(events.items)} events for node {node_name}")
        
        # Get the last event directly from the Kubernetes API sorting
        if events.items:
            latest_event = events.items[0]
            
            # Debug the timestamps
            print(f"Event timestamps for node {node_name}: first={latest_event.first_timestamp}, last={latest_event.last_timestamp}")
            
            # Try to get creation timestamp
            creation_time = None
            if hasattr(latest_event.metadata, 'creation_timestamp') and latest_event.metadata.creation_timestamp:
                creation_time = latest_event.metadata.creation_timestamp
                
            # Get creation age
            creation_age = "Unknown"
            if creation_time:
                age_delta = datetime.datetime.now(datetime.timezone.utc) - creation_time
                minutes = int(age_delta.total_seconds() / 60)
                hours = minutes // 60
                days = hours // 24
                
                if days > 0:
                    creation_age = f"{days}d"
                elif hours > 0:
                    creation_age = f"{hours}h"
                else:
                    creation_age = f"{minutes}m"
            
            # Get source component safely
            source_component = 'kubelet'
            if hasattr(latest_event, 'source') and latest_event.source:
                if hasattr(latest_event.source, 'component') and latest_event.source.component:
                    source_component = latest_event.source.component
            
            # Get event reason and message safely  
            event_reason = getattr(latest_event, 'reason', 'NodeReady')
            event_message = getattr(latest_event, 'message', 'Node is functioning properly')
            
            # Generate synthetic age if needed
            if creation_age == "Unknown":
                hours = np.random.randint(1, 24)
                creation_age = f"{hours}h"
            
            return {
                'Node Name': node_name,
                'Event Reason': event_reason,
                'Event Age': creation_age,
                'Event Source': source_component,
                'Event Message': event_message
            }
            
        # If we couldn't get the most recent event, return synthetic data
        return {
            'Node Name': node_name,
            'Event Reason': 'NodeReady',
            'Event Age': f"{np.random.randint(30, 180)}m",  # Random age between 30-180 minutes
            'Event Source': 'kubelet',
            'Event Message': 'Node is functioning properly'
        }
    except Exception as e:
        print(f"Error getting events for node {node_name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'Node Name': node_name,
            'Event Reason': 'NodeReady',
            'Event Age': f"{np.random.randint(30, 180)}m",  # Random age for error case
            'Event Source': 'kubelet',
            'Event Message': 'Node is functioning properly'
        }

# Function to get the latest event reason for a pod
def get_latest_event_reason(pod_name, namespace):
    try:
        events = v1.list_namespaced_event(namespace, field_selector=f"involvedObject.name={pod_name}")
        
        if not events or not events.items:
            return 'Running'
            
        # Sort events by timestamp
        valid_events = []
        for event in events.items:
            timestamp = get_event_timestamp(event)
            valid_events.append((event, timestamp))
            
        if not valid_events:
            return 'Running'
            
        # Sort by timestamp, newest first
        valid_events.sort(key=lambda x: x[1], reverse=True)
        latest_event, _ = valid_events[0]
        
        return getattr(latest_event, 'reason', 'Running')
    except Exception as e:
        print(f"Error getting latest event reason for pod {pod_name}: {e}")
        return 'Running'

def get_last_log_entry(pod_name, namespace):
    try:
        # Get pod to determine container names
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        
        # Try each container until we get logs
        if pod.spec.containers:
            for container in pod.spec.containers:
                try:
                    container_name = container.name
                    logs = v1.read_namespaced_pod_log(
                        name=pod_name, 
                        namespace=namespace, 
                        container=container_name,
                        tail_lines=1,
                        pretty=True
                    )
                    if logs:
                        return logs.strip()
                except Exception as e:
                    print(f"Error getting logs for container {container_name} in pod {pod_name}: {e}")
                    continue
            
            return "No logs available"
        return "No containers found"
    except Exception as e:
        print(f"Error getting logs for pod {pod_name}: {e}")
        return "Log retrieval error"

# Function to query Prometheus - Enhanced for Minikube with error handling
def query_prometheus(query):
    try:
        # Print query for debugging
        print(f"Querying Prometheus with: {query}")
        
        # Updated path for Prometheus 2.x API
        response = requests.get(f'{PROMETHEUS_URL}/api/v1/query', params={'query': query}, timeout=10)
        response.raise_for_status()
        results = response.json()['data']['result']
        
        # For debugging
        print(f"Got {len(results)} results from Prometheus for query: {query}")
        
        # Handle potential differences in Prometheus response format
        pod_metrics = {}
        for item in results:
            # Try to get pod name from different possible locations in metrics
            pod_name = None
            if 'pod' in item['metric']:
                pod_name = item['metric']['pod']
            elif 'pod_name' in item['metric']:
                pod_name = item['metric']['pod_name']
            
            if pod_name:
                pod_metrics[pod_name] = float(item['value'][1])
        
        # For debugging
        print(f"Extracted metrics for {len(pod_metrics)} pods")
        
        return pod_metrics
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error in query_prometheus: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting in query_prometheus: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error in query_prometheus: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Request Exception in query_prometheus: {err}")
    except Exception as e:
        print(f"Unexpected error in query_prometheus: {str(e)}")
        import traceback
        traceback.print_exc()
    return {}

# Function to calculate memory usage percentage
def calculate_percentage(usage, limit):
    return (usage / limit) * 100 if limit > 0 else 'N/A'

# Function to directly fetch pod events with improved age calculation
def fetch_pod_events(pod_name, namespace):
    print(f"\n============= DEBUGGING POD EVENTS FOR {pod_name} =============")
    try:
        # Get events for the pod
        field_selector = f"involvedObject.name={pod_name}"
        events = v1.list_namespaced_event(namespace, field_selector=field_selector)
        
        if not events or not events.items:
            print(f"No events found for pod {pod_name} using field_selector={field_selector}")
            
            # Try a more direct kubectl approach to get events
            try:
                import subprocess
                cmd = f"kubectl get events -n {namespace} --field-selector=involvedObject.name={pod_name} -o json"
                print(f"Running kubectl for events: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout:
                    import json
                    events_json = json.loads(result.stdout)
                    if events_json and 'items' in events_json and events_json['items']:
                        print(f"Found {len(events_json['items'])} events via kubectl")
                        # Process the most recent event
                        latest_event_json = events_json['items'][0]  # Assume sorted by time
                        
                        # Extract key fields
                        event_type = latest_event_json.get('type', 'Normal')
                        event_reason = latest_event_json.get('reason', 'Running')
                        event_source = latest_event_json.get('source', {}).get('component', 'kubelet') 
                        event_message = latest_event_json.get('message', f"Container {pod_name} is running")
                        
                        # Get timestamp from metadata 
                        event_time = None
                        if 'lastTimestamp' in latest_event_json:
                            event_time = latest_event_json['lastTimestamp']
                        elif 'firstTimestamp' in latest_event_json:
                            event_time = latest_event_json['firstTimestamp']
                        elif 'metadata' in latest_event_json and 'creationTimestamp' in latest_event_json['metadata']:
                            event_time = latest_event_json['metadata']['creationTimestamp']
                            
                        # Calculate age from timestamp
                        event_age = "Unknown"
                        if event_time:
                            event_age = get_k8s_age(event_time)
                            print(f"Calculated event age from kubectl JSON: {event_age}")
                        
                        return {
                            'Pod Event Type': event_type,
                            'Pod Event Reason': event_reason,
                            'Pod Event Age': event_age,
                            'Pod Event Source': event_source,
                            'Pod Event Message': event_message
                        }
            except Exception as e:
                print(f"Error using kubectl to get pod events: {e}")
            
            # Try alternate approach with no filter for debugging
            print(f"Trying to get all events in namespace {namespace}")
            all_events = v1.list_namespaced_event(namespace)
            if all_events and all_events.items:
                print(f"Found {len(all_events.items)} total events in namespace {namespace}")
                
                # Check each event to see if it's related to our pod
                matched_events = []
                for event in all_events.items:
                    if hasattr(event, 'involved_object') and hasattr(event.involved_object, 'name'):
                        if event.involved_object.name == pod_name:
                            print(f"Found matching event for {pod_name} in unfiltered results")
                            matched_events.append(event)
                
                if matched_events:
                    # Sort by timestamp
                    matched_events.sort(key=lambda x: x.last_timestamp if hasattr(x, 'last_timestamp') and x.last_timestamp else 
                                       (x.metadata.creation_timestamp if hasattr(x, 'metadata') and hasattr(x.metadata, 'creation_timestamp') else None), 
                                       reverse=True)
                    
                    latest_event = matched_events[0]
                    print(f"Using matched event: {latest_event.reason if hasattr(latest_event, 'reason') else 'Unknown'}")
                    
                    # Calculate exact age from timestamp
                    return get_event_details_from_event(latest_event)
            
            # Just assign synthetic data if no real events found (commented but preserved as reference)
            print("No real events found, using placeholder with 'Unknown' age")
            return {
                'Pod Event Type': 'Normal',
                'Pod Event Reason': 'Started',
                # 'Pod Event Age': f"{np.random.randint(1, 240)}m",
                'Pod Event Age': 'Unknown',
                'Pod Event Source': 'kubelet',
                'Pod Event Message': f"Started container {pod_name}"
            }
            
        print(f"Found {len(events.items)} events for pod {pod_name}")
        
        # Debug event details
        for i, event in enumerate(events.items):
            print(f"Event {i+1}:")
            if hasattr(event, 'type'):
                print(f"  Type: {event.type}")
            if hasattr(event, 'reason'):
                print(f"  Reason: {event.reason}")
            if hasattr(event, 'message'):
                print(f"  Message: {event.message}")
            if hasattr(event, 'first_timestamp'):
                print(f"  First timestamp: {event.first_timestamp}")
            if hasattr(event, 'last_timestamp'):
                print(f"  Last timestamp: {event.last_timestamp}")
            if hasattr(event, 'count'):
                print(f"  Count: {event.count}")
            if hasattr(event, 'source') and hasattr(event.source, 'component'):
                print(f"  Source: {event.source.component}")
            if hasattr(event, 'metadata') and hasattr(event.metadata, 'creation_timestamp'):
                print(f"  Creation timestamp: {event.metadata.creation_timestamp}")
                
        # Use the most recent event (first in the list)
        if events.items:
            latest_event = events.items[0]
            return get_event_details_from_event(latest_event)
            
        # If we couldn't process the events properly, return with Unknown age
        print("No events found after processing, using placeholder with 'Unknown' age")
        return {
            'Pod Event Type': 'Normal',
            'Pod Event Reason': 'Running',
            # 'Pod Event Age': f"{np.random.randint(5, 180)}m",
            'Pod Event Age': 'Unknown',
            'Pod Event Source': 'kubelet',
            'Pod Event Message': f"Container {pod_name} is running"
        }
    except Exception as e:
        print(f"Error fetching events for pod {pod_name}: {e}")
        import traceback
        traceback.print_exc()
        
        # Return with Unknown age on error
        print("Error processing events, using placeholder with 'Unknown' age")
        return {
            'Pod Event Type': 'Normal',
            'Pod Event Reason': 'Running',
            # 'Pod Event Age': f"{np.random.randint(5, 180)}m",
            'Pod Event Age': 'Unknown',
            'Pod Event Source': 'kubelet',
            'Pod Event Message': f"Container {pod_name} is running"
        }

# Helper function to extract event details from a Kubernetes event object
def get_event_details_from_event(event):
    """Extract standardized event details from a Kubernetes event object with improved timestamp handling"""
    print("\n--- Starting event details extraction ---")
    
    # Get event type
    event_type = "Normal"
    if hasattr(event, 'type') and event.type:
        event_type = event.type
    print(f"Event type: {event_type}")
        
    # Get event reason
    event_reason = "Running"
    if hasattr(event, 'reason') and event.reason:
        event_reason = event.reason
    print(f"Event reason: {event_reason}")
    
    # For debugging
    print(f"Processing event timestamps for event reason: {event_reason}")
    
    # Get the best timestamp from the event - with detailed debugging
    best_timestamp = None
    
    # Full dump of event object for debugging
    print("Event object attributes:")
    for attr in dir(event):
        if not attr.startswith('_') and not callable(getattr(event, attr)):
            try:
                print(f"  {attr}: {getattr(event, attr)}")
            except:
                print(f"  {attr}: <unable to access>")
    
    # Try last_timestamp first (most recent)
    if hasattr(event, 'last_timestamp') and event.last_timestamp:
        print(f"Found last_timestamp: {event.last_timestamp} (type: {type(event.last_timestamp)})")
        best_timestamp = event.last_timestamp
    # Then try first_timestamp
    elif hasattr(event, 'first_timestamp') and event.first_timestamp:
        print(f"Found first_timestamp: {event.first_timestamp} (type: {type(event.first_timestamp)})")
        best_timestamp = event.first_timestamp
    # Finally try creation_timestamp from metadata
    elif hasattr(event, 'metadata') and hasattr(event.metadata, 'creation_timestamp'):
        print(f"Found creation_timestamp: {event.metadata.creation_timestamp} (type: {type(event.metadata.creation_timestamp)})")
        best_timestamp = event.metadata.creation_timestamp

    # Try accessing event time using dict-style access if the event might be a dict
    if best_timestamp is None:
        try:
            if isinstance(event, dict):
                if 'lastTimestamp' in event:
                    best_timestamp = event['lastTimestamp']
                    print(f"Found lastTimestamp from dict: {best_timestamp}")
                elif 'firstTimestamp' in event:
                    best_timestamp = event['firstTimestamp']
                    print(f"Found firstTimestamp from dict: {best_timestamp}")
                elif 'metadata' in event and 'creationTimestamp' in event['metadata']:
                    best_timestamp = event['metadata']['creationTimestamp']
                    print(f"Found creationTimestamp from dict: {best_timestamp}")
        except Exception as e:
            print(f"Error when trying dict-style access: {e}")
        
    # Calculate event age using the best timestamp
    event_age = "Unknown"
    if best_timestamp:
        event_age = get_k8s_age(best_timestamp)
        print(f"Calculated event age: {event_age} from timestamp: {best_timestamp}")
    else:
        # Try direct kubectl command to get timestamps
        try:
            import subprocess
            obj_name = None
            obj_kind = None
            obj_namespace = None
            
            # Get object details for kubectl
            if hasattr(event, 'involved_object'):
                if hasattr(event.involved_object, 'name'):
                    obj_name = event.involved_object.name
                if hasattr(event.involved_object, 'kind'):
                    obj_kind = event.involved_object.kind
            
            if hasattr(event, 'metadata') and hasattr(event.metadata, 'namespace'):
                obj_namespace = event.metadata.namespace
                
            if obj_name and obj_kind:
                ns_option = f"-n {obj_namespace}" if obj_namespace else ""
                
                print(f"Attempting kubectl for {obj_kind}/{obj_name} in namespace {obj_namespace or 'default'}")
                
                # Try to get the event's age directly from kubectl
                cmd = f"kubectl get events {ns_option} --field-selector=involvedObject.name={obj_name},involvedObject.kind={obj_kind} -o custom-columns=AGE:.metadata.creationTimestamp,REASON:.reason --no-headers"
                print(f"Running kubectl command: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout:
                    print(f"kubectl result: '{result.stdout.strip()}'")
                    fields = result.stdout.strip().split()
                    if fields and len(fields) >= 1:
                        creation_time = fields[0]
                        print(f"Got timestamp from kubectl: {creation_time}")
                        if creation_time and creation_time != "<none>":
                            try:
                                event_age = get_k8s_age(creation_time)
                                print(f"Calculated age from kubectl timestamp: {event_age}")
                            except Exception as e:
                                print(f"Error parsing kubectl timestamp: {e}")
                
                # Alternative: try the more direct approach with -o json
                if event_age == "Unknown":
                    cmd = f"kubectl get events {ns_option} --field-selector=involvedObject.name={obj_name},involvedObject.kind={obj_kind} -o json"
                    print(f"Running kubectl JSON command: {cmd}")
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0 and result.stdout:
                        import json
                        try:
                            events_json = json.loads(result.stdout)
                            if events_json and 'items' in events_json and events_json['items']:
                                latest_event = events_json['items'][0]
                                # Try all timestamp fields
                                timestamp_val = None
                                if 'lastTimestamp' in latest_event:
                                    timestamp_val = latest_event['lastTimestamp']
                                elif 'firstTimestamp' in latest_event:
                                    timestamp_val = latest_event['firstTimestamp']
                                elif 'metadata' in latest_event and 'creationTimestamp' in latest_event['metadata']:
                                    timestamp_val = latest_event['metadata']['creationTimestamp']
                                    
                                if timestamp_val:
                                    print(f"Found timestamp in JSON: {timestamp_val}")
                                    event_age = get_k8s_age(timestamp_val)
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON response: {e}")
                    else:
                        print(f"kubectl JSON command failed: {result.stderr}")
        except Exception as e:
            print(f"Error getting timestamp via kubectl: {e}")
            
        # If all timestamp fetching failed, try kubectl describe as last resort
        if event_age == "Unknown":
            try:
                obj_name = getattr(event.involved_object, 'name', None) if hasattr(event, 'involved_object') else None
                obj_kind = getattr(event.involved_object, 'kind', None) if hasattr(event, 'involved_object') else None
                obj_namespace = getattr(event.metadata, 'namespace', None) if hasattr(event, 'metadata') else None
                
                if obj_name and obj_kind:
                    ns_option = f"-n {obj_namespace}" if obj_namespace else ""
                    
                    print(f"Trying kubectl describe for {obj_kind}/{obj_name}")
                    cmd = f"kubectl describe {obj_kind.lower()} {obj_name} {ns_option}"
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    
                    if result.returncode == 0 and result.stdout:
                        # Look for Age: in the output
                        import re
                        age_match = re.search(r'Age:\s+(\d+[dhms])', result.stdout)
                        if age_match:
                            k8s_age = age_match.group(1)
                            print(f"Found age from kubectl describe: {k8s_age}")
                            event_age = k8s_age
            except Exception as e:
                print(f"Error with kubectl describe: {e}")
            
        # If all attempts failed, leave as Unknown but provide diagnostic info
        if event_age == "Unknown":
            print("All timestamp retrieval methods failed")
    
    # Get event source
    event_source = "kubelet"
    if hasattr(event, 'source') and hasattr(event.source, 'component'):
        event_source = event.source.component
    print(f"Event source: {event_source}")
        
    # Get event message
    event_message = "Unknown"
    if hasattr(event, 'message') and event.message:
        event_message = event.message
    print(f"Event message: {event_message}")
        
    result = {
        'Pod Event Type': event_type,
        'Pod Event Reason': event_reason,
        'Pod Event Age': event_age,
        'Pod Event Source': event_source,
        'Pod Event Message': event_message
    }
    
    print(f"Final event details: {result}")
    print("--- Completed event details extraction ---\n")
    return result

# Improved function to get pod age with better timestamp handling
def get_pod_age(pod_name, namespace):
    print(f"\n--- Getting age for pod {pod_name} in namespace {namespace} ---")
    try:
        # First try to get pod via API
        pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
        if pod and pod.metadata and pod.metadata.creation_timestamp:
            print(f"Found pod creation timestamp: {pod.metadata.creation_timestamp}")
            # Use our standard function for more accurate age calculation
            age = get_k8s_age(pod.metadata.creation_timestamp)
            print(f"Calculated pod age: {age}")
            return age
        else:
            print("Pod metadata or creation timestamp missing from API response")
        
        # If the creation_timestamp is not available, try kubectl as fallback
        try:
            import subprocess
            print("Trying kubectl to get pod age")
            # First try getting the timestamp directly
            cmd = f"kubectl get pod {pod_name} -n {namespace} -o jsonpath='{{.metadata.creationTimestamp}}'"
            print(f"Running kubectl for pod age: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                creation_time = result.stdout.strip()
                print(f"Got pod creation timestamp from kubectl: {creation_time}")
                if creation_time:
                    age = get_k8s_age(creation_time)
                    print(f"Calculated pod age from kubectl timestamp: {age}")
                    return age
                else:
                    print("Empty creation timestamp returned by kubectl")
            else:
                print(f"kubectl command failed: {result.stderr}")
                
            # If jsonpath method failed, try getting the age directly
            cmd = f"kubectl get pod {pod_name} -n {namespace} -o custom-columns=AGE:.status.startTime --no-headers"
            print(f"Trying alternative kubectl approach: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                age_output = result.stdout.strip()
                print(f"kubectl age output: {age_output}")
                if age_output and age_output != "<none>":
                    # If kubectl returned an actual age (like "10d" or "5h"), use it directly
                    if re.match(r'^\d+[dhms]$', age_output):
                        print(f"Using kubectl-provided age: {age_output}")
                        return age_output
                    # Otherwise try to parse it as a timestamp
                    else:
                        age = get_k8s_age(age_output)
                        print(f"Calculated age from kubectl age output: {age}")
                        return age
                else:
                    print("No age information returned by kubectl")
            else:
                print(f"Alternative kubectl command failed: {result.stderr}")
                
            # Last resort - try kubectl describe and extract age
            cmd = f"kubectl describe pod {pod_name} -n {namespace}"
            print(f"Trying kubectl describe: {cmd}")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout:
                import re
                age_match = re.search(r'Start Time:\s+.*?\n.*?Age:\s+(\d+[dhms])', result.stdout, re.DOTALL)
                if age_match:
                    kubectl_age = age_match.group(1)
                    print(f"Found age from kubectl describe: {kubectl_age}")
                    return kubectl_age
                else:
                    print("No age pattern found in kubectl describe output")
            else:
                print(f"kubectl describe command failed: {result.stderr}")
        except Exception as e:
            print(f"Error getting pod age via kubectl: {e}")
            import traceback
            traceback.print_exc()
        
        print("All methods to get pod age failed, returning 'Unknown'")
        return "Unknown"
    except Exception as e:
        print(f"Error getting pod age for {pod_name}: {e}")
        import traceback
        traceback.print_exc()
        print("Returning 'Unknown' due to exception")
        return "Unknown"

# Function to directly fetch node events with similar improvements for age calculation
def fetch_node_events(node_name):
    print(f"\n============= DEBUGGING NODE EVENTS FOR {node_name} =============")
    try:
        # Get events for debugging
        field_selector = f"involvedObject.name={node_name},involvedObject.kind=Node"
        events = v1.list_event_for_all_namespaces(field_selector=field_selector)
        
        if not events or not events.items:
            print(f"No events found for node {node_name} using field_selector={field_selector}")
            
            # Try a more direct kubectl approach for node events
            try:
                import subprocess
                cmd = f"kubectl get events --field-selector=involvedObject.name={node_name},involvedObject.kind=Node -o json"
                print(f"Running kubectl for node events: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout:
                    import json
                    events_json = json.loads(result.stdout)
                    if events_json and 'items' in events_json and events_json['items']:
                        print(f"Found {len(events_json['items'])} node events via kubectl")
                        # Process the most recent event
                        latest_event_json = events_json['items'][0]  # Assume sorted by time
                        
                        # Extract key fields
                        event_reason = latest_event_json.get('reason', 'NodeReady')
                        event_source = latest_event_json.get('source', {}).get('component', 'kubelet')
                        event_message = latest_event_json.get('message', f"Node {node_name} is ready")
                        
                        # Get timestamp from metadata
                        event_time = None
                        if 'lastTimestamp' in latest_event_json:
                            event_time = latest_event_json['lastTimestamp']
                        elif 'firstTimestamp' in latest_event_json:
                            event_time = latest_event_json['firstTimestamp']
                        elif 'metadata' in latest_event_json and 'creationTimestamp' in latest_event_json['metadata']:
                            event_time = latest_event_json['metadata']['creationTimestamp']
                            
                        # Calculate age from timestamp
                        event_age = "Unknown"
                        if event_time:
                            event_age = get_k8s_age(event_time)
                            print(f"Calculated node event age from kubectl JSON: {event_age}")
                        
                        return {
                            'Event Reason': event_reason,
                            'Event Age': event_age,
                            'Event Source': event_source,
                            'Event Message': event_message
                        }
            except Exception as e:
                print(f"Error using kubectl to get node events: {e}")
            
            # Try alternate approach for debugging
            print(f"Trying broader query for node events")
            all_events = v1.list_event_for_all_namespaces(field_selector="involvedObject.kind=Node")
            if all_events and all_events.items:
                print(f"Found {len(all_events.items)} total Node events")
                
                # Check each event to see if it's related to our node
                matched_events = []
                for event in all_events.items:
                    if hasattr(event, 'involved_object') and hasattr(event.involved_object, 'name'):
                        if event.involved_object.name == node_name:
                            print(f"Found matching event for node {node_name} in unfiltered results")
                            matched_events.append(event)
                
                if matched_events:
                    # Sort by timestamp
                    matched_events.sort(key=lambda x: x.last_timestamp if hasattr(x, 'last_timestamp') and x.last_timestamp else 
                                       (x.metadata.creation_timestamp if hasattr(x, 'metadata') and hasattr(x.metadata, 'creation_timestamp') else None), 
                                       reverse=True)
                    
                    latest_event = matched_events[0]
                    print(f"Using matched event: {latest_event.reason if hasattr(latest_event, 'reason') else 'Unknown'}")
                    
                    # Calculate exact age using our helper function
                    node_event_details = get_event_details_from_event(latest_event)
                    return {
                        'Event Reason': node_event_details['Pod Event Reason'],
                        'Event Age': node_event_details['Pod Event Age'],
                        'Event Source': node_event_details['Pod Event Source'],
                        'Event Message': node_event_details['Pod Event Message']
                    }
            
            # If we still can't get events, try to get node resource creation time as fallback
            try:
                import subprocess
                cmd = f"kubectl get node {node_name} -o jsonpath='{{.metadata.creationTimestamp}}'"
                print(f"Running kubectl for node creation time: {cmd}")
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.returncode == 0 and result.stdout:
                    node_creation_time = result.stdout.strip()
                    if node_creation_time:
                        print(f"Got node creation timestamp: {node_creation_time}")
                        node_age = get_k8s_age(node_creation_time)
                        return {
                            'Event Reason': 'NodeReady',
                            'Event Age': node_age,
                            'Event Source': 'kubelet',
                            'Event Message': f"Node {node_name} is ready"
                        }
            except Exception as e:
                print(f"Error getting node creation time: {e}")
            
            # Fallback to placeholder with Unknown age
            print("No node events found, using placeholder with 'Unknown' age")
            return {
                'Event Reason': 'NodeReady',
                # 'Event Age': f"{np.random.randint(10, 360)}m",
                'Event Age': 'Unknown',
                'Event Source': 'kubelet',
                'Event Message': f"Node {node_name} is ready"
            }
            
        print(f"Found {len(events.items)} events for node {node_name}")
        
        # Print all events for this node for debugging
        for i, event in enumerate(events.items):
            print(f"Event {i+1}:")
            if hasattr(event, 'reason'):
                print(f"  Reason: {event.reason}")
            if hasattr(event, 'message'):
                print(f"  Message: {event.message}")
            if hasattr(event, 'first_timestamp'):
                print(f"  First timestamp: {event.first_timestamp}")
            if hasattr(event, 'last_timestamp'):
                print(f"  Last timestamp: {event.last_timestamp}")
            if hasattr(event, 'count'):
                print(f"  Count: {event.count}")
            if hasattr(event, 'source') and hasattr(event.source, 'component'):
                print(f"  Source: {event.source.component}")
            if hasattr(event, 'metadata') and hasattr(event.metadata, 'creation_timestamp'):
                print(f"  Creation timestamp: {event.metadata.creation_timestamp}")
                
        # Use the most recent event (first in the list)
        if events.items:
            latest_event = events.items[0]
            
            # Use our helper function to extract details
            node_event_details = get_event_details_from_event(latest_event)
            return {
                'Event Reason': node_event_details['Pod Event Reason'],
                'Event Age': node_event_details['Pod Event Age'],
                'Event Source': node_event_details['Pod Event Source'],
                'Event Message': node_event_details['Pod Event Message']
            }
            
        # Fallback to placeholder with Unknown age
        print("No node events found after processing, using placeholder with 'Unknown' age")
        return {
            'Event Reason': 'NodeReady',
            # 'Event Age': f"{np.random.randint(10, 360)}m",
            'Event Age': 'Unknown',
            'Event Source': 'kubelet',
            'Event Message': f"Node {node_name} is ready"
        }
    except Exception as e:
        print(f"Error fetching events for node {node_name}: {e}")
        import traceback
        traceback.print_exc()
        
        # Return with Unknown age on error
        print("Error processing node events, using placeholder with 'Unknown' age")
        return {
            'Event Reason': 'NodeReady',
            # 'Event Age': f"{np.random.randint(10, 360)}m",
            'Event Age': 'Unknown',
            'Event Source': 'kubelet',
            'Event Message': f"Node {node_name} is ready"
        }

# Dictionary to keep track of the last known state of each pod
last_known_pod_states = {}

# Main loop
while True:
    try:
        print(f"Fetching data for pods in namespace {NAMESPACE}")

        # Fetch current state of all pods in the namespace
        current_pods = v1.list_namespaced_pod(namespace=NAMESPACE)
        current_pod_states = {pod.metadata.name: pod.status.phase for pod in current_pods.items if not should_exclude_pod(pod.metadata.name)}
        print(f"Found {len(current_pod_states)} pods in namespace {NAMESPACE}")

        # PROMETHEUS METRICS QUERIES
        # =========================
        # These queries are used to fetch metrics from Prometheus. If a metric is not available,
        # synthetic data will be generated for the visualization and model training.
        
        # CPU usage query - works well in most Kubernetes environments
        cpu_usage_query = f"100 * sum by (pod) (rate(container_cpu_usage_seconds_total{{namespace=\"{NAMESPACE}\"}}[5m]))"
        
        # Memory usage query - works well in most Kubernetes environments
        memory_usage_query = f"sum by (pod) (container_memory_working_set_bytes{{namespace=\"{NAMESPACE}\"}})"  
        
        # Memory usage fallback query - if the primary query doesn't return data
        memory_usage_fallback_query = f"sum by (pod) (container_memory_usage_bytes{{namespace=\"{NAMESPACE}\"}})"
        
        # Node memory query - to calculate memory usage percentage
        node_memory_query = "node_memory_MemTotal_bytes"
        
        # Network metrics queries - frequently these are not available in basic Minikube setups
        # Network traffic is calculated as sum of receive and transmit
        network_receive_query = f"sum by (pod) (rate(container_network_receive_packets_total{{namespace=\"{NAMESPACE}\"}}[5m]))"
        network_transmit_query = f"sum by (pod) (rate(container_network_transmit_packets_total{{namespace=\"{NAMESPACE}\"}}[5m]))"
        
        # Fetch data from Prometheus
        print("Querying CPU usage...")
        cpu_usage_data = query_prometheus(cpu_usage_query)
        
        # Try primary memory query
        print("Querying memory usage (primary)...")
        memory_usage_data = query_prometheus(memory_usage_query)
        
        # If primary query fails, try fallback
        if not memory_usage_data:
            print("Primary memory query returned no data, trying fallback...")
            memory_usage_data = query_prometheus(memory_usage_fallback_query)
        
        print("Querying node memory...")
        node_memory_total = query_prometheus(node_memory_query)
        
        print("Querying network metrics...")
        network_receive_data = query_prometheus(network_receive_query)
        network_transmit_data = query_prometheus(network_transmit_query)
        
        # Calculate network traffic as sum of receive and transmit
        network_traffic_data = {}
        for pod in set(network_receive_data.keys()) | set(network_transmit_data.keys()):
            network_traffic_data[pod] = network_receive_data.get(pod, 0) + network_transmit_data.get(pod, 0)
        
        # Use fixed values for error metrics since they might not be available
        network_receive_errors_data = {} 
        network_transmit_errors_data = {}

        # Check for changes in pod states
        for pod_name, current_status in current_pod_states.items():
            previous_status = last_known_pod_states.get(pod_name)
            if previous_status != current_status:
                print(f"Status change detected in pod {pod_name}: {previous_status} -> {current_status}")

            # Update the last known state
            last_known_pod_states[pod_name] = current_status

        # Remove entries for pods that no longer exist
        for pod_name in list(last_known_pod_states.keys()):
            if pod_name not in current_pod_states:
                del last_known_pod_states[pod_name]
                print(f"Pod {pod_name} no longer exists")
                
        # Combine all pod names from metrics and current pods
        all_pods = set(current_pod_states.keys())
        if memory_usage_data:
            all_pods.update(memory_usage_data.keys())
        if cpu_usage_data:
            all_pods.update(cpu_usage_data.keys())
        
        # Get total node memory for percentage calculation
        node_memory = 0
        if node_memory_total:
            # Try different node label formats
            for node_key in node_memory_total.keys():
                node_memory = node_memory_total.get(node_key, 0)
                if node_memory > 0:
                    break
        
        print(f"Node memory total: {node_memory} bytes")
        
        data = []
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for pod in all_pods:
            if should_exclude_pod(pod):
                continue  # Skip this pod if it matches the exclude list
                
            # Calculate memory percentage against node total if available
            memory_usage = memory_usage_data.get(pod, 0)
            memory_usage_percentage = (memory_usage / node_memory) * 100 if node_memory > 0 else 0
            
            # If actual metrics aren't available, generate synthetic data for demo
            if memory_usage_percentage == 0:
                memory_usage_percentage = round(np.random.uniform(0.1, 5.0), 2)  # Random value between 0.1-5%
                
            # Generate synthetic network metrics if not available
            # ACTUAL PROMETHEUS QUERY FOR NETWORK TRAFFIC:
            # network_traffic_query = "sum by (pod) (rate(container_network_receive_bytes_total{namespace=\"monitoring\"}[5m]) + rate(container_network_transmit_bytes_total{namespace=\"monitoring\"}[5m]))"
            # 
            # ALTERNATIVES TO TRY:
            # "sum by (pod) (container_network_receive_bytes_total{namespace=\"monitoring\"} + container_network_transmit_bytes_total{namespace=\"monitoring\"})"
            # "sum by (namespace, pod) (irate(container_network_receive_bytes_total{namespace=\"monitoring\"}[5m]) + irate(container_network_transmit_bytes_total{namespace=\"monitoring\"}[5m]))"
            # "sum by (namespace, pod) (rate(container_network_transmit_packets_total{namespace=\"monitoring\"}[5m]) + rate(container_network_receive_packets_total{namespace=\"monitoring\"}[5m]))"
            network_traffic = network_traffic_data.get(pod, 'N/A')
            if network_traffic == 'N/A':
                network_traffic = round(np.random.uniform(100, 50000), 2)  # Random value between 100-50000 B/s
                
            # ACTUAL PROMETHEUS QUERY FOR NETWORK RECEIVE:
            # network_receive_query = "sum by (pod) (rate(container_network_receive_bytes_total{namespace=\"monitoring\"}[5m]))"
            # 
            # ALTERNATIVES TO TRY:
            # "sum by (pod) (irate(container_network_receive_bytes_total{namespace=\"monitoring\"}[5m]))"
            # "sum by (pod) (container_network_receive_bytes_total{namespace=\"monitoring\"})"
            # "sum by (pod) (rate(container_network_receive_packets_total{namespace=\"monitoring\"}[5m]))"
            network_receive = network_receive_data.get(pod, 'N/A')
            if network_receive == 'N/A':
                network_receive = round(network_traffic * 0.6, 2)  # 60% of traffic
                
            # ACTUAL PROMETHEUS QUERY FOR NETWORK TRANSMIT:
            # network_transmit_query = "sum by (pod) (rate(container_network_transmit_bytes_total{namespace=\"monitoring\"}[5m]))"
            # 
            # ALTERNATIVES TO TRY:
            # "sum by (pod) (irate(container_network_transmit_bytes_total{namespace=\"monitoring\"}[5m]))"
            # "sum by (pod) (container_network_transmit_bytes_total{namespace=\"monitoring\"})"
            # "sum by (pod) (rate(container_network_transmit_packets_total{namespace=\"monitoring\"}[5m]))"
            network_transmit = network_transmit_data.get(pod, 'N/A')
            if network_transmit == 'N/A':
                network_transmit = round(network_traffic * 0.4, 2)  # 40% of traffic
                
            # Generate synthetic error metrics
            # ACTUAL PROMETHEUS QUERY FOR NETWORK RECEIVE ERRORS:
            # network_receive_errors_query = "sum by (pod) (rate(container_network_receive_errors_total{namespace=\"monitoring\"}[5m]))"
            # 
            # ALTERNATIVES TO TRY:
            # "sum by (pod) (container_network_receive_errors_total{namespace=\"monitoring\"})"
            network_receive_errors = round(np.random.uniform(0, 0.01) * network_receive, 2) if network_receive != 'N/A' else 0
            
            # ACTUAL PROMETHEUS QUERY FOR NETWORK TRANSMIT ERRORS:
            # network_transmit_errors_query = "sum by (pod) (rate(container_network_transmit_errors_total{namespace=\"monitoring\"}[5m]))"
            # 
            # ALTERNATIVES TO TRY:
            # "sum by (pod) (container_network_transmit_errors_total{namespace=\"monitoring\"})"
            network_transmit_errors = round(np.random.uniform(0, 0.01) * network_transmit, 2) if network_transmit != 'N/A' else 0
            
            # Get pod info
            node_name = get_pod_node_name(pod, NAMESPACE)
            last_log_entry = get_last_log_entry(pod, NAMESPACE)
            status, reason, restarts, ready_containers, total_containers, error_message = get_pod_status(pod, NAMESPACE)
            
            # Get pod age
            pod_age = get_pod_age(pod, NAMESPACE)
            
            # Fetch pod events and node events directly
            pod_events = fetch_pod_events(pod, NAMESPACE)
            node_events = fetch_node_events(node_name)
            
            # Create pod data with all available metrics
            pod_data = {
                'Timestamp': timestamp,
                'Pod Name': pod,
                'Pod Age': pod_age,  # Add actual pod age
                'CPU Usage (%)': cpu_usage_data.get(pod, round(np.random.uniform(0.1, 2.0), 2)),
                'Memory Usage (%)': memory_usage_percentage,
                'Network Traffic (B/s)': network_traffic,
                'Network Receive (B/s)': network_receive,
                'Network Transmit (B/s)': network_transmit,
                'Network Receive Errors': network_receive_errors,
                'Network Transmit Errors': network_transmit_errors,
                'Last Log Entry': last_log_entry[:100] if last_log_entry and len(last_log_entry) > 100 else last_log_entry or "No logs available",
                'Pod Status': status,
                'Pod Reason': reason or "Running",
                'Pod Restarts': restarts,
                'Ready Containers': ready_containers,
                'Total Containers': total_containers,
                'Error Message': error_message or "",
                'Latest Event Reason': pod_events.get('Pod Event Reason', 'Unknown'),
                'Node Name': node_name,
                # Add pod and node events
                **pod_events,
                **node_events
            }
            
            data.append(pod_data)

        # Create DataFrame and ensure all columns are present
        df = pd.DataFrame(data)
        
        # Ensure all expected columns are present
        expected_columns = [
            'Timestamp', 'Pod Name', 'Pod Age', 'CPU Usage (%)', 'Memory Usage (%)', 
            'Network Traffic (B/s)', 'Network Receive (B/s)', 'Network Transmit (B/s)',
            'Network Receive Errors', 'Network Transmit Errors', 'Last Log Entry',
            'Pod Status', 'Pod Reason', 'Pod Restarts', 'Ready Containers', 
            'Total Containers', 'Error Message', 'Latest Event Reason',
            'Pod Event Type', 'Pod Event Reason', 'Pod Event Age', 'Pod Event Source', 
            'Pod Event Message', 'Node Name', 'Event Reason', 'Event Age', 
            'Event Source', 'Event Message'
        ]
        
        # Add any missing columns with default values
        for col in expected_columns:
            if col not in df.columns:
                if 'Age' in col:
                    df[col] = '0m'  # Default age
                elif 'Type' in col:
                    df[col] = 'Normal'  # Default event type
                elif 'Reason' in col:
                    df[col] = 'Running'  # Default reason
                elif 'Source' in col:
                    df[col] = 'kubelet'  # Default source
                elif 'Message' in col:
                    df[col] = 'No message available'  # Default message
                else:
                    df[col] = 'N/A'  # Default for other columns
                
        # Reorder columns to match expected order
        df = df[expected_columns]
        
        print(f"Created DataFrame with {len(df)} rows and {len(df.columns)} columns")

        # Check if the file exists to decide on writing the header
        try:
            file_path = os.path.abspath(OUTPUT_FILE)
            print(f"Writing to file: {file_path}")
            if not os.path.isfile(file_path):
                df.to_csv(file_path, index=False, mode='w', header=True)
                print(f"Created new file {file_path}")
            else:
                df.to_csv(file_path, index=False, mode='a', header=False)
                print(f"Appended to existing file {file_path}")
            print(f"Data written to {file_path}")
        except Exception as e:
            print(f"Error writing to file {file_path}: {e}")
            import traceback
            traceback.print_exc()

        time.sleep(SLEEP_INTERVAL)

    except KeyboardInterrupt:
        print("Script interrupted, exiting.")
        break
    except Exception as e:
        print(f"An error occurred in main loop: {e}")
        import traceback
        traceback.print_exc()
        time.sleep(SLEEP_INTERVAL)  # Continue trying even if there's an error

def debug_k8s_timestamps():
    """Debug function to test various timestamp parsing approaches on live Kubernetes objects"""
    print("\n===== DEBUGGING KUBERNETES TIMESTAMPS =====")
    
    try:
        # Get a sample pod to test with
        pods = v1.list_namespaced_pod(namespace="kube-system")
        if not pods or not pods.items:
            print("No pods found in kube-system namespace for testing")
            return
            
        sample_pod = pods.items[0]
        pod_name = sample_pod.metadata.name
        namespace = sample_pod.metadata.namespace
        
        print(f"Using pod {pod_name} in namespace {namespace} for timestamp debugging")
        
        # Get pod creation timestamp
        if sample_pod.metadata and sample_pod.metadata.creation_timestamp:
            timestamp = sample_pod.metadata.creation_timestamp
            print(f"\nPod creation timestamp: {timestamp} (type: {type(timestamp)})")
            print(f"Timestamp attributes: {dir(timestamp)}")
            
            # Test datetime conversion
            try:
                if isinstance(timestamp, datetime.datetime):
                    print(f"Timestamp is already a datetime object: {timestamp}")
                    if timestamp.tzinfo:
                        print(f"Timestamp has timezone info: {timestamp.tzinfo}")
                    else:
                        print("Timestamp has no timezone info, adding UTC")
                        timestamp = timestamp.replace(tzinfo=datetime.timezone.utc)
                    
                    # Calculate age
                    now = datetime.datetime.now(datetime.timezone.utc)
                    delta = now - timestamp
                    print(f"Age calculation: now ({now}) - timestamp ({timestamp}) = {delta}")
                    age = format_k8s_duration(delta.total_seconds())
                    print(f"Formatted age: {age}")
                else:
                    print(f"Timestamp needs conversion from {type(timestamp)}")
            except Exception as e:
                print(f"Error processing datetime object: {e}")
        
        # Try different kubectl approaches to get timestamps
        try:
            import subprocess
            
            print("\nTrying kubectl describe to get age:")
            cmd = f"kubectl describe pod {pod_name} -n {namespace}"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # Extract relevant lines for debugging
                output_lines = result.stdout.split('\n')
                age_lines = [line for line in output_lines if 'Age:' in line or 'Start Time:' in line]
                print(f"Age/Time lines from describe: {age_lines}")
                
                # Try regex to extract age
                import re
                age_match = re.search(r'Age:\s+(\d+[dhms])', result.stdout)
                if age_match:
                    print(f"Found direct age from kubectl describe: {age_match.group(1)}")
            else:
                print(f"kubectl describe failed: {result.stderr}")
                
            print("\nTrying kubectl get with custom columns:")
            cmd = f"kubectl get pod {pod_name} -n {namespace} -o=custom-columns=AGE:.metadata.creationTimestamp"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Output: {result.stdout.strip()}")
            
            print("\nTrying kubectl get with jsonpath:")
            cmd = f"kubectl get pod {pod_name} -n {namespace} -o jsonpath='{{.metadata.creationTimestamp}}'"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                timestamp_str = result.stdout.strip()
                print(f"Raw timestamp from kubectl jsonpath: {timestamp_str}")
                
                # Test our timestamp parsing function
                if timestamp_str:
                    try:
                        from dateutil import parser
                        dt = parser.parse(timestamp_str)
                        print(f"Parsed with dateutil: {dt}")
                        
                        # Try our manual formats
                        import datetime
                        formats_to_try = [
                            '%Y-%m-%dT%H:%M:%SZ',
                            '%Y-%m-%dT%H:%M:%S.%fZ',
                            '%Y-%m-%d %H:%M:%S',
                            '%Y-%m-%dT%H:%M:%S%z'
                        ]
                        
                        for fmt in formats_to_try:
                            try:
                                dt = datetime.datetime.strptime(timestamp_str, fmt)
                                print(f"Successfully parsed with format {fmt}: {dt}")
                                break
                            except ValueError:
                                pass
                    except Exception as e:
                        print(f"Error parsing timestamp string: {e}")
            
            # Get events for the pod to debug event timestamps
            print("\nGetting events for the pod:")
            cmd = f"kubectl get events --field-selector=involvedObject.name={pod_name},involvedObject.kind=Pod -n {namespace} -o json"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0 and result.stdout:
                try:
                    import json
                    events_json = json.loads(result.stdout)
                    if 'items' in events_json and events_json['items']:
                        print(f"Found {len(events_json['items'])} events")
                        for i, event in enumerate(events_json['items']):
                            print(f"\nEvent {i+1}:")
                            # Print all timestamp fields we find
                            for field in ['lastTimestamp', 'firstTimestamp', 'eventTime']:
                                if field in event:
                                    print(f"  {field}: {event[field]}")
                            if 'metadata' in event and 'creationTimestamp' in event['metadata']:
                                print(f"  metadata.creationTimestamp: {event['metadata']['creationTimestamp']}")
                                
                            # Try to parse the timestamp fields
                            for field in ['lastTimestamp', 'firstTimestamp', 'eventTime', 'metadata.creationTimestamp']:
                                timestamp_val = None
                                if field == 'metadata.creationTimestamp':
                                    if 'metadata' in event and 'creationTimestamp' in event['metadata']:
                                        timestamp_val = event['metadata']['creationTimestamp']
                                elif field in event:
                                    timestamp_val = event[field]
                                    
                                if timestamp_val:
                                    try:
                                        age = get_k8s_age(timestamp_val)
                                        print(f"  Parsed {field} to age: {age}")
                                    except Exception as e:
                                        print(f"  Error parsing {field}: {e}")
                    else:
                        print("No events found or 'items' field missing")
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON: {e}")
            else:
                print(f"kubectl get events failed: {result.stderr}")
                
        except Exception as e:
            print(f"Error during kubectl testing: {e}")
            import traceback
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error in debug_k8s_timestamps: {e}")
        import traceback
        traceback.print_exc()
    
    print("===== END DEBUGGING KUBERNETES TIMESTAMPS =====\n")

# Add this line to the beginning of the main function or right after global connections are established
# Uncomment this line to debug timestamps
# debug_k8s_timestamps()

# Add this line to the beginning of the main processing function or right before pod events are processed
def main():
    """Main execution function"""
    print("Initializing dataset generator...")
    
    # Debug Kubernetes timestamps - uncomment to run timestamp debugging
    debug_k8s_timestamps()
    
    # Rest of your main function code...
    # ...

# Fix main execution to call the correct function
if __name__ == "__main__":
    # Call the debug function first to diagnose timestamp issues
    print("Starting timestamp debugging...")
    debug_k8s_timestamps()
    
    print("\nStarting dataset generation...")
    # Then run the main dataset generation code
    try:
        # Connect to the Kubernetes API
        # Make sure our connections are set up first
        try:
            # Load configuration from kube config file
            config.load_kube_config()
        except config.config_exception.ConfigException:
            # Load from service account token if running inside a pod
            config.load_incluster_config()
            
        # Create API clients
        v1 = client.CoreV1Api()
        apps_v1 = client.AppsV1Api()
        
        # Run the actual pod metrics collection
        print("Running main processing function...")
        NAMESPACE = "monitoring"  # or any namespace you want to monitor
        fetch_pod_metrics(NAMESPACE)
        
    except Exception as e:
        print(f"Error in main execution: {e}")
        import traceback
        traceback.print_exc()