# LLaMA API route handlers for Kubernetes dashboard

from flask import Blueprint, request, jsonify
import os
import sys
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Add src/agents directory to path for imports
src_agents_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'agents'))
sys.path.append(src_agents_path)

# Create blueprint
llama_bp = Blueprint('llama', __name__, url_prefix='/api/llama')

# Import LlamaLLM class and initialize client
try:
    from k8s_multi_agent_system import LlamaLLM
    llama_client = LlamaLLM()
    llama_available = True
except Exception as e:
    print(f"Warning: Could not initialize LlamaLLM: {e}")
    llama_available = False

@llama_bp.route('/chat', methods=['POST'])
def chat():
    """Handle chat requests to LLaMA API"""
    try:
        # Check if LlamaLLM is available
        if not llama_available:
            return jsonify({
                'message': {
                    'role': 'assistant',
                    'content': 'I apologize, but the LLaMA API service is currently unavailable. Please try again later.',
                    'timestamp': datetime.now().isoformat()
                },
                'error': 'LlamaLLM client not available'
            }), 503  # Service Unavailable
            
        data = request.json
        messages = data.get('messages', [])
        
        if not messages:
            return jsonify({'error': 'No messages provided'}), 400
        
        # Format messages for LlamaLLM
        formatted_messages = []
        for msg in messages:
            formatted_messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # Add system message if not present
        if not any(msg['role'] == 'system' for msg in formatted_messages):
            formatted_messages.insert(0, {
                'role': 'system',
                'content': 'You are Koda, an intelligent Kubernetes anomaly detection and remediation specialist. '
                           'Provide concise, technical responses about Kubernetes operations, anomalies, and remediation strategies.'
            })
        
        # Generate response from LlamaLLM
        response_content = llama_client.generate(
            messages=formatted_messages,
            temperature=0.7,
            max_tokens=1024
        )
        
        # Create response object
        response = {
            'message': {
                'role': 'assistant',
                'content': response_content,
                'timestamp': datetime.now().isoformat()
            },
            'context': {
                'confidence': 0.85,  # Placeholder - would be provided by the model in production
                'relatedResources': []  # Placeholder - would be populated based on context
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@llama_bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze Kubernetes resources using LLaMA API"""
    try:
        # Check if LlamaLLM is available
        if not llama_available:
            return jsonify({
                'message': {
                    'role': 'assistant',
                    'content': 'I apologize, but the LLaMA API service is currently unavailable. Please try again later.',
                    'timestamp': datetime.now().isoformat()
                },
                'error': 'LlamaLLM client not available'
            }), 503  # Service Unavailable
            
        data = request.json
        resource_type = data.get('resourceType')
        resource_name = data.get('resourceName')
        namespace = data.get('namespace')
        
        if not all([resource_type, resource_name, namespace]):
            return jsonify({'error': 'Missing required parameters'}), 400
        
        # Create prompt for resource analysis
        prompt = f"""Analyze the Kubernetes {resource_type} named '{resource_name}' in namespace '{namespace}'.
        Provide insights on potential issues, optimization opportunities, and security considerations."""
        
        # Generate analysis from LlamaLLM
        analysis = llama_client.generate(
            messages=[{
                'role': 'system',
                'content': 'You are Koda, an intelligent Kubernetes anomaly detection and remediation specialist.'
            }, {
                'role': 'user',
                'content': prompt
            }],
            temperature=0.3,
            max_tokens=1024
        )
        
        # Create response object
        response = {
            'message': {
                'role': 'assistant',
                'content': analysis,
                'timestamp': datetime.now().isoformat()
            },
            'context': {
                'confidence': 0.9,  # Placeholder - would be provided by the model in production
                'clusterInfo': f"Namespace: {namespace}",  # Placeholder - would be populated with real data
                'relatedResources': [f"{resource_type}/{resource_name}"]  # Placeholder - would be populated based on context
            }
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500