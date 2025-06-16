
# Kubernetes Monitoring, Remediation, and RAG System

This project provides a comprehensive solution for monitoring Kubernetes clusters, detecting anomalies, providing remediation recommendations, and answering queries about Kubernetes using a Retrieval Augmented Generation (RAG) system with real-time Minikube integration.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Collection Layer                            │
│  ┌────────────────┐        ┌─────────────────────────────────┐  │
│  │ dataset-generator.py│        │run_agent_with_custom_metrics│  │
│  └────────────────┘        └─────────────────────────────────┘  │
│                               │                                  │
│                               ▼                                  │
│                      ┌───────────────┐                          │
│                      │pod_metrics.csv │                          │
│                      └───────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Processing Layer                            │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 Dataset Generator Agent                     │ │
│  │            (src/agents/dataset_generator_agent.py)          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────┐      │     ┌───────────────────────┐    │
│  │ Anomaly Prediction │◄─────┴────►│    pod_insights.json  │    │
│  │        Model       │            └───────────────────────┘    │
│  └────────────────┘                                         │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Analysis Layer                             │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                 Anomaly Detection Agent                     │ │
│  │            (src/agents/anomaly_detection_agent.py)          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                               │                                  │
│                               ▼                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     LLM Integration                         │ │
│  │           (Llama-3.1-Nemotron-70B-Instruct)                 │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Processing Layer

#### Dataset Generator Agent (src/agents/dataset_generator_agent.py)

**Purpose**: Processes collected metrics, performs preprocessing, and detects anomalies.

**Implementation Details**:
- Continuously watches CSV file for new data entries
- Maintains historical data for trend analysis
- Processes raw metrics into features suitable for the ML model
- Communicates with the anomaly detection model
- Generates structured insights based on model output

#### Anomaly Prediction Model (models/anomaly_prediction.py)

**Purpose**: ML model that detects anomalies in pod behavior patterns.

**Implementation Details**:
- LSTM-based neural network for time series analysis
- Trained on historical pod behavior patterns
- Uses statistical methods to identify deviations
- Returns anomaly probability scores for each pod

### Analysis Layer

#### Anomaly Detection Agent (src/agents/anomaly_detection_agent.py)

**Purpose**: Analyzes anomalies more deeply and generates explanations.

**Implementation Details**:
- Works with the Dataset Generator Agent's output
- Provides detailed analysis of why anomalies occurred
- Generates recommendations for remediation
- Can use LLM integration for enhanced analysis

#### K8s Metrics Collector (src/agents/k8s_metrics_collector.py)

**Purpose**: Collects metrics from Kubernetes API and Prometheus.

**Implementation Details**:
- Interfaces with Kubernetes API for pod information
- Retrieves metrics from Prometheus for detailed resource usage
- Formats metrics into standardized format for analysis

#### Multi-Agent System (src/agents/k8s_multi_agent_system.py)

**Purpose**: Orchestrates all components of the monitoring and remediation system.

**Implementation Details**:
- Coordinates metrics collection, anomaly detection, and remediation
- Manages state across different agents
- Provides unified interface for the entire system
- Handles communication between components

## Data Flow

### Monitoring and Remediation Flow

1. **Collection**: Kubernetes metrics are collected from cluster via API and Prometheus
2. **Storage**: Raw metrics are stored in CSV format (pod_metrics.csv)
3. **Processing**: The Dataset Generator Agent reads and processes this data
4. **Analysis**:
   - The agent applies the anomaly prediction model
   - Anomalies are detected and scored
   - Insights are generated (stored in pod_insights.json)
5. **Enhanced Analysis**:
   - The Anomaly Detection Agent performs deeper analysis
   - Optional LLM integration provides natural language insights
6. **Orchestration**:
   - The Multi-Agent System coordinates all components
   - Ensures proper flow of data and control between layers

### RAG System with Real-time Information Flow

1. **User Query**: User submits a question through the CLI interface
2. **Query Analysis**: System determines if the query requires real-time information
3. **Knowledge Retrieval**:
   - For general knowledge: Retrieves information from the ChromaDB knowledge base
   - For real-time queries: Fetches current information from the Minikube cluster
4. **Context Building**: Combines retrieved knowledge with real-time information
5. **Response Generation**: Uses an LLM to generate a comprehensive response
6. **Presentation**: Displays the formatted response to the user

## RAG System with Minikube Integration

The project now includes a Retrieval Augmented Generation (RAG) system that can answer questions about Kubernetes and fetch real-time information from your Minikube cluster.

### Features

- **Interactive CLI Chat Interface**: Ask questions about Kubernetes concepts, troubleshooting, or best practices
- **Real-time Kubernetes Information**: Fetch live information from your Minikube cluster
- **Context-aware Responses**: Combines static knowledge with real-time cluster state
- **Chain of Thought Reasoning**: Detailed explanations with step-by-step reasoning
- **Minikube Integration**: Automatically detects and adapts to Minikube environments

### Using the RAG System

Run the CLI interface:

```bash
# Navigate to the src directory
cd k8s/src

# Run the CLI
python agentic_rag_cli.py
```

If Minikube is running, the system will automatically detect it and enable real-time information fetching.

### Example Queries

You can ask various questions about Kubernetes concepts and your Minikube cluster:

- **General Kubernetes Knowledge**:
  - "What is a Pod in Kubernetes?"
  - "How do I troubleshoot a CrashLoopBackOff error?"
  - "Explain Kubernetes RBAC"

- **Real-time Minikube Information**:
  - "Show me the pods in my cluster"
  - "What services are running?"
  - "Display node information"
  - "Get the status of my deployments"
  - "Show me the logs for pod my-pod-name"

## Directory Structure

```
k8s/
├── config/                  # Configuration files
├── data/                    # Data storage directory
│   ├── pod_metrics.csv      # Raw metrics data
│   └── pod_insights.json    # Anomaly insights
├── logs/                    # Log files
├── models/                  # Machine learning models
│   ├── anomaly_prediction.py
│   └── model_artifacts/     # Trained model files
├── src/                     # Source code
│   ├── agents/              # Agent implementations
│   │   ├── anomaly_detection_agent.py
│   │   ├── dataset_generator_agent.py
│   │   └── k8s_multi_agent_system.py
│   ├── agentic_rag_cli.py   # RAG system CLI interface
│   ├── k8s_client_utils.py  # Kubernetes client utilities
│   ├── k8s_knowledge_fetcher.py # Kubernetes knowledge fetcher
│   ├── rag_utils.py         # RAG utilities
│   └── utils/               # Shared utilities
├── dataset-generator.py     # Data collection script
├── run_monitoring.py        # Orchestration script
└── requirements.txt         # Dependencies
```

## Commands

### Run the RAG System with Minikube Integration:

```bash
cd src
python agentic_rag_cli.py
```

### Run the Multi-Agent System:

```bash
cd src/agents
python k8s_multi_agent_system.py
```

### Run All Monitoring Components:

```bash
python run_monitoring.py
```

### Run Individual Components:

```bash
# Dataset Generator
python dataset-generator.py

# Dataset Generator Agent
python src/agents/dataset_generator_agent.py

# Anomaly Detection Agent
python anomaly_detection_agent.py

# Metrics Collection
python fetch_metrics.py
```

### Command-line Options:

```bash
# Run monitoring with custom parameters
python run_monitoring.py --prometheus-url http://localhost:8082 --namespace monitoring --generator-interval 5 --output-file pod_metrics.csv --watch-interval 10 --alert-threshold 0.7
```

Key parameters:
- `--prometheus-url`: Prometheus URL (default: http://localhost:8082)
- `--namespace`: Kubernetes namespace to monitor (default: monitoring)
- `--generator-interval`: Interval in seconds between metrics collection (default: 5)
- `--output-file`: Output file for metrics (default: pod_metrics.csv)
- `--watch-interval`: Interval in seconds between agent checks (default: 10)
- `--alert-threshold`: Probability threshold for anomaly alerts (default: 0.7)

## Installation and Setup

### Prerequisites

- Python 3.8 or higher
- Minikube (for local Kubernetes cluster)
- Kubernetes CLI (kubectl)
- Prometheus (optional, for metrics collection)

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/kubernetes-monitoring-rag.git
cd kubernetes-monitoring-rag
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set up environment variables (create a .env file in the project root):

```
# Required for LLM integration
LLAMA_API_KEY=your_llama_api_key
LLAMA_API_URL=your_llama_api_url

# Optional: Use NVIDIA API if available
NVIDIA_API_KEY=your_nvidia_api_key
```

### Setting up Minikube

For Windows:

```bash
./setup_minikube.ps1
```

For Linux/Mac:

```bash
./setup_minikube.sh
```

Or follow the manual setup instructions in MINIKUBE_SETUP.md.
```

        
