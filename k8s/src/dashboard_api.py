from flask import Flask, jsonify, request
from flask_cors import CORS
from kubernetes import client, config
import sys
import os
import logging
import random
from datetime import datetime, timedelta

# Add the parent directory to the Python path to import other modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from fetch_metrics import fetch_metrics
from k8s.backend.k8s_client_utils import (
    initialize_kubernetes_client,
    get_pod_info,
    get_node_info,
    get_deployment_info,
    get_service_info,
    get_namespace_info,
    get_cluster_info
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    stream=sys.stdout
)
logger = logging.getLogger("dashboard-api")

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load Kubernetes configuration
try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()
    logger.info("Successfully loaded Kubernetes configuration")
except Exception as e:
    logger.error(f"Failed to load Kubernetes configuration: {e}")
    logger.warning("API will run in mock mode with simulated data")

# Helper function to generate mock data for development
def generate_mock_data():
    return {
        "mock": True,
        "timestamp": datetime.now().isoformat()
    }

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/overview', methods=['GET'])
def get_overview():
    try:
        cluster_info = get_cluster_info()
        
        # Get pod statistics
        pods = get_pod_info()
        total_pods = len(pods)
        running_pods = sum(1 for pod in pods if pod['status'] == 'Running')
        
        # Get node statistics
        nodes = get_node_info()
        total_nodes = len(nodes)
        ready_nodes = sum(1 for node in nodes if node.get('status', {}).get('Ready', {}).get('status') == 'True')
        
        # Get deployment statistics
        deployments = get_deployment_info()
        total_deployments = len(deployments)
        
        # Get service statistics
        services = get_service_info()
        total_services = len(services)
        
        # Generate some mock anomaly and remediation counts
        anomaly_count = random.randint(0, 5)
        remediation_count = random.randint(0, anomaly_count)
        
        return jsonify({
            "cluster": {
                "name": "minikube" if cluster_info.get("is_minikube") else "kubernetes-cluster",
                "version": "v1.27.3",  # This would come from the actual cluster in production
                "status": "healthy"
            },
            "resources": {
                "nodes": {
                    "total": total_nodes,
                    "ready": ready_nodes
                },
                "pods": {
                    "total": total_pods,
                    "running": running_pods
                },
                "deployments": total_deployments,
                "services": total_services
            },
            "anomalies": {
                "total": anomaly_count,
                "critical": random.randint(0, anomaly_count)
            },
            "remediations": {
                "total": remediation_count,
                "automated": random.randint(0, remediation_count),
                "manual": random.randint(0, remediation_count)
            },
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Error getting overview data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pods', methods=['GET'])
def get_pods():
    try:
        namespace = request.args.get('namespace', 'default')
        pods_data = get_pod_info(namespace)
        
        # Enhance pod data with anomaly detection (mock for now)
        for pod in pods_data:
            # Randomly mark some pods as having anomalies for demonstration
            pod['isAnomaly'] = random.random() < 0.2
            pod['anomalyScore'] = random.uniform(0, 1) if pod['isAnomaly'] else 0
            pod['cpuUsage'] = f"{random.uniform(0, 100):.2f}%"
            pod['memoryUsage'] = f"{random.uniform(0, 100):.2f}%"
        
        # Calculate summary statistics
        total_pods = len(pods_data)
        anomaly_detected_pods = sum(1 for pod in pods_data if pod.get('isAnomaly'))
        remediated_pods = random.randint(0, anomaly_detected_pods)
        
        return jsonify({
            "pods": pods_data,
            "totalPods": total_pods,
            "anomalyDetectedPods": anomaly_detected_pods,
            "remediatedPods": remediated_pods
        })
    except Exception as e:
        logger.error(f"Error getting pods data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    try:
        nodes_data = get_node_info()
        
        # Enhance node data with usage metrics (mock for now)
        for node in nodes_data:
            node['cpu'] = f"{random.uniform(0, 100):.2f}%"
            node['memory'] = f"{random.uniform(0, 100):.2f}%"
            node['disk'] = f"{random.uniform(0, 100):.2f}%"
            node['network'] = f"{random.randint(1, 100)} MB/s"
        
        return jsonify({"nodes": nodes_data})
    except Exception as e:
        logger.error(f"Error getting nodes data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    try:
        # Get node metrics
        nodes_data = get_node_info()
        node_metrics = []
        
        for node in nodes_data:
            node_metrics.append({
                "name": node.get('name', 'unknown'),
                "cpu": f"{random.uniform(0, 100):.2f}%",
                "memory": f"{random.uniform(0, 100):.2f}%",
                "disk": f"{random.uniform(0, 100):.2f}%",
                "network": f"{random.randint(1, 100)} MB/s"
            })
        
        # Generate historical metrics for charts
        historical_metrics = []
        now = datetime.now()
        
        for i in range(8):  # Last 8 months
            month = now - timedelta(days=30 * i)
            historical_metrics.append({
                "month": month.strftime("%b"),
                "cpu_usage": random.uniform(20, 80),
                "memory_usage": random.uniform(30, 90),
                "pod_count": random.randint(10, 50)
            })
        
        return jsonify({
            "nodes": node_metrics,
            "historical": historical_metrics
        })
    except Exception as e:
        logger.error(f"Error getting metrics data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/anomalies', methods=['GET'])
def get_anomalies():
    try:
        # Generate mock anomalies for demonstration
        anomaly_types = [
            "High CPU Usage", "Memory Leak", "Disk Space Low", 
            "Network Latency", "Pod Crash Loop", "Container Restart"
        ]
        severity_levels = ["Critical", "Warning", "Info"]
        status_options = ["New", "In Progress", "Resolved"]
        
        anomalies = []
        for i in range(random.randint(5, 15)):
            anomaly_type = random.choice(anomaly_types)
            severity = random.choice(severity_levels)
            status = random.choice(status_options)
            
            # Create a timestamp within the last 24 hours
            hours_ago = random.randint(0, 24)
            timestamp = datetime.now() - timedelta(hours=hours_ago)
            
            anomalies.append({
                "id": f"anomaly-{i+1}",
                "type": anomaly_type,
                "severity": severity,
                "status": status,
                "timestamp": timestamp.isoformat(),
                "resource": {
                    "kind": "Pod" if random.random() < 0.7 else "Node",
                    "name": f"resource-{random.randint(1, 20)}",
                    "namespace": "default"
                },
                "description": f"Detected {anomaly_type.lower()} in {severity.lower()} state",
                "metrics": {
                    "value": random.uniform(50, 100) if severity == "Critical" else random.uniform(20, 50),
                    "threshold": 80 if severity == "Critical" else 50
                },
                "remediation_available": random.random() < 0.7
            })
        
        return jsonify({"anomalies": anomalies})
    except Exception as e:
        logger.error(f"Error getting anomalies data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/remediations', methods=['GET'])
def get_remediations():
    try:
        # Generate mock remediations for demonstration
        remediation_types = [
            "Scale Up Deployment", "Restart Pod", "Increase Resource Limits",
            "Clear Cache", "Redeploy Service", "Drain Node"
        ]
        status_options = ["Pending", "In Progress", "Completed", "Failed"]
        
        remediations = []
        for i in range(random.randint(3, 10)):
            remediation_type = random.choice(remediation_types)
            status = random.choice(status_options)
            
            # Create a timestamp within the last 24 hours
            hours_ago = random.randint(0, 24)
            timestamp = datetime.now() - timedelta(hours=hours_ago)
            
            remediations.append({
                "id": f"remediation-{i+1}",
                "type": remediation_type,
                "status": status,
                "timestamp": timestamp.isoformat(),
                "target_resource": f"{random.choice(['pod', 'deployment', 'node'])}/resource-{random.randint(1, 20)}",
                "description": f"Perform {remediation_type.lower()} to resolve issue",
                "suggested_by": "Koda" if random.random() < 0.8 else "User",
                "success_probability": random.uniform(0.5, 0.95) if status == "Pending" else None,
                "execution_time": random.randint(5, 120) if status in ["Completed", "Failed"] else None
            })
        
        return jsonify({"remediations": remediations})
    except Exception as e:
        logger.error(f"Error getting remediations data: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/insights', methods=['GET'])
def get_insights():
    try:
        # Generate mock insights for demonstration
        insight_types = [
            "Resource Optimization", "Performance Improvement", "Reliability Enhancement",
            "Cost Reduction", "Security Recommendation", "Best Practice"
        ]
        
        insights = []
        for i in range(random.randint(3, 8)):
            insight_type = random.choice(insight_types)
            
            # Create a timestamp within the last week
            days_ago = random.randint(0, 7)
            timestamp = datetime.now() - timedelta(days=days_ago)
            
            insights.append({
                "id": f"insight-{i+1}",
                "type": insight_type,
                "title": f"{insight_type} Opportunity",
                "description": f"Analysis suggests potential for {insight_type.lower()}",
                "timestamp": timestamp.isoformat(),
                "impact": random.choice(["High", "Medium", "Low"]),
                "target_resources": [
                    {"kind": "Deployment", "name": f"deployment-{random.randint(1, 10)}"},
                    {"kind": "Pod", "name": f"pod-{random.randint(1, 20)}"}
                ],
                "recommendation": f"Consider implementing {insight_type.lower()} strategy",
                "estimated_benefit": f"{random.randint(10, 40)}% improvement"
            })
        
        return jsonify({"insights": insights})
    except Exception as e:
        logger.error(f"Error getting insights data: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001, debug=True)