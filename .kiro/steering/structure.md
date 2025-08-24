# Project Structure

## Root Directory Layout

```
├── k8s/                    # Main backend directory
│   ├── src/                # Python source code
│   │   ├── agents/         # Multi-agent system components
│   │   ├── api_server.py   # API server implementations
│   │   ├── dashboard_api.py # Dashboard API endpoints
│   │   └── *.py           # Utility modules
│   ├── kubescape/         # Frontend React application
│   ├── data/              # Data storage (metrics, knowledge base)
│   ├── models/            # ML models and artifacts
│   ├── config/            # Configuration files
│   ├── logs/              # Application logs
│   └── requirements.txt   # Python dependencies
├── src/                   # Next.js source (if applicable)
├── public/                # Static assets
├── node_modules/          # Node.js dependencies
├── .next/                 # Next.js build artifacts
├── .venv/                 # Python virtual environment
└── package.json           # Node.js dependencies and scripts
```

## Key Directories

### `/backend/src/agents/`

Multi-agent system components:

- `k8s_multi_agent_system.py` - Main orchestrator
- `anomaly_detection_agent.py` - Anomaly detection logic
- `dataset_generator_agent.py` - Data processing agent
- `remediation_agent.py` - Automated remediation
- `k8s_metrics_collector.py` - Metrics collection
- `nvidia_llm.py` - LLM integration

### `/backend/src/`

Core backend modules:

- `api/api_server.py` - Main API server
- `api/dashboard_api.py` - Dashboard-specific endpoints
- `services/k8s_visualization_dashboard.py` - Visualization logic
- `services/fetch_metrics.py` - Kubernetes metrics fetching
- `services/load_knowledge_base.py` - RAG knowledge base loader
- `utils/rag_utils.py` - RAG utility functions
- `utils/k8s_client_utils.py` - Kubernetes client utilities

### `/backend/data/`

Data storage:

- `pod_metrics.csv` - Collected metrics data
- `pod_insights.json` - Processed insights
- `chroma_db/` - Vector database storage
- `k8s_knowledge.json` - Knowledge base content

### `/frontend/` (Frontend)

React application structure:

- `src/components/` - React components
- `src/pages/` - Next.js pages
- `public/` - Static assets
- `package.json` - Frontend dependencies

## File Naming Conventions

### Python Files

- **Agents**: `*_agent.py` (e.g., `anomaly_detection_agent.py`)
- **APIs**: `*_api.py` (e.g., `dashboard_api.py`)
- **Utilities**: Descriptive names (e.g., `fetch_metrics.py`)
- **Main scripts**: Descriptive names (e.g., `run_monitoring.py`)

### TypeScript/React Files

- **Components**: PascalCase (e.g., `ChatInterface.tsx`)
- **Pages**: lowercase with hyphens (e.g., `dashboard.tsx`)
- **Utilities**: camelCase (e.g., `apiClient.ts`)

### Configuration Files

- **PowerShell scripts**: `*.ps1` for Windows automation
- **Shell scripts**: `*.sh` for Linux/macOS automation
- **Environment**: `.env` files for secrets
- **Requirements**: `requirements.txt` for Python dependencies

## Data Flow Architecture

```
[Kubernetes API] → [Metrics Collector] → [Dataset Generator]
                                              ↓
[ChromaDB] ← [Knowledge Base] ← [Anomaly Detection] → [Insights JSON]
     ↓                                                      ↓
[RAG System] → [LLM APIs] → [Chat Interface] ← [Dashboard API]
```

## Import Patterns

### Python Modules

- Relative imports within agents: `from .utils import helper_function`
- Cross-module imports: `from src.agents.anomaly_detection_agent import AnomalyAgent`
- External libraries: Standard imports at top of file

### TypeScript/React

- Component imports: `import { Component } from '@/components/Component'`
- Utility imports: `import { helper } from '@/utils/helper'`
- External libraries: Standard npm imports

## Configuration Management

### Environment Variables

- Store in `.env` files (not committed)
- Reference in code via `python-dotenv` or Next.js env handling
- Document required variables in README files

### Settings Files

- Python: Use `config/` directory for structured configuration
- Frontend: Use Next.js configuration files (`next.config.js`)
- Kubernetes: YAML manifests in appropriate subdirectories
