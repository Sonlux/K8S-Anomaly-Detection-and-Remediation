#!/usr/bin/env python3
"""
Kubernetes Multi-Agent System Driver

This script integrates multiple AI agents for Kubernetes monitoring, 
anomaly detection, and remediation in a single unified system.

Features:
- Metrics collection and monitoring from Prometheus
- Anomaly detection using ML models
- LLM-powered analysis of system state
- Automated remediation with approval workflow
- LangGraph orchestration of all agent interactions
"""

import os
import sys
import time
import pandas as pd
import numpy as np
import logging
import json
import argparse
import signal
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Any, TypedDict, Optional, Tuple

# LangChain and LangGraph imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END

# Kubernetes imports
try:
    from kubernetes import client, config, watch
except ImportError:
    print("Warning: Kubernetes client not installed. Some features may not work.")

# Try to import local modules
try:
    from anomaly_prediction import predict_anomalies
except ImportError:
    # Define a stub function for testing
    def predict_anomalies(data):
        return pd.DataFrame({
            'predicted_anomaly': [1],
            'anomaly_probability': [0.85],
            'anomaly_type': ['resource_exhaustion']
        })

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('k8s_multi_agent.log')
    ]
)
logger = logging.getLogger("k8s-multi-agent")

# Global flags and configurations
TEST_MODE = os.environ.get("K8S_TEST_MODE", "false").lower() == "true"
DEBUG_MODE = os.environ.get("K8S_DEBUG_MODE", "false").lower() == "true"

if DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
    
# Global process management variables
stop_event_triggered = False

# LLM API configuration
API_CONFIG = {
    'openai_api_key': os.environ.get("OPENAI_API_KEY"),
    'nvidia_api_key': os.environ.get("NVIDIA_API_KEY", "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"),
    'use_llm': True,
    'use_nvidia_direct': False,
    'llm_provider': "auto"  # "auto", "openai", "nvidia", "none"
}

# Try to import NVIDIA LLM wrapper
try:
    from nvidia_llm import NvidiaLLM
    API_CONFIG['nvidia_available'] = True
except ImportError:
    API_CONFIG['nvidia_available'] = False

# Initialize Kubernetes client
try:
    if not TEST_MODE:
        try:
            config.load_kube_config()
            logger.info("Loaded Kubernetes config from default location")
        except Exception:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes configuration")
        
        core_api = client.CoreV1Api()
        apps_api = client.AppsV1Api()
    else:
        logger.info("Test mode enabled - using mock Kubernetes client")
        from unittest.mock import MagicMock
        core_api = MagicMock()
        apps_api = MagicMock()
except Exception as e:
    logger.error(f"Failed to initialize Kubernetes client: {e}")
    core_api = None
    apps_api = None

# Define state classes for each agent type
class MonitoringState(TypedDict):
    """State for the monitoring agent."""
    messages: List[Any]
    metrics_data: Dict[str, Any]
    pod_metrics: Dict[str, Dict[str, Any]]
    pod_history: Dict[str, List[Dict[str, Any]]]
    status: str
    last_run_time: float
    action: str

class AnomalyState(TypedDict):
    """State for the anomaly detection agent."""
    messages: List[Any]
    metrics_data: Dict[str, Any]
    prediction_result: Dict[str, Any]
    pod_info: Dict[str, Any]
    action: str

class RemediationState(TypedDict):
    """State for the remediation agent."""
    messages: List[Any]
    prediction: Dict[str, Any]
    pod_info: Dict[str, Any]
    remediation_plan: Dict[str, Any]
    approval_status: str  # "pending", "approved", "rejected", "complete"
    action_status: str  # "waiting", "in_progress", "success", "failed"

class OrchestratorState(TypedDict):
    """Main state for the orchestrator."""
    messages: List[Any]
    monitoring_state: Optional[MonitoringState]
    anomaly_state: Optional[AnomalyState]
    remediation_state: Optional[RemediationState]
    active_agent: str  # "monitoring", "anomaly", "remediation", "none"
    pods_with_anomalies: Dict[str, Dict[str, Any]]
    current_pod: Optional[str]
    approved_remediations: List[str]
    approval_queue: List[Dict[str, Any]]
    command: Optional[str]
    status: str
    iteration_count: int  # Add iteration counter

class LlamaLLM:
    """Wrapper for Llama LLM API"""
    
    def __init__(self, api_key=None, base_url=None):
        """Initialize the Llama LLM client.
        
        Args:
            api_key: Llama API key (default: reads from LLAMA_API_KEY env var)
            base_url: Llama API base URL (default: reads from LLAMA_API_URL env var)
        """
        self.api_key = api_key or os.environ.get("LLAMA_API_KEY")
        if not self.api_key:
            raise ValueError("Llama API key not provided and LLAMA_API_KEY env var not set")
        
        # Auto-detect if this is a NVIDIA API key and adjust the base_url accordingly
        if self.api_key.startswith("nvapi-"):
            logger.info("Detected NVIDIA API key, using NVIDIA endpoint")
            # Always use NVIDIA endpoint when NVIDIA API key is provided, regardless of base_url
            self.base_url = "https://integrate.api.nvidia.com/v1"
            self.model = "nvidia/llama-3.1-nemotron-70b-instruct"
            logger.info(f"Using NVIDIA endpoint: {self.base_url} with model: {self.model}")
        else:
            # For non-NVIDIA keys, use provided base_url or default
            self.base_url = base_url or os.environ.get("LLAMA_API_URL", "https://api.llama-api.com")
            self.model = "llama-3"
            logger.info(f"Using Llama endpoint: {self.base_url} with model: {self.model}")
        
        # Initialize the client using OpenAI client
        try:
            from openai import OpenAI
            self.client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key
            )
            logger.info(f"Llama LLM client initialized with OpenAI client to endpoint: {self.base_url}")
        except ImportError:
            # Fallback to langchain if OpenAI package is not available
            from langchain_openai import ChatOpenAI
            self.chat_model = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model_name=self.model
            )
            logger.info(f"Llama LLM client initialized with LangChain to endpoint: {self.base_url}")
    
    def generate(self, prompt, model=None, temperature=0.5, max_tokens=1024, stream=False):
        """Generate a response from the Llama LLM.
        
        Args:
            prompt: The prompt to send to the model
            model: The model ID (defaults to auto-detected model based on API key)
            temperature: Sampling temperature (default: 0.5)
            max_tokens: Maximum tokens to generate (default: 1024)
            stream: Whether to stream the response (default: False)
            
        Returns:
            Generated text if stream=False, or a generator yielding text chunks if stream=True
        """
        # Use provided model or default to the auto-detected one
        model = model or self.model
        
        try:
            if hasattr(self, 'client'):
                # Using direct OpenAI client
                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream
                )
                
                if stream:
                    # Return a generator that yields text chunks
                    def generate_stream():
                        for chunk in completion:
                            if chunk.choices[0].delta.content is not None:
                                yield chunk.choices[0].delta.content
                    return generate_stream()
                else:
                    # Return the full response
                    return completion.choices[0].message.content
            else:
                # Using LangChain
                from langchain_core.messages import HumanMessage
                
                if stream:
                    logger.warning("Streaming not supported with LangChain fallback")
                
                messages = [HumanMessage(content=prompt)]
                response = self.chat_model.invoke(messages)
                return response.content
                
        except Exception as e:
            logger.error(f"Error generating response with Llama API: {str(e)}")
            raise
    
    def analyze_k8s_metrics(self, metrics_data, prediction_result):
        """Analyze Kubernetes metrics and provide recommendations.
        
        Args:
            metrics_data: Dictionary containing pod metrics
            prediction_result: Dictionary containing prediction results
            
        Returns:
            Analysis text from the LLM
        """
        prompt = f"""As a Kubernetes expert, analyze these pod metrics and anomaly prediction:

METRICS:
{metrics_data}

PREDICTION:
{prediction_result}

Provide a concise analysis explaining:
1. What's happening with this pod
2. Potential root causes for any detected issues
3. Specific, actionable recommendations to resolve the problems
4. Priority level of the issue (Critical, High, Medium, Low)

If events are present, explain how the event age and count relate to the detected issues.
"""
        
        try:
            return self.generate(prompt, max_tokens=1024, temperature=0.3)
        except Exception as e:
            logger.error(f"Failed to analyze metrics: {str(e)}")
            return f"Error analyzing metrics: {str(e)}"
    
    def invoke(self, prompt):
        """LangChain compatible invoke method.
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            A response object with a content attribute
        """
        class Response:
            def __init__(self, text):
                self.content = text
        
        if isinstance(prompt, str):
            text = self.generate(prompt)
        elif isinstance(prompt, list):
            # Handle direct list of messages (common LangChain pattern)
            try:
                # Extract the last message which should contain the actual prompt
                last_message = prompt[-1]
                if hasattr(last_message, 'content'):
                    text = self.generate(last_message.content)
                else:
                    text = self.generate(str(last_message))
            except Exception as e:
                logger.error(f"Error processing message list: {str(e)}")
                text = f"Error processing message list: {str(e)}"
        else:
            # Handle LangChain ChatPromptTemplate format
            try:
                if hasattr(prompt, 'messages'):
                    messages = prompt.messages
                    last_message = messages[-1]
                    if hasattr(last_message, 'content'):
                        text = self.generate(last_message.content)
                    else:
                        text = self.generate(str(last_message))
                else:
                    text = self.generate(str(prompt))
            except Exception as e:
                logger.error(f"Error processing LangChain prompt: {str(e)}")
                text = f"Error processing prompt: {str(e)}"
        
        return Response(text)

# Initialize LLM
def initialize_llm():
    """Initialize the LLM based on available APIs."""
    global API_CONFIG
    
    # Get API keys from environment
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    nvidia_api_key = os.environ.get("NVIDIA_API_KEY", "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")
    llama_api_key = os.environ.get("LLAMA_API_KEY")
    
    # If Llama API key not provided but we want to use Llama, 
    # use NVIDIA key as fallback for compatibility
    if API_CONFIG.get("llm") == "llama" and not llama_api_key:
        llama_api_key = nvidia_api_key
        logger.info("Using NVIDIA API key as fallback for Llama API")
    
    llm_provider = API_CONFIG.get("llm", "auto")
    
    # Try initializing LLMs in order of preference
    # 1. First try Llama if key is available and provider is set to auto or llama
    if llama_api_key and (llm_provider == "auto" or llm_provider == "llama"):
        try:
            logger.info("Initializing with Llama API")
            
            # Initialize LlamaLLM with the appropriate URL
            # The LlamaLLM class will auto-detect if this is a NVIDIA key and adjust accordingly
            llm = LlamaLLM(api_key=llama_api_key)
            
            # Set provider based on the key type used
            if llama_api_key.startswith("nvapi-"):
                API_CONFIG["llm_provider"] = "nvidia-via-llama"
            else:
                API_CONFIG["llm_provider"] = "llama"
                
            logger.info(f"Successfully initialized Llama API")
            logger.info(f"LLM initialization complete. Provider: {API_CONFIG['llm_provider']}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize Llama API: {e}")
            # Continue to next option
    
    # 2. Try NVIDIA API if key available and provider is set to auto or nvidia
    if nvidia_api_key and nvidia_api_key.startswith("nvapi-") and (llm_provider == "auto" or llm_provider == "nvidia"):
        try:
            # First try to use the custom wrapper
            logger.info("Initializing with NVIDIA API")
            
            # Try importing NVIDIA LLM wrapper
            try:
                from nvidia_llm import NvidiaLLM
                NVIDIA_LLM_AVAILABLE = True
            except ImportError:
                logger.warning("NVIDIA LLM wrapper not available, will try direct initialization")
                NVIDIA_LLM_AVAILABLE = False
            
            if NVIDIA_LLM_AVAILABLE:
                try:
                    nvidia_llm = NvidiaLLM(api_key=nvidia_api_key)
                    logger.info("Successfully initialized NVIDIA API via custom wrapper")
                    API_CONFIG["llm_provider"] = "nvidia"
                    logger.info(f"LLM initialization complete. Provider: {API_CONFIG['llm_provider']}")
                    return nvidia_llm
                except Exception as e:
                    logger.error(f"Error initializing NVIDIA LLM with custom wrapper: {e}")
            
            # Fallback to LangChain/OpenAI
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    base_url="https://integrate.api.nvidia.com/v1",
                    api_key=nvidia_api_key
                )
                logger.info("Successfully initialized NVIDIA API via LangChain")
                API_CONFIG["llm_provider"] = "nvidia"
                logger.info(f"LLM initialization complete. Provider: {API_CONFIG['llm_provider']}")
                return llm
            except Exception as e:
                logger.error(f"Error initializing NVIDIA API via LangChain: {e}")
        except Exception as e:
            logger.error(f"Failed to initialize NVIDIA API: {e}")
            # Continue to next option
    
    # 3. Fallback to OpenAI if key available
    if openai_api_key and (llm_provider == "auto" or llm_provider == "openai"):
        try:
            logger.info("Initializing with OpenAI API")
            from langchain_openai import ChatOpenAI
            llm = ChatOpenAI(api_key=openai_api_key)
            logger.info("Successfully initialized OpenAI API")
            API_CONFIG["llm_provider"] = "openai"
            logger.info(f"LLM initialization complete. Provider: {API_CONFIG['llm_provider']}")
            return llm
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI API: {e}")
            # Continue to fallback
    
    # Basic analyzer fallback if all LLMs fail
    logger.warning("No valid LLM configurations found. Running without LLM.")
    
    # Create a basic analyzer that doesn't require LLM
    class BasicAnalyzer:
        def analyze_k8s_metrics(self, metrics, prediction):
            return generate_basic_analysis(metrics, prediction)
            
        def generate(self, prompt, temperature=0.7):
            return f"[Basic Mode] I'm unable to generate responses without an LLM. You asked: {prompt}"
            
        def invoke(self, prompt):
            class Response:
                def __init__(self, text):
                    self.content = text
            return Response(f"[Basic Mode] I'm unable to generate responses without an LLM.")
    
    API_CONFIG["llm_provider"] = "none"
    logger.info("LLM initialization complete. Using basic analyzer.")
    return BasicAnalyzer()

# Initialize LLM on startup
llm = initialize_llm()
logger.info(f"LLM initialization complete. Provider: {API_CONFIG['llm_provider']}")

# System prompts
monitoring_system_prompt = """You are an AI assistant specialized in Kubernetes monitoring.
Your task is to analyze metrics from Kubernetes pods and identify potential issues.

For each pod:
1. Analyze the resource usage metrics
2. Identify unusual patterns or high utilization
3. Flag pods that might need intervention
4. Determine priority for further analysis

Be concise and focus on actionable insights from the metrics data.
"""

anomaly_system_prompt = """You are an AI assistant specialized in analyzing Kubernetes metrics and anomalies.
You have access to a trained model that can detect anomalies in Kubernetes clusters.

When analyzing metrics, be concise but thorough in explaining what might be happening.
Focus on actionable insights that could help resolve the issues detected.

Pay special attention to:
1. Event ages (how long issues have been occurring)
2. Event counts (how frequently issues happen)
3. Pod restarts and their correlation with events
4. Resource utilization patterns

Provide clear, actionable recommendations.
"""

remediation_system_prompt = """You are an AI assistant specialized in Kubernetes remediation.
Your task is to analyze Kubernetes pod anomalies and suggest precise remediation steps.

For each anomaly:
1. Analyze the pod metrics and anomaly prediction
2. Identify the specific issue
3. Determine the appropriate remediation action
4. Estimate the impact of the remediation
5. Present a clear plan for approval

Consider these remediation options:
- Pod restart
- Resource limit adjustments
- Deployment scaling
- Node eviction
- Configuration changes

Be specific in your recommendations and always consider the potential impact.
"""

orchestrator_system_prompt = """You are an AI orchestrator for a Kubernetes monitoring and remediation system.
Your task is to coordinate between multiple specialized agents:
1. Monitoring Agent: Collects and analyzes metrics
2. Anomaly Agent: Detects and analyzes anomalies
3. Remediation Agent: Creates and executes remediation plans

You need to:
- Prioritize pods that need attention
- Manage the workflow between agents
- Track the status of remediations
- Handle user approvals and commands

The goal is to maintain a healthy Kubernetes cluster by identifying and addressing issues efficiently.
"""

# Prompt templates
metrics_analysis_prompt = ChatPromptTemplate.from_messages([
    ("system", anomaly_system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", """Here are the latest metrics from the Kubernetes pod: 
{metrics_data}

The anomaly detection model prediction is:
{prediction_result}

Based on this data, provide a concise analysis and specific recommendations. 
If there are events, analyze how the event age might relate to the detected anomaly.""")
])

remediation_plan_prompt = ChatPromptTemplate.from_messages([
    ("system", remediation_system_prompt),
    MessagesPlaceholder(variable_name="messages"),
    ("human", """I need to remediate an issue with a Kubernetes pod.

Pod Information:
{pod_info}

Anomaly Prediction:
{prediction}

Please generate a remediation plan including:
1. Issue summary
2. Root cause analysis
3. Recommended remediation steps
4. Potential impact
5. Warning level (low/medium/high)""")
])

# Utility functions for all agents
def signal_handler(sig, frame):
    """Signal handler for graceful shutdown."""
    global stop_event_triggered
    logger.info("Received termination signal, shutting down...")
    stop_event_triggered = True
    sys.exit(0)

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

def collect_pod_metrics(namespace="default") -> Dict[str, Dict[str, Any]]:
    """
    Collect metrics from pods in the specified namespace.
    
    In a real environment, this would connect to Prometheus or the Kubernetes API.
    For testing, it reads from a sample file.
    
    Args:
        namespace: Kubernetes namespace to monitor
        
    Returns:
        Dictionary mapping pod names to their metrics
    """
    pod_metrics = {}
    
    try:
        # In test mode, read from sample file
        if TEST_MODE:
            # Look for sample files in priority order
            sample_files = ['pod_metrics.csv', 'sample_metrics.json', 'prometheus_data.csv']
            
            for file in sample_files:
                if os.path.exists(os.path.join('K8S', file)):
                    filepath = os.path.join('K8S', file)
                    break
                elif os.path.exists(file):
                    filepath = file
                    break
            else:
                # If no files found, generate synthetic data
                logger.warning("No sample metrics files found, generating synthetic data")
                return generate_synthetic_metrics()
            
            # Read the file based on extension
            if filepath.endswith('.csv'):
                df = pd.read_csv(filepath)
                for _, row in df.iterrows():
                    if 'Pod Name' in row:
                        pod_name = row['Pod Name']
                        pod_metrics[pod_name] = row.to_dict()
            elif filepath.endswith('.json'):
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # If it's a dictionary of pod metrics
                        pod_metrics = data
                    elif isinstance(data, list):
                        # If it's a list of pod metrics
                        for item in data:
                            if 'name' in item:
                                pod_metrics[item['name']] = item
                            elif 'Pod Name' in item:
                                pod_metrics[item['Pod Name']] = item
            
            logger.info(f"Loaded {len(pod_metrics)} pod metrics from {filepath}")
        
        # In real mode, collect from Kubernetes API
        else:
            try:
                # Get pods in the namespace
                pods = core_api.list_namespaced_pod(namespace=namespace)
                
                for pod in pods.items:
                    pod_name = pod.metadata.name
                    
                    # Basic pod info
                    pod_info = {
                        'Pod Name': pod_name,
                        'namespace': pod.metadata.namespace,
                        'status': pod.status.phase,
                        'node': pod.spec.node_name if pod.spec.node_name else "Unknown",
                        'Pod Restarts': sum(container.restart_count for container in pod.status.container_statuses) if pod.status.container_statuses else 0,
                    }
                    
                    # Add container counts
                    total_containers = len(pod.spec.containers)
                    ready_containers = sum(1 for container in pod.status.container_statuses if container.ready) if pod.status.container_statuses else 0
                    pod_info['Pod Status'] = f"{ready_containers}/{total_containers}"
                    pod_info['Ready Containers'] = ready_containers
                    pod_info['Total Containers'] = total_containers
                    
                    # Add resource metrics if available
                    try:
                        # This would be expanded in a real implementation to fetch actual metrics
                        # from Prometheus or the Kubernetes Metrics API
                        pod_info['CPU Usage (%)'] = 0.0
                        pod_info['Memory Usage (%)'] = 0.0
                        pod_info['Memory Usage (MB)'] = 0.0
                    except Exception as e:
                        logger.warning(f"Error fetching metrics for pod {pod_name}: {e}")
                    
                    # Get recent events for this pod
                    try:
                        field_selector = f"involvedObject.name={pod_name}"
                        events = core_api.list_namespaced_event(
                            namespace=namespace,
                            field_selector=field_selector
                        )
                        
                        if events.items:
                            # Get the most recent event
                            latest_event = max(events.items, key=lambda e: e.last_timestamp) if events.items else None
                            
                            if latest_event:
                                pod_info['Event Reason'] = latest_event.reason
                                pod_info['Event Message'] = latest_event.message
                                
                                # Parse the event age
                                if latest_event.last_timestamp:
                                    age_seconds = (datetime.now(latest_event.last_timestamp.tzinfo) - latest_event.last_timestamp).total_seconds()
                                    pod_info['Event Age (minutes)'] = int(age_seconds / 60)
                                    
                                    # Format as string like "5m" or "2h"
                                    if age_seconds < 3600:
                                        pod_info['Pod Event Age'] = f"{int(age_seconds / 60)}m"
                                    elif age_seconds < 86400:
                                        pod_info['Pod Event Age'] = f"{int(age_seconds / 3600)}h"
                                    else:
                                        pod_info['Pod Event Age'] = f"{int(age_seconds / 86400)}d"
                                
                                pod_info['Event Count'] = latest_event.count
                    except Exception as e:
                        logger.warning(f"Error fetching events for pod {pod_name}: {e}")
                    
                    # Add to pod metrics
                    pod_metrics[pod_name] = pod_info
                
                logger.info(f"Collected metrics for {len(pod_metrics)} pods in {namespace} namespace")
            except Exception as e:
                logger.error(f"Error collecting metrics from Kubernetes API: {e}")
                # Fall back to synthetic data in case of error
                pod_metrics = generate_synthetic_metrics()
        
    except Exception as e:
        logger.error(f"Error in collect_pod_metrics: {e}")
        traceback.print_exc()
        # Generate synthetic data as a fallback
        pod_metrics = generate_synthetic_metrics()
    
    return pod_metrics

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

def create_monitoring_agent():
    """Create the monitoring agent graph."""
    # Define the workflow graph
    workflow = StateGraph(MonitoringState)
    
    # Add nodes
    workflow.add_node("collect_metrics", collect_metrics_node)
    workflow.add_node("analyze_metrics", analyze_metrics_node)
    
    # Add edges
    workflow.add_edge("collect_metrics", "analyze_metrics")
    
    # Set entry point
    workflow.set_entry_point("collect_metrics")
    
    # Compile the graph
    return workflow.compile()

def collect_metrics_node(state: MonitoringState) -> MonitoringState:
    """Collect metrics from Kubernetes pods."""
    messages = state["messages"]
    
    try:
        # Collect pod metrics
        pod_metrics = collect_pod_metrics()
        
        # Update metrics in state
        return {
            "messages": messages + [AIMessage(content="Collected metrics from Kubernetes pods")],
            "metrics_data": pod_metrics,
            "pod_metrics": pod_metrics,
            "pod_history": state.get("pod_history", {}),
            "status": "metrics_collected",
            "last_run_time": time.time(),
            "action": "analyze"
        }
    except Exception as e:
        error_msg = f"Error collecting metrics: {str(e)}"
        logger.error(error_msg)
        
        return {
            "messages": messages + [AIMessage(content=error_msg)],
            "metrics_data": {},
            "pod_metrics": {},
            "pod_history": state.get("pod_history", {}),
            "status": "error",
            "last_run_time": time.time(),
            "action": "complete"
        }

def analyze_metrics_node(state: MonitoringState) -> MonitoringState:
    """Analyze collected metrics and identify pods that need attention."""
    messages = state["messages"]
    pod_metrics = state["pod_metrics"]
    pod_history = state.get("pod_history", {})
    
    # Update pod history with new metrics
    for pod_name, metrics in pod_metrics.items():
        if pod_name not in pod_history:
            pod_history[pod_name] = []
        
        # Add timestamp if not present
        if "timestamp" not in metrics:
            metrics["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
        pod_history[pod_name].append(metrics)
        
        # Keep history limited to avoid memory issues
        if len(pod_history[pod_name]) > 100:
            pod_history[pod_name] = pod_history[pod_name][-100:]
    
    # Identify pods that need attention
    pods_of_interest = []
    
    for pod_name, metrics in pod_metrics.items():
        # Check for events
        if 'Event Reason' in metrics and metrics['Event Reason']:
            pods_of_interest.append({
                'pod_name': pod_name,
                'reason': metrics['Event Reason'],
                'age': metrics.get('Event Age (minutes)', 0),
                'count': metrics.get('Event Count', 1),
                'priority': calculate_pod_priority(metrics)
            })
            continue
            
        # Check for high restart counts
        if metrics.get('Pod Restarts', 0) > 5:
            pods_of_interest.append({
                'pod_name': pod_name,
                'reason': 'High restart count',
                'restarts': metrics['Pod Restarts'],
                'priority': calculate_pod_priority(metrics)
            })
            continue
            
        # Check for resource usage > 80%
        if metrics.get('CPU Usage (%)', 0) > 80 or metrics.get('Memory Usage (%)', 0) > 80:
            pods_of_interest.append({
                'pod_name': pod_name,
                'reason': 'High resource usage',
                'cpu': metrics.get('CPU Usage (%)', 0),
                'memory': metrics.get('Memory Usage (%)', 0),
                'priority': calculate_pod_priority(metrics)
            })
            continue
            
        # Check for network issues
        if metrics.get('Network Receive Packets Dropped (p/s)', 0) > 0 or metrics.get('Network Transmit Packets Dropped (p/s)', 0) > 0:
            pods_of_interest.append({
                'pod_name': pod_name,
                'reason': 'Network packet drops',
                'rx_drops': metrics.get('Network Receive Packets Dropped (p/s)', 0),
                'tx_drops': metrics.get('Network Transmit Packets Dropped (p/s)', 0),
                'priority': calculate_pod_priority(metrics)
            })
            continue
    
    # Sort pods by priority (descending)
    pods_of_interest.sort(key=lambda x: x['priority'], reverse=True)
    
    # Format message about pods needing attention
    if pods_of_interest:
        analysis_msg = f"Found {len(pods_of_interest)} pods that need attention:\n\n"
        for i, pod in enumerate(pods_of_interest[:5], 1):  # Show top 5
            analysis_msg += f"{i}. Pod '{pod['pod_name']}': {pod['reason']} (Priority: {pod['priority']})\n"
        
        if len(pods_of_interest) > 5:
            analysis_msg += f"\n...and {len(pods_of_interest) - 5} more pods."
    else:
        analysis_msg = "All pods appear to be healthy. No immediate attention needed."
    
    return {
        "messages": messages + [AIMessage(content=analysis_msg)],
        "metrics_data": state["metrics_data"],
        "pod_metrics": pod_metrics,
        "pod_history": pod_history,
        "status": "analysis_complete",
        "last_run_time": state["last_run_time"],
        "action": "complete"
    }

def calculate_pod_priority(metrics: Dict[str, Any]) -> int:
    """
    Calculate a priority score for a pod based on its metrics.
    Higher score = higher priority for remediation.
    
    Args:
        metrics: Pod metrics dictionary
        
    Returns:
        Priority score (0-100)
    """
    priority = 0
    
    # Event-based priority
    event_reason = metrics.get('Event Reason', '')
    event_age = metrics.get('Event Age (minutes)', 0)
    event_count = metrics.get('Event Count', 0)
    
    # Critical events
    if event_reason in ['OOMKilled', 'BackOff', 'CrashLoopBackOff', 'Failed']:
        priority += 40
    # Important events
    elif event_reason in ['Unhealthy', 'NodeNotReady', 'FailedMount']:
        priority += 30
    # Warning events
    elif event_reason:
        priority += 20
    
    # Recent events are more important
    if 0 < event_age <= 5:
        priority += 15
    elif 5 < event_age <= 30:
        priority += 10
    elif 30 < event_age <= 120:
        priority += 5
    
    # Frequent events are more important
    if event_count >= 10:
        priority += 15
    elif event_count >= 5:
        priority += 10
    elif event_count >= 3:
        priority += 5
    
    # Restart-based priority
    restarts = metrics.get('Pod Restarts', 0)
    if restarts >= 10:
        priority += 20
    elif restarts >= 5:
        priority += 15
    elif restarts >= 2:
        priority += 10
    
    # Resource-based priority
    cpu_usage = metrics.get('CPU Usage (%)', 0)
    memory_usage = metrics.get('Memory Usage (%)', 0)
    
    if cpu_usage >= 95 or memory_usage >= 95:
        priority += 15
    elif cpu_usage >= 85 or memory_usage >= 85:
        priority += 10
    elif cpu_usage >= 75 or memory_usage >= 75:
        priority += 5
    
    # Network-based priority
    rx_drops = metrics.get('Network Receive Packets Dropped (p/s)', 0)
    tx_drops = metrics.get('Network Transmit Packets Dropped (p/s)', 0)
    
    if rx_drops > 10 or tx_drops > 10:
        priority += 10
    elif rx_drops > 0 or tx_drops > 0:
        priority += 5
    
    # Cap priority at 100
    return min(priority, 100)

def create_anomaly_agent():
    """Create the anomaly detection agent graph."""
    # Define the workflow graph
    workflow = StateGraph(AnomalyState)
    
    # Add nodes
    workflow.add_node("detect_anomalies", detect_anomalies_node)
    workflow.add_node("analyze_anomalies", analyze_anomalies_node)
    
    # Add edges
    workflow.add_edge("detect_anomalies", "analyze_anomalies")
    
    # Set entry point
    workflow.set_entry_point("detect_anomalies")
    
    # Compile the graph
    return workflow.compile()

def detect_anomalies_node(state: AnomalyState) -> AnomalyState:
    """Run the anomaly detection model on pod metrics."""
    messages = state["messages"]
    metrics_data = state["metrics_data"]
    pod_info = state.get("pod_info", {})
    
    try:
        # Convert dictionary to DataFrame if needed
        if not isinstance(metrics_data, pd.DataFrame):
            df = pd.DataFrame([metrics_data])
        else:
            df = metrics_data
        
        # Preprocess metrics
        df = preprocess_metrics(df)
        
        # Run prediction
        prediction_df = predict_anomalies(df)
        prediction_result = prediction_df.iloc[0].to_dict()
        logger.info(f"Prediction result: {prediction_result}")
        
        is_anomaly = bool(prediction_result['predicted_anomaly'])
        anomaly_type = prediction_result['anomaly_type']
        prob = prediction_result['anomaly_probability']
        
        # Add additional context related to event age
        event_age = metrics_data.get('Event Age (minutes)', 0)
        if isinstance(metrics_data, dict) and 'Pod Event Age' in metrics_data:
            event_age = parse_event_age(metrics_data['Pod Event Age'])
            
        event_reason = metrics_data.get('Event Reason', '')
        event_count = metrics_data.get('Event Count', 0)
        
        # Create more detailed message based on both prediction and events
        if is_anomaly:
            if event_age and event_reason:
                # Anomaly with related events
                msg = f"Anomaly detected: Type - {anomaly_type}, Confidence: {prob:.4f}"
                msg += f"\nRelated event: {event_reason} occurred {event_age} minutes ago (count: {event_count})"
            else:
                # Anomaly without events
                msg = f"Anomaly detected: Type - {anomaly_type}, Confidence: {prob:.4f}"
                msg += f"\nNo related events found in the cluster"
        else:
            if event_age and event_reason:
                # No anomaly but events present (potential false negative)
                msg = f"No anomaly detected by model, but found event: {event_reason} from {event_age} minutes ago"
            else:
                # No anomaly and no events
                msg = f"No anomaly detected (confidence: {1-prob:.4f})"
        
        # Add event info to prediction result
        prediction_result['event_age_minutes'] = event_age
        prediction_result['event_reason'] = event_reason
        prediction_result['event_count'] = event_count
        
        return {
            "messages": messages + [AIMessage(content=msg)],
            "metrics_data": metrics_data,
            "prediction_result": prediction_result,
            "pod_info": pod_info,
            "action": "analyze"
        }
    except Exception as e:
        error_msg = f"Error in anomaly detection: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()
        
        return {
            "messages": messages + [AIMessage(content=error_msg)],
            "metrics_data": metrics_data,
            "prediction_result": {"error": str(e)},
            "pod_info": pod_info,
            "action": "complete"
        }

def analyze_anomalies_node(state: AnomalyState) -> AnomalyState:
    """Generate analysis using LLM based on metrics and prediction."""
    messages = state["messages"]
    metrics_data = state["metrics_data"]
    prediction_result = state["prediction_result"]
    pod_info = state.get("pod_info", {})
    
    # Skip analysis if there was an error in detection
    if "error" in prediction_result:
        return {
            "messages": messages,
            "metrics_data": metrics_data,
            "prediction_result": prediction_result,
            "pod_info": pod_info,
            "action": "complete"
        }
    
    # Skip detailed analysis if no anomaly was detected and no significant events
    if not prediction_result.get('predicted_anomaly', 0) and not metrics_data.get('Event Reason', ''):
        return {
            "messages": messages,
            "metrics_data": metrics_data,
            "prediction_result": prediction_result,
            "pod_info": pod_info,
            "action": "complete"
        }
    
    # Enhance the metrics with some additional insights about events
    enhanced_metrics = metrics_data.copy() if isinstance(metrics_data, dict) else metrics_data.to_dict('records')[0]
    event_age = enhanced_metrics.get('Event Age (minutes)', 0)
    event_reason = enhanced_metrics.get('Event Reason', '')
    
    # Add event age category if events exist
    if event_age and event_reason:
        if event_age < 10:
            enhanced_metrics['Event Age Category'] = "Recent issue (< 10 minutes)"
        elif event_age < 60:
            enhanced_metrics['Event Age Category'] = "Ongoing issue (< 1 hour)"
        elif event_age < 1440:  # 24 hours
            enhanced_metrics['Event Age Category'] = "Persistent issue (< 24 hours)"
        else:
            enhanced_metrics['Event Age Category'] = f"Long-standing issue ({event_age/1440:.1f} days)"
    
    # Try analysis methods in order of preference
    analysis_text = ""
    
    # 1. Use direct NVIDIA API if available
    if API_CONFIG['use_nvidia_direct'] and API_CONFIG['llm_provider'] == "nvidia":
        try:
            logger.info("Generating analysis with direct NVIDIA API")
            nvidia_llm = API_CONFIG['llm_instance']
            analysis_text = nvidia_llm.analyze_k8s_metrics(enhanced_metrics, prediction_result)
        except Exception as e:
            logger.error(f"Error with direct NVIDIA API: {e}")
            # Continue to next option
    
    # 2. Use LangChain LLM if available
    if not analysis_text and API_CONFIG['use_llm'] and API_CONFIG['llm_provider'] in ["openai", "nvidia-langchain"]:
        try:
            logger.info(f"Generating analysis with LangChain ({API_CONFIG['llm_provider']})")
            # Format the data for the prompt
            prompt = metrics_analysis_prompt.format(
                messages=messages,
                metrics_data=enhanced_metrics,
                prediction_result=prediction_result
            )
            
            # Generate the analysis
            llm = API_CONFIG['llm_instance']
            analysis = llm.invoke(prompt)
            analysis_text = analysis.content
        except Exception as e:
            logger.error(f"Error generating LLM analysis with LangChain: {str(e)}")
            # Fall through to basic analysis
    
    # 3. Fall back to basic analysis
    if not analysis_text:
        logger.info("Using basic analysis mode")
        analysis_text = generate_basic_analysis(enhanced_metrics, prediction_result)
        analysis_text = f"[Basic Analysis Mode]\n{analysis_text}"
    
    return {
        "messages": messages + [AIMessage(content=analysis_text)],
        "metrics_data": metrics_data,
        "prediction_result": prediction_result,
        "pod_info": pod_info,
        "action": "complete"
    }

def generate_basic_analysis(metrics: Dict[str, Any], prediction: Dict[str, Any]) -> str:
    """Generate a basic analysis without using an LLM."""
    is_anomaly = bool(prediction.get('predicted_anomaly', False))
    anomaly_type = prediction.get('anomaly_type', 'unknown')
    event_reason = metrics.get('Event Reason', '')
    event_age = metrics.get('Event Age (minutes)', 0)
    event_count = metrics.get('Event Count', 0)
    pod_restarts = metrics.get('Pod Restarts', 0)
    
    analysis = []
    
    # Add anomaly information
    if is_anomaly:
        analysis.append(f"ANOMALY DETECTED: Type - {anomaly_type}")
        analysis.append(f"Confidence: {prediction.get('anomaly_probability', 0):.4f}")
    else:
        analysis.append("No anomaly detected by the model.")
    
    # Add event information
    if event_reason:
        analysis.append(f"Event '{event_reason}' occurred {event_age} minutes ago (count: {event_count})")
        
        # Add specific recommendations based on event type
        if event_reason == 'BackOff':
            analysis.append("RECOMMENDATION: Check container logs for application errors")
            analysis.append("RECOMMENDATION: Verify container image and startup commands")
        elif event_reason == 'OOMKilled':
            analysis.append("RECOMMENDATION: Increase memory limits in pod specification")
            analysis.append("RECOMMENDATION: Check for memory leaks in the application")
        elif event_reason.startswith('Failed'):
            analysis.append("RECOMMENDATION: Check node resources and pod placement")
            
    # Add restart information
    if pod_restarts > 10:
        analysis.append(f"ALERT: Pod has restarted {pod_restarts} times - indicates persistent issue")
        analysis.append("RECOMMENDATION: Check application logs for recurring errors")
    
    # Add general recommendation if no specific ones
    if len(analysis) < 3:
        analysis.append("RECOMMENDATION: Monitor the pod for further issues")
    
    return "\n".join(analysis)

def create_remediation_agent():
    """Create the remediation agent graph."""
    workflow = StateGraph(RemediationState)
    
    # Add nodes
    workflow.add_node("detect_issue", detect_issue_node)
    workflow.add_node("generate_plan", generate_remediation_plan_node)
    workflow.add_node("request_approval", request_approval_node)
    workflow.add_node("execute_remediation", execute_remediation_node)
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "detect_issue",
        lambda state: END if state["approval_status"] == "complete" else "generate_plan"
    )
    
    workflow.add_edge("generate_plan", "request_approval")
    
    workflow.add_conditional_edges(
        "request_approval",
        lambda state: "execute_remediation" if state["approval_status"] == "approved" else END
    )
    
    workflow.add_edge("execute_remediation", END)
    
    # Set entry point
    workflow.set_entry_point("detect_issue")
    
    # Compile the graph
    return workflow.compile()

def detect_issue_node(state: RemediationState) -> RemediationState:
    """Analyze the anomaly and pod info to detect the specific issue."""
    prediction = state["prediction"]
    pod_info = state["pod_info"]
    messages = state["messages"]
    
    is_anomaly = prediction.get("predicted_anomaly", 0) == 1
    anomaly_type = prediction.get("anomaly_type", "unknown")
    probability = prediction.get("anomaly_probability", 0.0)
    
    if not is_anomaly:
        messages.append(AIMessage(content=f"No anomaly detected (confidence: {1-probability:.4f}). No remediation needed."))
        return {"messages": messages, "prediction": prediction, "pod_info": pod_info, 
                "remediation_plan": {}, "approval_status": "complete", "action_status": "success"}
    
    # Format the anomaly information for the LLM
    messages.append(AIMessage(content=f"Anomaly detected: {anomaly_type} with confidence {probability:.4f}. Generating remediation plan..."))
    
    # Return updated state
    return {"messages": messages, "prediction": prediction, "pod_info": pod_info, 
            "remediation_plan": {}, "approval_status": "pending", "action_status": "waiting"}

def generate_remediation_plan_node(state: RemediationState) -> RemediationState:
    """Generate a remediation plan using the LLM or basic logic if LLM is unavailable."""
    prediction = state["prediction"]
    pod_info = state["pod_info"]
    messages = state["messages"]
    
    # Get anomaly information
    anomaly_type = prediction.get("anomaly_type", "unknown")
    probability = prediction.get("anomaly_probability", 0.0)
    
    try:
        # Generate plan based on available LLM
        if API_CONFIG['use_llm']:
            if API_CONFIG['use_nvidia_direct'] and API_CONFIG['llm_provider'] == "nvidia":
                # Use the custom NVIDIA LLM wrapper
                prompt_text = f"""I need to remediate an issue with a Kubernetes pod.

Pod Information:
{pod_info}

Anomaly Prediction:
{prediction}

Please generate a remediation plan including:
1. Issue summary
2. Root cause analysis
3. Recommended remediation steps
4. Potential impact
5. Warning level (low/medium/high)"""

                # Generate the remediation plan using the custom wrapper
                nvidia_llm = API_CONFIG['llm_instance']
                plan_text = nvidia_llm.generate(prompt_text, temperature=0.3)
                
                # Add the response to messages
                messages.append(AIMessage(content=plan_text))
                
                # Parse the plan using our improved parser
                plan_dict = parse_llm_response(plan_text)
                
            elif API_CONFIG['llm_provider'] in ["openai", "nvidia-langchain"]:
                # Use LangChain with configured LLM
                # Format the data for the prompt
                prompt = remediation_plan_prompt.format(
                    messages=messages,
                    prediction=prediction,
                    pod_info=pod_info
                )
                
                # Generate the remediation plan
                llm = API_CONFIG['llm_instance']
                response = llm.invoke(prompt)
                messages.append(response)
                
                # Extract structured information from the response
                plan_text = response.content
                
                # Parse the plan
                plan_dict = parse_llm_response(plan_text)
            else:
                # Fall back to basic plan
                plan_dict = generate_basic_remediation_plan(prediction, pod_info)
        else:
            # Generate a basic remediation plan without LLM
            logger.info("Generating basic remediation plan without LLM")
            plan_dict = generate_basic_remediation_plan(prediction, pod_info)
            
            # Add basic plan to messages
            messages.append(AIMessage(content=f"[Basic Analysis Mode]\n\nIssue summary: {plan_dict.get('Issue summary', 'No summary')}\n\nRecommended steps: {plan_dict.get('Recommended remediation steps', 'No steps')}"))
        
        # Add action type based on anomaly
        if "action_type" not in plan_dict:
            if anomaly_type == "crash_loop":
                plan_dict["action_type"] = "restart_pod"
            elif anomaly_type == "oom_kill":
                plan_dict["action_type"] = "increase_memory"
            elif anomaly_type == "resource_exhaustion":
                plan_dict["action_type"] = "scale_deployment"
            elif anomaly_type == "network_issue":
                plan_dict["action_type"] = "restart_pod"
            else:
                plan_dict["action_type"] = "restart_pod"  # Default action
                
        # Set warning level if missing
        if "Warning level" not in plan_dict:
            plan_dict["Warning level"] = "medium"
            
        # Return updated state with the remediation plan
        return {"messages": messages, "prediction": prediction, "pod_info": pod_info,
                "remediation_plan": plan_dict, "approval_status": "pending", "action_status": "waiting"}
    except Exception as e:
        error_msg = f"Error generating remediation plan: {str(e)}"
        logger.error(error_msg)
        traceback.print_exc()
        
        # Fall back to basic plan in case of error
        fallback_plan = generate_basic_remediation_plan(prediction, pod_info)
        messages.append(AIMessage(content=f"[Error in plan generation, using basic mode]\n\nIssue summary: {fallback_plan.get('Issue summary', 'Error')}\n\nRecommended steps: {fallback_plan.get('Recommended remediation steps', 'Restart pod if needed')}"))
        
        return {"messages": messages, "prediction": prediction, "pod_info": pod_info,
                "remediation_plan": fallback_plan, "approval_status": "pending", "action_status": "waiting"}

def generate_basic_remediation_plan(prediction: Dict[str, Any], pod_info: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a basic remediation plan without using an LLM."""
    plan = {}
    
    # Extract key information
    anomaly_type = prediction.get("anomaly_type", "unknown")
    event_reason = prediction.get("event_reason", "")
    event_count = prediction.get("event_count", 0)
    restarts = pod_info.get("restart_count", pod_info.get("Pod Restarts", 0))
    pod_name = pod_info.get("name", pod_info.get("Pod Name", "unknown"))
    namespace = pod_info.get("namespace", "default")
    
    # Generate basic issue summary
    if anomaly_type == "crash_loop":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is in CrashLoopBackOff with {restarts} restarts."
        plan["Root cause analysis"] = "Pod is repeatedly crashing, likely due to application errors or resource issues."
        plan["Recommended remediation steps"] = "1. Restart the pod to clear any transient issues\n2. Check logs for application errors"
        plan["Potential impact"] = "Brief service interruption during pod restart."
        plan["Warning level"] = "medium"
        plan["action_type"] = "restart_pod"
        
    elif anomaly_type == "oom_kill":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is experiencing Out of Memory (OOM) kills."
        plan["Root cause analysis"] = "Pod is being terminated due to memory usage exceeding limits."
        plan["Recommended remediation steps"] = "1. Increase memory limits by 50%\n2. Monitor memory usage after increase"
        plan["Potential impact"] = "Application might restart during resource update."
        plan["Warning level"] = "high"
        plan["action_type"] = "increase_memory"
        
    elif anomaly_type == "resource_exhaustion":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is experiencing resource exhaustion."
        plan["Root cause analysis"] = "Pod's resources are near maximum, causing performance degradation."
        plan["Recommended remediation steps"] = "1. Scale up the deployment by adding 1 replica\n2. Consider increasing resource limits if scaling is not sufficient"
        plan["Potential impact"] = "New pod creation will consume additional cluster resources."
        plan["Warning level"] = "medium"
        plan["action_type"] = "scale_deployment"
        
    elif anomaly_type == "network_issue":
        plan["Issue summary"] = f"Pod {namespace}/{pod_name} is experiencing network issues."
        plan["Root cause analysis"] = "Network packet drops or connection issues detected."
        plan["Recommended remediation steps"] = "1. Restart the pod to re-establish network connections\n2. Check network policies if issue persists"
        plan["Potential impact"] = "Brief service interruption during pod restart."
        plan["Warning level"] = "medium"
        plan["action_type"] = "restart_pod"
        
    else:
        plan["Issue summary"] = f"Unknown anomaly detected for pod {namespace}/{pod_name}."
        plan["Root cause analysis"] = "The specific cause could not be determined from available metrics."
        plan["Recommended remediation steps"] = "1. Restart the pod as a general troubleshooting step\n2. Monitor the pod after restart"
        plan["Potential impact"] = "Brief service interruption during pod restart."
        plan["Warning level"] = "medium"
        plan["action_type"] = "restart_pod"
    
    # Add event information if available
    if event_reason and event_count > 0:
        plan["Issue summary"] += f" Event '{event_reason}' observed {event_count} times."
        
    return plan

def request_approval_node(state: RemediationState) -> RemediationState:
    """Present the remediation plan and request approval."""
    messages = state["messages"]
    remediation_plan = state["remediation_plan"]
    
    # Format the approval request
    # Get warning level and normalize it - carefully extract it from the string if needed
    warning_level_raw = remediation_plan.get("Warning level", "medium")
    
    # If warning level contains multiple lines or additional text, extract just the level
    if isinstance(warning_level_raw, str) and len(warning_level_raw) > 10:
        # Try to extract just the level (high/medium/low) from text
        if "high" in warning_level_raw.lower():
            warning_level = "high"
        elif "medium" in warning_level_raw.lower():
            warning_level = "medium"
        else:
            warning_level = "low"
    else:
        warning_level = warning_level_raw.lower().strip() if isinstance(warning_level_raw, str) else "medium"
        
    action_type = remediation_plan.get("action_type", "unknown")
    pod_name = state["pod_info"].get("name", state["pod_info"].get("Pod Name", "unknown"))
    namespace = state["pod_info"].get("namespace", "default")
    
    # Create color-coded warning based on level
    if warning_level == "high":
        warning_prefix = "⚠️ HIGH RISK"
    elif warning_level == "medium":
        warning_prefix = "⚠️ MEDIUM RISK"
    else:
        warning_prefix = "ℹ️ LOW RISK"
    
    # Get a concise issue summary
    issue_summary = remediation_plan.get('Issue summary', 'No summary available')
    if len(issue_summary) > 500:  # If summary is too long, get the first paragraph or sentence
        first_paragraph = issue_summary.split('\n\n')[0] if '\n\n' in issue_summary else issue_summary
        if len(first_paragraph) > 200:
            # Get first sentence or first 200 chars
            first_sentence = first_paragraph.split('.')[0] + '.'
            issue_summary = first_sentence if len(first_sentence) < 200 else first_paragraph[:197] + '...'
            
    # Get remediation steps
    remediation_steps = remediation_plan.get('Recommended remediation steps', 'No steps available')
    
    # Get potential impact
    potential_impact = remediation_plan.get('Potential impact', 'Impact not analyzed')
    
    approval_text = f"""{warning_prefix} REMEDIATION PLAN
    
Pod: {namespace}/{pod_name}
Action: {action_type}

{issue_summary}

Remediation steps:
{remediation_steps}

Potential impact:
{potential_impact}

Do you approve this remediation plan? (yes/no)"""
    
    messages.append(AIMessage(content=approval_text))
    
    # Return state with pending approval
    return {"messages": messages, "prediction": state["prediction"], "pod_info": state["pod_info"],
            "remediation_plan": remediation_plan, "approval_status": "pending", "action_status": "waiting"}

def execute_remediation_node(state: RemediationState) -> RemediationState:
    """Execute the approved remediation plan."""
    messages = state["messages"]
    remediation_plan = state["remediation_plan"]
    pod_info = state["pod_info"]
    
    # Only execute if approval status is "approved"
    if state["approval_status"] != "approved":
        return state
    
    # Get pod and action information
    pod_name = pod_info.get("name", pod_info.get("Pod Name", "unknown"))
    namespace = pod_info.get("namespace", "default")
    action_type = remediation_plan.get("action_type", "unknown")
    
    try:
        # Execute the appropriate remediation action
        if action_type == "restart_pod":
            try:
                # Delete pod to trigger recreation
                if not TEST_MODE:
                    core_api.delete_namespaced_pod(
                        name=pod_name,
                        namespace=namespace,
                        body=client.V1DeleteOptions()
                    )
                else:
                    logger.info(f"[TEST MODE] Would restart pod {namespace}/{pod_name}")
                    
                success_msg = f"Successfully restarted pod {namespace}/{pod_name}"
                messages.append(AIMessage(content=success_msg))
                logger.info(success_msg)
            except Exception as e:
                if hasattr(e, 'status') and e.status == 404:
                    # Pod not found - this is ok in test mode or if the pod was already deleted
                    warning_msg = f"Pod {namespace}/{pod_name} not found. It may have been already deleted or doesn't exist."
                    messages.append(AIMessage(content=warning_msg))
                    logger.warning(warning_msg)
                else:
                    # Re-raise other API exceptions
                    raise
            
        elif action_type == "increase_memory":
            try:
                # Get the deployment name from pod
                deployment_name = pod_info.get("owner_reference", pod_name.rsplit("-", 1)[0])
                
                if not TEST_MODE:
                    # Get current deployment
                    deployment = apps_api.read_namespaced_deployment(
                        name=deployment_name,
                        namespace=namespace
                    )
                    
                    # Update memory limits (increase by 50%)
                    containers = deployment.spec.template.spec.containers
                    for container in containers:
                        if container.resources and container.resources.limits and "memory" in container.resources.limits:
                            current_mem = container.resources.limits["memory"]
                            # Parse memory value (e.g., "256Mi")
                            value = int(''.join(filter(str.isdigit, current_mem)))
                            unit = ''.join(filter(str.isalpha, current_mem))
                            new_value = int(value * 1.5)
                            container.resources.limits["memory"] = f"{new_value}{unit}"
                            
                            # Also update requests if they exist
                            if container.resources.requests and "memory" in container.resources.requests:
                                req_value = int(''.join(filter(str.isdigit, container.resources.requests["memory"])))
                                req_unit = ''.join(filter(str.isalpha, container.resources.requests["memory"]))
                                new_req = int(req_value * 1.5)
                                container.resources.requests["memory"] = f"{new_req}{req_unit}"
                    
                    # Update the deployment
                    apps_api.patch_namespaced_deployment(
                        name=deployment_name,
                        namespace=namespace,
                        body=deployment
                    )
                else:
                    logger.info(f"[TEST MODE] Would increase memory for deployment {namespace}/{deployment_name} by 50%")
                
                success_msg = f"Successfully increased memory allocation for deployment {namespace}/{deployment_name}"
                messages.append(AIMessage(content=success_msg))
                logger.info(success_msg)
            except Exception as e:
                if hasattr(e, 'status') and e.status == 404:
                    warning_msg = f"Deployment {namespace}/{deployment_name} not found. It may have been deleted or doesn't exist."
                    messages.append(AIMessage(content=warning_msg))
                    logger.warning(warning_msg)
                else:
                    # Re-raise other API exceptions
                    raise
            
        elif action_type == "scale_deployment":
            try:
                # Get the deployment name from pod
                deployment_name = pod_info.get("owner_reference", pod_name.rsplit("-", 1)[0])
                
                if not TEST_MODE:
                    # Get current deployment
                    deployment = apps_api.read_namespaced_deployment(
                        name=deployment_name,
                        namespace=namespace
                    )
                    
                    # Scale up by 1 replica
                    current_replicas = deployment.spec.replicas
                    new_replicas = current_replicas + 1
                    
                    # Update replicas
                    deployment.spec.replicas = new_replicas
                    
                    # Update the deployment
                    apps_api.patch_namespaced_deployment(
                        name=deployment_name,
                        namespace=namespace,
                        body=deployment
                    )
                else:
                    logger.info(f"[TEST MODE] Would scale up deployment {namespace}/{deployment_name} by 1 replica")
                    current_replicas = 1  # Mock value for test mode
                    new_replicas = 2
                
                success_msg = f"Successfully scaled deployment {namespace}/{deployment_name} from {current_replicas} to {new_replicas} replicas"
                messages.append(AIMessage(content=success_msg))
                logger.info(success_msg)
            except Exception as e:
                if hasattr(e, 'status') and e.status == 404:
                    warning_msg = f"Deployment {namespace}/{deployment_name} not found. It may have been deleted or doesn't exist."
                    messages.append(AIMessage(content=warning_msg))
                    logger.warning(warning_msg)
                else:
                    # Re-raise other API exceptions
                    raise
            
        else:
            warning_msg = f"Unsupported action type: {action_type}. No remediation action taken."
            messages.append(AIMessage(content=warning_msg))
            logger.warning(warning_msg)
        
        # Return updated state
        return {"messages": messages, "prediction": state["prediction"], "pod_info": pod_info,
                "remediation_plan": remediation_plan, "approval_status": "approved", "action_status": "success"}
        
    except Exception as e:
        error_msg = f"Error executing remediation: {str(e)}"
        messages.append(AIMessage(content=error_msg))
        logger.error(error_msg)
        traceback.print_exc()
        
        # Return updated state with failure
        return {"messages": messages, "prediction": state["prediction"], "pod_info": pod_info,
                "remediation_plan": remediation_plan, "approval_status": "approved", "action_status": "failed"}

def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Parse LLM response text into structured sections."""
    logger.debug("Parsing LLM response into structured sections")
    
    # List of sections we're looking for
    sections = [
        "Issue summary", "Root cause analysis", "Recommended remediation steps", 
        "Potential impact", "Warning level"
    ]
    plan_dict = {}
    
    # First try to find sections based on exact headings or numbers
    current_section = None
    section_content = []
    
    # Log the first 100 chars of the response for debugging
    logger.debug(f"Response text preview: {response_text[:100]}...")
    
    for line in response_text.split('\n'):
        # Clean up the line
        clean_line = line.strip()
        if not clean_line:
            continue
            
        # Try different section heading patterns
        matched = False
        
        # Match exact section titles (regardless of case)
        for section in sections:
            if section.lower() in clean_line.lower() and len(clean_line) < len(section) + 15:
                logger.debug(f"Found section: {section} in line: {clean_line}")
                if current_section and section_content:
                    plan_dict[current_section] = '\n'.join(section_content).strip()
                    section_content = []
                current_section = section
                matched = True
                break
                
        # Match numbered sections like "1. Issue Summary" or "1) Issue Summary"
        if not matched:
            for i, section in enumerate(sections, 1):
                pattern = section.lower()
                if (f"{i}." in clean_line.lower() or f"{i})" in clean_line.lower()) and pattern in clean_line.lower():
                    logger.debug(f"Found numbered section {i}. {section} in line: {clean_line}")
                    if current_section and section_content:
                        plan_dict[current_section] = '\n'.join(section_content).strip()
                        section_content = []
                    current_section = section
                    matched = True
                    break
        
        # If no section matched, add to current section content
        if not matched and current_section:
            section_content.append(line)
    
    # Add the last section
    if current_section and section_content:
        plan_dict[current_section] = '\n'.join(section_content).strip()
        
    # If we couldn't find explicit sections, try a more aggressive approach
    if not plan_dict or len(plan_dict) < 3:
        logger.debug(f"Not enough sections found ({len(plan_dict)}), trying more aggressive parsing")
        # Split the response text by double newlines to find paragraphs
        paragraphs = response_text.split('\n\n')
        
        for i, section in enumerate(sections):
            if i < len(paragraphs):
                # Find the paragraph that might match this section
                for p in paragraphs:
                    if section.lower() in p.lower() or (i+1 < 10 and f"{i+1}." in p):
                        plan_dict[section] = p.replace(f"{i+1}. ", "").replace(f"{section}:", "").strip()
                        break
    
    # Special handling for warning level to ensure it's normalized
    if "Warning level" in plan_dict:
        warning_text = plan_dict["Warning level"].lower()
        if "high" in warning_text:
            plan_dict["Warning level"] = "high"
        elif "medium" in warning_text:
            plan_dict["Warning level"] = "medium"
        elif "low" in warning_text:
            plan_dict["Warning level"] = "low"
        else:
            # If we couldn't determine, default to medium
            plan_dict["Warning level"] = "medium"
    else:
        # Default to medium if we couldn't find it
        plan_dict["Warning level"] = "medium"
        logger.debug("Warning level not found, defaulting to 'medium'")
    
    return plan_dict

def process_approval(state: RemediationState, approval: str) -> RemediationState:
    """Process the user's approval response."""
    messages = state["messages"]
    
    # Update approval status based on user response
    approval_status = "approved" if approval.lower() in ["yes", "y", "approve", "approved"] else "rejected"
    
    if approval_status == "approved":
        messages.append(AIMessage(content="Remediation plan approved. Proceeding with execution..."))
        action_status = "in_progress"
    else:
        messages.append(AIMessage(content="Remediation plan rejected. No action will be taken."))
        action_status = "success"  # Nothing to do, so mark as success
    
    # Return updated state
    return {"messages": messages, "prediction": state["prediction"], "pod_info": state["pod_info"],
            "remediation_plan": state["remediation_plan"], "approval_status": approval_status, 
            "action_status": action_status}

def create_orchestrator_agent():
    """Create the orchestrator agent workflow."""
    workflow = StateGraph(OrchestratorState)
    
    # Add nodes
    workflow.add_node("initialize", initialize_orchestrator)
    workflow.add_node("collect_metrics", orchestrator_collect_metrics)
    workflow.add_node("detect_anomalies", orchestrator_detect_anomalies)
    workflow.add_node("plan_remediation", orchestrator_plan_remediation)
    workflow.add_node("execute_remediation", orchestrator_execute_remediation)
    workflow.add_node("process_command", process_command)
    
    # Define the main conditional edges - command handling
    workflow.add_conditional_edges(
        "initialize",
        lambda state: state["command"] is not None,
        {
            True: "process_command",
            False: "collect_metrics"
        }
    )
    
    # Check iteration limit as well as commands
    def collect_metrics_router(state):
        if state["command"] is not None:
            return "has_command"
        max_iterations = API_CONFIG.get("max_iterations", 0)
        if max_iterations > 0 and state["iteration_count"] >= max_iterations:
            return "max_iterations"
        return "continue"
        
    workflow.add_conditional_edges(
        "collect_metrics",
        collect_metrics_router,
        {
            "has_command": "process_command",
            "max_iterations": END,
            "continue": "detect_anomalies"
        }
    )
    
    # Define flow based on anomaly status
    # Use a function that returns a string key instead of a dict
    def detect_anomalies_router(state):
        if state["command"] is not None:
            return "has_command"
        max_iterations = API_CONFIG.get("max_iterations", 0)
        if max_iterations > 0 and state["iteration_count"] >= max_iterations:
            return "max_iterations"
        elif state["status"] == "anomalies_detected":
            return "has_anomalies"
        else:
            return "default"
            
    workflow.add_conditional_edges(
        "detect_anomalies",
        detect_anomalies_router,
        {
            "has_command": "process_command",
            "max_iterations": END,
            "has_anomalies": "plan_remediation",
            "default": "initialize"
        }
    )
    
    # Define flow based on remediation status
    # Use a function that returns a string key instead of a dict
    def plan_remediation_router(state):
        if state["command"] is not None:
            return "has_command"
        max_iterations = API_CONFIG.get("max_iterations", 0)
        if max_iterations > 0 and state["iteration_count"] >= max_iterations:
            return "max_iterations"
        elif state["status"] == "remediation_planned":
            return "has_plan"
        else:
            return "default"
            
    workflow.add_conditional_edges(
        "plan_remediation",
        plan_remediation_router,
        {
            "has_command": "process_command",
            "max_iterations": END,
            "has_plan": "execute_remediation",
            "default": "initialize"
        }
    )
    
    # Check for exit or max iterations
    def execute_remediation_router(state):
        if state["command"] is not None:
            return "has_command"
        max_iterations = API_CONFIG.get("max_iterations", 0)
        if max_iterations > 0 and state["iteration_count"] >= max_iterations:
            return "max_iterations"
        return "default"
        
    workflow.add_conditional_edges(
        "execute_remediation",
        execute_remediation_router,
        {
            "has_command": "process_command",
            "max_iterations": END,
            "default": "initialize"
        }
    )
    
    workflow.add_conditional_edges(
        "process_command",
        lambda state: state["command"] == "exit",
        {
            True: END,
            False: "initialize"
        }
    )
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    # Compile
    return workflow.compile()

def initialize_orchestrator(state: OrchestratorState) -> OrchestratorState:
    """Initialize the orchestrator agent."""
    messages = []
    
    # Add welcome message
    welcome_message = f"""Welcome to the Kubernetes Multi-Agent System!
    
I am the Orchestrator agent that coordinates monitoring, anomaly detection, and remediation.
    
Type 'help' for available commands or press Enter to start monitoring."""
    
    messages.append(SystemMessage(content=orchestrator_system_prompt))
    messages.append(AIMessage(content=welcome_message))
    
    # Initialize state with empty fields
    return {
        "messages": messages,
        "monitoring_state": {
            "messages": [],
            "metrics_data": {},
            "pod_metrics": {},
            "pod_history": {},
            "status": "idle",
            "last_run_time": 0,
            "action": "none"
        },
        "anomaly_state": {
            "messages": [],
            "metrics_data": {},
            "prediction_result": {},
            "pod_info": {},
            "action": "none"
        },
        "remediation_state": {
            "messages": [],
            "prediction": {},
            "pod_info": {},
            "remediation_plan": {},
            "approval_status": "pending",
            "action_status": "waiting"
        },
        "active_agent": "none",
        "pods_with_anomalies": {},
        "current_pod": None,
        "approved_remediations": [],
        "approval_queue": [],
        "command": None,
        "status": "initialized",
        "iteration_count": 0  # Add iteration counter
    }

def orchestrator_collect_metrics(state: OrchestratorState) -> OrchestratorState:
    """Collect metrics in the orchestrator workflow."""
    messages = state["messages"]
    
    # Initialize monitoring_state if it doesn't exist
    if state.get("monitoring_state") is None:
        logger.info("Initializing monitoring state")
        state["monitoring_state"] = {
            "messages": [],
            "metrics_data": {},
            "pod_metrics": {},
            "pod_history": {},
            "status": "idle",
            "last_run_time": 0,
            "action": "collect"
        }
    
    # Now we can safely use monitoring_state
    monitoring_state = state["monitoring_state"]
    
    messages.append(AIMessage(content="Collecting metrics from Kubernetes pods..."))
    
    # Get pod metrics
    try:
        if API_CONFIG.get("test_mode", False):
            pod_metrics = generate_synthetic_metrics()
            logger.info("Generated synthetic metrics for testing")
        else:
            pod_metrics = collect_pod_metrics(namespace=API_CONFIG.get("namespace", "default"))
            logger.info(f"Collected metrics from {len(pod_metrics)} pods")
        
        # Create a metrics dataframe for analysis
        metrics_data = {
            "pod_metrics": pod_metrics,
            "timestamp": time.time(),
            "pod_count": len(pod_metrics)
        }
        
        # Update the monitoring state with the new metrics
        return {
            **state,
            "monitoring_state": {
                "messages": monitoring_state["messages"],
                "metrics_data": metrics_data,
                "pod_metrics": pod_metrics,
                "pod_history": monitoring_state.get("pod_history", {}),
                "status": "metrics_collected",
                "last_run_time": time.time(),
                "action": "analyze"
            }
        }
    except Exception as e:
        error_msg = f"Error collecting metrics: {str(e)}"
        logger.error(error_msg)
        messages.append(AIMessage(content=error_msg))
        
        # Update state with error
        return {
            **state, 
            "monitoring_state": {
                **monitoring_state,
                "status": "error",
                "action": "none"
            }
        }

def orchestrator_detect_anomalies(state: OrchestratorState) -> OrchestratorState:
    """Detect anomalies in the orchestrator workflow."""
    messages = state["messages"]
    monitoring_state = state["monitoring_state"]
    
    # Initialize anomaly_state if it doesn't exist
    if state.get("anomaly_state") is None:
        logger.info("Initializing anomaly state")
        state["anomaly_state"] = {
            "messages": [],
            "metrics_data": {},
            "prediction_result": {},
            "pod_info": {},
            "action": "detect"
        }
    
    # Now we can safely use anomaly_state
    anomaly_state = state["anomaly_state"]
    
    # Check if we have pod metrics to analyze
    pod_metrics = monitoring_state.get("pod_metrics", {})
    if not pod_metrics:
        messages.append(AIMessage(content="No pod metrics available for anomaly detection."))
        return {**state, "active_agent": "none", "status": "no_metrics"}
    
    messages.append(AIMessage(content="Analyzing pod metrics for anomalies..."))
    
    # Process each pod and check for anomalies
    pods_with_anomalies = {}
    
    for pod_name, metrics in pod_metrics.items():
        try:
            # Format metrics for prediction
            is_anomaly, prediction = predict_pod_anomaly(metrics)
            
            if is_anomaly:
                pods_with_anomalies[pod_name] = {
                    'pod_metrics': metrics,
                    'prediction': prediction,
                    'priority': calculate_pod_priority(metrics)
                }
                logger.info(f"Detected anomaly in pod {pod_name}: {prediction.get('anomaly_type', 'unknown')}")
        except Exception as e:
            logger.error(f"Error analyzing pod {pod_name}: {str(e)}")
    
    # Update the state
    return {
        **state,
        "messages": messages,
        "pods_with_anomalies": pods_with_anomalies,
        "status": "anomalies_detected" if pods_with_anomalies else "no_anomalies",
        "active_agent": "anomaly" if pods_with_anomalies else "none"
    }

def orchestrator_plan_remediation(state: OrchestratorState) -> OrchestratorState:
    """Plan remediation for detected anomalies."""
    messages = state["messages"]
    pods_with_anomalies = state["pods_with_anomalies"]
    
    # Initialize remediation_state if it doesn't exist
    if state.get("remediation_state") is None:
        logger.info("Initializing remediation state")
        state["remediation_state"] = {
            "messages": [],
            "prediction": {},
            "pod_info": {},
            "remediation_plan": {},
            "approval_status": "pending",
            "action_status": "waiting"
        }
    
    # Now we can safely use remediation_state
    remediation_state = state["remediation_state"]
    
    # Check if we have pods with anomalies to remediate
    if not pods_with_anomalies:
        messages.append(AIMessage(content="No pods with anomalies detected for remediation planning."))
        return {**state, "active_agent": "none", "status": "no_anomalies"}
    
    messages.append(AIMessage(content=f"Planning remediation for {len(pods_with_anomalies)} pods with anomalies..."))
    
    # Track the number of intentional crashes
    intentional_crashes = 0
    
    # Create remediation plans
    remediation_plans = {}
    
    for pod_name, anomaly_data in pods_with_anomalies.items():
        prediction = anomaly_data.get('prediction', {})
        pod_metrics = anomaly_data.get('pod_metrics', {})
        anomaly_type = prediction.get('anomaly_type', 'unknown')
        details = prediction.get('details', {})
        
        # Check for intentional crashes
        if anomaly_type == "intentional_crash":
            intentional_crashes += 1
            plan = {
                "pod_name": pod_name,
                "issue": "Pod is intentionally configured to exit with code 1",
                "action": "no_action",
                "rationale": "Restarting will not help as pod is programmed to fail",
                "impact": "None - this behavior appears to be by design",
                "warning_level": "low"
            }
            messages.append(AIMessage(content=f"Pod {pod_name} is intentionally configured to crash. No remediation will be applied."))
        
        # Create a remediation plan based on anomaly type
        elif anomaly_type == "crash_loop":
            plan = {
                "pod_name": pod_name,
                "issue": f"Pod is crash looping with {details.get('restart_count', 'multiple')} restarts",
                "action": "restart_deployment",
                "rationale": "Restarting the deployment may resolve the initialization issues",
                "impact": "Momentary service disruption",
                "warning_level": "high"
            }
        elif anomaly_type == "resource_exhaustion":
            plan = {
                "pod_name": pod_name,
                "issue": f"Pod is experiencing resource exhaustion (CPU: {details.get('cpu_usage', 'high')}%, Memory: {details.get('memory_usage', 'high')}%)",
                "action": "increase_limits",
                "rationale": "Current resource limits are insufficient for the workload",
                "impact": "May require additional cluster resources",
                "warning_level": "medium"
            }
        elif anomaly_type == "pod_failure":
            event_reason = details.get('event_reason', 'unknown')
            event_message = details.get('event_message', '')
            
            plan = {
                "pod_name": pod_name,
                "issue": f"Pod is failing with reason: {event_reason} - {event_message}",
                "action": "restart_pod",
                "rationale": "Pod restart may resolve the issue",
                "impact": "Momentary service disruption",
                "warning_level": "medium"
            }
        elif anomaly_type == "network_issue":
            plan = {
                "pod_name": pod_name,
                "issue": f"Pod is experiencing network issues (dropped packets: RX={details.get('dropped_rx', 0)}, TX={details.get('dropped_tx', 0)})",
                "action": "restart_pod",
                "rationale": "Network issues may be resolved by restarting the pod",
                "impact": "Momentary service disruption",
                "warning_level": "medium"
            }
        elif anomaly_type == "container_failure":
            exit_code = details.get('exit_code', 'unknown')
            plan = {
                "pod_name": pod_name,
                "issue": f"Container terminated with exit code {exit_code}",
                "action": "restart_pod",
                "rationale": "Restarting the pod may resolve the issue",
                "impact": "Momentary service disruption",
                "warning_level": "medium"
            }
        else:
            plan = {
                "pod_name": pod_name,
                "issue": f"Pod is experiencing {anomaly_type} issues",
                "action": "restart_pod",
                "rationale": "Pod restart may resolve the issue",
                "impact": "Momentary service disruption",
                "warning_level": "medium"
            }
        
        # Only add plans that have actual actions
        if plan["action"] != "no_action":
            remediation_plans[pod_name] = plan
            messages.append(AIMessage(content=f"Remediation plan for {pod_name}: {plan['action']} ({plan['warning_level']} warning)"))
    
    # If all anomalies are intentional crashes, inform the user
    if intentional_crashes > 0 and len(remediation_plans) == 0:
        messages.append(AIMessage(content=f"All {intentional_crashes} detected anomalies are intentional crashes. No remediation actions will be taken."))
        return {**state, "active_agent": "none", "status": "no_actionable_anomalies"}
    
    # If we have no plans after filtering out "no_action" plans, return early
    if not remediation_plans:
        messages.append(AIMessage(content="No actionable remediation plans generated."))
        return {**state, "active_agent": "none", "status": "no_actionable_anomalies"}
    
    # Update the state
    return {
        **state,
        "remediation_state": {
            **remediation_state,
            "remediation_plan": remediation_plans
        },
        "status": "remediation_planned",
        "active_agent": "remediation"
    }

def orchestrator_execute_remediation(state: OrchestratorState) -> OrchestratorState:
    """Execute remediation plans."""
    messages = state["messages"]
    remediation_state = state.get("remediation_state", {})
    remediation_plans = remediation_state.get("remediation_plan", {})
    
    if not remediation_plans:
        messages.append(AIMessage(content="No remediation plans to execute."))
        return {**state, "active_agent": "none", "status": "no_remediation"}
    
    messages.append(AIMessage(content=f"Executing remediation plans for {len(remediation_plans)} pods..."))
    
    # Track if any remediation was successful
    any_successful_remediation = False
    remediation_results = {}
    
    for pod_name, plan in remediation_plans.items():
        action = plan.get("action", "unknown")
        namespace = "default"  # Default namespace
        
        # Get pod info from the monitoring state to find the namespace
        pod_metrics = state.get("monitoring_state", {}).get("pod_metrics", {}).get(pod_name, {})
        if pod_metrics:
            namespace = pod_metrics.get("Namespace", "default")
        
        try:
            # Improve logging to explain root cause
            logger.info(f"Executing remediation for pod {pod_name}: {action}")
            messages.append(AIMessage(content=f"Executing {action} for pod {namespace}/{pod_name}"))
            
            # Check pod status and reason for failure before remediation
            if not API_CONFIG.get("test_mode", False):
                try:
                    pod_info = core_api.read_namespaced_pod(name=pod_name, namespace=namespace)
                    status_phase = pod_info.status.phase
                    container_statuses = pod_info.status.container_statuses or []
                    
                    # Log detailed status information
                    if container_statuses:
                        for container in container_statuses:
                            if container.state.waiting:
                                reason = container.state.waiting.reason
                                message = container.state.waiting.message
                                messages.append(AIMessage(content=f"Container {container.name} is waiting: {reason} - {message}"))
                            elif container.state.terminated:
                                exit_code = container.state.terminated.exit_code
                                reason = container.state.terminated.reason
                                messages.append(AIMessage(content=f"Container {container.name} terminated with exit code {exit_code}: {reason}"))
                    
                    messages.append(AIMessage(content=f"Pod status before remediation: {status_phase}"))
                except Exception as e:
                    messages.append(AIMessage(content=f"Could not get pod status: {str(e)}"))
            
            # Execute the appropriate remediation action
            if action == "restart_pod":
                if not API_CONFIG.get("test_mode", False):
                    try:
                        # Delete pod to trigger recreation by the controller
                        core_api.delete_namespaced_pod(
                            name=pod_name,
                            namespace=namespace,
                            body=client.V1DeleteOptions()
                        )
                        success_msg = f"Successfully restarted pod {namespace}/{pod_name}"
                        messages.append(AIMessage(content=success_msg))
                        logger.info(success_msg)
                        any_successful_remediation = True
                        remediation_results[pod_name] = {"success": True, "action": action}
                    except Exception as e:
                        if hasattr(e, 'status') and e.status == 404:
                            # Pod not found - this is ok if the pod was already deleted
                            warning_msg = f"Pod {namespace}/{pod_name} not found. It may have been already deleted."
                            messages.append(AIMessage(content=warning_msg))
                            logger.warning(warning_msg)
                            remediation_results[pod_name] = {"success": False, "action": action, "reason": "Pod not found"}
                        else:
                            # Other API exceptions
                            error_msg = f"Error restarting pod {namespace}/{pod_name}: {str(e)}"
                            messages.append(AIMessage(content=error_msg))
                            logger.error(error_msg)
                            remediation_results[pod_name] = {"success": False, "action": action, "error": str(e)}
                else:
                    # Test mode simulation
                    test_msg = f"[TEST MODE] Would restart pod {namespace}/{pod_name}"
                    messages.append(AIMessage(content=test_msg))
                    logger.info(test_msg)
                    any_successful_remediation = True
                    remediation_results[pod_name] = {"success": True, "action": action, "test_mode": True}
            
            elif action == "restart_deployment":
                # Find the deployment for this pod
                if not API_CONFIG.get("test_mode", False):
                    try:
                        # This would typically involve finding the deployment and restarting it
                        # For now, just log what would be done
                        messages.append(AIMessage(content=f"Would restart deployment for pod {namespace}/{pod_name}"))
                        logger.info(f"Would restart deployment for pod {namespace}/{pod_name}")
                        remediation_results[pod_name] = {"success": False, "action": action, "reason": "Not implemented"}
                    except Exception as e:
                        error_msg = f"Error processing deployment for {namespace}/{pod_name}: {str(e)}"
                        messages.append(AIMessage(content=error_msg))
                        logger.error(error_msg)
                        remediation_results[pod_name] = {"success": False, "action": action, "error": str(e)}
                else:
                    messages.append(AIMessage(content=f"[TEST MODE] Would restart deployment for {namespace}/{pod_name}"))
                    remediation_results[pod_name] = {"success": True, "action": action, "test_mode": True}
            
            elif action == "increase_limits":
                # Would implement resource limit increases
                messages.append(AIMessage(content=f"Resource limit increase not implemented for {namespace}/{pod_name}"))
                remediation_results[pod_name] = {"success": False, "action": action, "reason": "Not implemented"}
            
            else:
                messages.append(AIMessage(content=f"Unknown action {action} for pod {namespace}/{pod_name}"))
                remediation_results[pod_name] = {"success": False, "action": action, "reason": "Unknown action"}
                
        except Exception as e:
            error_msg = f"Error executing remediation for pod {pod_name}: {str(e)}"
            logger.error(error_msg)
            messages.append(AIMessage(content=error_msg))
            remediation_results[pod_name] = {"success": False, "action": "unknown", "error": str(e)}
    
    # Log completion and add a summary message
    total_plans = len(remediation_plans)
    successful = sum(1 for result in remediation_results.values() if result.get("success", False))
    messages.append(AIMessage(content=f"Remediation completed. {successful}/{total_plans} actions successful."))
    
    # In non-test mode, we'd wait for the monitoring interval before running again
    # In test mode, display a message about waiting
    if API_CONFIG.get("test_mode", False):
        messages.append(AIMessage(content=f"Waiting {API_CONFIG.get('interval', 60)} seconds before next monitoring cycle..."))
    
    # If the pod is programmed to fail (i.e., it has a command to exit with error),
    # add a special note about this being an expected behavior
    if any("exit 1" in str(pod_metrics.get("Command", "")) for pod_name, pod_metrics in state.get("monitoring_state", {}).get("pod_metrics", {}).items()):
        messages.append(AIMessage(content="NOTE: Some pods are configured to exit with code 1 intentionally. This will cause repeated failures that cannot be fixed by restarting."))
    
    # Update the state
    # Only clear anomalies that were successfully remediated
    updated_pods_with_anomalies = {}
    if not any_successful_remediation:
        # If no remediation was successful, keep the anomalies
        updated_pods_with_anomalies = state["pods_with_anomalies"]
        messages.append(AIMessage(content="Warning: No successful remediations. Issues may persist."))
    
    return {
        **state,
        "status": "remediation_executed",
        "active_agent": "none",
        "pods_with_anomalies": updated_pods_with_anomalies,  # Only clear if successful
        "remediation_state": {
            **remediation_state,
            "remediation_plan": {},  # Clear remediation plans
            "remediation_results": remediation_results  # Store results for reference
        }
    }

def process_command(state: OrchestratorState) -> OrchestratorState:
    """Process user commands."""
    messages = state["messages"]
    command = state["command"]
    
    if not command:
        return {**state}
    
    if command.lower() == "help":
        help_text = """Available commands:
- help: Display this help message
- status: Show the current system status
- metrics: Show the latest metrics for all pods
- anomalies: Show detected anomalies
- remediate: Execute remediation for detected anomalies
- exit: Exit the system
"""
        messages.append(AIMessage(content=help_text))
    
    elif command.lower() == "status":
        status_text = f"""Current system status:
- Active agent: {state['active_agent']}
- Status: {state['status']}
- Pods with anomalies: {len(state['pods_with_anomalies'])}
- Last metrics collection: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(state['monitoring_state'].get('last_run_time', 0)))}
"""
        messages.append(AIMessage(content=status_text))
    
    elif command.lower() == "metrics":
        pod_metrics = state.get("monitoring_state", {}).get("pod_metrics", {})
        if pod_metrics:
            metrics_text = "Latest pod metrics:\n"
            for pod_name, metrics in pod_metrics.items():
                metrics_text += f"\n- {pod_name}:\n"
                for metric_name, value in metrics.items():
                    metrics_text += f"  {metric_name}: {value}\n"
            messages.append(AIMessage(content=metrics_text))
        else:
            messages.append(AIMessage(content="No metrics data available. Try running a monitoring cycle first."))
    
    elif command.lower() == "anomalies":
        pods_with_anomalies = state["pods_with_anomalies"]
        if pods_with_anomalies:
            anomalies_text = "Detected anomalies:\n"
            for pod_name, data in pods_with_anomalies.items():
                prediction = data.get('prediction', {})
                anomaly_type = prediction.get('anomaly_type', 'unknown')
                probability = prediction.get('anomaly_probability', 0)
                priority = data.get('priority', 0)
                anomalies_text += f"\n- {pod_name}:\n"
                anomalies_text += f"  Type: {anomaly_type}\n"
                anomalies_text += f"  Probability: {probability:.2f}\n"
                anomalies_text += f"  Priority: {priority}\n"
            messages.append(AIMessage(content=anomalies_text))
        else:
            messages.append(AIMessage(content="No anomalies detected."))
    
    elif command.lower() == "remediate":
        # Force the orchestrator to move to remediation planning
        if state["pods_with_anomalies"]:
            messages.append(AIMessage(content="Starting remediation planning for detected anomalies..."))
            return {**state, "command": None, "status": "anomalies_detected", "active_agent": "anomaly"}
        else:
            messages.append(AIMessage(content="No anomalies detected that require remediation."))
    
    elif command.lower() == "exit":
        messages.append(AIMessage(content="Exiting Kubernetes multi-agent system."))
        return {**state, "command": "exit"}
    
    else:
        messages.append(AIMessage(content=f"Unknown command: {command}. Type 'help' for available commands."))
    
    # Reset command after processing
    return {**state, "command": None}

def predict_pod_anomaly(metrics: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Predict if a pod has an anomaly using simple heuristics.
    
    Args:
        metrics: Dictionary of pod metrics
        
    Returns:
        Tuple of (is_anomaly, prediction_dict)
    """
    is_anomaly = False
    anomaly_type = "none"
    anomaly_probability = 0.0
    anomaly_details = {}
    
    # Check for intentional crashes first
    command = str(metrics.get("Command", ""))
    if "exit 1" in command:
        is_anomaly = True
        anomaly_type = "intentional_crash"
        anomaly_probability = 0.99
        anomaly_details["command"] = command
        anomaly_details["description"] = "Pod is configured to exit with code 1 intentionally"
    
    # Check restart count
    restart_count = metrics.get("Pod Restarts", 0)
    if restart_count > 5:
        is_anomaly = True
        if anomaly_type == "none":  # Don't override intentional crash
            anomaly_type = "crash_loop"
        anomaly_probability = max(anomaly_probability, min(0.5 + (restart_count / 20), 0.95))
        anomaly_details["restart_count"] = restart_count
    
    # Check resource usage
    cpu_usage = metrics.get("CPU Usage (%)", 0)
    memory_usage = metrics.get("Memory Usage (%)", 0)
    if cpu_usage > 90 or memory_usage > 90:
        is_anomaly = True
        if anomaly_type == "none":  # Don't override previous types
            anomaly_type = "resource_exhaustion"
        anomaly_probability = max(anomaly_probability, min(cpu_usage, memory_usage) / 100)
        anomaly_details["cpu_usage"] = cpu_usage
        anomaly_details["memory_usage"] = memory_usage
    
    # Check events
    event_reason = metrics.get("Event Reason", "")
    if event_reason in ["BackOff", "Failed", "FailedMount", "FailedScheduling", "OutOfmemory"]:
        is_anomaly = True
        if anomaly_type == "none" or (anomaly_type != "intentional_crash" and event_reason == "BackOff"):
            anomaly_type = "pod_failure"
        anomaly_probability = max(anomaly_probability, 0.85)
        anomaly_details["event_reason"] = event_reason
        anomaly_details["event_message"] = metrics.get("Event Message", "")
    
    # Check network issues
    dropped_rx = metrics.get("Network Receive Packets Dropped (p/s)", 0)
    dropped_tx = metrics.get("Network Transmit Packets Dropped (p/s)", 0)
    if dropped_rx > 0 or dropped_tx > 0:
        is_anomaly = True
        if anomaly_type == "none":  # Don't override previous types
            anomaly_type = "network_issue"
        anomaly_probability = max(anomaly_probability, 0.70)
        anomaly_details["dropped_rx"] = dropped_rx
        anomaly_details["dropped_tx"] = dropped_tx
    
    # Check container status
    container_state = metrics.get("Container State", "")
    if container_state == "terminated":
        exit_code = metrics.get("Exit Code", 0)
        if exit_code != 0:
            is_anomaly = True
            if anomaly_type == "none":
                if exit_code == 1 and "exit 1" in command:
                    anomaly_type = "intentional_crash"
                else:
                    anomaly_type = "container_failure"
            anomaly_probability = max(anomaly_probability, 0.90)
            anomaly_details["exit_code"] = exit_code
            anomaly_details["container_state"] = container_state
    
    prediction = {
        "predicted_anomaly": 1 if is_anomaly else 0,
        "anomaly_probability": anomaly_probability,
        "anomaly_type": anomaly_type,
        "details": anomaly_details
    }
    
    return is_anomaly, prediction

def main():
    """
    Main function to run the Kubernetes multi-agent system.
    """
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Kubernetes Multi-Agent System')
    parser.add_argument('--namespace', type=str, default='default',
                        help='Kubernetes namespace to monitor (default: default)')
    parser.add_argument('--interval', type=int, default=60,
                        help='Monitoring interval in seconds (default: 60)')
    parser.add_argument('--test', action='store_true',
                        help='Run in test mode (no actual Kubernetes actions)')
    parser.add_argument('--llm', type=str, choices=['auto', 'openai', 'nvidia', 'llama', 'none'], default='auto',
                        help='LLM provider to use (default: auto)')
    parser.add_argument('--llama-api-key', type=str, help='API key for Llama API')
    parser.add_argument('--llama-api-url', type=str, default='https://api.llama-api.com',
                        help='URL for Llama API (default: https://api.llama-api.com)')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--max-iterations', type=int, default=0,
                        help='Maximum number of iterations to run (0 for infinite)')
    parser.add_argument('--recursion-limit', type=int, default=10,
                        help='Maximum recursion depth in the workflow (default: 10)')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
        logger.setLevel(logging.INFO)
    
    # Configure global API settings
    global API_CONFIG
    API_CONFIG.update({
        "namespace": args.namespace,
        "interval": args.interval,
        "test_mode": args.test,
        "llm": args.llm,
        "max_iterations": args.max_iterations,
        "recursion_limit": args.recursion_limit
    })
    
    # Set API keys from arguments if provided
    if args.llama_api_key:
        os.environ["LLAMA_API_KEY"] = args.llama_api_key
    if args.llama_api_url:
        os.environ["LLAMA_API_URL"] = args.llama_api_url
    
    # Load Kubernetes configuration
    try:
        config.load_kube_config()
        logger.info("Loaded Kubernetes config from default location")
    except Exception:
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config")
        except Exception as e:
            if not args.test:
                logger.error(f"Failed to load Kubernetes configuration: {e}")
                logger.warning("Running in test mode due to Kubernetes config failure")
                API_CONFIG["test_mode"] = True
    
    # Display welcome banner
    print("\nKubernetes Multi-Agent System")
    print("===========================")
    print(f"Version: 1.0.0")
    print(f"LLM Provider: {API_CONFIG.get('llm_provider', 'none')}")
    print(f"Test Mode: {'Enabled' if API_CONFIG.get('test_mode', False) else 'Disabled'}")
    print(f"Debug Mode: {'Enabled' if args.debug else 'Disabled'}")
    print(f"Namespace: {args.namespace}")
    print(f"Monitoring Interval: {args.interval} seconds")
    print(f"Max Iterations: {args.max_iterations if args.max_iterations > 0 else 'Unlimited'}")
    print(f"Recursion Limit: {args.recursion_limit}")
    print("===========================")
    print("Type 'help' for available commands\n")
    
    try:
        # Run the monitoring cycle directly - simpler approach
        max_iterations = args.max_iterations
        iteration_count = 0
        
        # Initialize the state
        state = {
            "messages": [],
            "monitoring_state": {
                "messages": [],
                "metrics_data": {},
                "pod_metrics": {},
                "pod_history": {},
                "status": "idle",
                "last_run_time": 0,
                "action": "none"
            },
            "anomaly_state": {
                "messages": [],
                "metrics_data": {},
                "prediction_result": {},
                "pod_info": {},
                "action": "none"
            },
            "remediation_state": {
                "messages": [],
                "prediction": {},
                "pod_info": {},
                "remediation_plan": {},
                "approval_status": "pending",
                "action_status": "waiting"
            },
            "active_agent": "none",
            "pods_with_anomalies": {},
            "current_pod": None,
            "approved_remediations": [],
            "approval_queue": [],
            "command": None,
            "status": "starting",
            "iteration_count": 0
        }
        
        # Add welcome message
        welcome_message = """Welcome to the Kubernetes Multi-Agent System!
        
I am the Orchestrator agent that coordinates monitoring, anomaly detection, and remediation.
        
Type 'help' for available commands or press Enter to start monitoring."""
        state["messages"].append(AIMessage(content=welcome_message))
        
        # Main interactive loop
        running = True
        while running:
            if iteration_count >= max_iterations and max_iterations > 0:
                print(f"Reached maximum iterations: {max_iterations}")
                break
                
            print(f"\n--- Iteration {iteration_count + 1} ---")
            if state["messages"]:
                print(state["messages"][-1].content)
            
            # Step 1: Collect metrics
            print("\nCollecting metrics...")
            state = orchestrator_collect_metrics(state)
            if state["messages"]:
                print(state["messages"][-1].content)
            
            # Step 2: Detect anomalies
            print("\nDetecting anomalies...")
            state = orchestrator_detect_anomalies(state)
            if state["messages"]:
                print(state["messages"][-1].content)
            
            # Step 3: Plan remediation
            if state["pods_with_anomalies"]:
                print("\nPlanning remediation...")
                state = orchestrator_plan_remediation(state)
                if state["messages"]:
                    print(state["messages"][-1].content)
                
                # Add confirmation prompt for remediation execution
                execute_confirm = input("\nDo you want to execute the remediation plan? (y/n): ")
                if execute_confirm.lower() in ["y", "yes"]:
                    # Step 4: Execute remediation
                    print("\nExecuting remediation...")
                    state = orchestrator_execute_remediation(state)
                    if state["messages"]:
                        print(state["messages"][-1].content)
                else:
                    print("Remediation execution skipped.")
                    # Clear remediation plans since we're skipping execution
                    state["pods_with_anomalies"] = {}
                    if "remediation_state" in state:
                        state["remediation_state"]["remediation_plan"] = {}
            
            # Increment and check iteration count
            iteration_count += 1
            state["iteration_count"] = iteration_count
            
            # Check for user input
            if iteration_count < max_iterations or max_iterations == 0:
                try:
                    command = input("\nShould I continue to the next monitoring cycle? (y/n): ")
                    if command.lower() in ["n", "no", "exit"]:
                        print("Exiting...")
                        break
                    elif command.lower() not in ["y", "yes", ""]:
                        # Treat any non-yes/no input as a command
                        state["command"] = command
                        state = process_command(state)
                        if state["messages"]:
                            print(state["messages"][-1].content)
                        # After processing a command, ask again if user wants to continue
                        continue_resp = input("Continue to the next monitoring cycle? (y/n): ")
                        if continue_resp.lower() in ["n", "no"]:
                            print("Exiting...")
                            break
                except KeyboardInterrupt:
                    print("\nReceived keyboard interrupt, exiting...")
                    break
                
                # Wait before next iteration (unless it's the last iteration)
                if iteration_count < max_iterations or max_iterations == 0:
                    if API_CONFIG.get("test_mode", False):
                        print(f"\nWaiting {args.interval} seconds before next monitoring cycle...")
                        time.sleep(0.5)  # shorter sleep for test mode
                    else:
                        print(f"\nWaiting {args.interval} seconds before next monitoring cycle...")
                        time.sleep(args.interval)
                        
        print("\nMonitoring cycle completed.")
                
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
        import traceback
        traceback.print_exc()
    
    logger.info("Shutting down Kubernetes multi-agent system.")
    return 0

if __name__ == "__main__":
    main() 