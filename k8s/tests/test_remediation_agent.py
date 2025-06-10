#!/usr/bin/env python3
"""
Test script for the Kubernetes Remediation Agent

This script tests the remediation agent with sample anomaly data
without requiring a live Kubernetes cluster.
"""

import os
import sys
import json
import logging
import pandas as pd
from kubernetes import client, config
from unittest.mock import patch, MagicMock

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test-remediation")

# Sample test cases for different anomaly types
TEST_CASES = [
    {
        "name": "crash_loop",
        "prediction": {
            "predicted_anomaly": 1,
            "anomaly_probability": 0.96,
            "anomaly_type": "crash_loop",
            "event_age_minutes": 45,
            "event_reason": "BackOff",
            "event_count": 23
        },
        "pod_info": {
            "name": "web-frontend-5d8b4f8b76-2xvqz",
            "namespace": "default",
            "status": "Running",
            "owner_reference": "web-frontend",
            "restart_count": 15,
            "cpu_request": "100m",
            "memory_request": "256Mi",
            "cpu_limit": "200m",
            "memory_limit": "512Mi"
        }
    },
    {
        "name": "oom_kill",
        "prediction": {
            "predicted_anomaly": 1,
            "anomaly_probability": 0.89,
            "anomaly_type": "oom_kill",
            "event_age_minutes": 10,
            "event_reason": "OOMKilled",
            "event_count": 3
        },
        "pod_info": {
            "name": "api-service-7c9b6d6f59-f8hvq",
            "namespace": "backend",
            "status": "Running",
            "owner_reference": "api-service",
            "restart_count": 5,
            "cpu_request": "200m",
            "memory_request": "512Mi",
            "cpu_limit": "500m",
            "memory_limit": "1Gi"
        }
    },
    {
        "name": "resource_exhaustion",
        "prediction": {
            "predicted_anomaly": 1,
            "anomaly_probability": 0.78,
            "anomaly_type": "resource_exhaustion",
            "event_age_minutes": 30,
            "event_reason": "",
            "event_count": 0
        },
        "pod_info": {
            "name": "database-0",
            "namespace": "database",
            "status": "Running",
            "owner_reference": "database",
            "restart_count": 0,
            "cpu_request": "500m",
            "memory_request": "1Gi",
            "cpu_limit": "1",
            "memory_limit": "2Gi"
        }
    }
]

# Mock Kubernetes API client
class MockKubernetesClient:
    def __init__(self):
        self.deleted_pods = []
        self.updated_deployments = []
        self.scaled_deployments = []
    
    def mock_delete_namespaced_pod(self, name, namespace, body):
        logger.info(f"Mock: Deleted pod {namespace}/{name}")
        self.deleted_pods.append({"name": name, "namespace": namespace})
        return {"status": "Success"}
    
    def mock_read_namespaced_deployment(self, name, namespace):
        logger.info(f"Mock: Read deployment {namespace}/{name}")
        
        # Create mock container with resources
        container = MagicMock()
        container.name = "container-1"
        
        # Mock resources
        container.resources = MagicMock()
        container.resources.limits = {"cpu": "500m", "memory": "512Mi"}
        container.resources.requests = {"cpu": "250m", "memory": "256Mi"}
        
        # Create mock deployment
        deployment = MagicMock()
        deployment.metadata.name = name
        deployment.metadata.namespace = namespace
        deployment.spec.replicas = 1
        deployment.spec.template.spec.containers = [container]
        
        return deployment
    
    def mock_patch_namespaced_deployment(self, name, namespace, body):
        logger.info(f"Mock: Updated deployment {namespace}/{name}")
        
        # Check what kind of update was made
        if hasattr(body.spec, 'replicas') and body.spec.replicas > 1:
            self.scaled_deployments.append({
                "name": name, 
                "namespace": namespace,
                "replicas": body.spec.replicas
            })
            logger.info(f"Mock: Scaled deployment to {body.spec.replicas} replicas")
        else:
            self.updated_deployments.append({"name": name, "namespace": namespace})
            
            # Log container resources
            for container in body.spec.template.spec.containers:
                if container.resources and container.resources.limits:
                    logger.info(f"Mock: Updated container {container.name} resources: {container.resources.limits}")
        
        return {"status": "Success"}

# Apply patches before importing remediation_agent
mock_k8s = MockKubernetesClient()

# Use environment flag to signal we're in test mode to avoid actual NVIDIA API calls
os.environ["REMEDIATION_TEST_MODE"] = "true"

# Define mock nvidia_llm.generate function
def mock_generate(prompt, **kwargs):
    # Return a pre-formatted response based on what's in the prompt
    if "crash_loop" in prompt:
        return """Based on the pod information and anomaly prediction, here's a remediation plan:

**1. Issue summary**
The pod is experiencing a crash loop with 15 restarts. This is indicated by the 'BackOff' event that has occurred 23 times over 45 minutes.

**2. Root cause analysis**
Crash loops typically occur when a container repeatedly fails to start successfully. This could be due to:
- Application errors in the pod's code
- Missing dependencies or configuration
- Resource constraints (though this seems less likely given the current resource usage)
- Corrupted application state

**3. Recommended remediation steps**
1. Restart the pod to clear any transient issues:
   - Delete the pod to trigger recreation by the deployment controller
2. If the issue persists, check pod logs:
   - `kubectl logs web-frontend-5d8b4f8b76-2xvqz -n default`
3. Check for any recent changes to the application or configuration

**4. Potential impact**
- Brief service interruption during pod restart
- Potential for the issue to recur if the root cause is not addressed
- User requests might fail during the restart period

**5. Warning level**
**HIGH** - The pod is in a crash loop which indicates a critical failure requiring immediate attention."""
    elif "oom_kill" in prompt:
        return """Based on the pod information and anomaly prediction, here's a remediation plan:

**1. Issue summary**
The pod 'api-service-7c9b6d6f59-f8hvq' in the 'backend' namespace has been experiencing Out of Memory (OOM) kill events. The OOMKilled event has occurred 3 times in the last 10 minutes.

**2. Root cause analysis**
The pod is being terminated by the kernel's OOM killer because it's attempting to use more memory than its allocated limit of 1Gi. This suggests that:
- The application has a memory leak or inefficient memory usage
- The memory limit is set too low for the actual workload requirements
- There might be an unexpected spike in traffic or workload

**3. Recommended remediation steps**
1. Increase the memory limits by 50% to provide immediate relief:
   - Modify the deployment to increase memory limit from 1Gi to 1.5Gi
   - Also increase memory request from 512Mi to 768Mi
2. Monitor memory usage after the change
3. Consider investigating application code for memory optimization

**4. Potential impact**
- Pod will restart when the resource limits are changed
- Temporary service interruption during restart
- Increased memory consumption on the node

**5. Warning level**
**MEDIUM** - While OOM kills are serious, the relatively low frequency (3 times in 10 minutes) suggests this might be manageable with a resource adjustment."""
    else:
        return """Based on the pod information and anomaly prediction, here's a remediation plan:

**1. Issue summary**
The database-0 pod in the database namespace is experiencing resource exhaustion, with the anomaly detection model reporting a 78% probability of an issue.

**2. Root cause analysis**
The pod appears to be hitting resource limits, which can lead to degraded performance. Since there are no specific Kubernetes events reported, this is likely a gradual performance degradation rather than a hard failure. The most probable causes are:
- Increased workload on the database
- Inefficient queries consuming excessive resources
- Background processes within the database consuming resources

**3. Recommended remediation steps**
1. Scale up the StatefulSet/Deployment to add another replica:
   - `kubectl scale statefulset/database --replicas=2 -n database`
2. Consider implementing connection pooling if not already in place
3. Review database queries for optimization opportunities
4. Monitor resource usage after scaling to ensure it resolves the issue

**4. Potential impact**
- Increased resource consumption on the cluster
- Temporary connection failures during scaling operation
- Potential data synchronization overhead between database instances

**5. Warning level**
**LOW** - Resource exhaustion without complete failure indicates a performance issue rather than an outage. This should be addressed soon but is not an immediate emergency."""

# Patch Kubernetes API clients
@patch('kubernetes.client.CoreV1Api')
@patch('kubernetes.client.AppsV1Api')
def test_remediation_agent(mock_apps_api, mock_core_api):
    # Configure mocks
    mock_core_api.return_value.delete_namespaced_pod.side_effect = mock_k8s.mock_delete_namespaced_pod
    mock_apps_api.return_value.read_namespaced_deployment.side_effect = mock_k8s.mock_read_namespaced_deployment
    mock_apps_api.return_value.patch_namespaced_deployment.side_effect = mock_k8s.mock_patch_namespaced_deployment
    
    # First create the mock for nvidia_llm
    mock_nvidia_llm = MagicMock()
    mock_nvidia_llm.generate = mock_generate
    
    # Using patch context manager for nvidia_llm
    with patch.dict('sys.modules', {'nvidia_llm': mock_nvidia_llm}):
        # Import the remediation agent after patching
        from remediation_agent import remediate_pod
        
        # Also directly patch the module's nvidia_llm attribute
        import remediation_agent
        if hasattr(remediation_agent, 'nvidia_llm'):
            # Only replace if it exists
            remediation_agent.nvidia_llm = mock_nvidia_llm
        
        # Test each case
        for test_case in TEST_CASES:
            print("\n" + "="*80)
            print(f"TEST CASE: {test_case['name']}")
            print("="*80)
            
            # Clear previous actions
            mock_k8s.deleted_pods = []
            mock_k8s.updated_deployments = []
            mock_k8s.scaled_deployments = []
            
            # Run agent with test case (first run without approval)
            messages = remediate_pod(test_case["prediction"], test_case["pod_info"])
            
            # Print messages
            for msg in messages:
                from langchain_core.messages import AIMessage
                prefix = "AI: " if isinstance(msg, AIMessage) else "Human: "
                content = msg.content if hasattr(msg, 'content') else str(msg)
                print(f"{prefix}{content}")
            
            # Ask for user approval
            user_input = input("\nDo you approve this remediation plan? (yes/no): ")
            
            if user_input.lower() in ["yes", "y", "approve", "approved"]:
                print("\nExecuting remediation plan...")
                
                # Execute remediation with approval
                approval_messages = remediate_pod(test_case["prediction"], test_case["pod_info"], user_input)
                
                # Print only the new messages (those added after approval)
                for msg in approval_messages[-2:]:
                    prefix = "AI: " if isinstance(msg, AIMessage) else "Human: "
                    content = msg.content if hasattr(msg, 'content') else str(msg)
                    print(f"{prefix}{content}")
                    
                # Print summary of K8s actions taken
                print("\nK8s Actions Taken:")
                if mock_k8s.deleted_pods:
                    print(f"- Pods deleted: {mock_k8s.deleted_pods}")
                if mock_k8s.updated_deployments:
                    print(f"- Deployments updated: {mock_k8s.updated_deployments}")
                if mock_k8s.scaled_deployments:
                    print(f"- Deployments scaled: {mock_k8s.scaled_deployments}")
                if not any([mock_k8s.deleted_pods, mock_k8s.updated_deployments, mock_k8s.scaled_deployments]):
                    print("- No K8s actions taken")
            else:
                print("\nRemediation plan rejected. No action taken.")

if __name__ == "__main__":
    # Ensure we don't try to talk to a real K8s cluster
    os.environ["KUBECONFIG"] = "/tmp/nonexistent"
    
    # Run tests
    test_remediation_agent() 