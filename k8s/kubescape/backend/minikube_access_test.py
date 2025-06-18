# minikube_access_test.py
from kubernetes import client, config

try:
    config.load_kube_config()
    v1 = client.CoreV1Api()
    pods = v1.list_pod_for_all_namespaces().items
    print("Successfully connected to Minikube!")
    print(f"Found {len(pods)} pods:")
    for pod in pods:
        print(f"- {pod.metadata.namespace}/{pod.metadata.name}")
except Exception as e:
    print("Failed to connect to Minikube or fetch pods.")
    print(e)
