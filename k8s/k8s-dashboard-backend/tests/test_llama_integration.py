# Test script for LLaMA API integration

import os
import sys
import json
import unittest
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the Flask app and LlamaLLM class
from api.llama_routes import llama_bp
from k8s_multi_agent_system import LlamaLLM

# Create a simple Flask app for testing
from flask import Flask

app = Flask(__name__)
app.register_blueprint(llama_bp)

class TestLlamaIntegration(unittest.TestCase):
    """Test cases for LLaMA API integration"""
    
    def setUp(self):
        """Set up test client"""
        self.client = app.test_client()
        self.client.testing = True
    
    @patch('api.llama_routes.llama_client.generate')
    def test_chat_endpoint(self, mock_generate):
        """Test the chat endpoint"""
        # Mock the LlamaLLM generate method
        mock_generate.return_value = "This is a test response from the LLaMA API."
        
        # Test data
        test_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "What are the best practices for Kubernetes security?",
                    "timestamp": "2023-06-01T12:00:00Z"
                }
            ]
        }
        
        # Send request to the endpoint
        response = self.client.post(
            '/api/llama/chat',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message']['role'], 'assistant')
        self.assertEqual(data['message']['content'], "This is a test response from the LLaMA API.")
        self.assertIn('context', data)
        self.assertIn('confidence', data['context'])
    
    @patch('api.llama_routes.llama_client.generate')
    def test_analyze_endpoint(self, mock_generate):
        """Test the analyze endpoint"""
        # Mock the LlamaLLM generate method
        mock_generate.return_value = "Analysis of deployment 'test-app' in namespace 'default'."
        
        # Test data
        test_data = {
            "resourceType": "deployment",
            "resourceName": "test-app",
            "namespace": "default"
        }
        
        # Send request to the endpoint
        response = self.client.post(
            '/api/llama/analyze',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['message']['role'], 'assistant')
        self.assertEqual(data['message']['content'], "Analysis of deployment 'test-app' in namespace 'default'.")
        self.assertIn('context', data)
        self.assertIn('clusterInfo', data['context'])
        self.assertIn('relatedResources', data['context'])
    
    def test_chat_endpoint_missing_messages(self):
        """Test the chat endpoint with missing messages"""
        # Test data with missing messages
        test_data = {}
        
        # Send request to the endpoint
        response = self.client.post(
            '/api/llama/chat',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
    
    def test_analyze_endpoint_missing_params(self):
        """Test the analyze endpoint with missing parameters"""
        # Test data with missing parameters
        test_data = {
            "resourceType": "deployment"
            # Missing resourceName and namespace
        }
        
        # Send request to the endpoint
        response = self.client.post(
            '/api/llama/analyze',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

class TestLlamaLLM(unittest.TestCase):
    """Test cases for LlamaLLM class"""
    
    @patch('k8s_multi_agent_system.OpenAI')
    def test_llama_llm_initialization(self, mock_openai):
        """Test LlamaLLM initialization"""
        # Create mock OpenAI client
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Initialize LlamaLLM
        llama = LlamaLLM(api_key="test_key", base_url="https://test.api")
        
        # Check initialization
        mock_openai.assert_called_once_with(
            api_key="test_key",
            base_url="https://test.api"
        )
    
    @patch('k8s_multi_agent_system.OpenAI')
    def test_llama_llm_generate(self, mock_openai):
        """Test LlamaLLM generate method"""
        # Create mock OpenAI client and response
        mock_client = MagicMock()
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai.return_value = mock_client
        
        # Initialize LlamaLLM and generate response
        llama = LlamaLLM(api_key="test_key", base_url="https://test.api")
        response = llama.generate(
            messages=[{"role": "user", "content": "Test prompt"}],
            temperature=0.7,
            max_tokens=100
        )
        
        # Check response
        self.assertEqual(response, "Test response")
        mock_client.chat.completions.create.assert_called_once()

if __name__ == '__main__':
    unittest.main()