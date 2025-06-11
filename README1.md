
The Kubernetes Monitoring and Remediation System is a comprehensive solution for monitoring Kubernetes clusters, detecting anomalies, and providing remediation recommendations.

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
│   └── utils/               # Shared utilities
├── dataset-generator.py     # Data collection script
├── run_monitoring.py        # Orchestration script
└── requirements.txt         # Dependencies
```

## Commands

### Run the Multi-Agent System:

```bash
cd src/agents
python k8s_multi_agent_system.py
```

### Run All Components:

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
```

        