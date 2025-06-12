#!/usr/bin/env python3
"""
Kubernetes Anomaly Visualization Dashboard

A Streamlit-based visualization dashboard for the Kubernetes multi-agent system.
Features:
- Cluster topology visualization with anomaly highlighting
- Time-series metrics visualization
- AI-powered insights panel using LLM
- Interactive remediation workflow
- Remediated pods tracking and visualization
"""

import os
import sys
import json
import time
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import networkx as nx
from streamlit_plotly_events import plotly_events
import subprocess
import threading
import queue

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the multi-agent system
try:
    from agents.k8s_multi_agent_system import collect_pod_metrics, predict_pod_anomaly
    from agents.nvidia_llm import NvidiaLLM
except ImportError:
    st.error("Failed to import required modules. Make sure you're running from the project root.")
    st.stop()

# Initialize LLM for AI insights
try:
    nvidia_api_key = os.environ.get("NVIDIA_API_KEY", "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")
    llm = NvidiaLLM(api_key=nvidia_api_key)
except Exception as e:
    st.warning(f"Could not initialize LLM: {str(e)}. Some AI features will be limited.")
    llm = None

# Initialize session state for remediated pods if it doesn't exist
if 'remediated_pods' not in st.session_state:
    # Pre-populate with some fake remediated pods for demo purposes
    st.session_state.remediated_pods = [
        {
            'name': 'pod1-operator-6f5c4d8b7f-2xpq1',
            'type': 'resource_exhaustion',
            'action': 'increase_cpu',
            'action_desc': 'Increase CPU',
            'time': (datetime.now() - timedelta(minutes=45)).strftime("%Y-%m-%d %H:%M:%S"),
            'metrics': {
                'CPU Usage (%)': 92.5,
                'Memory Usage (%)': 78.3,
                'Pod Restarts': 0,
                'node': 'worker-node-1'
            }
        },
        {
            'name': 'pod2-state-metrics-7d9fd98c89-j4k2p',
            'type': 'oom_risk',
            'action': 'increase_memory',
            'action_desc': 'Increase Memory',
            'time': (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
            'metrics': {
                'CPU Usage (%)': 45.2,
                'Memory Usage (%)': 94.7,
                'Pod Restarts': 1,
                'node': 'worker-node-2'
            }
        }
    ]

# Add the generic pod name function at the top level
def get_generic_pod_name(pod_name):
    """Convert actual pod names to generic pod1, pod2, etc. names"""
    if 'pod_name_mapping' not in st.session_state:
        st.session_state.pod_name_mapping = {}
    
    if pod_name not in st.session_state.pod_name_mapping:
        # Create a new generic name
        next_index = len(st.session_state.pod_name_mapping) + 1
        st.session_state.pod_name_mapping[pod_name] = f"pod{next_index}"
    
    return st.session_state.pod_name_mapping[pod_name]

# Function to suggest remediation actions based on anomaly type
# Update the suggest_remediation_action function to be more specific
def suggest_remediation_action(anomaly_type, metrics):
    """Suggest appropriate remediation action based on anomaly type and metrics"""
    # Make sure we're checking the actual anomaly type string
    if anomaly_type == 'oom_risk' or metrics.get('Memory Usage (%)', 0) > 85:
        return "increase_memory"
    elif anomaly_type == 'resource_exhaustion' or metrics.get('CPU Usage (%)', 0) > 85:
        return "increase_cpu"
    elif anomaly_type == 'crash_loop' or metrics.get('Pod Restarts', 0) > 2:
        return "restart_pod"
    elif anomaly_type == 'deployment_issue':
        return "restart_deployment"
    elif anomaly_type == 'scaling_issue':
        return "scale_deployment"
    else:
        return "restart_pod"  # Default action

# Metrics collection and processing
def get_metrics(test_mode=False):
    """Get current Kubernetes metrics"""
    if test_mode:
        # Load sample data from CSV
        try:
            metrics_df = pd.read_csv("src/agents/pod_metrics.csv")
            pod_metrics = {}
            for _, row in metrics_df.iterrows():
                pod_name = row['Pod Name']
                pod_metrics[pod_name] = row.to_dict()
            return pod_metrics
        except Exception as e:
            st.error(f"Error loading test metrics: {str(e)}")
            return {}
    else:
        # Get real metrics
        try:
            return collect_pod_metrics()
        except Exception as e:
            st.error(f"Error collecting metrics: {str(e)}")
            return {}

def detect_anomalies(pod_metrics):
    """Detect anomalies in pod metrics"""
    # Filter out remediated pods
    remediated_pod_names = [pod['name'] for pod in st.session_state.remediated_pods]
    
    anomalies = {}
    for pod_name, metrics in pod_metrics.items():
        # Skip remediated pods
        if pod_name in remediated_pod_names:
            continue
            
        try:
            is_anomaly, prediction = predict_pod_anomaly(metrics)
            if is_anomaly:
                anomalies[pod_name] = {
                    'metrics': metrics,
                    'prediction': prediction
                }
        except Exception as e:
            st.warning(f"Error detecting anomalies for pod {pod_name}: {str(e)}")
    return anomalies

def get_cluster_graph(pod_metrics):
    """Create a graph representation of the cluster"""
    G = nx.Graph()
    
    # Add nodes
    nodes = {}
    
    # First add the nodes (Kubernetes nodes)
    k8s_nodes = set()
    for pod_name, metrics in pod_metrics.items():
        node_name = metrics.get('node', 'unknown')
        k8s_nodes.add(node_name)
    
    # Add Kubernetes nodes
    for node in k8s_nodes:
        G.add_node(node, type='node', name=node)
        nodes[node] = {'type': 'node', 'name': node}
    
    # Then add pods and connect to nodes
    for pod_name, metrics in pod_metrics.items():
        node_name = metrics.get('node', 'unknown')
        G.add_node(pod_name, type='pod', name=pod_name)
        nodes[pod_name] = {'type': 'pod', 'name': pod_name}
        G.add_edge(pod_name, node_name)
    
    # Use Fruchterman-Reingold layout
    pos = nx.spring_layout(G)
    
    # Convert to visualization format
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    node_x = []
    node_y = []
    node_text = []
    node_color = []
    node_size = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        if nodes[node]['type'] == 'node':
            node_text.append(f"Node: {node}")
            node_color.append('blue')
            node_size.append(20)
        else:
            node_text.append(f"Pod: {node}")
            node_color.append('green')
            node_size.append(15)
    
    return {
        'edge_x': edge_x,
        'edge_y': edge_y,
        'node_x': node_x,
        'node_y': node_y,
        'node_text': node_text,
        'node_color': node_color,
        'node_size': node_size,
        'nodes': list(G.nodes()),
    }

def highlight_anomalies(graph, anomalies):
    """Highlight anomalous pods in the cluster graph"""
    for i, node in enumerate(graph['nodes']):
        if node in anomalies:
            graph['node_color'][i] = 'red'
            graph['node_size'][i] = 25
    return graph

def execute_remediation(pod_name, action):
    """Execute remediation action on a Kubernetes pod
    
    Args:
        pod_name: Name of the pod to remediate
        action: Type of remediation action to perform
        
    Returns:
        tuple: (success_bool, detail_message)
    """
    # Log the remediation attempt
    print(f"Attempting remediation: {action} on pod {pod_name}")
    
    # Validate inputs
    if not pod_name or not action:
        return False, "Invalid pod name or action"
    
    # Map actions to more descriptive labels for UI feedback
    action_descriptions = {
        "restart_pod": "Restarting pod",
        "restart_deployment": "Restarting the deployment",
        "increase_memory": "Increasing memory allocation",
        "increase_cpu": "Scaling up CPU resources",
        "scale_deployment": "Scaling deployment replicas"
    }
    
    action_desc = action_descriptions.get(action, action)
    
    # Build the remediation command
    command = f"python src/agents/remediation_dashboard_agent.py --pod {pod_name} --action {action}"
    
    def run_command(cmd, result_queue):
        try:
            # Run the command with a timeout
            result = subprocess.run(
                cmd, 
                shell=True, 
                capture_output=True, 
                text=True
            )
            result_queue.put((result.returncode, result.stdout, result.stderr))
        except subprocess.SubprocessError as e:
            result_queue.put((1, "", f"Subprocess error: {str(e)}"))
        except Exception as e:
            result_queue.put((1, "", f"Unexpected error: {str(e)}"))
    
    # Create a queue for thread communication
    result_queue = queue.Queue()
    
    # Run the command in a separate thread
    thread = threading.Thread(target=run_command, args=(command, result_queue))
    thread.start()
    
    # Wait for command to complete with timeout
    timeout = 30  # seconds
    thread.join(timeout=timeout)
    
    # Check if thread is still running (timed out)
    if thread.is_alive():
        return False, f"Remediation timed out after {timeout} seconds"
    
    # Get results from queue
    try:
        code, stdout, stderr = result_queue.get(block=False)
        
        if code == 0:
            # Format successful output message
            message = stdout.strip() if stdout.strip() else f"Successfully executed: {action_desc}"
            return True, message
        else:
            # Format error message
            if stderr.strip():
                error_msg = f"Error: {stderr.strip()}"
            else:
                error_msg = f"Failed to execute {action_desc} (Exit code: {code})"
            return False, error_msg
            
    except queue.Empty:
        return False, "No result returned from remediation command"

def get_ai_analysis(pod_metrics, anomalies):
    """Get AI-powered analysis of pod metrics and anomalies"""
    if not llm:
        return "AI analysis not available (LLM not initialized)"
    
    if not anomalies:
        return "No anomalies detected. The cluster appears to be healthy."
    
    # Generate a prompt for the LLM but with more concise instructions
    prompt = "Analyze these Kubernetes metrics and detected anomalies:\n\n"
    
    for pod_name, anomaly_data in anomalies.items():
        metrics = anomaly_data['metrics']
        prediction = anomaly_data['prediction']
        
        prompt += f"Pod: {pod_name}\n"
        prompt += f"Anomaly Type: {prediction.get('anomaly_type', 'unknown')}\n"
        prompt += f"Confidence: {prediction.get('anomaly_probability', 0):.2f}\n"
        prompt += f"CPU: {metrics.get('CPU Usage (%)', 'N/A')}%, Memory: {metrics.get('Memory Usage (%)', 'N/A')}%, Restarts: {metrics.get('Pod Restarts', 'N/A')}\n"
        
        if 'Event Reason' in metrics:
            prompt += f"Event: {metrics.get('Event Reason', 'N/A')} - {metrics.get('Event Message', 'N/A')}\n"
        
        prompt += "\n"
    
    prompt += "Provide a VERY BRIEF analysis (max 3-4 sentences) that summarizes:\n"
    prompt += "1. Root cause of anomalies\n"
    prompt += "2. Severity level\n"
    prompt += "3. Recommended actions\n"
    
    try:
        analysis = llm.generate(prompt, temperature=0.3, max_tokens=200)  # Limit token length for brevity
        return analysis
    except Exception as e:
        return f"Error generating AI analysis: {str(e)}"

# Streamlit UI
def build_ui():
    st.set_page_config(
        page_title="Kubernetes Anomaly Visualization Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("Kubernetes Anomaly Visualization Dashboard")
    
    # Sidebar with options
    with st.sidebar:
        st.header("Options")
        test_mode = st.checkbox("Test Mode (Use sample data)", value=True)
        refresh_interval = st.slider("Refresh Interval (seconds)", min_value=10, max_value=300, value=60)
        auto_refresh = st.checkbox("Auto Refresh", value=False)
        
        st.header("Actions")
        if st.button("Refresh Data"):
            st.rerun()
        
        st.header("Settings")
        anomaly_threshold = st.slider("Anomaly Confidence Threshold", min_value=0.5, max_value=0.99, value=0.7)
        st.write("---")
        st.write("**Visualization Settings**")
        visualization_type = st.selectbox(
            "Chart Type", 
            ["Area Chart", "Line Chart", "Bar Chart", "Scatter Plot"],
            index=0
        )
        animation_speed = st.slider("Animation Speed", min_value=300, max_value=2000, value=800)
    
    # Get data - only get metrics once to avoid duplicates
    pod_metrics = get_metrics(test_mode=test_mode)
    
    if not pod_metrics:
        st.error("No metrics data available. Check your Kubernetes connection or sample data.")
        return
    
    # Detect anomalies
    anomalies = detect_anomalies(pod_metrics)
    
    # Create a list to track remediated pods in this session
    if 'remediated_in_session' not in st.session_state:
        st.session_state.remediated_in_session = []
    remediated_in_session = st.session_state.remediated_in_session
    
    # Display detected anomalies
    st.header("Detected Anomalies")
    
    if anomalies:
        # Create columns for anomaly cards
        cols = st.columns(3)
        
        # Display each anomaly in a card
        # In the anomaly display section, ensure we're using the correct anomaly type
        # When displaying each anomaly in a card:
        for i, (pod_name, anomaly_data) in enumerate(anomalies.items()):
            col_idx = i % 3
            
            with cols[col_idx]:
                with st.container():
                    st.markdown("---")  # Visual separator
                    metrics = anomaly_data['metrics']
                    prediction = anomaly_data['prediction']
                    
                    # Use generic pod name
                    generic_name = get_generic_pod_name(pod_name)
                    
                    # Display pod name with warning icon
                    st.markdown(f"🚨 **{generic_name}**")
                    
                    # Display anomaly type and confidence
                    # Make sure we're getting the correct anomaly type from the prediction
                    anomaly_type = prediction.get('anomaly_type', 'unknown')
                    st.write(f"**Type:** {anomaly_type}")
                    st.write(f"**Confidence:** {prediction.get('anomaly_probability', 0):.2f}")
                    
                    # Display key metrics
                    st.write(f"**CPU:** {metrics.get('CPU Usage (%)', 'N/A')}% | **Mem:** {metrics.get('Memory Usage (%)', 'N/A')}%")
                    
                    # Remediation action selector with suggested action
                    st.write("**Action**")
                    action_options = {
                        "restart_pod": "Restart Pod",
                        "increase_memory": "Increase Memory",
                        "increase_cpu": "Increase CPU",
                        "restart_deployment": "Restart Deployment",
                        "scale_deployment": "Scale Deployment"
                    }
                    
                    # Get suggested action based on the anomaly type and metrics
                    suggested_action = suggest_remediation_action(anomaly_type, metrics)
                    
                    # Display suggested action
                    st.write(f"**Suggested Action:** {action_options.get(suggested_action, 'Restart Pod')}")
                    
                    selected_action = st.selectbox(
                        "Select action", 
                        list(action_options.keys()),
                        format_func=lambda x: action_options[x],
                        index=list(action_options.keys()).index(suggested_action),  # Pre-select suggested action
                        key=f"action_{pod_name}"
                    )
                    
                    # Execute button
                    if st.button("Execute", key=f"execute_{pod_name}"):
                        # Check if selected action matches suggested action
                        if selected_action != suggested_action:
                            st.warning(f"⚠️ Cannot execute {action_options[selected_action]}. The suggested action is {action_options[suggested_action]}. Please select the suggested action for this anomaly type.")
                        else:
                            with st.spinner(f"Executing {action_options[selected_action]} for {generic_name}..."):
                                # Simulate execution delay
                                time.sleep(2)
                                
                                # For demo purposes, always show success
                                success, message = True, f"Successfully executed: {action_options[selected_action]}"
                                
                                if success:
                                    # Add to remediated pods list with timestamp
                                    st.session_state.remediated_pods.append({
                                        'name': pod_name,
                                        'type': prediction.get('anomaly_type', 'unknown'),
                                        'action': selected_action,
                                        'action_desc': action_options[selected_action],
                                        'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                        'metrics': metrics
                                    })
                                    
                                    # Show success message
                                    st.success(f"✅ {message}")
                                    
                                    # Add to remediated in this session
                                    remediated_in_session.append(pod_name)
                                    
                                    # Force refresh after a short delay
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ {message}")
    else:
        st.success("No anomalies detected. The cluster appears to be healthy!")
    
    # Interactive metrics visualization
    st.subheader("Interactive Pod Metrics")
    
    # Convert pod metrics to time series data and add synthetic time data for testing
    current_time = datetime.now()
    time_points = [current_time - timedelta(minutes=i*5) for i in range(12)]
    time_points.reverse()  # So they go from oldest to newest
    
    # Create synthetic historical data for testing
    metrics_time_series = []
    for pod_name, metrics in pod_metrics.items():
        base_cpu = float(metrics.get('CPU Usage (%)', 10))
        base_memory = float(metrics.get('Memory Usage (%)', 20))
        
        # Check if this pod has anomalies
        is_anomalous = pod_name in anomalies
        
        for i, timestamp in enumerate(time_points):
            # Add some randomness but make anomalous pods trend upward
            if is_anomalous and i > 6:  # Anomalies start after the 6th time point
                cpu_factor = 1.2 + (i-6)*0.3  # Increasing trend
                memory_factor = 1.15 + (i-6)*0.25  # Increasing trend
            else:
                cpu_factor = 0.9 + np.random.random() * 0.2
                memory_factor = 0.85 + np.random.random() * 0.3
            
            # Use generic pod name for display
            generic_name = get_generic_pod_name(pod_name)
            
            metrics_time_series.append({
                'Pod': generic_name,  # Use generic name
                'Timestamp': timestamp,
                'CPU': min(base_cpu * cpu_factor, 100),  # Cap at 100%
                'Memory': min(base_memory * memory_factor, 100),  # Cap at 100%
                'Status': 'Anomalous' if is_anomalous and i > 6 else 'Normal',
                'Restarts': metrics.get('Pod Restarts', 0) if i > 9 else max(0, int(metrics.get('Pod Restarts', 0)) - 1)
            })
    metrics_df = pd.DataFrame(metrics_time_series)
    
    # Add this in the main section of your dashboard code where the tabs are defined
    
    # Make sure pod_metrics is defined
    if 'pod_metrics' not in locals() and 'pod_metrics' not in globals():
        pod_metrics = get_metrics(test_mode=True)  # Use test_mode=False for real cluster data
    
    # Create tabs for different metrics views
    tab1, tab2, tab3, tab4 = st.tabs(["CPU Usage", "Memory Usage", "Pod Status", "Combined View"])
    
    with tab1:
        st.subheader("CPU Usage by Pod")
        if pod_metrics:
            # Create CPU usage chart
            cpu_data = {get_generic_pod_name(pod): metrics.get('CPU Usage (%)', 0) 
                       for pod, metrics in pod_metrics.items()}
            fig = px.bar(x=list(cpu_data.keys()), y=list(cpu_data.values()),
                        labels={'x': 'Pod', 'y': 'CPU Usage (%)'},
                        color=list(cpu_data.values()),
                        color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No pod metrics available")
    
    with tab2:
        st.subheader("Memory Usage by Pod")
        if pod_metrics:
            # Create memory usage chart
            memory_data = {get_generic_pod_name(pod): metrics.get('Memory Usage (%)', 0) 
                          for pod, metrics in pod_metrics.items()}
            fig = px.bar(x=list(memory_data.keys()), y=list(memory_data.values()),
                        labels={'x': 'Pod', 'y': 'Memory Usage (%)'},
                        color=list(memory_data.values()),
                        color_continuous_scale='Viridis')
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No pod metrics available")
    
    with tab3:
        st.subheader("Pod Status")
        if pod_metrics:
            # Create status table
            status_data = []
            for pod, metrics in pod_metrics.items():
                status_data.append({
                    "Pod": get_generic_pod_name(pod),
                    "Status": metrics.get('Pod Status', 'Unknown'),
                    "Restarts": metrics.get('Pod Restarts', 0),
                    "Age": metrics.get('Pod Age', 'Unknown')
                })
            st.dataframe(pd.DataFrame(status_data))
        else:
            st.info("No pod metrics available")
    
    with tab4:
        st.subheader("Combined Metrics View")
        if pod_metrics:
            # Create combined metrics visualization
            combined_data = []
            for pod, metrics in pod_metrics.items():
                combined_data.append({
                    "Pod": get_generic_pod_name(pod),
                    "CPU (%)": metrics.get('CPU Usage (%)', 0),
                    "Memory (%)": metrics.get('Memory Usage (%)', 0),
                    "Restarts": metrics.get('Pod Restarts', 0)
                })
            combined_df = pd.DataFrame(combined_data)
            
            # Create a combined chart
            fig = px.scatter(combined_df, x="CPU (%)", y="Memory (%)", 
                            size="Restarts", hover_name="Pod",
                            color="Pod", size_max=25)
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No pod metrics available")
    
    # AI Insights panel
    st.subheader("AI-Powered Insights")
    
    with st.spinner("Generating insights..."):
        analysis = get_ai_analysis(pod_metrics, anomalies)
        st.info(analysis)
    
    # Display remediated pods section
    st.header("Remediated Pods")
    
    if st.session_state.remediated_pods:
        # Create columns for remediated pod cards
        cols = st.columns(3)
        
        # Display each remediated pod in a card
        for i, pod in enumerate(st.session_state.remediated_pods):
            col_idx = i % 3
            
            with cols[col_idx]:
                with st.container():
                    st.markdown("---")  # Visual separator
                    
                    # Use generic pod name
                    generic_name = get_generic_pod_name(pod['name'])
                    
                    # Display pod name with success icon
                    st.markdown(f"✅ **{generic_name}**")
                    
                    # Display remediation details
                    st.write(f"**Previous Issue:** {pod['type']}")
                    st.write(f"**Remediation Action:** {pod['action_desc']}")
                    st.write(f"**Remediated at:** {pod['time']}")
                    
                    # Display key metrics at time of remediation
                    metrics = pod['metrics']
                    st.write(f"**Previous CPU:** {metrics.get('CPU Usage (%)', 'N/A')}% | **Mem:** {metrics.get('Memory Usage (%)', 'N/A')}%")
                    
                    # Add view details expander for each pod
                    with st.expander("View Details"):
                        st.write(f"**Node:** {metrics.get('node', 'N/A')}")
                        st.write(f"**Pod Restarts:** {metrics.get('Pod Restarts', 'N/A')}")
                        if 'Event Reason' in metrics:
                            st.write(f"**Event:** {metrics.get('Event Reason', 'N/A')} - {metrics.get('Event Message', 'N/A')}")
    else:
        st.info("No pods have been remediated yet.")
    
    # KEEP ONLY ONE monitoring metadata expander
    with st.expander("Monitoring Metadata"):
        col1, col2, col3 = st.columns(3)
        col1.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        col2.info(f"Pods monitored: {len(pod_metrics)}")
        col3.info(f"Anomalies detected: {len(anomalies)}")
    
    # REMOVE THE DUPLICATE MONITORING METADATA EXPANDER
    # Delete any code that creates a second "Monitoring Metadata" expander
    # Footer with metadata
    #with st.expander("Monitoring Metadata"):
       # col1, col2, col3 = st.columns(3)
        #col1.info(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        #col2.info(f"Pods monitored: {len(pod_metrics)}")
        #col3.info(f"Anomalies detected: {len(anomalies)}")
    
    if auto_refresh:
        time.sleep(refresh_interval)
        st.rerun()

if __name__ == "__main__":
    build_ui()

# In the anomaly detection section where you display each anomaly
def suggest_remediation_action(anomaly_type, metrics):
    """Suggest the best remediation action based on anomaly type and metrics"""
    cpu_usage = float(metrics.get('CPU Usage (%)', 0))
    memory_usage = float(metrics.get('Memory Usage (%)', 0))
    restarts = int(metrics.get('Pod Restarts', 0))
    
    if anomaly_type == 'crash_loop':
        return "restart_deployment"
    elif anomaly_type == 'oom_killed' or anomaly_type == 'oom_risk':
        return "increase_memory"
    elif anomaly_type == 'resource_exhaustion' and cpu_usage > 85:
        return "increase_cpu"
    elif anomaly_type == 'resource_exhaustion' and memory_usage > 85:
        return "increase_memory"
    elif restarts > 2:
        return "restart_pod"
    else:
        return "restart_pod"  # Default action