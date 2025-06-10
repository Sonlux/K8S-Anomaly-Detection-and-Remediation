#!/usr/bin/env python3
"""
Kubernetes Monitoring Runner Script

This script runs the dataset generator, anomaly detection agent, and any other
agents together to provide continuous monitoring of Kubernetes pods.
"""

import os
import sys
import time
import argparse
import subprocess
import signal
import logging
from multiprocessing import Process, Event

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('k8s_monitoring.log')
    ]
)
logger = logging.getLogger("k8s-monitoring")

# Global variables for process management
processes = []
stop_event = Event()

def signal_handler(sig, frame):
    """Handle termination signals to gracefully shut down processes"""
    logger.info("Received termination signal, shutting down...")
    stop_event.set()
    
    for proc in processes:
        if proc.is_alive():
            logger.info(f"Terminating process {proc.name}")
            proc.terminate()
    
    logger.info("All processes terminated, exiting")
    sys.exit(0)

def run_dataset_generator(stop_event, prometheus_url, namespace, output_file, interval):
    """Run the dataset generator process"""
    logger.info(f"Starting dataset generator with prometheus_url={prometheus_url}, " 
               f"namespace={namespace}, output_file={output_file}, interval={interval}s")
    
    # Import the dataset generator (which has its own main loop)
    try:
        # Set environment variables for dataset generator
        os.environ['PROMETHEUS_URL'] = prometheus_url
        os.environ['NAMESPACE'] = namespace
        os.environ['OUTPUT_FILE'] = output_file
        os.environ['SLEEP_INTERVAL'] = str(interval)
        
        # Run the script as a module
        import importlib.util
        spec = importlib.util.spec_from_file_location("dataset_generator", 
                                                     os.path.join(os.path.dirname(__file__), 
                                                                 "dataset-generator.py"))
        generator_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(generator_module)
        
        logger.info("Dataset generator module loaded and running")
        
        # The module will run its main loop until a KeyboardInterrupt
        while not stop_event.is_set():
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Dataset generator received interrupt")
    except Exception as e:
        logger.error(f"Error in dataset generator: {e}")
        import traceback
        traceback.print_exc()

def run_dataset_agent(stop_event, input_file, watch_interval, alert_threshold, openai_api_key=None, use_lang_models=True):
    """Run the dataset generator agent process"""
    logger.info(f"Starting dataset agent with input_file={input_file}, "
               f"watch_interval={watch_interval}s, alert_threshold={alert_threshold}, "
               f"use_lang_models={use_lang_models}")
    
    try:
        # Get the absolute path to the agent file for reliable importing
        agent_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "src", "agents", "dataset_generator_agent.py")
        
        logger.info(f"Using dataset agent module from: {agent_file}")
        
        # Direct import using importlib for maximum reliability
        import importlib.util
        spec = importlib.util.spec_from_file_location("dataset_generator_agent", agent_file)
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)
        
        # Get the class and create an instance
        DatasetGeneratorAgent = agent_module.DatasetGeneratorAgent
        agent = DatasetGeneratorAgent(
            input_file=input_file,
            watch_interval=watch_interval,
            alert_threshold=alert_threshold,
            use_lang_models=use_lang_models,
            openai_api_key=openai_api_key
        )
        
        # Create a wrapper for the run method that respects the stop event
        def run_with_stop_check():
            logger.info("Dataset agent started")
            try:
                while not stop_event.is_set():
                    # Read new data
                    new_data = agent.read_new_data()
                    if not new_data.empty:
                        # Update metrics
                        agent.update_pod_metrics(new_data)
                    
                    # Check stop event more frequently than the watch interval
                    for _ in range(min(10, watch_interval)):
                        if stop_event.is_set():
                            break
                        time.sleep(1)
            except Exception as e:
                logger.error(f"Error in dataset agent loop: {e}")
                import traceback
                traceback.print_exc()
            
            logger.info("Dataset agent stopped")
        
        # Run the wrapper
        run_with_stop_check()
        
    except KeyboardInterrupt:
        logger.info("Dataset agent received interrupt")
    except Exception as e:
        logger.error(f"Error in dataset agent: {e}")
        import traceback
        traceback.print_exc()

def run_anomaly_agent(stop_event, input_file, watch_interval, alert_threshold):
    """Run the anomaly detection agent process"""
    logger.info(f"Starting anomaly agent with input_file={input_file}, "
               f"watch_interval={watch_interval}s, alert_threshold={alert_threshold}")
    
    try:
        # Get the absolute path to the agent file for reliable importing
        agent_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "src", "agents", "anomaly_detection_agent.py")
        
        logger.info(f"Using anomaly agent module from: {agent_file}")
        
        # Direct import using importlib for maximum reliability
        import importlib.util
        spec = importlib.util.spec_from_file_location("anomaly_detection_agent", agent_file)
        agent_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(agent_module)
        
        # Get the class and create an instance
        AnomalyDetectionAgent = agent_module.AnomalyDetectionAgent
        agent = AnomalyDetectionAgent(
            alert_threshold=alert_threshold
        )
        
        # Create a wrapper for monitoring the metrics file and detecting anomalies
        def run_with_stop_check():
            logger.info("Anomaly agent started")
            
            # Track the last processed position in the file
            last_position = 0
            
            while not stop_event.is_set():
                try:
                    if not os.path.exists(input_file):
                        logger.warning(f"Input file {input_file} does not exist")
                        time.sleep(watch_interval)
                        continue
                    
                    # Read the file and process new data
                    df = pd.read_csv(input_file)
                    
                    if len(df) <= last_position:
                        logger.debug("No new rows to process")
                    else:
                        # Process new rows
                        new_df = df.iloc[last_position:]
                        last_position = len(df)
                        
                        if not new_df.empty:
                            logger.info(f"Processing {len(new_df)} new rows of metrics data")
                            
                            # Group data by pod name
                            pod_history = {}
                            for pod_name, pod_df in new_df.groupby('Pod Name'):
                                pod_history[pod_name] = pod_df.to_dict('records')
                            
                            # Detect anomalies
                            anomalies = agent.detect_anomalies(pod_history)
                            
                            # Generate insights
                            insights = agent.generate_insights(anomalies)
                            
                            # Output insights
                            if insights:
                                agent.output_insights(insights, 'pod_insights.json')
                
                except Exception as e:
                    logger.error(f"Error in anomaly agent loop: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Check stop event more frequently than the watch interval
                for _ in range(min(10, watch_interval)):
                    if stop_event.is_set():
                        break
                    time.sleep(1)
            
            logger.info("Anomaly agent stopped")
        
        # Import pandas here to avoid circular imports
        import pandas as pd
        
        # Run the wrapper
        run_with_stop_check()
        
    except KeyboardInterrupt:
        logger.info("Anomaly agent received interrupt")
    except Exception as e:
        logger.error(f"Error in anomaly agent: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Parse arguments and start monitoring"""
    parser = argparse.ArgumentParser(description='Run Kubernetes monitoring with anomaly detection')
    
    # Dataset generator options
    parser.add_argument('--prometheus-url', type=str, default='http://localhost:8082',
                        help='Prometheus URL (default: http://localhost:8082)')
    parser.add_argument('--namespace', type=str, default='monitoring',
                        help='Kubernetes namespace to monitor (default: monitoring)')
    parser.add_argument('--generator-interval', type=int, default=5,
                        help='Interval in seconds between metrics collection (default: 5)')
    
    # Agent options
    parser.add_argument('--output-file', type=str, default='pod_metrics.csv',
                        help='Output file for metrics (default: pod_metrics.csv)')
    parser.add_argument('--watch-interval', type=int, default=10,
                        help='Interval in seconds between agent checks (default: 10)')
    parser.add_argument('--alert-threshold', type=float, default=0.7,
                        help='Probability threshold for anomaly alerts (default: 0.7)')
    parser.add_argument('--openai-api-key', type=str, default=None,
                        help='OpenAI API key for advanced analysis (default: None)')
    parser.add_argument('--disable-lang-models', action='store_true',
                        help='Disable LangChain and LangGraph enhanced analysis')
    
    # Mode options
    parser.add_argument('--generator-only', action='store_true',
                        help='Run only the dataset generator')
    parser.add_argument('--dataset-agent-only', action='store_true',
                        help='Run only the dataset agent')
    parser.add_argument('--anomaly-agent-only', action='store_true',
                        help='Run only the anomaly detection agent')
    
    args = parser.parse_args()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Start processes based on mode
        if args.dataset_agent_only:
            logger.info("Running in dataset-agent-only mode")
            dataset_agent_process = Process(
                target=run_dataset_agent,
                args=(stop_event, args.output_file, args.watch_interval, args.alert_threshold, 
                      args.openai_api_key, not args.disable_lang_models),
                name="DatasetAgentProcess"
            )
            dataset_agent_process.start()
            processes.append(dataset_agent_process)
            
        elif args.anomaly_agent_only:
            logger.info("Running in anomaly-agent-only mode")
            anomaly_agent_process = Process(
                target=run_anomaly_agent,
                args=(stop_event, args.output_file, args.watch_interval, args.alert_threshold),
                name="AnomalyAgentProcess"
            )
            anomaly_agent_process.start()
            processes.append(anomaly_agent_process)
            
        elif args.generator_only:
            logger.info("Running in generator-only mode")
            generator_process = Process(
                target=run_dataset_generator,
                args=(stop_event, args.prometheus_url, args.namespace, args.output_file, args.generator_interval),
                name="GeneratorProcess"
            )
            generator_process.start()
            processes.append(generator_process)
            
        else:
            logger.info("Running all components")
            
            # Start the dataset generator
            generator_process = Process(
                target=run_dataset_generator,
                args=(stop_event, args.prometheus_url, args.namespace, args.output_file, args.generator_interval),
                name="GeneratorProcess"
            )
            generator_process.start()
            processes.append(generator_process)
            
            # Give the generator a head start to create the file
            time.sleep(2)
            
            # Start the dataset agent
            dataset_agent_process = Process(
                target=run_dataset_agent,
                args=(stop_event, args.output_file, args.watch_interval, args.alert_threshold,
                      args.openai_api_key, not args.disable_lang_models),
                name="DatasetAgentProcess"
            )
            dataset_agent_process.start()
            processes.append(dataset_agent_process)
            
            # Start the anomaly agent
            anomaly_agent_process = Process(
                target=run_anomaly_agent,
                args=(stop_event, args.output_file, args.watch_interval, args.alert_threshold),
                name="AnomalyAgentProcess"
            )
            anomaly_agent_process.start()
            processes.append(anomaly_agent_process)
        
        # Wait for processes to finish
        for proc in processes:
            proc.join()
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt in main process")
        stop_event.set()
        
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=5)
                
    except Exception as e:
        logger.error(f"Error in main process: {e}")
        import traceback
        traceback.print_exc()
        
        stop_event.set()
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
    
    logger.info("Monitoring stopped")

if __name__ == "__main__":
    main() 