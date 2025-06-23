#!/usr/bin/env python3
"""
Test script to verify that the RAG system is properly feeding pod data to the LLM.
"""

import os
import sys
import logging
import time
import json

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_system():
    """Test the RAG system with a pod query."""
    try:
        from agentic_rag_cli import KubernetesAgenticRAG
        
        # Initialize the RAG system
        logger.info("Initializing RAG system...")
        rag_system = KubernetesAgenticRAG(debug=True)
        
        # Test queries
        test_queries = [
            "get pods",
            "show me all the nodes",
            "list deployments",
            "what's the status of my cluster"
        ]
        
        # Test each query
        for query in test_queries:
            logger.info(f"\nTesting query: {query}")
            start_time = time.time()
            
            # Get response from RAG system
            response = rag_system.chat(query)
            
            # Log response
            elapsed_time = time.time() - start_time
            logger.info(f"Response received in {elapsed_time:.2f} seconds:\n")
            
            print("=" * 80)
            print(f"QUERY: {query}")
            print("=" * 80)
            print(response)
            print("=" * 80)
            
            # Check if response contains expected sections
            if "Real-Time Kubernetes Data" not in response:
                logger.warning(f"⚠️ Response for '{query}' may not contain expected sections")
        
        # Test agentic reasoning loop directly
        logger.info("\nTesting agentic reasoning loop directly...")
        
        # Simulate a direct tool request and response
        direct_test_query = "show me the pods in the default namespace"
        response = rag_system.chat(direct_test_query)
        
        print("=" * 80)
        print("DIRECT AGENTIC REASONING TEST:")
        print("=" * 80)
        print(response)
        print("=" * 80)
        
        if "Real-Time Kubernetes Data" not in response:
            logger.warning("⚠️ Direct agentic reasoning test may have failed")
        
        # Test fallback formatter
        logger.info("\nTesting fallback mechanism...")
        
        # Create a simple tool result
        test_tool_result = [{"name": "test-pod", "status": "Running"}]
        
        # Apply fallback formatter to a response without the expected sections
        fallback_test = rag_system.apply_fallback_formatter("Test response without sections", test_tool_result)
        
        print("=" * 80)
        print("FALLBACK FORMATTER TEST:")
        print("=" * 80)
        print(fallback_test)
        print("=" * 80)
        
        if "Real-Time Kubernetes Data" in fallback_test and "Analysis & Recommendations" in fallback_test:
            logger.info("✅ SUCCESS: Fallback formatter test passed")
        else:
            logger.error("❌ ERROR: Fallback formatter test failed")
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ ERROR: {e}", exc_info=True)
        print("\n❌ Test failed!")

if __name__ == "__main__":
    test_rag_system() 