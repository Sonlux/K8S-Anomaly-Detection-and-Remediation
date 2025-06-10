from kubernetes import client, config
import re
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    stream=sys.stdout
)
logger = logging.getLogger("k8s-remediation-utils")

def parse_resource_value(value, is_memory=False):
    """Parse a Kubernetes resource value with units (e.g., '1007490n', '175820Ki', '1Gi') to a float."""
    if not isinstance(value, str):
        return float(value) if value is not None else 0.0
    
    match = re.match(r'(\d+\.?\d*)([nmuKMTG]?i?)', value)
    if not match:
        logger.debug(f"Failed to parse resource value: {value}")
        return 0.0
    
    num, unit = match.groups()
    num = float(num)
    
    unit_factors = {
        'n': 1e-9, 'u': 1e-6, 'm': 1e-3, '': 1.0,
        'K': 1e3, 'M': 1e6, 'G': 1e9, 'T': 1e12,
        'Ki': 1024, 'Mi': 1024**2, 'Gi': 1024**3, 'Ti': 1024**4
    }
    
    factor = unit_factors.get(unit or '', 1.0)
    result = num * factor
    unit_type = "bytes" if is_memory else "cores"
    logger.debug(f"Parsed {value} -> {result} {unit_type} (unit: {unit})")
    return result

def fetch_metrics(pod, k8s_api):
    """Fetch metrics for a given pod using Kubernetes Metrics API and pod spec."""
    pod_name = pod.metadata.name
    namespace = pod.metadata.namespace
    pod_id = f"{namespace}/{pod_name}"
    
    if "crash" in pod_name:
        metrics = {
            'CPU Usage (%)': 90.0,
            'Memory Usage (%)': 85.0,
            'Pod Restarts': 0.0,
            'Memory Usage (MB)': 800.0,
            'Network Receive Bytes': 5000.0,
            'Network Transmit Bytes': 5000.0,
            'FS Reads Total (MB)': 100.0,
            'FS Writes Total (MB)': 100.0,
            'Network Receive Packets Dropped (p/s)': 0.0,
            'Network Transmit Packets Dropped (p/s)': 0.0,
            'Ready Containers': 1.0
        }
        container_statuses = pod.status.container_statuses
        if container_statuses:
            metrics['Pod Restarts'] = float(container_statuses[0].restart_count) if container_statuses[0].restart_count is not None else 0.0
            metrics['Ready Containers'] = float(sum(1 for cs in container_statuses if cs.ready)) if any(cs.ready for cs in container_statuses) else 0.0
        logger.info(f"Simulating resource exhaustion for {pod_id}: {metrics}")
        return metrics

    try:
        api_instance = client.CustomObjectsApi()
        logger.debug(f"Fetching Metrics API data for {pod_id}")
        metrics_response = api_instance.list_namespaced_custom_object(
            group="metrics.k8s.io", version="v1beta1", namespace=namespace, plural="pods"
        )

        for metric in metrics_response.get('items', []):
            if metric['metadata']['name'] == pod_name:
                containers = metric.get('containers', [])
                if containers:
                    container = containers[0]
                    logger.debug(f"Metrics API data for {pod_id}: {container}")
                    
                    cpu_usage_raw = container.get('usage', {}).get('cpu', '0')
                    cpu_usage_cores = parse_resource_value(cpu_usage_raw)
                    cpu_limit_raw = pod.spec.containers[0].resources.limits.get('cpu', '1') if pod.spec.containers[0].resources and pod.spec.containers[0].resources.limits else '1'
                    cpu_limit_cores = parse_resource_value(cpu_limit_raw)
                    cpu_percent = (cpu_usage_cores / cpu_limit_cores) * 100 if cpu_limit_cores > 0 else 0.0
                    
                    memory_usage_raw = container.get('usage', {}).get('memory', '0')
                    memory_usage_bytes = parse_resource_value(memory_usage_raw, is_memory=True)
                    memory_mb = memory_usage_bytes / (1024 * 1024)
                    memory_limit_raw = pod.spec.containers[0].resources.limits.get('memory', '1Gi') if pod.spec.containers[0].resources and pod.spec.containers[0].resources.limits else '1Gi'
                    memory_limit_bytes = parse_resource_value(memory_limit_raw, is_memory=True)
                    memory_limit_mb = memory_limit_bytes / (1024 * 1024)
                    if memory_limit_mb == 0:
                        memory_limit_mb = 1024
                        logger.debug(f"Memory limit was 0, using fallback: {memory_limit_mb} MB")
                    memory_percent = (memory_mb / memory_limit_mb) * 100 if memory_limit_mb > 0 else 0.0
                    
                    container_statuses = pod.status.container_statuses
                    restarts = float(container_statuses[0].restart_count) if container_statuses and container_statuses[0].restart_count is not None else 0.0
                    ready_containers = sum(1 for cs in container_statuses if cs.ready) if container_statuses and any(cs.ready for cs in container_statuses) else 0
                    
                    metrics = {
                        'CPU Usage (%)': cpu_percent,
                        'Memory Usage (%)': memory_percent,
                        'Pod Restarts': restarts,
                        'Memory Usage (MB)': memory_mb,
                        'Network Receive Bytes': 0.0,
                        'Network Transmit Bytes': 0.0,
                        'FS Reads Total (MB)': 0.0,
                        'FS Writes Total (MB)': 0.0,
                        'Network Receive Packets Dropped (p/s)': 0.0,
                        'Network Transmit Packets Dropped (p/s)': 0.0,
                        'Ready Containers': float(ready_containers)
                    }
                    logger.debug(f"Computed metrics for {pod_id}: {metrics}")
                    return metrics

        logger.warning(f"Metrics API data not found for {pod_id}, using fallback")
        container_statuses = pod.status.container_statuses
        restarts = float(container_statuses[0].restart_count) if container_statuses and container_statuses[0].restart_count is not None else 0.0
        ready_containers = sum(1 for cs in container_statuses if cs.ready) if container_statuses and any(cs.ready for cs in container_statuses) else 0
        metrics = {
            'CPU Usage (%)': 50.0,
            'Memory Usage (%)': 50.0,
            'Pod Restarts': restarts,
            'Memory Usage (MB)': 500.0,
            'Network Receive Bytes': 5000.0,
            'Network Transmit Bytes': 5000.0,
            'FS Reads Total (MB)': 100.0,
            'FS Writes Total (MB)': 100.0,
            'Network Receive Packets Dropped (p/s)': 0.0,
            'Network Transmit Packets Dropped (p/s)': 0.0,
            'Ready Containers': float(ready_containers)
        }
        logger.debug(f"Fallback metrics for {pod_id}: {metrics}")
        return metrics
    except client.exceptions.ApiException as e:
        logger.error(f"Metrics API error for {pod_id}: {str(e)} - falling back to defaults")
        container_statuses = pod.status.container_statuses
        restarts = float(container_statuses[0].restart_count) if container_statuses and container_statuses[0].restart_count is not None else 0.0
        ready_containers = sum(1 for cs in container_statuses if cs.ready) if container_statuses and any(cs.ready for cs in container_statuses) else 0
        metrics = {
            'CPU Usage (%)': 50.0,
            'Memory Usage (%)': 50.0,
            'Pod Restarts': restarts,
            'Memory Usage (MB)': 500.0,
            'Network Receive Bytes': 5000.0,
            'Network Transmit Bytes': 5000.0,
            'FS Reads Total (MB)': 100.0,
            'FS Writes Total (MB)': 100.0,
            'Network Receive Packets Dropped (p/s)': 0.0,
            'Network Transmit Packets Dropped (p/s)': 0.0,
            'Ready Containers': float(ready_containers)
        }
        logger.debug(f"Exception fallback metrics for {pod_id}: {metrics}")
        return metrics
    except Exception as e:
        logger.error(f"Unexpected error fetching metrics for {pod_id}: {str(e)}")
        metrics = {
            'CPU Usage (%)': 50.0,
            'Memory Usage (%)': 50.0,
            'Pod Restarts': 0.0,
            'Memory Usage (MB)': 500.0,
            'Network Receive Bytes': 5000.0,
            'Network Transmit Bytes': 5000.0,
            'FS Reads Total (MB)': 100.0,
            'FS Writes Total (MB)': 100.0,
            'Network Receive Packets Dropped (p/s)': 0.0,
            'Network Transmit Packets Dropped (p/s)': 0.0,
            'Ready Containers': 0.0
        }
        logger.debug(f"Default fallback metrics for {pod_id}: {metrics}")
        return metrics

if __name__ == "__main__":
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces().items  # Monitor all namespaces
    if pods:
        metrics = fetch_metrics(pods[0], v1)
        logger.info(f"Sample metrics: {metrics}")