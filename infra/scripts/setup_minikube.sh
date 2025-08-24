#!/bin/bash
# Minikube Setup Script for Kubernetes Monitoring Project
# This script helps set up a Minikube environment with the necessary addons and configurations

# Set text colors
GREEN="\033[0;32m"
CYAN="\033[0;36m"
YELLOW="\033[0;33m"
RED="\033[0;31m"
NC="\033[0m" # No Color

# Check if Minikube is installed
if command -v minikube &> /dev/null; then
    minikube_version=$(minikube version)
    echo -e "${GREEN}Found Minikube: ${minikube_version}${NC}"
else
    echo -e "${RED}Minikube not found. Please install Minikube first:${NC}"
    echo -e "${YELLOW}Visit: https://minikube.sigs.k8s.io/docs/start/${NC}"
    exit 1
fi

# Check if kubectl is installed
if command -v kubectl &> /dev/null; then
    kubectl_version=$(kubectl version --client)
    echo -e "${GREEN}Found kubectl: ${kubectl_version}${NC}"
else
    echo -e "${RED}kubectl not found. Please install kubectl first:${NC}"
    echo -e "${YELLOW}Visit: https://kubernetes.io/docs/tasks/tools/install-kubectl/${NC}"
    exit 1
fi

# Start Minikube with recommended resources
echo -e "${CYAN}Starting Minikube with recommended resources...${NC}"
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable necessary addons
echo -e "${CYAN}Enabling necessary addons...${NC}"
minikube addons enable metrics-server
minikube addons enable dashboard
minikube addons enable prometheus

# Wait for addons to be ready
echo -e "${CYAN}Waiting for addons to be ready...${NC}"
sleep 30

# Set up port forwarding for Prometheus in background
echo -e "${CYAN}Setting up port forwarding for Prometheus...${NC}"
kubectl port-forward -n monitoring service/prometheus-server 9090:80 &
PROMETHEUS_PID=$!

# Display information about the Minikube environment
echo -e "\n${GREEN}Minikube environment is ready!${NC}"
echo -e "\n${YELLOW}Useful commands:${NC}"
echo -e "- Access Dashboard: minikube dashboard"
echo -e "- Access Prometheus: http://localhost:9090"
echo -e "- Check pod status: kubectl get pods -A"
echo -e "- Get pod metrics: kubectl top pods"

# Set environment variables for the project
export PROMETHEUS_URL="http://localhost:9090"
export NAMESPACE="monitoring"

echo -e "\n${YELLOW}Environment variables set:${NC}"
echo -e "PROMETHEUS_URL=$PROMETHEUS_URL"
echo -e "NAMESPACE=$NAMESPACE"

echo -e "\n${GREEN}You can now run the Kubernetes monitoring project with Minikube!${NC}"
echo -e "${YELLOW}Note: Prometheus port forwarding is running in the background (PID: $PROMETHEUS_PID)${NC}"
echo -e "${YELLOW}To stop it, run: kill $PROMETHEUS_PID${NC}"