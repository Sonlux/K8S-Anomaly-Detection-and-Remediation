# Configuration Management

The Kubernetes monitoring system uses a centralized configuration management system that provides a clean, secure, and maintainable way to manage all application settings.

## Overview

The configuration system provides:

- **Centralized Configuration**: All settings in one place
- **Environment Variable Support**: Load from `.env` files or system environment
- **Validation**: Automatic validation of configuration values
- **Defaults**: Sensible defaults for all settings
- **Type Safety**: Strongly typed configuration with dataclasses
- **Backward Compatibility**: Easy integration with existing code

## Quick Start

### 1. Create Configuration File

Use the setup script to create your configuration:

```bash
python backend/scripts/setup_config.py
```

Or manually create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your settings
```

### 2. Test Configuration

Verify your configuration is working:

```bash
python backend/src/config/test_config.py
```

### 3. Use in Your Code

```python
from backend.src.config.loader import get_config, setup_logging

# Setup logging
setup_logging()

# Get configuration
config = get_config()

# Use configuration
api_key = config.api.nvidia_api_key
port = config.api.api_server_port
```

## Configuration Sections

### API Configuration

Controls LLM APIs and server settings:

```python
config.api.nvidia_api_key      # NVIDIA API key
config.api.llama_api_key       # Llama API key
config.api.llama_api_url       # Llama API URL
config.api.openai_api_key      # OpenAI API key
config.api.api_server_host     # API server host
config.api.api_server_port     # API server port
config.api.dashboard_api_port  # Dashboard API port
config.api.mcp_server_port     # MCP server port
config.api.prometheus_url      # Prometheus URL
```

### Kubernetes Configuration

Controls Kubernetes client settings:

```python
config.kubernetes.namespace      # Default namespace
config.kubernetes.kubeconfig_path  # Path to kubeconfig
config.kubernetes.in_cluster    # Running in cluster
config.kubernetes.test_mode     # Test mode enabled
```

### Database Configuration

Controls data storage paths:

```python
config.database.chroma_db_path      # ChromaDB path
config.database.metrics_csv_path    # Metrics CSV path
config.database.insights_json_path  # Insights JSON path
config.database.knowledge_base_path # Knowledge base path
```

### Logging Configuration

Controls logging behavior:

```python
config.logging.level          # Log level (DEBUG, INFO, etc.)
config.logging.format         # Log format string
config.logging.log_file       # Log file path (optional)
config.logging.max_file_size  # Max log file size
config.logging.backup_count   # Number of backup files
```

### Security Configuration

Controls security settings:

```python
config.security.cors_origins         # CORS allowed origins
config.security.rate_limit_per_minute # Rate limiting
config.security.max_request_size     # Max request size
```

### Monitoring Configuration

Controls monitoring and metrics:

```python
config.monitoring.metrics_collection_interval  # Collection interval
config.monitoring.anomaly_detection_threshold  # Detection threshold
config.monitoring.enable_health_checks        # Health checks enabled
config.monitoring.performance_metrics         # Performance metrics
```

## Environment Variables

All configuration can be set via environment variables:

### Required Variables

```bash
# At least one LLM API key is required
NVIDIA_API_KEY=your_nvidia_api_key
# OR
LLAMA_API_KEY=your_llama_api_key
# OR
OPENAI_API_KEY=your_openai_api_key
```

### Optional Variables

```bash
# Server Configuration
API_SERVER_HOST=0.0.0.0
API_SERVER_PORT=8000
DASHBOARD_API_PORT=5000
MCP_SERVER_PORT=8000

# Kubernetes Configuration
K8S_NAMESPACE=default
KUBECONFIG=/path/to/kubeconfig
K8S_IN_CLUSTER=false
K8S_TEST_MODE=false

# External Services
PROMETHEUS_URL=http://localhost:9090

# Logging
LOG_LEVEL=INFO
LOG_FILE=backend/logs/app.log

# Security
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=60

# Monitoring
METRICS_COLLECTION_INTERVAL=30
ANOMALY_DETECTION_THRESHOLD=0.8
```

## Usage Examples

### Basic Usage

```python
from backend.src.config.loader import get_config

config = get_config()
print(f"API Server: {config.api.api_server_host}:{config.api.api_server_port}")
```

### Setup Logging

```python
from backend.src.config.loader import setup_logging

# Setup logging with configuration
setup_logging()

import logging
logger = logging.getLogger(__name__)
logger.info("Application started")
```

### Backward Compatibility

For easy integration with existing code:

```python
from backend.src.config.loader import (
    get_nvidia_api_key,
    get_kubernetes_config,
    is_test_mode
)

# Get specific values
api_key = get_nvidia_api_key()
k8s_config = get_kubernetes_config()
test_mode = is_test_mode()
```

### Validation

```python
from backend.src.config.loader import validate_environment

if not validate_environment():
    print("Configuration is invalid!")
    exit(1)
```

### Directory Setup

```python
from backend.src.config.loader import ensure_data_directories

# Create all required directories
ensure_data_directories()
```

## Configuration Files

### .env File

The `.env` file contains your actual configuration values:

```bash
# .env
NVIDIA_API_KEY=nvapi-your-actual-key
API_SERVER_PORT=8080
LOG_LEVEL=DEBUG
```

### .env.example File

The `.env.example` file is a template with all available options:

```bash
# Copy this file to .env and fill in your values
NVIDIA_API_KEY=your_nvidia_api_key_here
API_SERVER_PORT=8000
# ... more options
```

## Security Best Practices

1. **Never commit .env files**: Add `.env` to `.gitignore`
2. **Use strong API keys**: Rotate keys regularly
3. **Limit CORS origins**: Don't use `*` in production
4. **Enable rate limiting**: Protect against abuse
5. **Use HTTPS**: In production environments

## Troubleshooting

### Common Issues

**No LLM API keys configured**

```bash
# Solution: Set at least one API key
export NVIDIA_API_KEY=your_key
# OR create .env file with the key
```

**Configuration not loading**

```bash
# Test configuration
python backend/src/config/test_config.py

# Check .env file exists and has correct format
cat .env
```

**Permission errors**

```bash
# Ensure data directories are writable
chmod -R 755 backend/data/
```

### Debug Mode

Enable debug mode for verbose logging:

```bash
export K8S_DEBUG_MODE=true
export LOG_LEVEL=DEBUG
```

### Test Mode

Enable test mode to use mock data:

```bash
export K8S_TEST_MODE=true
```

## Migration Guide

### From Environment Variables

If you're currently using environment variables directly:

**Before:**

```python
api_key = os.environ.get("NVIDIA_API_KEY")
```

**After:**

```python
from backend.src.config.loader import get_nvidia_api_key
api_key = get_nvidia_api_key()
```

### From Hardcoded Values

**Before:**

```python
port = 8000
host = "0.0.0.0"
```

**After:**

```python
from backend.src.config.loader import get_config
config = get_config()
port = config.api.api_server_port
host = config.api.api_server_host
```

## Advanced Usage

### Custom Configuration Loading

```python
from backend.src.config.settings import ConfigurationManager

# Load from specific .env file
config = ConfigurationManager(env_file="custom.env")
```

### Configuration Validation

```python
from backend.src.config.settings import get_config

config = get_config()

# Custom validation
if not config.api.nvidia_api_key:
    raise ValueError("NVIDIA API key is required")
```

### Runtime Configuration Changes

```python
import os
from backend.src.config.loader import get_config

# Change environment variable
os.environ["LOG_LEVEL"] = "DEBUG"

# Get fresh configuration
config = get_config()  # Will use cached instance

# Force reload (if needed)
from backend.src.config.settings import _config_instance
_config_instance = None
config = get_config()  # Will create new instance
```
