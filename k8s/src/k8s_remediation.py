from kubernetes import client, config, watch
from fetch_metrics import fetch_metrics
import logging
import time
import sys  # Added missing import

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True,
    stream=sys.stdout  # Now works with sys imported
)
logger = logging.getLogger("k8s-remediation-utils")

def monitor_pods():
    config.load_kube_config()
    v1 = client.CoreV1Api()
    w = watch.Watch()

    try:
        for event in w.stream(v1.list_pod_for_all_namespaces, timeout_seconds=300):  # 5-minute timeout
            pod = event['object']
            status = pod.status.phase
            event_type = event['type']
            logger.debug(f"Processing event for {pod.metadata.namespace}/{pod.metadata.name}, status: {status}, event type: {event_type}")

            if status in ['Running', 'Pending', 'CrashLoopBackOff']:
                metrics = fetch_metrics(pod, v1)
                logger.debug(f"Fetched metrics for {pod.metadata.namespace}/{pod.metadata.name}: {metrics}")

                # Example remediation threshold
                if metrics['CPU Usage (%)'] > 80.0 or metrics['Memory Usage (%)'] > 80.0:
                    logger.info(f"Remediating resource exhaustion for {pod.metadata.namespace}/{pod.metadata.name}")
                    # Add scaling logic here (e.g., kubectl scale deployment)

            time.sleep(1)  # Prevent overwhelming the API
    except Exception as e:
        logger.error(f"Error in monitoring loop: {str(e)}")
    finally:
        logger.info("Stopped real-time cluster monitoring")
        w.stop()

if __name__ == "__main__":
    monitor_pods()