#!/usr/bin/env python3
"""
Test script to verify that the RAG system is properly feeding pod data to the LLM.
"""

import os
import sys
import logging

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
        
        # Test query
        test_query = "get pods"
        logger.info(f"Testing query: {test_query}")
        
        # Get response
        response = rag_system.query(test_query)
        
        logger.info("Response received:")
        print("\n" + "="*80)
        print("RESPONSE:")
        print("="*80)
        print(response)
        print("="*80)
        
        # Check if the response contains both pod data and LLM analysis
        if "--- Real-Time Kubernetes Data ---" in response and "--- LLM Reasoning & Guidance ---" in response:
            logger.info("✅ SUCCESS: Response contains both pod data and LLM analysis")
            return True
        else:
            logger.warning("⚠️ Response may not contain expected sections")
            return False
            
    except Exception as e:
        logger.error(f"❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_system()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed!")
        sys.exit(1) 