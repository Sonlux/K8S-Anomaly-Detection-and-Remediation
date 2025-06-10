#!/usr/bin/env python3
"""
Test script for the Llama API wrapper
"""

import os
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_llama_api")

# Import the LlamaLLM class from the k8s_multi_agent_system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from k8s_multi_agent_system import LlamaLLM

def test_llama_api():
    """Test the Llama API wrapper functionality"""
    try:
        # Default API key that works with NVIDIA API
        default_api_key = "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"
        
        # Get the API key from environment or command line
        api_key = os.environ.get("LLAMA_API_KEY")
        if not api_key and len(sys.argv) > 1:
            api_key = sys.argv[1]
        
        # If still no API key, use the default NVIDIA API key
        if not api_key:
            print("No Llama API key provided, using NVIDIA API key as default")
            api_key = default_api_key
            # When using NVIDIA API key, explicitly set the NVIDIA base URL
            base_url = "https://integrate.api.nvidia.com/v1"
            print(f"Using NVIDIA API endpoint: {base_url}")
        else:
            # Get the base URL from environment or use default
            base_url = os.environ.get("LLAMA_API_URL")
        
        # Initialize the Llama LLM client
        print(f"Initializing Llama API client with base URL: {base_url or 'default'}")
        llama_llm = LlamaLLM(api_key=api_key, base_url=base_url)
        
        # Example metrics data
        sample_metrics = {
            'CPU Usage (%)': 0.012098631,
            'Memory Usage (%)': 4.747099786,
            'Pod Restarts': 370,
            'Memory Usage (MB)': 18.47939985,
            'Network Receive Bytes': 0.014544437,
            'Network Transmit Bytes': 0.122316709,
            'FS Reads Total (MB)': 0.000586664,
            'FS Writes Total (MB)': 0.000836434,
            'Network Receive Packets Dropped (p/s)': 0,
            'Network Transmit Packets Dropped (p/s)': 0,
            'Ready Containers': 0,
            'Event Reason': 'BackOff',
            'Event Message': 'Back-off restarting failed container',
            'Event Age (minutes)': 120,
            'Event Count': 45
        }
        
        sample_prediction = {
            'predicted_anomaly': 1,
            'anomaly_probability': 0.96,
            'anomaly_type': 'crash_loop'
        }
        
        # Test a simple generation first
        print("\nTesting simple text generation...")
        simple_prompt = "What is Kubernetes and how does it handle pod scheduling? (Keep your answer brief)"
        print(f"Prompt: {simple_prompt}")
        simple_response = llama_llm.generate(simple_prompt)
        print(f"\nResponse: {simple_response}")
        
        # Test metrics analysis
        print("\nTesting Kubernetes metrics analysis...")
        analysis = llama_llm.analyze_k8s_metrics(sample_metrics, sample_prediction)
        print("\nAnalysis Result:")
        print(analysis)
        
        # Test the invoke method for LangChain compatibility
        print("\nTesting LangChain compatibility...")
        from langchain_core.messages import HumanMessage
        invoke_result = llama_llm.invoke([HumanMessage(content="What's a common way to debug a CrashLoopBackOff in Kubernetes? (Answer briefly)")])
        print(f"\nInvoke Result: {invoke_result.content}")
        
        print("\nAll tests completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error testing Llama API: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(test_llama_api()) 