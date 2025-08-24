from flask import Flask, jsonify
from flask_cors import CORS
from kubernetes import client, config
import sys
import os
import logging

# Import configuration management
from backend.src.config.loader import (
    get_config, setup_logging, get_kubernetes_config, 
    validate_environment, ensure_data_directories
)

# Import from services module
from backend.src.services.fetch_metrics import fetch_metrics

# Setup logging and configuration
setup_logging()
logger = logging.getLogger(__name__)

# Validate environment
if not validate_environment():
    logger.error("Environment validation failed. Please check your configuration.")
    sys.exit(1)

# Ensure data directories exist
ensure_data_directories()

# Get configuration
app_config = get_config()
k8s_config = get_kubernetes_config()

# Add the k8s-dashboard-backend directory to the Python path to import llama_routes
k8s_dashboard_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'k8s-dashboard-backend'))
sys.path.append(k8s_dashboard_backend_path)

# Import the LLaMA blueprint
try:
    from api.llama_routes import llama_bp
    llama_available = True
    logger.info("LLaMA routes imported successfully")
except ImportError as e:
    logger.warning(f"Could not import LLaMA routes: {e}")
    llama_available = False

app = Flask(__name__)

# Configure CORS with security settings
CORS(app, origins=app_config.security.cors_origins)

# Load Kubernetes configuration
try:
    if k8s_config["in_cluster"]:
        config.load_incluster_config()
        logger.info("Loaded in-cluster Kubernetes configuration")
    else:
        if k8s_config["kubeconfig_path"]:
            config.load_kube_config(config_file=k8s_config["kubeconfig_path"])
        else:
            config.load_kube_config()
        logger.info("Loaded Kubernetes configuration from kubeconfig")
    
    v1 = client.CoreV1Api()
    logger.info("Kubernetes client initialized successfully")
except Exception as e:
    if k8s_config["test_mode"]:
        logger.warning(f"Kubernetes configuration failed, running in test mode: {e}")
        v1 = None
    else:
        logger.error(f"Failed to load Kubernetes configuration: {e}")
        sys.exit(1)

@app.route('/api/metrics', methods=['GET'])
def get_k8s_metrics():
    try:
        if k8s_config["test_mode"] or v1 is None:
            # Return mock data in test mode
            logger.info("Returning mock metrics data (test mode)")
            return jsonify([
                {
                    'pod_name': 'test-pod-1',
                    'namespace': 'default',
                    'metrics': {
                        'cpu_usage': '50m',
                        'memory_usage': '128Mi',
                        'status': 'Running'
                    }
                },
                {
                    'pod_name': 'test-pod-2',
                    'namespace': 'kube-system',
                    'metrics': {
                        'cpu_usage': '25m',
                        'memory_usage': '64Mi',
                        'status': 'Running'
                    }
                }
            ])
        
        # Get pods from specified namespace or all namespaces
        if k8s_config["namespace"] != "default":
            pods = v1.list_namespaced_pod(namespace=k8s_config["namespace"]).items
        else:
            pods = v1.list_pod_for_all_namespaces().items
        
        all_metrics = []
        for pod in pods:
            metrics = fetch_metrics(pod, v1)
            all_metrics.append({
                'pod_name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'metrics': metrics
            })
        
        logger.info(f"Retrieved metrics for {len(all_metrics)} pods")
        return jsonify(all_metrics)
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/remediations', methods=['GET'])
def get_remediations():
    mock_remediations = [
        {
            "id": "r1",
            "type": "Scale Up Deployment",
            "status": "pending",
            "description": "Increase replicas for 'data-processor' due to high memory usage.",
            "timestamp": "2023-10-26T09:45:00Z",
            "target_resource": "deployment/data-processor",
            "suggested_by": "Koda",
        },
        {
            "id": "r2",
            "type": "Restart Pod",
            "status": "completed",
            "description": "Restart 'my-app-pod-1' to clear CPU spike.",
            "timestamp": "2023-10-26T10:15:00Z",
            "target_resource": "pod/my-app-pod-1",
            "suggested_by": "Koda",
        },
    ]
    return jsonify(mock_remediations)

@app.route('/api/clusters', methods=['GET'])
def get_clusters():
    mock_clusters = [
        {
            "id": "c1",
            "name": "minikube-cluster",
            "status": "healthy",
            "node_count": 1,
            "pod_count": 15,
            "namespace_count": 5,
            "kubernetes_version": "v1.27.3",
            "cloud_provider": "minikube",
        }
    ]
    return jsonify(mock_clusters)

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    if not app_config.monitoring.enable_health_checks:
        return jsonify({'status': 'disabled'}), 404
    
    health_status = {
        'status': 'healthy',
        'timestamp': '2023-10-26T12:00:00Z',
        'kubernetes': 'connected' if v1 else 'disconnected',
        'test_mode': k8s_config["test_mode"]
    }
    
    return jsonify(health_status)

# Register the LLaMA blueprint if available
if llama_available:
    app.register_blueprint(llama_bp)
    logger.info("LLaMA API routes registered successfully")

if __name__ == '__main__':
    logger.info(f"Starting API server on {app_config.api.api_server_host}:{app_config.api.api_server_port}")
    app.run(
        host=app_config.api.api_server_host, 
        port=app_config.api.api_server_port, 
        debug=(app_config.logging.level == "DEBUG")
    )