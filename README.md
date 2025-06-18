# Kubernetes Monitoring, RAG, and Dashboard System

## Overview

This project is a full-stack, production-grade solution for:

- Monitoring Kubernetes clusters (with Minikube support)
- Detecting anomalies and providing remediation recommendations
- Answering Kubernetes questions using Retrieval Augmented Generation (RAG) with LLMs
- Providing a modern, interactive dashboard UI (React, Vite, Tailwind, shadcn-ui)

---

## Features

### Backend

- Multi-agent system for metrics collection, anomaly detection, and remediation
- RAG system with Minikube integration for real-time cluster Q&A
- FastAPI backend with REST API for chat and dashboard
- Modular Python codebase with support for LLMs (Llama, NVIDIA, etc.)
- Real-time and historical anomaly detection
- Automated and manual remediation workflows
- Integration with Prometheus and Kubernetes API
- Logging and audit trails for all actions

### Frontend

- Modern React dashboard (Vite, TypeScript, Tailwind CSS, shadcn-ui)
- Real-time chat interface with draggable/resizable panel
- Data visualizations (charts, tables, cluster health, etc.)
- Responsive and accessible UI
- User authentication and role-based access (optional)
- Customizable themes and layouts
- Notification and alert system

---

## Architecture Diagram

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

---

## Directory Structure

```
k8s/
├── backend/                # FastAPI backend, agents, and utilities
│   ├── app.py              # FastAPI entrypoint
│   ├── agentic_rag_cli.py  # RAG CLI
│   ├── agents/             # Agent modules (anomaly, remediation, etc.)
│   └── ...                 # Other backend utilities
├── data/                   # Data storage (metrics, insights, chroma_db, etc.)
├── models/                 # ML models and artifacts
├── src/                    # Python source code (agents, utils, etc.)
├── kubescape/              # Frontend (React, Vite, etc.)
│   ├── src/                # React source code
│   ├── public/             # Static assets
│   ├── package.json        # Frontend dependencies
│   └── ...                 # Other frontend files
└── requirements.txt        # Python dependencies
```

---

## Backend: Setup & Usage

### Prerequisites

- Python 3.8+
- Minikube (for local K8s)
- kubectl
- Prometheus (optional)
- LLM API keys (for RAG/LLM features)

### Install & Run

```sh
# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend
cd k8s/kubescape/backend
uvicorn app:app --host 0.0.0.0 --port 8000

# (Optional) Run RAG CLI
cd k8s/src
python agentic_rag_cli.py
```

### Environment Variables

Create a `.env` file in `k8s/kubescape/backend/`:

```
LLAMA_API_KEY=your_llama_api_key
LLAMA_API_URL=your_llama_api_url
NVIDIA_API_KEY=your_nvidia_api_key
```

---

## Frontend: Setup & Usage

### Prerequisites

- Node.js (use nvm if possible)
- npm

### Install & Run

```sh
cd k8s/kubescape
npm install
npm run dev
```

- The dashboard will be available at `http://localhost:5173` (or as shown in your terminal).

---

## Key Components

### Backend

- **Chat API**: `backend/app.py` (FastAPI endpoints)
- **Agents**: `src/agents/` (Python multi-agent system)
- **RAG CLI**: `src/agentic_rag_cli.py`
- **Dataset Generator**: `dataset-generator.py`
- **Anomaly Detection**: `models/anomaly_prediction.py`
- **Remediation Logic**: `src/agents/remediation_agent.py`

### Frontend

- **Chatbot**: `src/components/Chat/ChatInterface.tsx` (draggable, resizable chat UI)
- **Dashboard**: `src/components/Dashboard/`
- **Charts**: `src/components/Dashboard/Charts/`
- **UI Library**: shadcn-ui, Tailwind CSS

---

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

### RAG System with Minikube Integration

1. **User Query**: User submits a question through the CLI or dashboard chat
2. **Query Analysis**: System determines if the query requires real-time information
3. **Knowledge Retrieval**:
   - For general knowledge: Retrieves information from the ChromaDB knowledge base
   - For real-time queries: Fetches current information from the Minikube cluster
4. **Context Building**: Combines retrieved knowledge with real-time information
5. **Response Generation**: Uses an LLM to generate a comprehensive response
6. **Presentation**: Displays the formatted response to the user

---

## Example Commands

- Run all monitoring: `python run_monitoring.py`
- Run dataset generator: `python dataset-generator.py`
- Run multi-agent system: `python src/agents/k8s_multi_agent_system.py`
- Run the RAG CLI: `python src/agentic_rag_cli.py`

---

## Example Queries

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

---

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

---

## Frontend Details

### Technologies Used

- Vite
- React 18 (TypeScript)
- Tailwind CSS
- shadcn-ui
- Zustand (state management)
- React Query (server state)
- Recharts, D3.js (visualizations)

### Main UI Components

- **ChatInterface**: Draggable, resizable chatbot panel
- **Dashboard**: Cluster overview, anomaly feed, metrics grid, charts
- **Remediation Center**: Manual and automated remediation actions
- **Settings**: User preferences, notification settings

### Running the Frontend

```sh
cd k8s/kubescape
npm install
npm run dev
```

---

## Backend Details

### Main Python Modules

- `agentic_rag_cli.py`: CLI for RAG system
- `app.py`: FastAPI backend
- `agents/`: Multi-agent orchestration, anomaly detection, remediation
- `models/`: ML models for anomaly prediction
- `data/`: Metrics, insights, and ChromaDB

### Running the Backend

```sh
cd k8s/kubescape/backend
uvicorn app:app --host 0.0.0.0 --port 8000
```

---

## Contributing

1. Fork the repo and create a feature branch.
2. Make your changes and add tests if needed.
3. Open a pull request with a clear description.

---

## License

MIT License (or your chosen license)

---

## Acknowledgements

- Kubernetes, Minikube, Prometheus
- Llama, NVIDIA, and other LLM providers
- React, Vite, Tailwind CSS, shadcn-ui
- All contributors and open-source libraries used in this project

---

For more details, see the individual module READMEs and documentation files in the repo.
