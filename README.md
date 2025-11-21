# Kubernetes Monitoring, RAG, and Dashboard System

## 🚀 Overview

A comprehensive, production-ready platform that combines intelligent Kubernetes cluster monitoring with AI-powered insights and natural language querying capabilities.

### Key Features

- **🔍 Intelligent Monitoring**: Multi-agent system for automated metrics collection, anomaly detection, and remediation
- **🤖 AI-Powered Q&A**: Natural language interface for querying cluster status using RAG and multiple LLM providers
- **📊 Modern Dashboard**: React-based UI with real-time visualizations, interactive charts, and responsive design
- **🛡️ Production Ready**: Comprehensive security, error handling, logging, and monitoring capabilities
- **🐳 Container Native**: Full Docker support with optimized multi-stage builds and Kubernetes deployment

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │  Kubernetes     │
│   (React/TS)    │◄──►│   (FastAPI)     │◄──►│   Cluster       │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • Multi-Agent   │    │ • Metrics API   │
│ • Chat UI       │    │ • RAG System    │    │ • Prometheus    │
│ • Visualizations│    │ • LLM APIs      │    │ • Pod Logs      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Docker** (optional, for containerized deployment)
- **Kubernetes cluster** or **Minikube** for local development
- **LLM API key** (NVIDIA, Llama, or OpenAI)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd kubernetes-monitoring-system

# Create and activate Python virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings (see Configuration section below)
# At minimum, add one LLM API key:
# NVIDIA_API_KEY=your_nvidia_api_key_here
```

### 3. Install Dependencies

```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies
cd ../frontend
npm install
```

### 4. Start Services

```bash
# Terminal 1: Start backend API server
cd backend
uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Start frontend development server
cd frontend
npm run dev

# Terminal 3: Start monitoring system (optional)
cd backend
python src/agents/k8s_multi_agent_system.py
```

### 5. Access the Application

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## ⚙️ Configuration

The system uses a centralized configuration management system. All settings can be configured via environment variables or the `.env` file.

### Required Configuration

**LLM API Key** (choose one):

```bash
# NVIDIA API (recommended)
NVIDIA_API_KEY=your_nvidia_api_key_here

# OR Llama API
LLAMA_API_KEY=your_llama_api_key_here
LLAMA_API_URL=https://api.llama-api.com

# OR OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
```

### Quick Configuration Setup

```bash
# Use the setup script for guided configuration
python backend/scripts/setup_config.py

# Test your configuration
python backend/src/config/test_config.py
```

### Common Configuration Options

```bash
# Server Settings
API_SERVER_HOST=0.0.0.0
API_SERVER_PORT=8000

# Kubernetes Settings
K8S_NAMESPACE=default
K8S_TEST_MODE=false  # Set to true for development with mock data

# Logging
LOG_LEVEL=INFO
LOG_FILE=backend/logs/app.log

# Security
CORS_ORIGINS=*  # Restrict in production
RATE_LIMIT_PER_MINUTE=60
```

For complete configuration options, see the [Configuration Guide](backend/docs/configuration.md).

## 📁 Project Structure

```
├── README.md                    # This file - main project documentation
├── .env.example                 # Environment configuration template
├── docker-compose.yml           # Container orchestration for local development
├── backend/                     # Python backend services
│   ├── src/
│   │   ├── agents/              # Multi-agent monitoring system
│   │   ├── api/                 # FastAPI REST endpoints
│   │   ├── config/              # Configuration management
│   │   ├── services/            # Business logic and utilities
│   │   └── utils/               # Shared utility functions
│   ├── tests/                   # Backend test suite
│   ├── docs/                    # Backend-specific documentation
│   ├── data/                    # Data storage (metrics, vector DB)
│   ├── models/                  # ML models and artifacts
│   ├── requirements.txt         # Python dependencies
│   └── Dockerfile               # Backend container configuration
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── components/          # Reusable React components
│   │   ├── pages/               # Next.js pages and routing
│   │   ├── hooks/               # Custom React hooks
│   │   ├── lib/                 # Frontend utilities and helpers
│   │   └── styles/              # CSS and styling
│   ├── public/                  # Static assets and images
│   ├── docs/                    # Frontend-specific documentation
│   ├── package.json             # Node.js dependencies and scripts
│   └── Dockerfile               # Frontend container configuration
├── infra/                       # Infrastructure and deployment
│   ├── k8s/                     # Kubernetes manifests and configs
│   ├── monitoring/              # Prometheus and Grafana configs
│   └── scripts/                 # Deployment and setup scripts
└── shared/                      # Shared resources and documentation
    ├── configs/                 # Shared configuration files
    └── docs/                    # Additional project documentation
```

---

## 🔧 Development Setup

### Local Development with Docker

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Development Setup

**Backend Development:**

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run development server with auto-reload
uvicorn src.api.api_server:app --reload --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Run monitoring system
python src/agents/k8s_multi_agent_system.py
```

**Frontend Development:**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

---

## 🛠️ Key Components

### Multi-Agent Monitoring System

- **Metrics Collector**: `backend/src/agents/k8s_metrics_collector.py` - Gathers cluster metrics
- **Anomaly Detection**: `backend/src/agents/anomaly_detection_agent.py` - AI-powered anomaly detection
- **Remediation Agent**: `backend/src/agents/remediation_agent.py` - Automated issue resolution
- **Dataset Generator**: `backend/src/agents/dataset_generator_agent.py` - Data processing and analysis

### API Services

- **Main API Server**: `backend/src/api/api_server.py` - FastAPI REST endpoints
- **Dashboard API**: `backend/src/api/dashboard_api.py` - Dashboard-specific endpoints
- **MCP Server**: `backend/src/api/mcp_server.py` - Model Context Protocol integration

### Frontend Components

- **Dashboard**: `frontend/src/components/Dashboard/` - Main monitoring interface
- **Chat Interface**: `frontend/src/components/Chat/` - AI-powered Q&A system
- **Visualizations**: `frontend/src/components/Charts/` - Data visualization components
- **UI Components**: Built with React, TypeScript, and Tailwind CSS

---

## 🔄 Data Flow Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Kubernetes     │    │   Collection    │    │   Processing    │
│   Cluster       │───►│     Layer       │───►│     Layer       │
│                 │    │                 │    │                 │
│ • Metrics API   │    │ • Metrics       │    │ • Dataset       │
│ • Prometheus    │    │   Collector     │    │   Generator     │
│ • Pod Logs      │    │ • Log Scraper   │    │ • Anomaly       │
└─────────────────┘    └─────────────────┘    │   Detection     │
                                              └─────────────────┘
                                                       │
┌─────────────────┐    ┌─────────────────┐           │
│   Presentation  │    │   LLM Layer     │◄──────────┘
│     Layer       │◄───│                 │
│                 │    │ • RAG System    │
│ • Dashboard UI  │    │ • Vector DB     │
│ • Chat Interface│    │ • Multi-LLM     │
│ • Visualizations│    │   Support       │
└─────────────────┘    └─────────────────┘
```

**Flow Steps:**

1. **Collection**: Metrics from Kubernetes API and Prometheus
2. **Storage**: Raw metrics in CSV files and ChromaDB vector database
3. **Processing**: Dataset generator processes and analyzes data
4. **Analysis**: Anomaly detection with ML models and scoring
5. **LLM Integration**: RAG system provides intelligent insights and Q&A
6. **Presentation**: Results displayed in dashboard and chat interface

---

## 💬 Usage Examples

### Natural Language Queries

Ask questions about your Kubernetes cluster in plain English:

**General Kubernetes Knowledge:**

- "What is a Pod in Kubernetes?"
- "How do I troubleshoot a CrashLoopBackOff error?"
- "Explain Kubernetes RBAC and security best practices"
- "What's the difference between a Deployment and a StatefulSet?"

**Real-time Cluster Information:**

- "Show me all pods in the default namespace"
- "What services are currently running?"
- "Display node resource utilization"
- "Get the status of my deployments"
- "Show me recent events in the cluster"
- "Which pods are consuming the most CPU?"

### API Endpoints

**Health and Status:**

```bash
# Check API health
curl http://localhost:8000/health

# Get cluster status
curl http://localhost:8000/api/cluster/status

# Get metrics summary
curl http://localhost:8000/api/metrics/summary
```

**Chat and Q&A:**

```bash
# Ask a question via API
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me pod status"}'
```

### Command Line Operations

**Start Individual Services:**

```bash
# Start API server only
cd backend
uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000

# Start monitoring agents
python src/agents/k8s_multi_agent_system.py

# Start anomaly detection
python src/agents/anomaly_detection_agent.py

# Generate test data
python src/agents/dataset_generator_agent.py
```

**Infrastructure Management:**

```bash
# Setup Minikube (Windows)
.\infra\scripts\setup_minikube.ps1

# Setup Minikube (Linux/macOS)
./infra/scripts/setup_minikube.sh

# Deploy to Kubernetes
kubectl apply -f infra/k8s/
```

## 🚨 Troubleshooting

### Common Issues

**Configuration Problems:**

```bash
# No LLM API keys configured
Error: No valid LLM API key found
Solution: Set NVIDIA_API_KEY, LLAMA_API_KEY, or OPENAI_API_KEY in .env

# Configuration validation failed
python backend/src/config/test_config.py
# Follow the output to fix configuration issues
```

**Connection Issues:**

```bash
# Cannot connect to Kubernetes cluster
Error: Unable to load Kubernetes config
Solution:
- Check kubectl is configured: kubectl cluster-info
- For Minikube: minikube status
- Set K8S_TEST_MODE=true for development with mock data
```

**Port Conflicts:**

```bash
# Port already in use
Error: [Errno 48] Address already in use
Solution: Change ports in .env file or stop conflicting services
```

**Dependency Issues:**

```bash
# Python dependencies
pip install --upgrade -r backend/requirements.txt

# Node.js dependencies
cd frontend && npm install --force
```

### Getting Help

- **Configuration**: See [Configuration Guide](backend/docs/configuration.md)
- **Backend Development**: See [Backend Documentation](backend/docs/)
- **Frontend Development**: See [Frontend Documentation](frontend/docs/)
- **Deployment**: See [Infrastructure Documentation](infra/README.md)

---

## 📚 Documentation

### Core Documentation

- **[Configuration Guide](backend/docs/configuration.md)** - Complete configuration reference
- **[Backend Development](backend/docs/)** - Backend development guide
- **[Frontend Development](frontend/docs/)** - Frontend development guide

### Additional Resources

- **[Minikube Setup](shared/docs/MINIKUBE_SETUP.md)** - Local Kubernetes setup
- **[NVIDIA API Integration](shared/docs/NVIDIA_API_INTEGRATION.md)** - NVIDIA API setup
- **[Llama API Integration](shared/docs/LLAMA_API_INTEGRATION.md)** - Llama API setup
- **[RAG System](shared/docs/RAG_FIX_SUMMARY.md)** - RAG system overview

---

## 🧑‍💻 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository** and create a feature branch
2. **Follow coding standards**:
   - Python: PEP 8, type hints, docstrings
   - TypeScript: ESLint rules, proper typing
   - Tests: Write tests for new features
3. **Test your changes**:

   ```bash
   # Backend tests
   cd backend && pytest tests/

   # Frontend tests
   cd frontend && npm test

   # Configuration tests
   python backend/src/config/test_config.py
   ```

4. **Submit a pull request** with clear description
5. **Code review**: All changes require peer review

### Development Guidelines

- **Security**: Never commit API keys or sensitive data
- **Documentation**: Update docs for new features
- **Backward Compatibility**: Maintain API compatibility
- **Performance**: Consider performance impact of changes

---

## 🔒 Security

### Security Best Practices

- **API Keys**: Store in `.env` files, never commit to version control
- **CORS**: Restrict origins in production (don't use `*`)
- **Rate Limiting**: Configure appropriate limits for your environment
- **Updates**: Keep dependencies updated for security patches

### Reporting Security Issues

Please report security vulnerabilities privately to the maintainers

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- **Kubernetes Ecosystem**: Kubernetes, Minikube, kubectl, Prometheus
- **AI/ML Providers**: NVIDIA, Llama, OpenAI for LLM APIs
- **Frontend Stack**: React, Next.js, TypeScript, Tailwind CSS, Vite
- **Backend Stack**: FastAPI, Python, ChromaDB, LangChain
- **Development Tools**: Docker, pytest, ESLint, and all open-source contributors

---

## 📞 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Check the docs/ directories for detailed guides
- **Configuration Help**: Use `python backend/scripts/setup_config.py` for guided setup
