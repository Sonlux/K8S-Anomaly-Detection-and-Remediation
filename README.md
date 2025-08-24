# Kubernetes Monitoring, RAG, and Dashboard System

## 🚀 Overview

A full-stack, production-grade platform for:

- **Monitoring** Kubernetes clusters (with Minikube support)
- **Anomaly detection** and actionable remediation
- **Natural language Q&A** about your cluster using Retrieval Augmented Generation (RAG) and LLMs
- **Modern dashboard UI** (React, Vite, Tailwind, shadcn-ui)

---

## 🧩 Features

### Backend

- Multi-agent system for metrics collection, anomaly detection, and remediation
- RAG system with Minikube integration for real-time cluster Q&A
- FastAPI backend with REST API for chat and dashboard
- Modular Python codebase with LLM support (Llama, NVIDIA, etc.)
- Real-time and historical anomaly detection
- Automated/manual remediation workflows
- Prometheus and Kubernetes API integration
- Logging and audit trails

### Frontend

- Modern React dashboard (Vite, TypeScript, Tailwind CSS, shadcn-ui)
- Real-time chat interface (draggable/resizable)
- Data visualizations: charts, tables, cluster health, etc.
- Responsive, accessible UI
- (Optional) User authentication and role-based access
- Customizable themes and layouts
- Notification and alert system

---

## ⚙️ Configuration

The system uses a centralized configuration management system for easy setup and maintenance.

### Quick Setup

1. **Create configuration file:**

   ```bash
   python backend/scripts/setup_config.py
   ```

2. **Or copy the example:**

   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

3. **Test configuration:**
   ```bash
   python backend/src/config/test_config.py
   ```

### Required Settings

At minimum, you need one LLM API key:

```bash
# .env file
NVIDIA_API_KEY=your_nvidia_api_key_here
# OR
LLAMA_API_KEY=your_llama_api_key_here
# OR
OPENAI_API_KEY=your_openai_api_key_here
```

For detailed configuration options, see [Configuration Guide](backend/docs/configuration.md).

---

## 🏗️ Architecture

```
[Collection Layer] → [Processing Layer] → [Analysis Layer] → [LLM Integration]
```

- **Collection:** Metrics from Kubernetes API/Prometheus
- **Processing:** Dataset generator, anomaly prediction
- **Analysis:** Anomaly detection agent, multi-agent orchestration
- **LLM:** RAG with real-time cluster data, LLM-powered insights

---

## 📁 Directory Structure

```
├── backend/             # Python backend services
│   ├── src/
│   │   ├── agents/      # Multi-agent system components
│   │   ├── api/         # FastAPI endpoints
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utility functions
│   ├── tests/           # Backend tests
│   ├── models/          # ML models and artifacts
│   ├── data/            # Data storage (metrics, chroma_db)
│   └── requirements.txt # Python dependencies
├── frontend/            # React frontend application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Application pages
│   │   ├── hooks/       # Custom hooks
│   │   └── lib/         # Utilities
│   ├── public/          # Static assets
│   └── package.json     # Node dependencies
├── infra/               # Infrastructure and deployment
│   ├── k8s/             # Kubernetes manifests
│   ├── monitoring/      # Prometheus configs
│   └── scripts/         # Deployment scripts
└── shared/              # Shared configurations
    ├── configs/         # Environment and config files
    └── docs/            # Documentation
```

---

## ⚡ Quickstart

### Prerequisites

- Python 3.8+
- Node.js (use nvm if possible)
- npm
- Minikube (for local K8s)
- kubectl
- Prometheus (optional)
- LLM API keys (NVIDIA, Llama, etc.)

### Backend Setup

```sh
cd backend
pip install -r requirements.txt

# Create .env file with your API keys:
# LLAMA_API_KEY=your_llama_api_key
# LLAMA_API_URL=your_llama_api_url
# NVIDIA_API_KEY=your_nvidia_api_key

# Start the FastAPI server
uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```sh
cd frontend
npm install
npm run dev
# Visit http://localhost:5173
```

---

## 🛠️ Key Components

### Backend

- **Chat API:** `backend/src/api/api_server.py` (FastAPI endpoints)
- **Agents:** `backend/src/agents/` (multi-agent system)
- **Dataset Generator:** `dataset-generator.py`
- **Anomaly Detection:** `backend/models/anomaly_prediction.py`
- **Remediation Logic:** `backend/src/agents/remediation_agent.py`

### Frontend

- **Chatbot:** `frontend/src/components/Chat/ChatInterface.tsx`
- **Dashboard:** `frontend/src/components/Dashboard/`
- **Charts:** `frontend/src/components/Dashboard/Charts/`
- **UI Library:** shadcn-ui, Tailwind CSS

---

## 🔄 Data & Query Flow

1. **Collection:** Metrics from cluster via API/Prometheus
2. **Storage:** Raw metrics in CSV (`pod_metrics.csv`)
3. **Processing:** Dataset generator agent processes data
4. **Analysis:** Anomaly prediction, scoring, insights (`pod_insights.json`)
5. **LLM Integration:** Real-time and knowledge-based Q&A, actionable summaries
6. **Presentation:** Results in dashboard/chat

---

## 💬 Example Usage

### Example Commands

```sh
# Backend services
cd backend
uvicorn src.api.api_server:app --reload --host 0.0.0.0 --port 8000
python src/agents/k8s_multi_agent_system.py
python src/agents/anomaly_detection_agent.py

# Frontend development
cd frontend
npm run dev

# Infrastructure setup
./infra/scripts/setup_minikube.ps1  # Windows
./infra/scripts/setup_minikube.sh   # Linux/macOS
```

### Example Queries

- **General:**
  - "What is a Pod in Kubernetes?"
  - "How do I troubleshoot a CrashLoopBackOff error?"
  - "Explain Kubernetes RBAC"
- **Real-time:**
  - "Show me the pods in my cluster"
  - "What services are running?"
  - "Display node information"
  - "Get the status of my deployments"
  - "Show me the logs for pod my-pod-name"

---

## 🧑‍💻 Contributing

1. Fork the repo and create a feature branch.
2. Make your changes and add tests if needed.
3. Open a pull request with a clear description.
4. All merges require peer review and must pass CI.

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Kubernetes, Minikube, Prometheus
- Llama, NVIDIA, and other LLM providers
- React, Vite, Tailwind CSS, shadcn-ui
- All contributors and open-source libraries used in this project

---

For more details, see the individual module READMEs and documentation files in the repo.
