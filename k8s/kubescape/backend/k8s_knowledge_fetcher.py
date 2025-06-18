#!/usr/bin/env python3

from datetime import datetime
import logging
from typing import List, Dict, Any
from k8s_client_utils import (
    get_pod_info,
    get_node_info,
    get_deployment_info,
    get_service_info,
    get_namespace_info,
    get_cluster_info,
    get_pod_logs,
    initialize_kubernetes_client
)

logger = logging.getLogger("k8s-knowledge-fetcher")

def fetch_k8s_info(query: str) -> str:
    query = query.lower()
    logger.info(f"fetch_k8s_info called with query: {query}")
    try:
        if not initialize_kubernetes_client():
            logger.warning("Could not initialize k8s client.")
            return "❌ Unable to connect to Kubernetes cluster. Please ensure Minikube is running."

        # Pods
        if "pod" in query or "pods" in query:
            namespace = 'default'
            # Try to extract namespace from query
            if "all namespaces" in query or "--all-namespaces" in query or ('pods' in query and 'namespace' not in query):
                # Show all pods in all namespaces by default
                from kubernetes import client
                core_api = client.CoreV1Api()
                pods = core_api.list_pod_for_all_namespaces().items
                if not pods:
                    return "❌ No pods found in any namespace."
                result = f"📦 **Pods in all namespaces:**\n\n"
                for pod in pods:
                    status_emoji = "✅" if pod.status.phase == 'Running' else "⚠️" if pod.status.phase == 'Pending' else "❌"
                    result += f"{status_emoji} **{pod.metadata.name}** (Namespace: {pod.metadata.namespace})\n"
                    result += f"   Status: {pod.status.phase}\n"
                    result += f"   Node: {pod.spec.node_name}\n"
                    result += f"   IP: {pod.status.pod_ip}\n"
                    if pod.status.container_statuses:
                        result += "   Containers:\n"
                        for container in pod.status.container_statuses:
                            ready_emoji = "✅" if container.ready else "❌"
                            result += f"     {ready_emoji} {container.name} (Restarts: {container.restart_count})\n"
                    result += "\n"
                return result
            else:
                namespace = 'default'
                if 'namespace' in query:
                    ns_split = query.split('namespace')[-1].strip().split()
                    if ns_split:
                        namespace = ns_split[0]
                pods = get_pod_info(namespace)
                if not pods:
                    return f"❌ No pods found in namespace '{namespace}'"
                result = f"📦 **Pods in '{namespace}' namespace:**\n\n"
                for pod in pods:
                    status_emoji = "✅" if pod['status'] == 'Running' else "⚠️" if pod['status'] == 'Pending' else "❌"
                    result += f"{status_emoji} **{pod['name']}**\n"
                    result += f"   Status: {pod['status']}\n"
                    result += f"   Node: {pod.get('node', 'Unknown')}\n"
                    result += f"   IP: {pod.get('ip', 'Unknown')}\n"
                    if pod.get('containers'):
                        result += "   Containers:\n"
                        for container in pod['containers']:
                            ready_emoji = "✅" if container.get('ready') else "❌"
                            result += f"     {ready_emoji} {container.get('name', 'Unknown')} (Restarts: {container.get('restart_count', 0)})\n"
                    result += "\n"
                return result

        # Nodes
        if "node" in query or "nodes" in query:
            return fetch_node_info()

        # Deployments
        if "deployment" in query or "deployments" in query:
            namespace = 'default'
            if "namespace" in query:
                ns_split = query.split('namespace')[-1].strip().split()
                if ns_split:
                    namespace = ns_split[0]
            return fetch_deployment_info(namespace)

        # Services
        if "service" in query or "services" in query:
            namespace = 'default'
            if "namespace" in query:
                ns_split = query.split('namespace')[-1].strip().split()
                if ns_split:
                    namespace = ns_split[0]
            return fetch_service_info(namespace)

        # Namespaces
        if "namespace" in query or "namespaces" in query:
            return fetch_namespace_info()

        # Logs
        if "log" in query or "logs" in query:
            # Try to extract pod name and namespace
            import re
            pod_name = None
            namespace = 'default'
            pod_match = re.search(r'logs?\s+([^\s]+)', query)
            if pod_match:
                pod_name = pod_match.group(1)
            ns_match = re.search(r'namespace\s+([^\s]+)', query)
            if ns_match:
                namespace = ns_match.group(1)
            if pod_name:
                return fetch_pod_logs(pod_name, namespace)
            else:
                return "❌ Please specify a pod name to fetch logs."

        # Cluster status/overview
        if any(word in query for word in ['status', 'cluster', 'overview', 'health']):
            return fetch_cluster_info()

        # Default: cluster info
        logger.info("Falling through to default: cluster overview")
        return fetch_cluster_info()

    except Exception as e:
        logger.error(f"Error in fetch_k8s_info: {e}")
        return f"❌ Error fetching Kubernetes information: {str(e)}"

def fetch_pod_info(namespace: str = 'default') -> str:
    pods = get_pod_info(namespace)
    if not pods:
        return f"❌ No pods found in namespace '{namespace}'"
    result = f"📦 **Pods in '{namespace}' namespace:**\n\n"
    for pod in pods:
        status_emoji = "✅" if pod['status'] == 'Running' else "⚠️" if pod['status'] == 'Pending' else "❌"
        result += f"{status_emoji} **{pod['name']}**\n"
        result += f"   Status: {pod['status']}\n"
        result += f"   Node: {pod.get('node', 'Unknown')}\n"
        result += f"   IP: {pod.get('ip', 'Unknown')}\n"
        if pod.get('containers'):
            result += "   Containers:\n"
            for container in pod['containers']:
                ready_emoji = "✅" if container.get('ready') else "❌"
                result += f"     {ready_emoji} {container.get('name', 'Unknown')} (Restarts: {container.get('restart_count', 0)})\n"
        result += "\n"
    return result

def fetch_pod_info_all_namespaces() -> str:
    try:
        from kubernetes import client
        core_api = client.CoreV1Api()
        pods = core_api.list_pod_for_all_namespaces().items
        if not pods:
            return "❌ No pods found in any namespace."
        result = f"📦 **Pods in all namespaces:**\n\n"
        for pod in pods:
            status_emoji = "✅" if pod.status.phase == 'Running' else "⚠️" if pod.status.phase == 'Pending' else "❌"
            result += f"{status_emoji} **{pod.metadata.name}** (Namespace: {pod.metadata.namespace})\n"
            result += f"   Status: {pod.status.phase}\n"
            result += f"   Node: {pod.spec.node_name}\n"
            result += f"   IP: {pod.status.pod_ip}\n"
            if pod.status.container_statuses:
                result += "   Containers:\n"
                for container in pod.status.container_statuses:
                    ready_emoji = "✅" if container.ready else "❌"
                    result += f"     {ready_emoji} {container.name} (Restarts: {container.restart_count})\n"
            result += "\n"
        return result
    except Exception as e:
        logger.error(f"Error fetching all pods: {e}")
        return f"❌ Error fetching all pods: {str(e)}"

def fetch_node_info() -> str:
    nodes = get_node_info()
    if not nodes:
        return "❌ No nodes found in the cluster."
    result = "🖥️ **Node Information:**\n\n"
    for node in nodes:
        result += f"• Name: {node['name']}\n"
        result += f"  Status: {node['status']}\n"
        result += f"  Capacity: {node['capacity']}\n"
        result += f"  Allocatable: {node['allocatable']}\n\n"
    return result

def fetch_deployment_info(namespace: str = 'default') -> str:
    deployments = get_deployment_info(namespace)
    if not deployments:
        return f"❌ No deployments found in namespace '{namespace}'"
    result = f"📦 **Deployments in '{namespace}' namespace:**\n\n"
    for dep in deployments:
        result += f"**{dep['name']}**\n"
        result += f"  Replicas: {dep.get('replicas', 0)}\n"
        result += f"  Available: {dep.get('available_replicas', 0)}\n"
        result += f"  Ready: {dep.get('ready_replicas', 0)}\n"
        result += f"  Strategy: {dep.get('strategy', 'Unknown')}\n"
        if dep.get('containers'):
            result += "  Containers:\n"
            for c in dep['containers']:
                result += f"    - {c['name']} (Image: {c['image']})\n"
        result += "\n"
    return result

def fetch_service_info(namespace: str = 'default') -> str:
    services = get_service_info(namespace)
    if not services:
        return f"❌ No services found in namespace '{namespace}'"
    result = f"🛠️ **Services in '{namespace}' namespace:**\n\n"
    for svc in services:
        result += f"**{svc['name']}**\n"
        result += f"  Type: {svc.get('type', 'Unknown')}\n"
        result += f"  Cluster IP: {svc.get('cluster_ip', 'Unknown')}\n"
        result += f"  Selector: {svc.get('selector', {})}\n"
        if svc.get('ports'):
            result += "  Ports:\n"
            for port in svc['ports']:
                result += f"    - {port}\n"
        result += "\n"
    return result

def fetch_namespace_info() -> str:
    namespaces = get_namespace_info()
    if not namespaces:
        return "❌ No namespaces found in the cluster."
    result = "📂 **Namespaces:**\n\n"
    for ns in namespaces:
        result += f"• Name: {ns['name']}\n"
        result += f"  Status: {ns['status']}\n"
        result += f"  Labels: {ns.get('labels', {})}\n\n"
    return result

def fetch_pod_logs(pod_name: str, namespace: str = 'default', container: str = None, tail_lines: int = 100) -> str:
    logs = get_pod_logs(pod_name, namespace, container, tail_lines)
    if not logs or "Error" in logs:
        return f"❌ Could not fetch logs for pod '{pod_name}' in namespace '{namespace}'."
    return f"📄 **Logs for pod '{pod_name}' in namespace '{namespace}':**\n\n{logs}"

def fetch_cluster_info() -> str:
    cluster = get_cluster_info()
    if cluster.get('error'):
        return f"❌ Error: {cluster['error']}"
    return "\n".join(f"{k.replace('_', ' ').capitalize()}: {v}" for k, v in cluster.items())

def is_minikube_available() -> bool:
    try:
        cluster_info = get_cluster_info()
        return cluster_info.get("is_minikube", False)
    except Exception:
        return False
