# Minikube Setup for Kubernetes Monitoring Project

This guide provides instructions for setting up and using the Kubernetes Monitoring Project with Minikube, a local Kubernetes environment.

## Prerequisites

- [Minikube](https://minikube.sigs.k8s.io/docs/start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- [Docker](https://www.docker.com/products/docker-desktop/) (recommended driver for Minikube)

## Automated Setup

We provide setup scripts that automate the Minikube configuration process:

### Windows

1. Open PowerShell as Administrator
2. Navigate to the project directory
3. Run the setup script:

```powershell
.\setup_minikube.ps1
```

### Linux/macOS

1. Open Terminal
2. Navigate to the project directory
3. Make the script executable and run it:

```bash
chmod +x ./setup_minikube.sh
./setup_minikube.sh
```

## Manual Setup

If you prefer to set up Minikube manually, follow these steps:

1. Start Minikube with sufficient resources:

```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

2. Enable necessary addons:

```bash
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable prometheus
```

3. Set up port forwarding for Prometheus:

```bash
kubectl port-forward -n monitoring service/prometheus-server 9090:80
```

4. Set environment variables for the project:

```bash
# For Linux/macOS
export PROMETHEUS_URL="http://localhost:9090"
export NAMESPACE="monitoring"

# For Windows PowerShell
$env:PROMETHEUS_URL = "http://localhost:9090"
$env:NAMESPACE = "monitoring"
```

## Verifying the Setup

1. Check that all pods are running:

```bash
kubectl get pods -A
```

2. Verify metrics collection is working:

```bash
kubectl top pods
```

3. Access the Kubernetes dashboard:

```bash
minikube dashboard
```

4. Access Prometheus at [http://localhost:9090](http://localhost:9090)

## Running the Project with Minikube

Once Minikube is set up, you can run the Kubernetes monitoring project:

```bash
python agentic_rag_cli.py
```

The system will now use your local Minikube cluster for Kubernetes operations and metrics collection.

## Troubleshooting

### Metrics API Not Available

If you encounter issues with the Metrics API, ensure the metrics-server addon is enabled and running:

```bash
minikube addons enable metrics-server
kubectl get pods -n kube-system | grep metrics-server
```

### Prometheus Not Accessible

If Prometheus is not accessible at http://localhost:9090, check the port forwarding:

```bash
# Stop any existing port forwarding
pkill -f "kubectl port-forward"

# Start port forwarding again
kubectl port-forward -n monitoring service/prometheus-server 9090:80
```

### Resource Constraints

If Minikube is struggling with performance, you may need to allocate more resources:

```bash
minikube stop
minikube start --cpus=6 --memory=12288 --driver=docker
```

## Cleaning Up

To stop and clean up your Minikube environment:

```bash
minikube stop
minikube delete
```