#!/usr/bin/env python3
"""
Kubernetes Remediation Dashboard Agent

This module provides remediation execution capabilities for the visualization dashboard.
Exposes an API for executing remediation actions directly from the dashboard.
"""

import os
import sys
import argparse
import logging
import json
import traceback
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('remediation_dashboard_agent.log')
    ]
)
logger = logging.getLogger("remediation-dashboard-agent")

# Add parent directory to path for imports
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import from the multi-agent system
try:
    from kubernetes import client, config, watch
    HAS_K8S = True
except ImportError:
    logger.warning("Kubernetes client not installed. Running in simulation mode.")
    HAS_K8S = False

# Initialize Kubernetes client if available
if HAS_K8S:
    try:
        config.load_kube_config()
        logger.info("Loaded Kubernetes config from default location")
        k8s_core_api = client.CoreV1Api()
        k8s_apps_api = client.AppsV1Api()
    except Exception as e:
        try:
            config.load_incluster_config()
            logger.info("Loaded in-cluster Kubernetes config")
            k8s_core_api = client.CoreV1Api()
            k8s_apps_api = client.AppsV1Api()
        except Exception as e2:
            logger.error(f"Failed to load Kubernetes configuration: {e}, {e2}")
            HAS_K8S = False

def restart_pod(pod_name: str, namespace: str = "default") -> Tuple[bool, str]:
    """Restart a pod by deleting it (controller will recreate)
    
    Args:
        pod_name: Name of the pod to restart
        namespace: Kubernetes namespace where the pod is located
        
    Returns:
        Tuple of (success, message)
    """
    if not HAS_K8S:
        return True, f"[SIMULATION] Would restart pod {namespace}/{pod_name}"
        
    try:
        # Get pod info first to check if it exists
        pod = k8s_core_api.read_namespaced_pod(name=pod_name, namespace=namespace)
        logger.info(f"Found pod {namespace}/{pod_name}, status: {pod.status.phase}")
        
        # Delete the pod
        delete_options = client.V1DeleteOptions()
        k8s_core_api.delete_namespaced_pod(name=pod_name, namespace=namespace, body=delete_options)
        logger.info(f"Successfully deleted pod {namespace}/{pod_name}")
        
        return True, f"Successfully restarted pod {namespace}/{pod_name}"
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return False, f"Pod {namespace}/{pod_name} not found"
        else:
            logger.error(f"Error restarting pod {namespace}/{pod_name}: {e}")
            return False, f"API error: {e}"
    except Exception as e:
        logger.error(f"Error restarting pod {namespace}/{pod_name}: {e}")
        return False, f"Error: {str(e)}"

def restart_deployment(deployment_name: str, namespace: str = "default") -> Tuple[bool, str]:
    """Restart a deployment by patching it with a restart annotation
    
    Args:
        deployment_name: Name of the deployment to restart
        namespace: Kubernetes namespace where the deployment is located
        
    Returns:
        Tuple of (success, message)
    """
    if not HAS_K8S:
        return True, f"[SIMULATION] Would restart deployment {namespace}/{deployment_name}"
    
    try:
        # Check if deployment exists
        deployment = k8s_apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        logger.info(f"Found deployment {namespace}/{deployment_name}")
        
        # Patch it with a restart annotation (causes rolling restart)
        body = {
            "spec": {
                "template": {
                    "metadata": {
                        "annotations": {
                            "kubectl.kubernetes.io/restartedAt": f"{datetime.now().isoformat()}"
                        }
                    }
                }
            }
        }
        
        k8s_apps_api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=body
        )
        
        logger.info(f"Successfully restarted deployment {namespace}/{deployment_name}")
        return True, f"Successfully restarted deployment {namespace}/{deployment_name}"
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return False, f"Deployment {namespace}/{deployment_name} not found"
        else:
            logger.error(f"Error restarting deployment {namespace}/{deployment_name}: {e}")
            return False, f"API error: {e}"
    except Exception as e:
        logger.error(f"Error restarting deployment {namespace}/{deployment_name}: {e}")
        return False, f"Error: {str(e)}"

def increase_memory(pod_or_deployment: str, namespace: str = "default", percent: int = 50) -> Tuple[bool, str]:
    """Increase memory allocation for a deployment
    
    Args:
        pod_or_deployment: Name of the pod or deployment to modify
        namespace: Kubernetes namespace
        percent: Percentage to increase memory by
        
    Returns:
        Tuple of (success, message)
    """
    if not HAS_K8S:
        return True, f"[SIMULATION] Would increase memory for {namespace}/{pod_or_deployment} by {percent}%"
    
    try:
        # Try to get deployment name from pod if this is a pod name
        deployment_name = pod_or_deployment
        try:
            pod = k8s_core_api.read_namespaced_pod(name=pod_or_deployment, namespace=namespace)
            # Try to find the owner reference
            for owner_ref in pod.metadata.owner_references:
                if owner_ref.kind == "ReplicaSet":
                    # Get the ReplicaSet to find the Deployment
                    rs = k8s_apps_api.read_namespaced_replica_set(name=owner_ref.name, namespace=namespace)
                    for rs_owner in rs.metadata.owner_references:
                        if rs_owner.kind == "Deployment":
                            deployment_name = rs_owner.name
                            break
                    break
        except:
            # This might be a direct deployment name, continue
            pass
            
        # Get the deployment
        deployment = k8s_apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        
        # Update memory limits (increase by specified percent)
        patched = False
        containers = deployment.spec.template.spec.containers
        
        for container in containers:
            if container.resources and container.resources.limits and "memory" in container.resources.limits:
                current_mem = container.resources.limits["memory"]
                # Parse memory value (e.g., "256Mi")
                value = ''.join(filter(str.isdigit, current_mem))
                unit = ''.join(filter(str.isalpha, current_mem))
                if not value:  # Skip if parsing failed
                    continue
                    
                new_value = int(int(value) * (1 + percent/100))
                container.resources.limits["memory"] = f"{new_value}{unit}"
                
                # Also update requests if they exist
                if container.resources.requests and "memory" in container.resources.requests:
                    req_value = ''.join(filter(str.isdigit, container.resources.requests["memory"]))
                    req_unit = ''.join(filter(str.isalpha, container.resources.requests["memory"]))
                    if req_value:  # Skip if parsing failed
                        new_req = int(int(req_value) * (1 + percent/100))
                        container.resources.requests["memory"] = f"{new_req}{req_unit}"
                
                patched = True
        
        if not patched:
            return False, f"No memory limits found to update in deployment {namespace}/{deployment_name}"
            
        # Update the deployment
        k8s_apps_api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )
        
        logger.info(f"Successfully increased memory for deployment {namespace}/{deployment_name}")
        return True, f"Successfully increased memory for deployment {namespace}/{deployment_name} by {percent}%"
    except Exception as e:
        logger.error(f"Error increasing memory: {e}")
        return False, f"Error: {str(e)}"

def increase_cpu(pod_or_deployment: str, namespace: str = "default", percent: int = 50) -> Tuple[bool, str]:
    """Increase CPU allocation for a deployment
    
    Args:
        pod_or_deployment: Name of the pod or deployment to modify
        namespace: Kubernetes namespace
        percent: Percentage to increase CPU by
        
    Returns:
        Tuple of (success, message)
    """
    if not HAS_K8S:
        return True, f"[SIMULATION] Would increase CPU for {namespace}/{pod_or_deployment} by {percent}%"
    
    try:
        # Try to get deployment name from pod if this is a pod name
        deployment_name = pod_or_deployment
        try:
            pod = k8s_core_api.read_namespaced_pod(name=pod_or_deployment, namespace=namespace)
            # Try to find the owner reference
            for owner_ref in pod.metadata.owner_references:
                if owner_ref.kind == "ReplicaSet":
                    # Get the ReplicaSet to find the Deployment
                    rs = k8s_apps_api.read_namespaced_replica_set(name=owner_ref.name, namespace=namespace)
                    for rs_owner in rs.metadata.owner_references:
                        if rs_owner.kind == "Deployment":
                            deployment_name = rs_owner.name
                            break
                    break
        except:
            # This might be a direct deployment name, continue
            pass
            
        # Get the deployment
        deployment = k8s_apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        
        # Update CPU limits (increase by specified percent)
        patched = False
        containers = deployment.spec.template.spec.containers
        
        for container in containers:
            if container.resources and container.resources.limits and "cpu" in container.resources.limits:
                current_cpu = container.resources.limits["cpu"]
                
                # Parse CPU value (e.g., "500m" or "0.5")
                if current_cpu.endswith('m'):
                    value = int(current_cpu[:-1])
                    is_millicpu = True
                else:
                    value = float(current_cpu)
                    is_millicpu = False
                    
                if is_millicpu:
                    new_value = int(value * (1 + percent/100))
                    container.resources.limits["cpu"] = f"{new_value}m"
                else:
                    new_value = value * (1 + percent/100)
                    container.resources.limits["cpu"] = f"{new_value}"
                
                # Also update requests if they exist
                if container.resources.requests and "cpu" in container.resources.requests:
                    current_cpu = container.resources.requests["cpu"]
                    if current_cpu.endswith('m'):
                        value = int(current_cpu[:-1])
                        is_millicpu = True
                    else:
                        value = float(current_cpu)
                        is_millicpu = False
                        
                    if is_millicpu:
                        new_value = int(value * (1 + percent/100))
                        container.resources.requests["cpu"] = f"{new_value}m"
                    else:
                        new_value = value * (1 + percent/100)
                        container.resources.requests["cpu"] = f"{new_value}"
                
                patched = True
        
        if not patched:
            return False, f"No CPU limits found to update in deployment {namespace}/{deployment_name}"
            
        # Update the deployment
        k8s_apps_api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )
        
        logger.info(f"Successfully increased CPU for deployment {namespace}/{deployment_name}")
        return True, f"Successfully increased CPU for deployment {namespace}/{deployment_name} by {percent}%"
    except Exception as e:
        logger.error(f"Error increasing CPU: {e}")
        return False, f"Error: {str(e)}"

def scale_deployment(deployment_name: str, namespace: str = "default", replicas: int = None) -> Tuple[bool, str]:
    """Scale a deployment to a specified number of replicas or by one
    
    Args:
        deployment_name: Name of the deployment to scale
        namespace: Kubernetes namespace
        replicas: Target number of replicas (if None, increments by 1)
        
    Returns:
        Tuple of (success, message)
    """
    if not HAS_K8S:
        return True, f"[SIMULATION] Would scale deployment {namespace}/{deployment_name}"
    
    try:
        # Get current deployment
        deployment = k8s_apps_api.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        current_replicas = deployment.spec.replicas
        
        # Determine new replica count
        if replicas is None:
            new_replicas = current_replicas + 1
        else:
            new_replicas = replicas
            
        # Update replicas
        deployment.spec.replicas = new_replicas
        
        # Update the deployment
        k8s_apps_api.patch_namespaced_deployment(
            name=deployment_name,
            namespace=namespace,
            body=deployment
        )
        
        logger.info(f"Scaled deployment {namespace}/{deployment_name} from {current_replicas} to {new_replicas} replicas")
        return True, f"Successfully scaled deployment {namespace}/{deployment_name} from {current_replicas} to {new_replicas} replicas"
    except client.exceptions.ApiException as e:
        if e.status == 404:
            return False, f"Deployment {namespace}/{deployment_name} not found"
        else:
            logger.error(f"Error scaling deployment {namespace}/{deployment_name}: {e}")
            return False, f"API error: {e}"
    except Exception as e:
        logger.error(f"Error scaling deployment {namespace}/{deployment_name}: {e}")
        return False, f"Error: {str(e)}"

def execute_remediation(pod: str, action: str, namespace: str = "default") -> Tuple[bool, str]:
    """Execute a remediation action
    
    Args:
        pod: Name of the pod to remediate
        action: Remediation action to take
        namespace: Kubernetes namespace
        
    Returns:
        Tuple of (success, message)
    """
    logger.info(f"Executing remediation action '{action}' for pod {namespace}/{pod}")
    
    try:
        if action == "restart_pod":
            return restart_pod(pod, namespace)
            
        elif action == "restart_deployment":
            # Extract deployment name from pod name (assumes pod name format: deployment-random-suffix)
            deployment_name = '-'.join(pod.split('-')[:-2]) if '-' in pod else pod
            return restart_deployment(deployment_name, namespace)
            
        elif action == "increase_memory":
            return increase_memory(pod, namespace)
            
        elif action == "increase_cpu":
            return increase_cpu(pod, namespace)
            
        elif action == "scale_deployment":
            # Extract deployment name from pod name
            deployment_name = '-'.join(pod.split('-')[:-2]) if '-' in pod else pod
            return scale_deployment(deployment_name, namespace)
            
        else:
            return False, f"Unknown remediation action: {action}"
    except Exception as e:
        logger.error(f"Error executing remediation: {e}")
        traceback.print_exc()
        return False, f"Error: {str(e)}"

def main():
    """Main function to run the remediation agent"""
    parser = argparse.ArgumentParser(description='Kubernetes Remediation Agent')
    parser.add_argument('--pod', type=str, required=True, help='Pod name to remediate')
    parser.add_argument('--action', type=str, required=True, 
                        choices=['restart_pod', 'restart_deployment', 'increase_memory', 
                                'increase_cpu', 'scale_deployment'],
                        help='Remediation action to take')
    parser.add_argument('--namespace', type=str, default='default', help='Kubernetes namespace')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    # Execute the remediation
    success, message = execute_remediation(args.pod, args.action, args.namespace)
    
    # Output format for easier parsing
    result = {
        "success": success,
        "message": message,
        "pod": args.pod,
        "action": args.action,
        "namespace": args.namespace
    }
    
    print(json.dumps(result))
    
    if success:
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main()) 