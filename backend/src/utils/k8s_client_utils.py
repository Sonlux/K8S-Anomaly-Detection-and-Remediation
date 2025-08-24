from kubernetes import client, config
import logging
from datetime import datetime

logger = logging.getLogger("k8s-client-utils")

def initialize_kubernetes_client():
    try:
        config.load_kube_config()
        logger.info("Loaded kubeconfig successfully")
        
        # Test the connection with a simple API call
        v1 = client.CoreV1Api()
        v1.list_namespace(limit=1)  # Simple test call
        logger.info("Successfully connected to Kubernetes cluster")
        
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Kubernetes client: {e}")
        logger.error("If using Minikube, ensure it is running with: minikube start")
        return False

def get_available_api_versions():
    """Get available API versions. Returns common versions if discovery fails."""
    try:
        apis_api = client.ApisApi()
        group_list = apis_api.get_api_versions()
        
        version_list = ["v1"]  # Always include core API
        for group in group_list.groups:
            if hasattr(group, 'preferred_version') and group.preferred_version:
                version_list.append(group.preferred_version.group_version)
        
        return sorted(set(version_list))
    except Exception as e:
        logger.warning(f"Could not retrieve API versions, using defaults: {e}")
        return ["v1", "apps/v1", "extensions/v1beta1", "networking.k8s.io/v1"]

def get_pod_info(namespace='default'):
    # Initialize client first
    if not initialize_kubernetes_client():
        return []
        
    try:
        core_api = client.CoreV1Api()
        pods = core_api.list_namespaced_pod(namespace=namespace).items
        pod_data = []
        
        for pod in pods:
            containers = []
            for c in pod.status.container_statuses or []:
                container_info = {
                    'name': c.name,
                    'image': c.image,
                    'ready': c.ready,
                    'restart_count': c.restart_count,
                    'state': list(c.state.to_dict().keys())[0] if c.state else None,
                    'reason': getattr(c.state.waiting, 'reason', '') if c.state and c.state.waiting else ''
                }
                containers.append(container_info)
                
            pod_data.append({
                'name': pod.metadata.name,
                'namespace': pod.metadata.namespace,
                'status': pod.status.phase,
                'node': pod.spec.node_name,
                'ip': pod.status.pod_ip,
                'containers': containers
            })
        
        return pod_data
    except Exception as e:
        logger.error(f"Error getting pod info: {e}")
        return []

def get_cluster_info():
    try:
        # First ensure the client is properly initialized
        if not initialize_kubernetes_client():
            return {"is_minikube": False, "error": "Failed to initialize Kubernetes client"}
        
        # Use the proper Kubernetes API clients
        version_api = client.VersionApi()
        version_info = version_api.get_code()
        
        core_api = client.CoreV1Api()
        namespaces = core_api.list_namespace().items
        pods = core_api.list_pod_for_all_namespaces().items
        nodes = core_api.list_node().items

        # Use the robust detection function here!
        is_mk = is_minikube_cluster()

        return {
            "is_minikube": is_mk,
            "node_count": len(nodes),
            "namespace_count": len(namespaces),
            "pod_count": len(pods),
            "api_versions": get_available_api_versions(),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to retrieve cluster info: {e}")
        return {
            "is_minikube": False,
            "error": str(e)
        }


def get_node_info():
    if not initialize_kubernetes_client():
        return []
        
    try:
        core_api = client.CoreV1Api()
        nodes = core_api.list_node().items
        node_data = []
        
        for node in nodes:
            node_data.append({
                'name': node.metadata.name,
                'status': {cond.type: {'status': cond.status, 'reason': getattr(cond, 'reason', '')}
                          for cond in node.status.conditions},
                'capacity': node.status.capacity,
                'allocatable': node.status.allocatable
            })
        return node_data
    except Exception as e:
        logger.error(f"Error getting node info: {e}")
        return []

def get_deployment_info(namespace='default'):
    if not initialize_kubernetes_client():
        return []
        
    try:
        apps_api = client.AppsV1Api()
        deployments = apps_api.list_namespaced_deployment(namespace=namespace).items
        data = []
        
        for dep in deployments:
            data.append({
                'name': dep.metadata.name,
                'namespace': dep.metadata.namespace,
                'replicas': dep.spec.replicas,
                'available_replicas': dep.status.available_replicas,
                'ready_replicas': dep.status.ready_replicas,
                'strategy': dep.spec.strategy.type,
                'containers': [{
                    'name': c.name,
                    'image': c.image,
                    'resources': c.resources.to_dict()
                } for c in dep.spec.template.spec.containers]
            })
        return data
    except Exception as e:
        logger.error(f"Error getting deployment info: {e}")
        return []

def get_service_info(namespace='default'):
    if not initialize_kubernetes_client():
        return []
        
    try:
        core_api = client.CoreV1Api()
        services = core_api.list_namespaced_service(namespace=namespace).items
        data = []
        
        for svc in services:
            data.append({
                'name': svc.metadata.name,
                'namespace': svc.metadata.namespace,
                'type': svc.spec.type,
                'cluster_ip': svc.spec.cluster_ip,
                'selector': svc.spec.selector or {},
                'ports': [p.to_dict() for p in svc.spec.ports]
            })
        return data
    except Exception as e:
        logger.error(f"Error getting service info: {e}")
        return []

def get_namespace_info():
    if not initialize_kubernetes_client():
        return []
        
    try:
        core_api = client.CoreV1Api()
        namespaces = core_api.list_namespace().items
        return [{
            'name': ns.metadata.name,
            'status': ns.status.phase,
            'labels': ns.metadata.labels or {}
        } for ns in namespaces]
    except Exception as e:
        logger.error(f"Error getting namespace info: {e}")
        return []

def get_pod_logs(pod_name, namespace='default', container=None, tail_lines=100):
    if not initialize_kubernetes_client():
        return "Failed to initialize Kubernetes client"
        
    try:
        core_api = client.CoreV1Api()
        return core_api.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            container=container,
            tail_lines=tail_lines
        )
    except Exception as e:
        logger.error(f"Error getting pod logs: {e}")
        return f"Error getting logs: {e}"

def is_minikube_cluster():
    """
    Robustly detect if the current cluster is a Minikube cluster.
    Checks node names, node labels, and version string.
    """
    try:
        from kubernetes import client
        core_api = client.CoreV1Api()
        nodes = core_api.list_node().items
        for node in nodes:
            if node.metadata.name == "minikube":
                return True
            if node.metadata.labels and any("minikube" in k for k in node.metadata.labels.keys()):
                return True
        # Fallback to version string
        version_api = client.VersionApi()
        version_info = version_api.get_code()
        if "minikube" in version_info.git_version.lower():
            return True
    except Exception as e:
        logger.error(f"Error detecting minikube: {e}")
    return False

# For backward compatibility with other imports
is_minikube_available = is_minikube_cluster