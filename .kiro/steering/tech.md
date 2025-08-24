# Technology Stack

## Frontend

- **Framework**: Next.js 15.3+ with React 18.3+
- **Language**: TypeScript with strict mode enabled
- **Styling**: Tailwind CSS 4.1+ with custom design system
- **UI Components**: Custom components with Heroicons, shadcn-ui patterns
- **State Management**: Zustand for client state
- **Data Visualization**: Recharts, D3.js, Three.js for 3D visualizations
- **HTTP Client**: Axios for API communication

## Backend

- **Language**: Python 3.8+
- **Web Framework**: FastAPI for REST APIs, Flask for legacy endpoints
- **ML/AI Stack**:
  - TensorFlow 2.12 with tf-keras
  - scikit-learn for traditional ML
  - sentence-transformers for embeddings
- **LLM Integration**:
  - LangChain for orchestration
  - ChromaDB for vector storage
  - NVIDIA API, Llama API support
- **Kubernetes**: Official kubernetes Python client
- **Data Processing**: pandas, numpy for data manipulation

## Infrastructure

- **Container Orchestration**: Kubernetes, Minikube for local development
- **Monitoring**: Prometheus integration
- **Database**: ChromaDB for vector storage, CSV files for metrics storage

## Development Tools

- **Package Management**: npm (frontend), pip with requirements.txt (backend)
- **Linting**: ESLint for TypeScript, pylint for Python
- **Testing**: pytest for Python backend

## Common Commands

### Frontend Development

```bash
# Install dependencies
npm install

# Development server
npm run dev

# Production build
npm run build
npm start

# Linting
npm run lint
```

### Backend Development

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Install dependencies
pip install -r requirements.txt
pip install -r k8s/requirements.txt

# Run FastAPI server
cd backend
uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000

# Run monitoring system
python run_monitoring.py

# Run multi-agent system
python src/agents/k8s_multi_agent_system.py

# Run RAG CLI
python src/agentic_rag_cli.py
```

### Kubernetes/Minikube

```bash
# Start Minikube
minikube start

# Setup monitoring
.\setup_minikube.ps1  # Windows
./setup_minikube.sh   # Linux/macOS
```

## Environment Variables

- `LLAMA_API_KEY`: Llama API authentication
- `LLAMA_API_URL`: Llama API endpoint
- `NVIDIA_API_KEY`: NVIDIA API authentication
- `FASTMCP_LOG_LEVEL`: Logging level for MCP components
