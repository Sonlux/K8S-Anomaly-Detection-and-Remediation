# Backend

This directory contains the Python backend services for the Kubernetes monitoring, RAG, and dashboard system.

## Structure

- `src/agents/` - Multi-agent system components
- `src/api/` - FastAPI endpoints and API servers
- `src/services/` - Business logic and service layer
- `src/utils/` - Utility functions and helpers
- `tests/` - Test suite
- `models/` - ML models and artifacts
- `data/` - Data storage and knowledge base

## Dependencies

- `requirements.txt` - Main Python dependencies
- `requirements-dashboard.txt` - Dashboard-specific dependencies
- `nvidia_api_requirements.txt` - NVIDIA API dependencies
- `pyproject.toml` - Modern Python project configuration

## Running the Backend

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run API server
cd src/api
python api_server.py
```
