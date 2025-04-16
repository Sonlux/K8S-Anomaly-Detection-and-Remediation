# Kubernetes Monitoring and Remediation System

A comprehensive platform for monitoring Kubernetes clusters, detecting anomalies using machine learning, generating actionable insights, and performing automated remediation with user approval.

## 📋 Table of Contents

- [Overview](#overview)
- [System Architecture](#system-architecture)
- [Components](#components)
- [Installation](#installation)
- [Setting Up Kubernetes Locally](#setting-up-kubernetes-locally)
- [Usage Guide](#usage-guide)
  - [Basic Usage](#basic-usage)
  - [Advanced Configuration](#advanced-configuration)
  - [Command Line Options](#command-line-options)
- [Multi-Agent System](#multi-agent-system)
- [Agent Modes](#agent-modes)
- [Metrics Collection](#metrics-collection)
- [Anomaly Detection](#anomaly-detection)
- [Remediation Actions](#remediation-actions)
- [Integration with LLMs](#integration-with-llms)
- [Output and Logs](#output-and-logs)
- [Troubleshooting](#troubleshooting)
- [Development Guide](#development-guide)
- [License](#license)

## 🔍 Overview

This system provides end-to-end Kubernetes cluster monitoring with intelligent anomaly detection and automated remediation capabilities. It combines traditional metrics collection with machine learning models and optional Language Model (LLM) integration to provide deeper insights and context-aware remediation recommendations.

## 🏗️ System Architecture

The system follows a modular architecture with the following key components:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  K8s Cluster    │───▶│  Dataset        │───▶│  CSV Metrics    │
│  (Pods/Nodes)   │    │  Generator      │    │  File           │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│                 │    │                 │    │                 │
│  Remediation    │◀───│  Anomaly        │◀───│  Dataset        │
│  Agent          │    │  Detection      │    │  Generator      │
│                 │    │  Agent          │    │  Agent          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🧩 Components

### Dataset Generator (`dataset-generator.py`)
Collects real-time metrics from Kubernetes pods including:
- CPU and memory usage
- Network traffic and errors
- Pod status and restart counts
- Container statuses
- Custom metrics via Prometheus (optional)

### Dataset Generator Agent (`src/agents/dataset_generator_agent.py`)
Monitors metrics files and provides actionable insights:
- Watches CSV metrics files for changes
- Preprocesses raw metrics data
- Maintains historical metrics for trend analysis
- Detects anomalies using the prediction model
- Generates and outputs actionable insights

### Anomaly Detection Agent (`src/agents/anomaly_detection_agent.py`)
Analyzes pod metrics for anomalies:
- Uses machine learning to identify abnormal behavior
- Generates detailed insights about detected issues
- Supports integration with different ML models

### Remediation Agent (`run_remediation.py`)
Interactive agent that proposes and executes corrective actions:
- Suggests remediation based on detected anomalies
- Requires explicit approval before taking action
- Provides feedback on remediation outcomes
- Logs all actions for audit purposes

### Integration Scripts
- `run_monitoring.py`: Orchestrates dataset generation and agent monitoring
- `run_agent_with_custom_metrics.py`: Supports custom metric collection

## 💻 Installation

### Prerequisites
- Python 3.8+
- Kubernetes cluster (Minikube/local or remote)
- Prometheus monitoring (optional but recommended)

### Step-by-Step Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kubernetes-monitoring.git
   cd kubernetes-monitoring
   ```

2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/Mac:
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Kubernetes access:
   - For Minikube: `minikube start`
   - For remote clusters: Ensure your `~/.kube/config` is properly configured

5. Verify installation:
   ```bash
   python dataset-generator.py --test
   ```

## 🌐 Setting Up Kubernetes Locally

To run this system with a local Kubernetes environment, follow these steps:

### 1. Starting Minikube

Minikube is a tool that lets you run Kubernetes locally. To start a Minikube cluster:

```bash
minikube start
```

This command creates a local Kubernetes cluster with a single node. You can customize the resources with:

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

### 2. Setting Up Prometheus for Monitoring

The system works best with Prometheus for metrics collection. To set up Prometheus:

1. **Install Prometheus using Helm**:
   ```bash
   # Add Prometheus Helm repository
   helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
   helm repo update

   # Create a monitoring namespace
   kubectl create namespace monitoring
   
   # Install Prometheus stack
   helm install prometheus prometheus-community/kube-prometheus-stack --namespace monitoring
   ```

2. **Set up port-forwarding for Prometheus**:
   ```bash
   kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
   ```
   
   This command makes Prometheus accessible at `http://localhost:9090`

3. **Verify Prometheus is working**:
   - Open `http://localhost:9090` in your browser
   - You should see the Prometheus UI

### 3. Deploy Test Applications (Optional)

To generate meaningful metrics, deploy some test applications to your cluster:

```bash
kubectl apply -f config/test-deployments.yaml
```

This will create test pods that generate variable workloads for monitoring.

## 🚀 Usage Guide

### Basic Usage

#### 1. All-in-one Monitoring

Run the complete monitoring system with a single command:

```bash
python run_monitoring.py
```

This will start both the dataset generator and monitoring agents in a coordinated process.

#### 2. Component-by-Component Approach

Alternatively, run each component separately:

1. **Generate Dataset**:
   ```bash
   python dataset-generator.py --output-file pod_metrics.csv
   ```

2. **Run Dataset Generator Agent**:
   ```bash
   python src/agents/dataset_generator_agent.py --input-file pod_metrics.csv
   ```

3. **Run Remediation Agent**:
   ```bash
   python run_remediation.py --metrics-file pod_metrics.csv
   ```

### Advanced Configuration

#### Configuration Files

You can create custom configuration files in the `config/` directory:

- `config/prometheus.yaml`: Configure Prometheus connection details
- `config/agent_config.yaml`: Set agent behavior parameters
- `config/model_config.yaml`: Configure ML model parameters

#### Environment Variables

Key environment variables you can set:

```bash
# Model configuration
export MODEL_PATH=/path/to/custom/model.h5
export THRESHOLD=0.75

# Kubernetes configuration
export KUBECONFIG=/path/to/custom/config
export K8S_NAMESPACE=monitoring

# OpenAI integration (optional)
export OPENAI_API_KEY=your-api-key
```

### Command Line Options

#### Dataset Generator

```bash
python dataset-generator.py [OPTIONS]

Options:
  --output-file TEXT       Output file for metrics (default: pod_metrics.csv)
  --prometheus-url TEXT    Prometheus server URL (default: http://localhost:9090)
  --namespace TEXT         Kubernetes namespace to monitor (default: default)
  --interval INTEGER       Interval in seconds between metric collection (default: 30)
  --test                   Test connection without collecting metrics
```

#### Dataset Generator Agent

```bash
python src/agents/dataset_generator_agent.py [OPTIONS]

Options:
  --input-file TEXT        Input metrics CSV file (default: pod_metrics.csv)
  --watch-interval INTEGER Interval in seconds between checks (default: 10)
  --alert-threshold FLOAT  Probability threshold for anomaly alerts (default: 0.7)
  --test                   Test agent setup without running the main loop
  -agent, --agent-only     Run only the agent component (analyzes existing metrics)
  -fetch, --fetch-only     Run only the dataset generator (fetches new metrics)
```

#### Remediation Agent

```bash
python run_remediation.py [OPTIONS]

Options:
  --metrics-file TEXT      Path to metrics CSV file (default: pod_metrics.csv)
  --watch-interval INTEGER Seconds between checks (default: 10)
  --confidence-threshold FLOAT  Threshold for anomaly alerts (default: 0.7)
  --dry-run                Show recommendations without applying changes
  --auto-approve           Automatically approve remediation actions (USE WITH CAUTION)
```

## 🤖 Multi-Agent System

The core of this platform is the Multi-Agent System, which orchestrates all monitoring and remediation functions.

### Running the Multi-Agent System

The `k8s_multi_agent_system.py` script provides a unified interface to run all agents together:

```bash
python k8s_multi_agent_system.py
```

This comprehensive script:
- Coordinates data collection, analysis, and remediation
- Manages communication between agents
- Maintains a central state for the entire system
- Provides a unified CLI for controlling all system aspects

### Configuration Options

The Multi-Agent System supports all configuration options from individual components, plus:

```bash
python k8s_multi_agent_system.py [OPTIONS]

Options:
  --config-file TEXT      Path to a YAML configuration file
  --agent-mode TEXT       Operation mode: full, monitoring, or remediation
  --log-level TEXT        Logging level: debug, info, warning, error
  --ui                    Enable web UI dashboard (experimental)
  --openai-api-key TEXT   OpenAI API key for LLM integration
```

### Advanced Features

The Multi-Agent System includes several advanced features:

1. **Agent Coordination**: Intelligent coordination between all agents
2. **Unified State Management**: Centralized state tracking across all agents
3. **Dynamic Reconfiguration**: Adjust system parameters without restarting
4. **Integrated Dashboard**: Web UI for monitoring system status (when --ui is enabled)

## 🔄 Agent Modes

The system supports different operation modes to fit various use cases:

### Dataset Generator Agent Modes

```bash
# Run both the dataset generator and agent (default)
python src/agents/dataset_generator_agent.py

# Run only the agent component (analyzing existing metrics)
python src/agents/dataset_generator_agent.py -agent

# Run only the dataset generator (fetching metrics)
python src/agents/dataset_generator_agent.py -fetch
```

### Monitoring Script Modes

```bash
# Run all components (default)
python run_monitoring.py

# Run only the dataset generator
python run_monitoring.py --generator-only

# Run only the dataset agent
python run_monitoring.py --dataset-agent-only

# Run only the anomaly agent
python run_monitoring.py --anomaly-agent-only
```

## 📊 Metrics Collection

### Core Metrics

The system collects the following core metrics:

- **Resource Utilization**: CPU and memory usage percentages
- **Network**: Bytes received/transmitted, dropped packets
- **Container Status**: Ready/total containers, restarts
- **Events**: Recent pod events and their frequencies
- **Pod Phase**: Running, Pending, Failed, etc.

### Custom Metrics

You can extend the metrics collection by:

1. Adding Prometheus queries in `dataset-generator.py`
2. Using the custom metrics integration script:
   ```bash
   python run_agent_with_custom_metrics.py --metric-name "your_custom_metric"
   ```

## 🔍 Anomaly Detection

### Machine Learning Models

The system uses an LSTM-based model for anomaly detection located in `models/anomaly_prediction.py`. Key features:

- Trained on pod behavior patterns
- Detects anomalies based on statistical deviations
- Produces anomaly probability scores

### Threshold Configuration

Adjust the anomaly detection sensitivity:

```bash
# Command line
python run_monitoring.py --alert-threshold 0.8

# Environment variable
export ANOMALY_THRESHOLD=0.8
```

## 🛠️ Remediation Actions

The remediation agent can perform the following actions:

### Pod Management
- **Restart Pod**: Delete and recreate problematic pods
- **Scale Deployment**: Adjust replica count for deployments
- **Change Resource Limits**: Update CPU/memory limits

### Node Management
- **Cordon/Uncordon**: Mark nodes as unschedulable during maintenance
- **Drain Node**: Safely evict pods from a node

### All actions require explicit user approval before execution (unless `--auto-approve` is used, which is not recommended for production).

## 🤖 Integration with LLMs

For enhanced analysis, the system can integrate with OpenAI or other LLM providers:

### Setup

1. Provide an API key:
   ```bash
   export OPENAI_API_KEY=your-api-key
   ```

2. Enable LLM features:
   ```bash
   python run_monitoring.py --enable-llm
   ```

### LLM Features

When enabled, the LLM integration provides:
- Detailed root cause analysis
- Natural language explanations of anomalies
- Context-aware remediation recommendations
- Pattern recognition across multiple incidents

## 📝 Output and Logs

### Primary Outputs

- **pod_metrics.csv**: Raw metrics data from Kubernetes pods
- **pod_insights.json**: Structured anomaly insights and recommendations
- **remediation_history.json**: Record of all remediation actions

### Log Files

- **dataset_generator_agent.log**: Logs from the dataset agent
- **k8s_monitoring.log**: General monitoring system logs
- **k8s_remediation.log**: Remediation actions and outcomes

### Log Configuration

Customize logging by editing the `logging.basicConfig` section in each agent file.

## ❓ Troubleshooting

### Common Issues

#### "Connection to Kubernetes failed"
- Verify your Kubernetes config with `kubectl config view`
- Ensure the cluster is running with `kubectl cluster-info`
- Check if you're in the correct context with `kubectl config current-context`

#### "No metrics found in CSV file"
- Verify the dataset generator is running and has permissions to collect metrics
- Check if Prometheus is correctly set up and accessible
- Ensure the file path is correct and the directory is writable

#### "Model prediction errors"
- Check if model files exist at expected locations
- Ensure the input metrics format matches what the model expects
- Try updating model files with the latest versions

#### "Remediation agent fails to apply changes"
- Verify the user has appropriate RBAC permissions
- Check if the affected resources exist in the specified namespace
- Look for detailed error messages in the `k8s_remediation.log`

## 🧪 Development Guide

### Project Structure

```
K8S/
├── config/               # Configuration files
├── data/                 # Data storage directory
├── logs/                 # Log files
├── models/               # Machine learning models
│   ├── anomaly_prediction.py
│   └── model_artifacts/
├── src/                  # Source code
│   ├── agents/           # Agent implementations
│   │   ├── anomaly_detection_agent.py
│   │   └── dataset_generator_agent.py
│   └── utils/            # Utility functions
├── tests/                # Test cases
├── dataset-generator.py  # Main data collection script
├── run_monitoring.py     # Orchestration script
├── run_remediation.py    # Remediation script
└── requirements.txt      # Dependencies
```

### Adding Custom Agents

1. Create a new file in `src/agents/`
2. Implement the required interface (similar to existing agents)
3. Add integration to `run_monitoring.py`

### Testing

Run tests with:
```bash
python -m unittest discover tests
```

## 📄 License

MIT 