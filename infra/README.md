# Infrastructure

This directory contains infrastructure code, deployment scripts, and Kubernetes manifests.

## Structure

- `k8s/` - Kubernetes manifests and deployment configurations
- `monitoring/` - Prometheus and monitoring configurations
- `scripts/` - Deployment and setup scripts

## Scripts

- `setup_minikube.ps1/.sh` - Minikube setup for local development
- `run_*.ps1/.sh` - Various service startup scripts
- `setup_and_run.ps1` - Complete setup and run script

## Usage

```bash
# Setup Minikube (Windows)
.\scripts\setup_minikube.ps1

# Setup Minikube (Linux/macOS)
./scripts/setup_minikube.sh
```
