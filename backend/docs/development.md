# Backend Development Guide

This guide covers backend development for the Kubernetes Monitoring, RAG, and Dashboard System.

## Overview

The backend is built with Python 3.8+ and FastAPI, providing:

- **Multi-agent monitoring system** for Kubernetes clusters
- **RAG (Retrieval Augmented Generation)** system with LLM integration
- **REST API** for frontend communication
- **Real-time metrics collection** and anomaly detection
- **Automated remediation** capabilities

## Technology Stack

### Core Technologies

- **Python 3.8+** - Primary language
- **FastAPI** - Web framework for REST APIs
- **Pydantic** - Data validation and settings management
- **ChromaDB** - Vector database for RAG system
- **LangChain** - LLM orchestration framework

### ML/AI Stack

- **TensorFlow 2.12** with tf-keras for machine learning
- **scikit-learn** for traditional ML algorithms
- **sentence-transformers** for text embeddings
- **Multiple LLM providers**: NVIDIA, Llama, OpenAI

### Kubernetes Integration

- **kubernetes** - Official Python client
- **prometheus-client** - Metrics collection
- **pandas/numpy** - Data processing

## Project Structure

```
backend/
├── src/
│   ├── agents/              # Multi-agent system
│   │   ├── k8s_multi_agent_system.py    # Main orchestrator
│   │   ├── anomaly_detection_agent.py   # Anomaly detection
│   │   ├── dataset_generator_agent.py   # Data processing
│   │   ├── remediation_agent.py         # Issue remediation
│   │   └── k8s_metrics_collector.py     # Metrics collection
│   ├── api/                 # REST API endpoints
│   │   ├── api_server.py               # Main API server
│   │   ├── dashboard_api.py            # Dashboard endpoints
│   │   └── mcp_server.py               # MCP integration
│   ├── config/              # Configuration management
│   │   ├── settings.py                 # Configuration classes
│   │   ├── loader.py                   # Configuration loader
│   │   └── test_config.py              # Configuration testing
│   ├── services/            # Business logic
│   │   ├── k8s_visualization_dashboard.py
│   │   ├── fetch_metrics.py
│   │   └── load_knowledge_base.py
│   └── utils/               # Utility functions
│       ├── rag_utils.py                # RAG utilities
│       └── k8s_client_utils.py         # Kubernetes utilities
├── tests/                   # Test suite
├── docs/                    # Documentation
├── data/                    # Data storage
├── models/                  # ML models
├── scripts/                 # Utility scripts
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project configuration
└── Dockerfile              # Container configuration
```

## Development Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment tool (venv, conda, etc.)
- Access to a Kubernetes cluster or Minikube
- LLM API key (NVIDIA, Llama, or OpenAI)

### Environment Setup

1. **Create virtual environment:**

```bash
cd backend
python -m venv .venv

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate
```

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Configure environment:**

```bash
# Copy environment template
cp ../.env.example ../.env

# Edit .env with your settings
# At minimum, set one LLM API key:
# NVIDIA_API_KEY=your_nvidia_api_key_here
```

4. **Test configuration:**

```bash
python src/config/test_config.py
```

### Development Server

**Start the main API server:**

```bash
uvicorn src.api.api_server:app --reload --host 0.0.0.0 --port 8000
```

**Start additional services:**

```bash
# Multi-agent monitoring system
python src/agents/k8s_multi_agent_system.py

# Anomaly detection agent
python src/agents/anomaly_detection_agent.py

# Dashboard API (if running separately)
python src/api/dashboard_api.py
```

## API Development

### FastAPI Structure

The main API server (`src/api/api_server.py`) provides:

- **Health endpoints**: `/health`, `/ready`
- **Chat endpoints**: `/api/chat` for LLM interactions
- **Metrics endpoints**: `/api/metrics/*` for cluster data
- **Cluster endpoints**: `/api/cluster/*` for Kubernetes info

### Adding New Endpoints

1. **Define endpoint in appropriate API file:**

```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    namespace: str = "default"

@router.post("/api/custom/endpoint")
async def custom_endpoint(request: QueryRequest):
    try:
        # Your logic here
        result = process_query(request.query, request.namespace)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

2. **Register router in main app:**

```python
# In api_server.py
from .custom_endpoints import router as custom_router
app.include_router(custom_router)
```

### Error Handling

Use consistent error handling patterns:

```python
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def endpoint_function():
    try:
        # Your logic
        pass
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
```

## Agent Development

### Multi-Agent Architecture

The system uses a multi-agent architecture where each agent has specific responsibilities:

- **Orchestrator**: Coordinates all agents
- **Metrics Collector**: Gathers cluster metrics
- **Anomaly Detector**: Identifies unusual patterns
- **Dataset Generator**: Processes and analyzes data
- **Remediation Agent**: Suggests and applies fixes

### Creating New Agents

1. **Create agent class:**

```python
from abc import ABC, abstractmethod
import logging

class BaseAgent(ABC):
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"agent.{name}")

    @abstractmethod
    async def execute(self, context: dict) -> dict:
        """Execute agent logic"""
        pass

    def log_info(self, message: str):
        self.logger.info(f"[{self.name}] {message}")

class CustomAgent(BaseAgent):
    def __init__(self):
        super().__init__("custom")

    async def execute(self, context: dict) -> dict:
        self.log_info("Starting custom agent execution")
        # Your agent logic here
        return {"status": "completed", "data": {}}
```

2. **Register agent in orchestrator:**

```python
# In k8s_multi_agent_system.py
from .custom_agent import CustomAgent

class MultiAgentOrchestrator:
    def __init__(self):
        self.agents = {
            "custom": CustomAgent(),
            # ... other agents
        }
```

## Configuration Management

### Using Configuration

```python
from backend.src.config.loader import get_config, setup_logging

# Setup logging first
setup_logging()

# Get configuration
config = get_config()

# Use configuration values
api_key = config.api.nvidia_api_key
namespace = config.kubernetes.namespace
log_level = config.logging.level
```

### Adding New Configuration Options

1. **Add to settings class:**

```python
# In src/config/settings.py
@dataclass
class CustomConfig:
    custom_setting: str = "default_value"
    custom_timeout: int = 30

@dataclass
class AppConfig:
    # ... existing configs
    custom: CustomConfig = field(default_factory=CustomConfig)
```

2. **Add environment variable mapping:**

```python
# In src/config/loader.py
def load_config_from_env() -> AppConfig:
    return AppConfig(
        # ... existing mappings
        custom=CustomConfig(
            custom_setting=os.getenv("CUSTOM_SETTING", "default_value"),
            custom_timeout=int(os.getenv("CUSTOM_TIMEOUT", "30")),
        )
    )
```

## Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_api.py

# Run with coverage
pytest --cov=src tests/

# Run with verbose output
pytest -v tests/
```

### Writing Tests

**API Tests:**

```python
import pytest
from fastapi.testclient import TestClient
from src.api.api_server import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_chat_endpoint():
    response = client.post(
        "/api/chat",
        json={"message": "test query"}
    )
    assert response.status_code == 200
    assert "response" in response.json()
```

**Agent Tests:**

```python
import pytest
from unittest.mock import Mock, patch
from src.agents.custom_agent import CustomAgent

@pytest.fixture
def custom_agent():
    return CustomAgent()

@pytest.mark.asyncio
async def test_agent_execution(custom_agent):
    context = {"test": "data"}
    result = await custom_agent.execute(context)

    assert result["status"] == "completed"
    assert "data" in result
```

**Configuration Tests:**

```python
import os
import pytest
from src.config.loader import get_config

def test_config_loading():
    # Set test environment variables
    os.environ["NVIDIA_API_KEY"] = "test_key"

    config = get_config()
    assert config.api.nvidia_api_key == "test_key"
```

### Test Configuration

Use test-specific configuration:

```python
# tests/conftest.py
import pytest
import os

@pytest.fixture(autouse=True)
def setup_test_env():
    # Set test environment variables
    os.environ["K8S_TEST_MODE"] = "true"
    os.environ["LOG_LEVEL"] = "DEBUG"
    yield
    # Cleanup after tests
```

## Debugging

### Logging

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
export K8S_DEBUG_MODE=true
```

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.debug(f"Processing data: {len(data)} items")
    try:
        result = complex_operation(data)
        logger.info(f"Successfully processed {len(result)} results")
        return result
    except Exception as e:
        logger.error(f"Failed to process data: {e}", exc_info=True)
        raise
```

### Development Tools

**Interactive debugging:**

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or use modern debugger
import ipdb; ipdb.set_trace()
```

**API debugging:**

```bash
# Test endpoints with curl
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'

# Use httpie for better formatting
http POST localhost:8000/api/chat message="test"
```

## Performance Optimization

### Async Programming

Use async/await for I/O operations:

```python
import asyncio
import aiohttp

async def fetch_metrics():
    async with aiohttp.ClientSession() as session:
        async with session.get("http://prometheus:9090/api/v1/query") as response:
            return await response.json()

async def process_multiple_requests():
    tasks = [fetch_metrics() for _ in range(10)]
    results = await asyncio.gather(*tasks)
    return results
```

### Caching

Implement caching for expensive operations:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def expensive_computation(param):
    # Expensive operation
    time.sleep(1)
    return f"result for {param}"

# Or use async cache
import asyncio
from functools import wraps

def async_cache(maxsize=128):
    cache = {}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = str(args) + str(kwargs)
            if key not in cache:
                cache[key] = await func(*args, **kwargs)
            return cache[key]
        return wrapper
    return decorator
```

### Database Optimization

Optimize ChromaDB queries:

```python
# Batch operations
collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

# Use appropriate similarity search
results = collection.query(
    query_texts=["query"],
    n_results=10,
    where={"namespace": "default"}
)
```

## Security Best Practices

### Input Validation

Use Pydantic for request validation:

```python
from pydantic import BaseModel, validator
from typing import Optional

class QueryRequest(BaseModel):
    message: str
    namespace: Optional[str] = "default"

    @validator('message')
    def message_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v

    @validator('namespace')
    def namespace_must_be_valid(cls, v):
        if v and not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Invalid namespace format')
        return v
```

### API Security

Implement rate limiting and CORS:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat_endpoint(request: Request, query: QueryRequest):
    # Endpoint logic
    pass
```

### Secrets Management

Never hardcode secrets:

```python
from backend.src.config.loader import get_config

config = get_config()

# Good: Use configuration
api_key = config.api.nvidia_api_key

# Bad: Hardcoded secret
# api_key = "nvapi-1234567890"
```

## Deployment

### Docker Development

Build and run with Docker:

```bash
# Build image
docker build -t k8s-monitoring-backend .

# Run container
docker run -p 8000:8000 \
  -e NVIDIA_API_KEY=your_key \
  -v $(pwd)/data:/app/data \
  k8s-monitoring-backend
```

### Production Considerations

- **Environment Variables**: Use proper secrets management
- **Logging**: Configure structured logging with log aggregation
- **Monitoring**: Add health checks and metrics endpoints
- **Security**: Use HTTPS, restrict CORS origins, implement authentication
- **Performance**: Use production ASGI server (gunicorn + uvicorn)

```bash
# Production server
gunicorn src.api.api_server:app \
  -w 4 \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Common Patterns

### Error Handling Pattern

```python
from typing import Optional
import logging

logger = logging.getLogger(__name__)

async def safe_operation(param: str) -> Optional[dict]:
    try:
        result = await risky_operation(param)
        logger.info(f"Operation successful for {param}")
        return result
    except ValueError as e:
        logger.warning(f"Invalid parameter {param}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error for {param}: {e}", exc_info=True)
        raise
```

### Configuration Pattern

```python
from backend.src.config.loader import get_config

class ServiceClass:
    def __init__(self):
        self.config = get_config()
        self.api_key = self.config.api.nvidia_api_key
        self.timeout = self.config.api.timeout

    async def make_request(self):
        # Use self.config values
        pass
```

### Logging Pattern

```python
import logging
from functools import wraps

def log_execution(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        logger.info(f"Starting {func.__name__}")
        try:
            result = await func(*args, **kwargs)
            logger.info(f"Completed {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"Failed {func.__name__}: {e}")
            raise
    return wrapper

@log_execution
async def important_function():
    # Function logic
    pass
```

## Troubleshooting

### Common Issues

**Import Errors:**

```bash
# Ensure you're in the backend directory and virtual environment is activated
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
python -c "import src.api.api_server"
```

**Configuration Issues:**

```bash
# Test configuration
python src/config/test_config.py

# Check environment variables
python -c "from src.config.loader import get_config; print(get_config())"
```

**Kubernetes Connection:**

```bash
# Test Kubernetes connection
kubectl cluster-info

# Use test mode for development
export K8S_TEST_MODE=true
```

**Port Conflicts:**

```bash
# Check what's using port 8000
netstat -tulpn | grep 8000  # Linux
netstat -ano | findstr 8000  # Windows

# Use different port
uvicorn src.api.api_server:app --port 8001
```

### Debug Mode

Enable comprehensive debugging:

```bash
export LOG_LEVEL=DEBUG
export K8S_DEBUG_MODE=true
export FASTMCP_LOG_LEVEL=DEBUG

python src/api/api_server.py
```

## Contributing

### Code Style

Follow Python best practices:

- **PEP 8**: Use black for formatting
- **Type Hints**: Add type annotations
- **Docstrings**: Document functions and classes
- **Error Handling**: Use appropriate exception types

```bash
# Format code
black src/

# Check types
mypy src/

# Lint code
pylint src/
```

### Pull Request Process

1. Create feature branch from main
2. Write tests for new functionality
3. Ensure all tests pass
4. Update documentation
5. Submit pull request with clear description

### Testing Requirements

- Unit tests for new functions
- Integration tests for API endpoints
- Configuration tests for new settings
- Minimum 80% code coverage

This guide should help you get started with backend development. For specific questions, refer to the code documentation or create an issue in the repository.
