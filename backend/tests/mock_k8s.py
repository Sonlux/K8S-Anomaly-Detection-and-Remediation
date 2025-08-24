#!/usr/bin/env python
"""
Mock Kubernetes API for testing remediation logic
This provides minimal mocks for K8s client objects
"""

class V1ResourceRequirements:
    def __init__(self, limits=None, requests=None):
        self.limits = limits or {}
        self.requests = requests or {}

class V1Container:
    def __init__(self, name, resources=None):
        self.name = name
        self.resources = resources or V1ResourceRequirements()

class V1ContainerStatus:
    def __init__(self, name, ready=True, restart_count=0):
        self.name = name
        self.ready = ready
        self.restart_count = restart_count

class V1PodCondition:
    def __init__(self, type, status, reason="", message=""):
        self.type = type
        self.status = status
        self.reason = reason
        self.message = message

class V1PodStatus:
    def __init__(self, phase="Running", conditions=None, container_statuses=None):
        self.phase = phase
        self.conditions = conditions or []
        self.container_statuses = container_statuses or []

class V1ObjectMeta:
    def __init__(self, name, namespace, owner_references=None, annotations=None):
        self.name = name
        self.namespace = namespace
        self.owner_references = owner_references or []
        self.annotations = annotations or {}

class V1OwnerReference:
    def __init__(self, name, kind, uid="123", controller=True):
        self.name = name
        self.kind = kind
        self.uid = uid
        self.controller = controller

class V1PodSpec:
    def __init__(self, containers=None):
        self.containers = containers or []

class V1Pod:
    def __init__(self, name, namespace, phase="Running", containers=None):
        self.metadata = V1ObjectMeta(name=name, namespace=namespace)
        self.spec = V1PodSpec(containers=containers or [V1Container(name="container-1")])
        
        # Set up some default container statuses
        container_statuses = [
            V1ContainerStatus(name="container-1", ready=(phase == "Running"), restart_count=0)
        ]
        
        # Set up default conditions
        conditions = [
            V1PodCondition(type="Ready", status="True" if phase == "Running" else "False")
        ]
        
        self.status = V1PodStatus(phase=phase, container_statuses=container_statuses, conditions=conditions)

class CoreV1Api:
    """Mock Kubernetes CoreV1Api"""
    
    def __init__(self):
        self.pods = {}
        
    def create_namespaced_pod(self, namespace, body):
        pod_id = f"{namespace}/{body.metadata.name}"
        self.pods[pod_id] = body
        return body
    
    def delete_namespaced_pod(self, name, namespace, body=None):
        pod_id = f"{namespace}/{name}"
        if pod_id in self.pods:
            del self.pods[pod_id]
        return None
    
    def read_namespaced_pod(self, name, namespace):
        pod_id = f"{namespace}/{name}"
        if pod_id not in self.pods:
            # Return a mock pod if it doesn't exist
            pod = V1Pod(name=name, namespace=namespace)
            self.pods[pod_id] = pod
        return self.pods[pod_id]
    
    def list_pod_for_all_namespaces(self, **kwargs):
        # Create a mock response object with an items attribute
        class MockResponse:
            def __init__(self, items):
                self.items = items
        
        return MockResponse(list(self.pods.values()))
    
    def read_namespaced_pod_log(self, name, namespace, **kwargs):
        return "Mock pod logs"

class AppsV1Api:
    """Mock Kubernetes AppsV1Api"""
    
    def __init__(self):
        self.deployments = {}
        self.replica_sets = {}
    
    def read_namespaced_deployment(self, name, namespace):
        deployment_id = f"{namespace}/{name}"
        if deployment_id not in self.deployments:
            # Create a mock deployment
            class V1Deployment:
                def __init__(self, name, namespace):
                    self.metadata = V1ObjectMeta(name=name, namespace=namespace)
                    self.spec = type('obj', (object,), {
                        'replicas': 1,
                        'template': type('obj', (object,), {
                            'metadata': V1ObjectMeta(name=name, namespace=namespace),
                            'spec': V1PodSpec(containers=[V1Container(name="container-1")])
                        })
                    })
            
            self.deployments[deployment_id] = V1Deployment(name, namespace)
        
        return self.deployments[deployment_id]
    
    def read_namespaced_replica_set(self, name, namespace):
        rs_id = f"{namespace}/{name}"
        if rs_id not in self.replica_sets:
            # Create a mock replica set
            class V1ReplicaSet:
                def __init__(self, name, namespace, deployment_name=None):
                    self.metadata = V1ObjectMeta(
                        name=name, 
                        namespace=namespace,
                        owner_references=[V1OwnerReference(name=deployment_name or "mock-deployment", kind="Deployment")]
                    )
            
            self.replica_sets[rs_id] = V1ReplicaSet(name, namespace)
        
        return self.replica_sets[rs_id]
    
    def patch_namespaced_deployment(self, name, namespace, body, **kwargs):
        deployment_id = f"{namespace}/{name}"
        self.deployments[deployment_id] = body
        return body

# Mock for the watch API
class Watch:
    def __init__(self):
        self.stopped = False
    
    def stream(self, func, **kwargs):
        # Just return an empty list to avoid infinite loops
        if self.stopped:
            return []
        
        # Get pods from the function
        response = func()
        
        # Yield one event per pod
        for pod in response.items:
            yield {'type': 'MODIFIED', 'object': pod}
            
        self.stopped = True
    
    def stop(self):
        self.stopped = True

# Utility function to create a mock Kubernetes client
def create_mock_k8s_client():
    return CoreV1Api(), AppsV1Api() 