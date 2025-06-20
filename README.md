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
k8s/
├── kubescape/           # Frontend (React, Vite, etc.)
│   ├── src/             # React source code
│   ├── public/          # Static assets
│   └── ...              # Frontend configs
├── backend/             # FastAPI backend, agents, and utilities
│   ├── app.py           # FastAPI entrypoint
│   ├── agentic_rag_cli.py # RAG CLI
│   ├── agents/          # Agent modules (anomaly, remediation, etc.)
│   └── ...              # Other backend utilities
├── data/                # Data storage (metrics, insights, chroma_db, etc.)
├── models/              # ML models and artifacts
├── src/                 # Python source code (agents, utils, etc.)
└── requirements.txt     # Python dependencies
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
pip install -r requirements.txt
cd k8s/kubescape/backend
# Create .env with your API keys:
# LLAMA_API_KEY=your_llama_api_key
# LLAMA_API_URL=your_llama_api_url
# NVIDIA_API_KEY=your_nvidia_api_key
uvicorn app:app --host 0.0.0.0 --port 8000
```

### Frontend Setup

```sh
cd k8s/kubescape
npm install
npm run dev
# Visit http://localhost:5173
```

---

## 🛠️ Key Components

### Backend

- **Chat API:** `backend/app.py` (FastAPI endpoints)
- **Agents:** `src/agents/` (multi-agent system)
- **RAG CLI:** `src/agentic_rag_cli.py`
- **Dataset Generator:** `dataset-generator.py`
- **Anomaly Detection:** `models/anomaly_prediction.py`
- **Remediation Logic:** `src/agents/remediation_agent.py`

### Frontend

- **Chatbot:** `src/components/Chat/ChatInterface.tsx`
- **Dashboard:** `src/components/Dashboard/`
- **Charts:** `src/components/Dashboard/Charts/`
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

- Run all monitoring: `python run_monitoring.py`
- Run dataset generator: `python dataset-generator.py`
- Run multi-agent system: `python src/agents/k8s_multi_agent_system.py`
- Run the RAG CLI: `python src/agentic_rag_cli.py`

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

MIT License (or your chosen license)

---

## 🙏 Acknowledgements

- Kubernetes, Minikube, Prometheus
- Llama, NVIDIA, and other LLM providers
- React, Vite, Tailwind CSS, shadcn-ui
- All contributors and open-source libraries used in this project

---

For more details, see the individual module READMEs and documentation files in the repo.
