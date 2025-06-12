#!/usr/bin/env python3
"""
Test script for the NVIDIA API integration with both direct OpenAI client and LangChain
"""

import os
import logging
import sys

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_nvidia_api")

def test_direct_openai_client():
    """Test the direct OpenAI client approach for NVIDIA API"""
    try:
        from openai import OpenAI
        
        # Default API key for testing
        api_key = os.environ.get("NVIDIA_API_KEY", "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")
        
        # Initialize the client
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
        
        print("\nTesting direct OpenAI client with NVIDIA API...")
        
        # Create a completion
        prompt = "What is Kubernetes and how does it handle pod scheduling? (Keep your answer brief)"
        print(f"Prompt: {prompt}")
        
        # Non-streaming response
        print("\nGenerating non-streaming response...")
        completion = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024
        )
        
        print(f"Response: {completion.choices[0].message.content}")
        
        # Streaming response
        print("\nGenerating streaming response...")
        completion = client.chat.completions.create(
            model="meta/llama-3.3-70b-instruct",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
            stream=True
        )
        
        print("Response: ", end="")
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
        print("\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error testing direct OpenAI client: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

def test_langchain_nvidia():
    """Test the LangChain integration for NVIDIA API"""
    try:
        # Check if langchain_nvidia_ai_endpoints is installed
        try:
            from langchain_nvidia_ai_endpoints import ChatNVIDIA
        except ImportError:
            print("\nlangchain_nvidia_ai_endpoints is not installed. Skipping LangChain test.")
            print("To install, run: pip install langchain-nvidia-ai-endpoints")
            return 0
        
        # Default API key for testing
        api_key = os.environ.get("NVIDIA_API_KEY", "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")
        
        # Initialize the client
        client = ChatNVIDIA(
            model="meta/llama-3.3-70b-instruct",
            api_key=api_key,
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024,
        )
        
        print("\nTesting LangChain integration with NVIDIA API...")
        
        # Create a completion
        prompt = "What are the best practices for Kubernetes resource management? (Keep your answer brief)"
        print(f"Prompt: {prompt}")
        
        # Non-streaming response
        print("\nGenerating non-streaming response...")
        response = client.invoke([{"role": "user", "content": prompt}])
        print(f"Response: {response.content}")
        
        # Streaming response
        print("\nGenerating streaming response...")
        print("Response: ", end="")
        for chunk in client.stream([{"role": "user", "content": prompt}]):
            print(chunk.content, end="")
        print("\n")
        
        return 0
    
    except Exception as e:
        logger.error(f"Error testing LangChain integration: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

def main():
    """Run all tests"""
    print("=== Testing NVIDIA API Integration ===\n")
    
    # Test direct OpenAI client
    result1 = test_direct_openai_client()
    
    # Test LangChain integration
    result2 = test_langchain_nvidia()
    
    if result1 == 0 and result2 == 0:
        print("\nAll tests completed successfully!")
        return 0
    else:
        print("\nSome tests failed. Check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())