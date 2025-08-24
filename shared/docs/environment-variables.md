# Environment Variables Reference

This document provides a comprehensive reference for all environment variables used in the Kubernetes Monitoring, RAG, and Dashboard System.

## Overview

The system uses environment variables for configuration to ensure security, flexibility, and ease of deployment across different environments. All variables can be set in a `.env` file or as system environment variables.

## Quick Setup

1. **Copy the template:**

   ```bash
   cp .env.example .env
   ```

2. **Edit with your values:**

   ```bash
   # Edit .env file with your API keys and settings
   ```

3. **Test configuration:**
   ```bash
   python backend/src/config/test_config.py
   ```

## Required Variables

### LLM API Configuration

At least one LLM API key must be configured for the system to function:

| Variable         | Description                            | Example                     | Required            |
| ---------------- | -------------------------------------- | --------------------------- | ------------------- |
| `NVIDIA_API_KEY` | NVIDIA API key for AI-powered insights | `nvapi-1234567890abcdef`    | One of the LLM keys |
| `LLAMA_API_KEY`  | Llama API authentication key           | `llama-key-1234567890`      | One of the LLM keys |
| `LLAMA_API_URL`  | Llama API endpoint URL                 | `https://api.llama-api.com` | If using Llama      |
| `OPENAI_API_KEY` | OpenAI API key for GPT models          | `sk-1234567890abcdef`       | One of the LLM keys |

**Getting API Keys:**

- **NVIDIA**: Get your key from [https://build.nvidia.com/](https://build.nvidia.com/)
- **Llama**: Register at your Llama API provider
- **OpenAI**: Get your key from [https://platform.openai.com/](https://platform.openai.com/)

## Server Configuration

### API Server Settings

| Variable             | Description                                  | Default   | Example     |
| -------------------- | -------------------------------------------- | --------- | ----------- |
| `API_SERVER_HOST`    | Host address for the API server              | `0.0.0.0` | `localhost` |
| `API_SERVER_PORT`    | Port for the main API server                 | `8000`    | `8080`      |
| `DASHBOARD_API_PORT` | Port for dashboard-specific API              | `5000`    | `5001`      |
| `MCP_SERVER_PORT`    | Port for MCP (Model Context Protocol) server | `8000`    | `8001`      |

### Frontend Configuration

| Variable                  | Description                         | Default                 | Example                      |
| ------------------------- | ----------------------------------- | ----------------------- | ---------------------------- |
| `NEXT_PUBLIC_API_URL`     | Backend API URL for frontend        | `http://localhost:8000` | `https://api.yourdomain.com` |
| `NEXT_PUBLIC_WS_URL`      | WebSocket URL for real-time updates | `ws://localhost:8000`   | `wss://api.yourdomain.com`   |
| `NEXT_PUBLIC_ENVIRONMENT` | Environment identifier              | `development`           | `production`                 |

## Kubernetes Configuration

### Cluster Connection

| Variable         | Description                                 | Default        | Example               |
| ---------------- | ------------------------------------------- | -------------- | --------------------- |
| `K8S_NAMESPACE`  | Default Kubernetes namespace to monitor     | `default`      | `kube-system`         |
| `KUBECONFIG`     | Path to kubeconfig file                     | System default | `/path/to/kubeconfig` |
| `K8S_IN_CLUSTER` | Whether running inside a Kubernetes cluster | `false`        | `true`                |
| `K8S_TEST_MODE`  | Enable test mode with mock data             | `false`        | `true`                |
| `K8S_DEBUG_MODE` | Enable debug mode for Kubernetes operations | `false`        | `true`                |

**Notes:**

- If `KUBECONFIG` is not set, the system uses the default kubectl configuration
- Set `K8S_IN_CLUSTER=true` when deploying inside Kubernetes
- Use `K8S_TEST_MODE=true` for development without a real cluster

## External Services

### Monitoring and Metrics

| Variable         | Description                                  | Default | Example                 |
| ---------------- | -------------------------------------------- | ------- | ----------------------- |
| `PROMETHEUS_URL` | Prometheus server URL for metrics collection | None    | `http://localhost:9090` |

**Note:** Prometheus integration is optional. The system can collect metrics directly from the Kubernetes API if Prometheus is not available.

## Database and Storage Configuration

### Data Persistence

| Variable              | Description                           | Default                           | Example                |
| --------------------- | ------------------------------------- | --------------------------------- | ---------------------- |
| `CHROMA_DB_PATH`      | ChromaDB vector database storage path | `backend/data/chroma_db`          | `/data/chroma_db`      |
| `METRICS_CSV_PATH`    | Path for storing metrics CSV files    | `backend/data/pod_metrics.csv`    | `/data/metrics.csv`    |
| `INSIGHTS_JSON_PATH`  | Path for storing processed insights   | `backend/data/pod_insights.json`  | `/data/insights.json`  |
| `KNOWLEDGE_BASE_PATH` | Path for Kubernetes knowledge base    | `backend/data/k8s_knowledge.json` | `/data/knowledge.json` |

**Notes:**

- Ensure the specified directories are writable
- Use absolute paths for production deployments
- Consider using persistent volumes in Kubernetes deployments

## Logging Configuration

### Log Settings

| Variable            | Description                        | Default                                                | Options                                         |
| ------------------- | ---------------------------------- | ------------------------------------------------------ | ----------------------------------------------- |
| `LOG_LEVEL`         | Logging level for the application  | `INFO`                                                 | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` |
| `LOG_FORMAT`        | Log message format string          | `%(asctime)s - %(name)s - %(levelname)s - %(message)s` | Custom format                                   |
| `LOG_FILE`          | Path to log file (optional)        | None (console only)                                    | `backend/logs/app.log`                          |
| `LOG_MAX_FILE_SIZE` | Maximum log file size in bytes     | `10485760` (10MB)                                      | `52428800` (50MB)                               |
| `LOG_BACKUP_COUNT`  | Number of backup log files to keep | `5`                                                    | `10`                                            |

**Log Levels:**

- `DEBUG`: Detailed information for debugging
- `INFO`: General information about application flow
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for handled exceptions
- `CRITICAL`: Critical errors that may cause application failure

## Security Configuration

### Access Control

| Variable                | Description                             | Default           | Example                                        |
| ----------------------- | --------------------------------------- | ----------------- | ---------------------------------------------- |
| `CORS_ORIGINS`          | Allowed CORS origins (comma-separated)  | `*`               | `http://localhost:3000,https://yourdomain.com` |
| `RATE_LIMIT_PER_MINUTE` | API rate limiting (requests per minute) | `60`              | `100`                                          |
| `MAX_REQUEST_SIZE`      | Maximum request size in bytes           | `16777216` (16MB) | `33554432` (32MB)                              |

**Security Best Practices:**

- Never use `CORS_ORIGINS=*` in production
- Set appropriate rate limits based on your usage patterns
- Limit request size to prevent abuse

## Monitoring and Performance

### System Monitoring

| Variable                      | Description                              | Default | Example |
| ----------------------------- | ---------------------------------------- | ------- | ------- |
| `METRICS_COLLECTION_INTERVAL` | Metrics collection interval in seconds   | `30`    | `60`    |
| `ANOMALY_DETECTION_THRESHOLD` | Anomaly detection threshold (0.0 to 1.0) | `0.8`   | `0.9`   |
| `ENABLE_HEALTH_CHECKS`        | Enable health check endpoints            | `true`  | `false` |
| `PERFORMANCE_METRICS`         | Enable performance metrics collection    | `true`  | `false` |

**Performance Tuning:**

- Increase `METRICS_COLLECTION_INTERVAL` to reduce system load
- Adjust `ANOMALY_DETECTION_THRESHOLD` based on your cluster's normal behavior
- Disable `PERFORMANCE_METRICS` in production if not needed

## Development and Debugging

### Development Settings

| Variable                  | Description                  | Default       | Example      |
| ------------------------- | ---------------------------- | ------------- | ------------ |
| `FASTMCP_LOG_LEVEL`       | Log level for MCP components | `ERROR`       | `DEBUG`      |
| `NODE_ENV`                | Node.js environment          | `development` | `production` |
| `NEXT_TELEMETRY_DISABLED` | Disable Next.js telemetry    | `1`           | `0`          |

**Development Tips:**

- Set `LOG_LEVEL=DEBUG` for verbose logging during development
- Use `K8S_TEST_MODE=true` to work without a real Kubernetes cluster
- Enable `K8S_DEBUG_MODE=true` for detailed Kubernetes operation logs

## Environment-Specific Configurations

### Development Environment

```bash
# .env.development
LOG_LEVEL=DEBUG
K8S_TEST_MODE=true
K8S_DEBUG_MODE=true
CORS_ORIGINS=*
RATE_LIMIT_PER_MINUTE=1000
METRICS_COLLECTION_INTERVAL=10
```

### Production Environment

```bash
# .env.production
LOG_LEVEL=INFO
K8S_TEST_MODE=false
K8S_DEBUG_MODE=false
CORS_ORIGINS=https://yourdomain.com
RATE_LIMIT_PER_MINUTE=60
METRICS_COLLECTION_INTERVAL=30
LOG_FILE=/var/log/k8s-monitoring/app.log
```

### Testing Environment

```bash
# .env.test
LOG_LEVEL=WARNING
K8S_TEST_MODE=true
ENABLE_HEALTH_CHECKS=false
PERFORMANCE_METRICS=false
CHROMA_DB_PATH=/tmp/test_chroma_db
```

## Docker Configuration

### Container Environment Variables

When running in Docker, you can pass environment variables using:

```bash
# Docker run
docker run -e NVIDIA_API_KEY=your_key -e LOG_LEVEL=DEBUG your-image

# Docker Compose
version: '3.8'
services:
  backend:
    image: k8s-monitoring-backend
    environment:
      - NVIDIA_API_KEY=${NVIDIA_API_KEY}
      - LOG_LEVEL=INFO
      - K8S_TEST_MODE=false
    env_file:
      - .env
```

## Kubernetes Deployment

### ConfigMap and Secrets

```yaml
# ConfigMap for non-sensitive configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: k8s-monitoring-config
data:
  LOG_LEVEL: "INFO"
  K8S_NAMESPACE: "default"
  METRICS_COLLECTION_INTERVAL: "30"
  CORS_ORIGINS: "https://yourdomain.com"

---
# Secret for sensitive data
apiVersion: v1
kind: Secret
metadata:
  name: k8s-monitoring-secrets
type: Opaque
stringData:
  NVIDIA_API_KEY: "your-nvidia-api-key"
  LLAMA_API_KEY: "your-llama-api-key"
```

## Validation and Testing

### Configuration Validation

The system provides built-in configuration validation:

```bash
# Test configuration
python backend/src/config/test_config.py

# Validate specific settings
python -c "from backend.src.config.loader import validate_environment; print(validate_environment())"
```

### Common Validation Errors

| Error                          | Cause                          | Solution                                                                 |
| ------------------------------ | ------------------------------ | ------------------------------------------------------------------------ |
| "No valid LLM API key found"   | No LLM API key configured      | Set at least one: `NVIDIA_API_KEY`, `LLAMA_API_KEY`, or `OPENAI_API_KEY` |
| "Invalid log level"            | Incorrect `LOG_LEVEL` value    | Use: `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`                  |
| "Cannot connect to Kubernetes" | Kubernetes configuration issue | Check `kubectl` setup or set `K8S_TEST_MODE=true`                        |
| "Invalid CORS origins"         | Malformed `CORS_ORIGINS`       | Use comma-separated URLs or `*`                                          |

## Migration Guide

### From Hardcoded Values

If you're migrating from hardcoded configuration values:

**Before:**

```python
api_key = "nvapi-1234567890"
port = 8000
```

**After:**

```bash
# .env file
NVIDIA_API_KEY=nvapi-1234567890
API_SERVER_PORT=8000
```

### From Different Configuration Systems

**From JSON config files:**

1. Extract values from JSON files
2. Set corresponding environment variables
3. Remove JSON config files
4. Update code to use configuration loader

**From YAML config files:**

1. Map YAML keys to environment variable names
2. Set environment variables
3. Test with configuration validation
4. Remove YAML files

## Troubleshooting

### Configuration Issues

**Problem: Configuration not loading**

```bash
# Check if .env file exists and is readable
ls -la .env
cat .env

# Test configuration loading
python backend/src/config/test_config.py
```

**Problem: Environment variables not recognized**

```bash
# Check environment variables are set
env | grep -E "(NVIDIA|LLAMA|OPENAI|K8S|LOG)"

# Test specific variable
echo $NVIDIA_API_KEY
```

**Problem: Permission errors with data directories**

```bash
# Check directory permissions
ls -la backend/data/

# Fix permissions
chmod -R 755 backend/data/
```

### Debug Configuration

Enable debug mode to see configuration loading:

```bash
export LOG_LEVEL=DEBUG
export K8S_DEBUG_MODE=true
python backend/src/config/test_config.py
```

## Security Considerations

### Sensitive Data

**Never commit sensitive data:**

- Add `.env` to `.gitignore`
- Use `.env.example` as a template
- Rotate API keys regularly

**Production security:**

- Use secrets management systems (AWS Secrets Manager, Azure Key Vault, etc.)
- Restrict CORS origins
- Enable rate limiting
- Use HTTPS in production

### Best Practices

1. **Principle of Least Privilege**: Only set necessary permissions
2. **Environment Separation**: Use different configurations for dev/staging/prod
3. **Secret Rotation**: Regularly rotate API keys and secrets
4. **Monitoring**: Monitor for configuration changes and access
5. **Backup**: Backup configuration templates and documentation

## Support

For configuration help:

- Use the setup script: `python backend/scripts/setup_config.py`
- Check the configuration guide: `backend/docs/configuration.md`
- Test your configuration: `python backend/src/config/test_config.py`
- Report issues via GitHub Issues

This reference should help you configure the system for any environment. For specific deployment scenarios, refer to the deployment documentation in the respective service directories.
