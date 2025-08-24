from flask import Flask, jsonify
from flask_cors import CORS
from kubernetes import client, config
import sys
import os

# Import from services module
from backend.src.services.fetch_metrics import fetch_metrics

# Add the k8s-dashboard-backend directory to the Python path to import llama_routes
k8s_dashboard_backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'k8s-dashboard-backend'))
sys.path.append(k8s_dashboard_backend_path)

# Import the LLaMA blueprint
try:
    from api.llama_routes import llama_bp
    llama_available = True
except ImportError as e:
    print(f"Warning: Could not import LLaMA routes: {e}")
    llama_available = False

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Load Kubernetes configuration
config.load_kube_config()
v1 = client.CoreV1Api()

@app.route('/api/metrics', methods=['GET'])
def get_k8s_metrics():
    try:
        pods = v1.list_pod_for_all_namespaces().items
        all_metrics = []
        for pod in pods:
            metrics = fetch_metrics(pod, v1)
            all_metrics.append({
                'pod_name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'metrics': metrics
            })
        return jsonify(all_metrics)
    except Exception as e:
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

# Register the LLaMA blueprint if available
if llama_available:
    app.register_blueprint(llama_bp)
    print("LLaMA API routes registered successfully")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)