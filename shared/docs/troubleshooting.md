# Troubleshooting Guide

This guide helps you diagnose and resolve common issues when setting up and running the Kubernetes Monitoring, RAG, and Dashboard System.

## Quick Diagnostics

### System Health Check

Run these commands to quickly check system health:

```bash
# Test configuration
python backend/src/config/test_config.py

# Check API server
curl http://localhost:8000/health

# Check frontend
curl http://localhost:3000

# Check Kubernetes connection
kubectl cluster-info

# Check Docker services
docker-compose ps
```

### Log Analysis

Check logs for error messages:

```bash
# Backend logs
tail -f backend/logs/app.log

# Docker logs
docker-compose logs -f

# Kubernetes logs
kubectl logs -f deployment/k8s-monitoring
```

## Configuration Issues

### No LLM API Keys Configured

**Error Message:**

```
Error: No valid LLM API key found. Please set NVIDIA_API_KEY, LLAMA_API_KEY, or OPENAI_API_KEY
```

**Cause:** No LLM API key is configured in environment variables.

**Solution:**

1. **Set at least one API key:**

   ```bash
   # Option 1: NVIDIA API (recommended)
   export NVIDIA_API_KEY=your_nvidia_api_key_here

   # Option 2: Llama API
   export LLAMA_API_KEY=your_llama_api_key_here
   export LLAMA_API_URL=https://api.llama-api.com

   # Option 3: OpenAI API
   export OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Or add to .env file:**

   ```bash
   cp .env.example .env
   # Edit .env file with your API key
   ```

3. **Test configuration:**
   ```bash
   python backend/src/config/test_config.py
   ```

**Getting API Keys:**

- **NVIDIA**: [https://build.nvidia.com/](https://build.nvidia.com/)
- **OpenAI**: [https://platform.openai.com/](https://platform.openai.com/)
- **Llama**: Contact your Llama API provider

### Configuration File Not Found

**Error Message:**

```
FileNotFoundError: [Errno 2] No such file or directory: '.env'
```

**Cause:** The `.env` file doesn't exist.

**Solution:**

1. **Create .env file from template:**

   ```bash
   cp .env.example .env
   ```

2. **Edit with your settings:**

   ```bash
   # Windows
   notepad .env

   # Linux/macOS
   nano .env
   ```

3. **Verify file exists:**
   ```bash
   ls -la .env
   cat .env
   ```

### Invalid Configuration Values

**Error Message:**

```
ValueError: Invalid log level: 'INVALID'
```

**Cause:** Configuration values don't match expected formats.

**Common Issues and Solutions:**

| Setting           | Valid Values                                    | Example                              |
| ----------------- | ----------------------------------------------- | ------------------------------------ |
| `LOG_LEVEL`       | `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` | `LOG_LEVEL=INFO`                     |
| `K8S_IN_CLUSTER`  | `true`, `false`                                 | `K8S_IN_CLUSTER=false`               |
| `API_SERVER_PORT` | Integer 1-65535                                 | `API_SERVER_PORT=8000`               |
| `CORS_ORIGINS`    | URLs or `*`                                     | `CORS_ORIGINS=http://localhost:3000` |

**Fix invalid values:**

```bash
# Check current values
python -c "from backend.src.config.loader import get_config; print(get_config())"

# Update .env file with correct values
```

## Connection Issues

### Cannot Connect to Kubernetes Cluster

**Error Message:**

```
kubernetes.config.config_exception.ConfigException: Unable to load in-cluster config
```

**Cause:** Kubernetes configuration is not properly set up.

**Solutions:**

1. **Check kubectl configuration:**

   ```bash
   kubectl cluster-info
   kubectl get nodes
   ```

2. **For Minikube users:**

   ```bash
   # Start Minikube
   minikube start

   # Check status
   minikube status

   # Set context
   kubectl config use-context minikube
   ```

3. **For development without cluster:**

   ```bash
   # Enable test mode
   export K8S_TEST_MODE=true
   ```

4. **Check kubeconfig file:**

   ```bash
   # Default location
   ls -la ~/.kube/config

   # Custom location
   export KUBECONFIG=/path/to/your/kubeconfig
   ```

5. **Verify cluster access:**
   ```bash
   kubectl auth can-i get pods
   kubectl get namespaces
   ```

### API Server Connection Refused

**Error Message:**

```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='localhost', port=8000): Max retries exceeded
```

**Cause:** Backend API server is not running or not accessible.

**Solutions:**

1. **Check if server is running:**

   ```bash
   # Check process
   ps aux | grep uvicorn

   # Check port
   netstat -tulpn | grep 8000  # Linux
   netstat -ano | findstr 8000  # Windows
   ```

2. **Start the backend server:**

   ```bash
   cd backend
   uvicorn src.api.api_server:app --host 0.0.0.0 --port 8000
   ```

3. **Check server logs:**

   ```bash
   # Look for startup errors
   tail -f backend/logs/app.log
   ```

4. **Test server health:**

   ```bash
   curl http://localhost:8000/health
   ```

5. **Check firewall/network:**

   ```bash
   # Test local connection
   telnet localhost 8000

   # Check if port is blocked
   sudo ufw status  # Linux
   ```

### Frontend Cannot Connect to Backend

**Error Message:**

```
Network Error: Request failed with status code 500
```

**Cause:** Frontend cannot reach backend API or CORS issues.

**Solutions:**

1. **Check backend URL in frontend:**

   ```bash
   # Check environment variables
   echo $NEXT_PUBLIC_API_URL

   # Should be: http://localhost:8000
   ```

2. **Update frontend configuration:**

   ```bash
   # In .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   NEXT_PUBLIC_WS_URL=ws://localhost:8000
   ```

3. **Check CORS configuration:**

   ```bash
   # In backend .env
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173
   ```

4. **Test API directly:**

   ```bash
   curl -X GET http://localhost:8000/api/cluster/status
   ```

5. **Check browser console:**
   - Open browser developer tools (F12)
   - Look for network errors in Console tab
   - Check Network tab for failed requests

## Port Conflicts

### Port Already in Use

**Error Message:**

```
OSError: [Errno 48] Address already in use
```

**Cause:** Another process is using the required port.

**Solutions:**

1. **Find process using port:**

   ```bash
   # Linux/macOS
   lsof -i :8000
   sudo netstat -tulpn | grep 8000

   # Windows
   netstat -ano | findstr 8000
   ```

2. **Kill conflicting process:**

   ```bash
   # Linux/macOS
   kill -9 <PID>

   # Windows
   taskkill /PID <PID> /F
   ```

3. **Use different port:**

   ```bash
   # Backend
   export API_SERVER_PORT=8001
   uvicorn src.api.api_server:app --port 8001

   # Frontend
   npm run dev -- --port 3001
   ```

4. **Update configuration:**

   ```bash
   # Update .env file
   API_SERVER_PORT=8001

   # Update frontend .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8001
   ```

## Dependency Issues

### Python Dependencies

**Error Message:**

```
ModuleNotFoundError: No module named 'fastapi'
```

**Cause:** Python dependencies are not installed or virtual environment is not activated.

**Solutions:**

1. **Check virtual environment:**

   ```bash
   # Check if activated (should show (.venv) in prompt)
   which python

   # Activate if needed
   # Windows
   .venv\Scripts\activate

   # Linux/macOS
   source .venv/bin/activate
   ```

2. **Install dependencies:**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Upgrade pip:**

   ```bash
   python -m pip install --upgrade pip
   ```

4. **Clear pip cache:**

   ```bash
   pip cache purge
   pip install --no-cache-dir -r requirements.txt
   ```

5. **Check Python version:**
   ```bash
   python --version  # Should be 3.8+
   ```

### Node.js Dependencies

**Error Message:**

```
Error: Cannot find module 'react'
```

**Cause:** Node.js dependencies are not installed.

**Solutions:**

1. **Install dependencies:**

   ```bash
   cd frontend
   npm install

   # Or with yarn
   yarn install
   ```

2. **Clear npm cache:**

   ```bash
   npm cache clean --force
   rm -rf node_modules package-lock.json
   npm install
   ```

3. **Check Node.js version:**

   ```bash
   node --version  # Should be 16+
   npm --version
   ```

4. **Use correct Node.js version:**
   ```bash
   # With nvm
   nvm install 18
   nvm use 18
   ```

### Docker Dependencies

**Error Message:**

```
docker: command not found
```

**Cause:** Docker is not installed or not in PATH.

**Solutions:**

1. **Install Docker:**

   - **Windows/macOS**: Download Docker Desktop
   - **Linux**: Follow distribution-specific instructions

2. **Check Docker status:**

   ```bash
   docker --version
   docker-compose --version
   docker info
   ```

3. **Start Docker service:**

   ```bash
   # Linux
   sudo systemctl start docker

   # macOS/Windows
   # Start Docker Desktop application
   ```

4. **Fix permissions (Linux):**
   ```bash
   sudo usermod -aG docker $USER
   # Log out and back in
   ```

## Performance Issues

### Slow API Responses

**Symptoms:**

- API requests take more than 10 seconds
- Frontend shows loading states for extended periods
- Timeout errors

**Solutions:**

1. **Check system resources:**

   ```bash
   # CPU and memory usage
   top
   htop

   # Disk usage
   df -h

   # Check for high I/O
   iotop
   ```

2. **Optimize configuration:**

   ```bash
   # Increase collection interval
   METRICS_COLLECTION_INTERVAL=60

   # Reduce log level
   LOG_LEVEL=WARNING

   # Disable debug mode
   K8S_DEBUG_MODE=false
   ```

3. **Check database performance:**

   ```bash
   # ChromaDB size
   du -sh backend/data/chroma_db/

   # Clear old data if needed
   rm -rf backend/data/chroma_db/
   ```

4. **Monitor network:**

   ```bash
   # Check network latency
   ping kubernetes.default.svc.cluster.local

   # Check DNS resolution
   nslookup kubernetes.default.svc.cluster.local
   ```

### High Memory Usage

**Symptoms:**

- System becomes unresponsive
- Out of memory errors
- Processes being killed

**Solutions:**

1. **Monitor memory usage:**

   ```bash
   # Check memory usage
   free -h
   ps aux --sort=-%mem | head

   # Check for memory leaks
   top -o %MEM
   ```

2. **Optimize Python memory:**

   ```bash
   # Limit worker processes
   gunicorn --workers 2 src.api.api_server:app

   # Use memory profiling
   pip install memory-profiler
   python -m memory_profiler your_script.py
   ```

3. **Optimize Node.js memory:**

   ```bash
   # Increase Node.js memory limit
   export NODE_OPTIONS="--max-old-space-size=4096"
   npm run build
   ```

4. **Clear caches:**

   ```bash
   # Clear Python cache
   find . -type d -name __pycache__ -delete

   # Clear Node.js cache
   npm cache clean --force

   # Clear system cache (Linux)
   sudo sync && sudo sysctl vm.drop_caches=3
   ```

## Data Issues

### ChromaDB Connection Errors

**Error Message:**

```
chromadb.errors.ConnectionError: Could not connect to ChromaDB
```

**Solutions:**

1. **Check ChromaDB directory:**

   ```bash
   ls -la backend/data/chroma_db/

   # Create if missing
   mkdir -p backend/data/chroma_db/
   ```

2. **Check permissions:**

   ```bash
   chmod -R 755 backend/data/
   chown -R $USER:$USER backend/data/
   ```

3. **Reset ChromaDB:**

   ```bash
   # Backup existing data
   mv backend/data/chroma_db backend/data/chroma_db.backup

   # Create fresh database
   mkdir -p backend/data/chroma_db/
   ```

4. **Check disk space:**
   ```bash
   df -h backend/data/
   ```

### Missing Data Files

**Error Message:**

```
FileNotFoundError: [Errno 2] No such file or directory: 'backend/data/pod_metrics.csv'
```

**Solutions:**

1. **Create data directories:**

   ```bash
   mkdir -p backend/data/
   mkdir -p backend/logs/
   ```

2. **Initialize data files:**

   ```bash
   # Create empty CSV with headers
   echo "timestamp,pod_name,cpu_usage,memory_usage" > backend/data/pod_metrics.csv

   # Create empty JSON
   echo "{}" > backend/data/pod_insights.json
   ```

3. **Run data collection:**
   ```bash
   python backend/src/agents/k8s_metrics_collector.py
   ```

## Authentication Issues

### Kubernetes RBAC Errors

**Error Message:**

```
Forbidden: User "system:serviceaccount:default:default" cannot get resource "pods"
```

**Solutions:**

1. **Check current permissions:**

   ```bash
   kubectl auth can-i get pods
   kubectl auth can-i get nodes
   kubectl auth can-i get services
   ```

2. **Create service account with permissions:**

   ```yaml
   # rbac.yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: k8s-monitoring
     namespace: default
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRole
   metadata:
     name: k8s-monitoring
   rules:
     - apiGroups: [""]
       resources: ["pods", "nodes", "services", "events"]
       verbs: ["get", "list", "watch"]
     - apiGroups: ["apps"]
       resources: ["deployments", "replicasets"]
       verbs: ["get", "list", "watch"]
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRoleBinding
   metadata:
     name: k8s-monitoring
   roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: ClusterRole
     name: k8s-monitoring
   subjects:
     - kind: ServiceAccount
       name: k8s-monitoring
       namespace: default
   ```

3. **Apply RBAC configuration:**

   ```bash
   kubectl apply -f rbac.yaml
   ```

4. **Use service account:**
   ```bash
   kubectl patch deployment k8s-monitoring -p '{"spec":{"template":{"spec":{"serviceAccountName":"k8s-monitoring"}}}}'
   ```

## Development Issues

### Hot Reload Not Working

**Symptoms:**

- Changes to code don't reflect in browser
- Need to manually refresh page
- Development server doesn't restart

**Solutions:**

1. **Check file watchers (Linux):**

   ```bash
   # Increase inotify limit
   echo fs.inotify.max_user_watches=524288 | sudo tee -a /etc/sysctl.conf
   sudo sysctl -p
   ```

2. **Restart development servers:**

   ```bash
   # Backend
   uvicorn src.api.api_server:app --reload

   # Frontend
   npm run dev
   ```

3. **Clear caches:**

   ```bash
   # Next.js cache
   rm -rf .next/

   # Python cache
   find . -name "*.pyc" -delete
   ```

### Import Errors

**Error Message:**

```
ImportError: attempted relative import with no known parent package
```

**Solutions:**

1. **Check Python path:**

   ```bash
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"
   ```

2. **Use absolute imports:**

   ```python
   # Instead of: from .utils import helper
   # Use: from backend.src.utils import helper
   ```

3. **Check working directory:**
   ```bash
   # Run from project root
   cd /path/to/kubernetes-monitoring-system
   python backend/src/api/api_server.py
   ```

## Getting Help

### Debug Mode

Enable comprehensive debugging:

```bash
# Backend debug mode
export LOG_LEVEL=DEBUG
export K8S_DEBUG_MODE=true
export FASTMCP_LOG_LEVEL=DEBUG

# Frontend debug mode
export NODE_ENV=development
export DEBUG=*
```

### Collecting Debug Information

When reporting issues, include:

1. **System information:**

   ```bash
   # Operating system
   uname -a

   # Python version
   python --version

   # Node.js version
   node --version

   # Docker version
   docker --version

   # Kubernetes version
   kubectl version
   ```

2. **Configuration:**

   ```bash
   # Test configuration (removes sensitive data)
   python backend/src/config/test_config.py
   ```

3. **Logs:**

   ```bash
   # Recent logs
   tail -100 backend/logs/app.log

   # Docker logs
   docker-compose logs --tail=100
   ```

4. **Network connectivity:**
   ```bash
   # Test API endpoints
   curl -v http://localhost:8000/health
   curl -v http://localhost:3000
   ```

### Support Channels

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check `docs/` directories for detailed guides
- **Configuration Help**: Use `python backend/scripts/setup_config.py`
- **Community**: Join discussions in project forums

### Common Commands Summary

```bash
# Quick health check
python backend/src/config/test_config.py
curl http://localhost:8000/health
kubectl cluster-info

# Reset everything
docker-compose down
rm -rf .next/ backend/data/chroma_db/
docker-compose up -d

# Debug mode
export LOG_LEVEL=DEBUG K8S_DEBUG_MODE=true
python backend/src/api/api_server.py

# Clean install
rm -rf node_modules/ .venv/
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt
cd frontend && npm install
```

This troubleshooting guide should help you resolve most common issues. If you encounter problems not covered here, please check the specific component documentation or create an issue with detailed information about your setup and the error messages you're seeing.
