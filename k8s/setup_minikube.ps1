# Minikube Setup Script for Kubernetes Monitoring Project
# This script helps set up a Minikube environment with the necessary addons and configurations

# Check if Minikube is installed
try {
    $minikubeVersion = minikube version
    Write-Host "Found Minikube: $minikubeVersion" -ForegroundColor Green
} catch {
    Write-Host "Minikube not found. Please install Minikube first:" -ForegroundColor Red
    Write-Host "Visit: https://minikube.sigs.k8s.io/docs/start/" -ForegroundColor Yellow
    exit 1
}

# Check if kubectl is installed
try {
    $kubectlVersion = kubectl version --client
    Write-Host "Found kubectl: $kubectlVersion" -ForegroundColor Green
} catch {
    Write-Host "kubectl not found. Please install kubectl first:" -ForegroundColor Red
    Write-Host "Visit: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/" -ForegroundColor Yellow
    exit 1
}

# Start Minikube with recommended resources
Write-Host "Starting Minikube with recommended resources..." -ForegroundColor Cyan
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable necessary addons
Write-Host "Enabling necessary addons..." -ForegroundColor Cyan
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable prometheus

# Wait for addons to be ready
Write-Host "Waiting for addons to be ready..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

# Set up port forwarding for Prometheus in background
Write-Host "Setting up port forwarding for Prometheus..." -ForegroundColor Cyan
Start-Job -ScriptBlock {
    kubectl port-forward -n monitoring service/prometheus-server 9090:80
}

# Display information about the Minikube environment
Write-Host "\nMinikube environment is ready!" -ForegroundColor Green
Write-Host "\nUseful commands:" -ForegroundColor Yellow
Write-Host "- Access Dashboard: minikube dashboard" -ForegroundColor White
Write-Host "- Access Prometheus: http://localhost:9090" -ForegroundColor White
Write-Host "- Check pod status: kubectl get pods -A" -ForegroundColor White
Write-Host "- Get pod metrics: kubectl top pods" -ForegroundColor White

# Set environment variables for the project
$env:PROMETHEUS_URL = "http://localhost:9090"
$env:NAMESPACE = "monitoring"

Write-Host "\nEnvironment variables set:" -ForegroundColor Yellow
Write-Host "PROMETHEUS_URL=$env:PROMETHEUS_URL" -ForegroundColor White
Write-Host "NAMESPACE=$env:NAMESPACE" -ForegroundColor White

Write-Host "\nYou can now run the Kubernetes monitoring project with Minikube!" -ForegroundColor Green