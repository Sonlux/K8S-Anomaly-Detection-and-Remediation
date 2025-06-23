#!/usr/bin/env python3
"""
Kubernetes Agentic RAG CLI Chat Interface

This script provides a command-line interface for interacting with the Kubernetes
knowledge base using RAG (Retrieval Augmented Generation) and LLM capabilities.

Features:
- Interactive chat interface for querying Kubernetes knowledge
- Chain of thought reasoning for complex queries
- Integration with existing RAG utilities and LLM providers
- Context-aware responses based on the Kubernetes project
- Real-time information fetching from Minikube clusters

Usage:
    python agentic_rag_cli.py
"""

import os
import sys
import logging
import argparse
from typing import List, Dict, Any, Optional
import json
import re
from datetime import datetime, timezone
import colorama
from colorama import Fore, Style
# Add this import near the top of your agentic_rag_cli.py file, with your other imports
from k8s_client_utils import initialize_kubernetes_client, get_cluster_info
import time


# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RAG utilities
from rag_utils import (
    get_chroma_client,
    get_or_create_collection,
    query_knowledge_base,
    load_documents_from_json,
    hybrid_search,
    add_documents_to_knowledge_base,
    build_bm25_index
)

# Import Kubernetes knowledge fetcher
try:
    from k8s_knowledge_fetcher import (
        fetch_k8s_info,
        fetch_pod_info,
        fetch_node_info,
        fetch_deployment_info,
        fetch_service_info,
        fetch_namespace_info,
        fetch_cluster_info,
        fetch_pod_logs,
        is_minikube_available
    )
    # Also import the client utilities
    from k8s_client_utils import initialize_kubernetes_client, get_cluster_info
    k8s_fetcher_available = True
except ImportError as e:
    logging.warning(f"Could not import Kubernetes knowledge fetcher: {e}")
    k8s_fetcher_available = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import LLM-related modules
try:
    from agents.nvidia_llm import NvidiaLLM
    llm_available = True
except ImportError as e:
    logger.warning(f"Could not import LLM modules: {e}")
    llm_available = False

# Constants
SYSTEM_PROMPT = """
You are Koda, a Kubernetes Anomaly Remediation Agent. Your mission is to provide clear, accurate, and actionable advice on Kubernetes issues.

You have access to a set of tools for fetching real-time Kubernetes data (pods, nodes, deployments, logs, etc.).

**IMPORTANT INSTRUCTIONS FOR TOOL USAGE:**
1. When the user asks for real-time Kubernetes data (e.g., show pods, fetch pods, get nodes, get logs, show deployments, etc.), you MUST:
   a. First output a TOOL_REQUEST block in this format:
      TOOL_REQUEST: {"tool": "tool_name", "args": {"arg1": "value1", ...}}
   b. Wait for the TOOL_RESULT
   c. ALWAYS summarize the data from TOOL_RESULT in a clear, structured format (table or bullet points)
   d. Include counts, status summaries, and any issues detected

2. NEVER skip the summary step! The user cannot see the raw TOOL_RESULT data!

3. For ANY query about pods, nodes, deployments, services, etc., use the appropriate tool rather than relying on static knowledge.

**EXAMPLE INTERACTION:**
User Query: show pods
TOOL_REQUEST: {"tool": "get_pods", "args": {"namespace": "default"}}
TOOL_RESULT: [
  {"name": "nginx-123", "namespace": "default", "status": "Running", "node": "minikube", "ip": "10.1.1.1", "containers": [{"name": "nginx", "ready": true, "restart_count": 0}]},
  {"name": "api-456", "namespace": "default", "status": "Pending", "node": "minikube", "ip": null, "containers": [{"name": "api", "ready": false, "restart_count": 2}]}
]
YOUR RESPONSE MUST INCLUDE:
```
Pod Status Summary:
- Total pods in default namespace: 2
- Running: 1 (nginx-123)
- Pending: 1 (api-456)
- Problematic pods: api-456 (2 restarts, not ready)

Recommendation: Check logs for api-456 to diagnose why it's not running.
```

**RESPONSE FORMAT REQUIREMENTS:**
1. For tool results, ALWAYS format your response as:
   ```
   --- Real-Time Kubernetes Data ---
   [Summary of the data in table or bullet points]
   
   --- Analysis & Recommendations ---
   [Your insights and advice based on the data]
   ```

2. NEVER respond with just "I'll help you with that" or similar phrases without actual data.

3. If you receive empty results from a tool, explicitly state that (e.g., "No pods found in the default namespace").

Your task is to follow these steps to construct your answer:
1. **Analyze the User's Query**: Understand what Kubernetes information they need.
2. **Use the Appropriate Tool**: Select and call the right tool to fetch real-time data.
3. **Summarize the Results**: Create a clear, structured summary of the tool results.
4. **Provide Analysis**: Highlight issues, patterns, or important information.
5. **Give Recommendations**: Suggest next steps or fixes for any problems found.
"""

# Tool registry and tool-calling interface
TOOL_REGISTRY = {}
def register_tool(name):
    def decorator(func):
        TOOL_REGISTRY[name] = func
        return func
    return decorator
# Example tool registration
@register_tool("get_pods")
def tool_get_pods(namespace: str = "default"):
    if k8s_fetcher_available:
        from k8s_client_utils import get_pod_info
        return get_pod_info(namespace)
    return {"error": "Kubernetes fetcher not available"}

@register_tool("get_nodes")
def tool_get_nodes():
    if k8s_fetcher_available:
        from k8s_client_utils import get_node_info
        return get_node_info()
    return {"error": "Kubernetes fetcher not available"}

@register_tool("get_deployments")
def tool_get_deployments(namespace: str = "default"):
    if k8s_fetcher_available:
        from k8s_client_utils import get_deployment_info
        return get_deployment_info(namespace)
    return {"error": "Kubernetes fetcher not available"}

@register_tool("get_services")
def tool_get_services(namespace: str = "default"):
    if k8s_fetcher_available:
        from k8s_client_utils import get_service_info
        return get_service_info(namespace)
    return {"error": "Kubernetes fetcher not available"}

@register_tool("get_namespaces")
def tool_get_namespaces():
    if k8s_fetcher_available:
        from k8s_client_utils import get_namespace_info
        return get_namespace_info()
    return {"error": "Kubernetes fetcher not available"}

@register_tool("get_cluster_info")
def tool_get_cluster_info():
    if k8s_fetcher_available:
        from k8s_client_utils import get_cluster_info
        return get_cluster_info()
    return {"error": "Kubernetes fetcher not available"}

@register_tool("get_pod_logs")
def tool_get_pod_logs(pod_name: str, namespace: str = "default"):
    if k8s_fetcher_available:
        from k8s_knowledge_fetcher import fetch_pod_logs
        return fetch_pod_logs(pod_name, namespace)
    return {"error": "Kubernetes fetcher not available"}

@register_tool("get_events")
def tool_get_events(namespace: str = "default"):
    if k8s_fetcher_available:
        from k8s_knowledge_fetcher import fetch_k8s_info
        return fetch_k8s_info(f"get events in namespace {namespace}")
    return {"error": "Kubernetes fetcher not available"}

class ChatMessage:
    """Represents a message in the chat history."""
    
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the message to a dictionary."""
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp
        }

class KubernetesAgenticRAG:
    """Main class for the Kubernetes Agentic RAG system."""
    
    def __init__(self, rebuild_kb=False, debug=False):
        """Initialize the RAG system."""
        self.debug = debug
        self.messages = []
        
        # Initialize knowledge base
        self.initialize_knowledge_base(rebuild=rebuild_kb)
        
        # Initialize LLM
        self.initialize_llm()
        
        # Check if we have access to Kubernetes
        self.k8s_fetcher_available = False
        self.is_minikube = False
        
        try:
            # Try to initialize the Kubernetes client
            from k8s_client_utils import initialize_kubernetes_client, get_cluster_info
            api = initialize_kubernetes_client()
            
            # Check if we're connected to a cluster
            cluster_info = get_cluster_info(api)
            if cluster_info:
                self.k8s_fetcher_available = True
                self.is_minikube = cluster_info.get("is_minikube", False)
                if self.debug:
                    logger.info(f"[DEBUG] Connected to Kubernetes cluster: {cluster_info}")
        except Exception as e:
            if self.debug:
                logger.warning(f"[DEBUG] Failed to connect to Kubernetes: {e}")
            self.k8s_fetcher_available = False
    
    def clear_and_rebuild_collection(self):
        """Clears and rebuilds the knowledge base collection."""
        try:
            logger.info(f"Clearing collection: {self.collection.name}")
            self.client.delete_collection(name=self.collection.name)
            self.collection = get_or_create_collection(self.client)
            logger.info("Collection cleared. Rebuilding from sources...")

            # Here you would call your document loading functions
            # For this example, we'll assume a default loading mechanism exists
            # In a real app, you would load from JSON files or other sources
            # Example:
            # docs, metas, ids = load_documents_from_json('path/to/your/data.json')
            # add_documents_to_knowledge_base(self.collection, docs, metas, ids)

            logger.info("Knowledge base rebuild process initiated.")
        except Exception as e:
            logger.error(f"Failed to clear and rebuild collection: {e}")

    def initialize_knowledge_base(self, rebuild: bool = False):
        """Initialize the knowledge base."""
        try:
            # Get the ChromaDB client and collection
            client = get_chroma_client()
            self.collection = get_or_create_collection(client)
            
            # Check if the collection is empty or if rebuild is requested
            if rebuild or self.collection.count() == 0:
                logger.info("Building knowledge base...")
                
                # Load documents from JSON
                documents_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'k8s_docs.json')
                documents, metadatas, ids = load_documents_from_json(documents_path)
                
                if documents:
                    # Clear the collection if it exists
                    if self.collection.count() > 0:
                        self.collection.delete()
                        self.collection = get_or_create_collection(client)
                    
                    # Add documents to the collection with deduplication
                    add_documents_to_knowledge_base(self.collection, documents, metadatas, ids)
                    
                    # Build the BM25 index for hybrid search
                    build_bm25_index(self.collection)
                    
                    logger.info(f"Knowledge base initialized with {self.collection.count()} chunks")
                else:
                    logger.warning("No documents found for knowledge base")
            else:
                # Build the BM25 index for hybrid search if not rebuilding
                build_bm25_index(self.collection)
                
                logger.info(f"Using existing knowledge base with {self.collection.count()} chunks")
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {e}")
            self.collection = None
            
    def detect_minikube_environment(self):
        """Detect if the system is running in a Minikube environment."""
        try:
            # Use the k8s_knowledge_fetcher if available
            if k8s_fetcher_available:
                try:
                    return is_minikube_available()
                except Exception as e:
                    logger.warning(f"Error using k8s_knowledge_fetcher: {e}")
            
            # Fallback: try to detect from cluster info
            try:
                cluster_info = get_cluster_info()
                return cluster_info.get('is_minikube', False)
            except Exception as e:
                logger.warning(f"Error getting cluster info: {e}")
            
            return False
        except Exception as e:
            logger.warning(f"Error detecting Minikube environment: {e}")
            return False
    
    def initialize_llm(self):
        """Initialize the LLM for generating responses."""
        if llm_available:
            try:
                # Use the NVIDIA API key from environment variable or .env file
                nvidia_api_key = os.environ.get("NVIDIA_API_KEY")
                if not nvidia_api_key:
                    try:
                        from dotenv import load_dotenv
                        load_dotenv()
                        nvidia_api_key = os.environ.get("NVIDIA_API_KEY")
                    except Exception as e:
                        logger.warning(f"Could not load .env file: {e}")
                
                if not nvidia_api_key:
                    logger.warning("NVIDIA_API_KEY not set in environment or .env file. LLM will not be available.")
                    self.llm = None
                    return
                
                self.llm = NvidiaLLM(api_key=nvidia_api_key)
                logger.info("LLM initialized successfully with NVIDIA API.")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                self.llm = None
        else:
            logger.warning("LLM not available. Running in retrieval-only mode.")
            self.llm = None
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat history.
        
        Args:
            role: The role of the message sender (user or assistant).
            content: The content of the message.
        """
        message = ChatMessage(role, content)
        self.messages.append(message)
    
    def get_chat_history_as_text(self) -> str:
        """Get the chat history as a formatted text string.
        
        Returns:
            The formatted chat history.
        """
        history_text = ""
        for msg in self.messages:
            if msg.role == "user":
                history_text += f"User: {msg.content}\n"
            else:
                history_text += f"Assistant: {msg.content}\n"
        return history_text
    
    def validator_agent(self, user_query: str, context: str, real_time_data: str, main_answer: str) -> dict:
        """
        Validator agent: checks if the main answer is faithful, complete, and non-hallucinated.
        Returns a dict: {verdict: str, reason: str, suggestion: str}
        """
        if self.llm:
            prompt = (
                "You are a validator agent. Your job is to review the following answer for a Kubernetes user query.\n"
                "Check if the answer is:\n"
                "- Faithful to the provided context and real-time data\n"
                "- Complete (answers the user's question)\n"
                "- Free of hallucinations or unsupported claims\n"
                "If the answer is incomplete, hallucinated, or unfaithful, explain why and suggest what is missing.\n"
                "\nUser Query:\n" + user_query +
                "\nContext:\n" + context +
                "\nReal-Time Data:\n" + real_time_data +
                "\nMain Agent Answer:\n" + main_answer +
                "\n\nRespond in JSON: {verdict: string, reason: string, suggestion: string}"
            )
            try:
                result = self.llm.generate(prompt)
                import json
                # Extract JSON from result
                import re
                match = re.search(r'\{.*\}', result, re.DOTALL)
                if match:
                    return json.loads(match.group(0))
                else:
                    return {"verdict": "unknown", "reason": "Validator could not parse response.", "suggestion": "Manual review needed."}
            except Exception as e:
                return {"verdict": "error", "reason": str(e), "suggestion": "Validator failed."}
        else:
            # Simple rules-based fallback
            verdict = "faithful"
            reason = ""
            suggestion = ""
            if not main_answer or "no relevant information" in main_answer.lower():
                verdict = "incomplete"
                reason = "The answer is empty or says no relevant information."
                suggestion = "Try rephrasing the query or providing more context."
            return {"verdict": verdict, "reason": reason, "suggestion": suggestion}

    def chat(self, user_input: str, chat_history: str = "") -> str:
        """Process a user query and return a response."""
        try:
            start_time = time.time()
            
            # Check if the user's query is about Kubernetes resources
            k8s_resource_query = self.is_k8s_resource_query(user_input)
            
            # Log debug info
            if self.debug:
                logger.info(f"[DEBUG] User query: {user_input}")
                logger.info(f"[DEBUG] k8s_fetcher_available: {self.k8s_fetcher_available}, is_minikube: {self.is_minikube}")
            
            # Get context from knowledge base
            context_chunks = self.retrieve_context(user_input)
            
            # Initialize tool results
            tool_results = []
            
            # Format the input for the LLM
            llm_input = self.format_llm_input(user_input, context_chunks, chat_history, tool_results)
            
            # Get the response from the LLM
            response = self.get_llm_response(llm_input)
            
            # Check if the response contains a tool request
            tool_request = self.parse_tool_request(response)
            
            if tool_request and self.k8s_fetcher_available:
                # Execute the tool and get the results
                tool_name = tool_request.get("tool")
                tool_args = tool_request.get("args", {})
                
                if self.debug:
                    logger.info(f"[DEBUG] Tool request: {tool_name}, args: {tool_args}")
                
                # Execute the tool
                tool_results = self.execute_tool(tool_name, tool_args)
                
                # Format the input for the LLM with the tool results
                llm_input = self.format_llm_input(user_input, context_chunks, chat_history, tool_results)
                
                # Get the final response from the LLM
                response = self.get_llm_response(llm_input)
            
            # Process the LLM response to ensure data is shown
            final_response = self.process_llm_response(response, user_input, tool_results)
            
            # Log the time taken
            if self.debug:
                logger.info(f"[DEBUG] Response time: {time.time() - start_time:.2f}s")
            
            return final_response
        
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            return f"I encountered an error while processing your query: {str(e)}"

    def _is_k8s_info_query(self, query: str) -> bool:
        """Check if the query is asking for real-time Kubernetes information.
        
        Args:
            query: The user's query.
            
        Returns:
            True if the query is asking for real-time Kubernetes information, False otherwise.
        """
        # List of patterns that indicate a request for real-time Kubernetes information
        k8s_info_patterns = [
            r'\b(show|get|list|display|fetch)\b.*(pod|pods|node|nodes|deployment|deployments|service|services|namespace|namespaces)\b',
            r'\b(what|which)\b.*(pod|pods|node|nodes|deployment|deployments|service|services|namespace|namespaces)\b',
            r'\b(status|health|state)\b.*(cluster|minikube|pod|node|deployment|service)\b',
            r'\b(running|available)\b.*(pod|pods|node|nodes|deployment|deployments|service|services)\b',
            r'\b(log|logs)\b.*(pod|container)\b',
            r'\bminikube\b.*(status|info|information)\b',
            r'\bkubernetes\b.*(status|info|information)\b',
            r'\bk8s\b.*(status|info|information)\b',
            r'\bcluster\b.*(status|info|information)\b'
        ]
        
        # Check if any of the patterns match the query
        for pattern in k8s_info_patterns:
            if re.search(pattern, query.lower()):
                return True
        
        return False
    
    def _fallback_response(self, query: str, context: str) -> str:
        """Generate a fallback response when LLM is not available.
        
        Args:
            query: The user's query.
            context: The retrieved context.
            
        Returns:
            A fallback response.
        """
        return f"I found the following information that might help with your query about '{query}':\n\n{context}\n\nUnfortunately, I'm currently running in retrieval-only mode and cannot generate a detailed analysis. Please check the documentation or try again later when the LLM service is available."

    def _strip_pod_list_from_llm_output(self, llm_output: str) -> str:
        """Remove any markdown or formatted pod list from the LLM output."""
        import re
        lines = llm_output.splitlines()
        filtered = []
        in_pod_block = False
        for line in lines:
            # Detect start of pod list block (markdown, emoji, or table)
            if (
                line.strip().startswith('📦') or
                re.match(r'^[✅⚠️❌]', line.strip()) or
                line.strip().startswith('| Name') or
                line.strip().startswith('--- Real-Time Kubernetes Data ---')
            ):
                in_pod_block = True
                continue
            # End pod block if we hit a reasoning/summary section
            if in_pod_block and (
                line.strip().startswith('--- LLM Reasoning') or
                line.strip().startswith('###') or
                line.strip().startswith('Step') or
                line.strip().startswith('Analysis') or
                line.strip().startswith('Next Steps')
            ):
                in_pod_block = False
            if not in_pod_block:
                filtered.append(line)
        # Remove leading/trailing empty lines
        return '\n'.join([l for l in filtered if l.strip()])

    def agentic_reasoning_loop(self, user_input: str) -> str:
        """Implements an agentic reasoning loop that can call tools and reason about results."""
        context = self.retrieve_context(user_input)
        chat_history = self.get_chat_history_as_text()
        tool_results = []
        
        # First pass - check if we need to call tools
        llm_input = self.format_llm_input(user_input, context, chat_history, tool_results)
        llm_output = self.llm_generate(llm_input)
        
        # Parse for tool requests
        tool_request = self.parse_tool_request(llm_output)
        
        # Maximum tool calls to prevent infinite loops
        max_tool_calls = 3
        tool_calls = 0
        
        while tool_request and tool_calls < max_tool_calls:
            tool_calls += 1
            # Execute the tool
            tool_name = tool_request.get("tool")
            tool_args = tool_request.get("args", {})
            
            if tool_name in TOOL_REGISTRY:
                try:
                    result = TOOL_REGISTRY[tool_name](**tool_args)
                    # Format the result for the LLM
                    tool_results.append({
                        "request": tool_request,
                        "result": result
                    })
                    # Log the tool result for debugging
                    if self.debug:
                        print(f"TOOL RESULT: {json.dumps(result, indent=2)}")
                except Exception as e:
                    error_msg = f"Error executing tool {tool_name}: {str(e)}"
                    tool_results.append({
                        "request": tool_request,
                        "error": error_msg
                    })
            
            # Get the next action from the LLM
            llm_input = self.format_llm_input(user_input, context, chat_history, tool_results)
            llm_output = self.llm_generate(llm_input)
            
            # Check for more tool requests
            tool_request = self.parse_tool_request(llm_output)
        
        # Final response generation with all tool results
        final_llm_input = self.format_llm_input(user_input, context, chat_history, tool_results)
        final_response = self.llm_generate(final_llm_input)
        
        # FALLBACK: If the response doesn't include a proper summary of the tool results,
        # add a formatted summary ourselves
        if tool_results and not "Real-Time Kubernetes Data" in final_response:
            summary = self._format_tool_results_summary(tool_results)
            final_response = f"{summary}\n\n{final_response}"
        
        return final_response

    def _format_tool_results_summary(self, tool_results: list) -> str:
        """Format tool results into a structured summary when the LLM fails to do so."""
        summary = "--- Real-Time Kubernetes Data ---\n"
        
        for tool_result in tool_results:
            request = tool_result.get("request", {})
            result = tool_result.get("result", [])
            error = tool_result.get("error")
            
            tool_name = request.get("tool", "unknown_tool")
            
            if error:
                summary += f"\n{tool_name} error: {error}\n"
                continue
                
            if tool_name == "get_pods":
                summary += f"\nPod Status Summary:\n"
                if not result:
                    summary += "- No pods found in the specified namespace.\n"
                else:
                    summary += f"- Total pods: {len(result)}\n"
                    status_counts = {}
                    for pod in result:
                        status = pod.get("status", "Unknown")
                        if status not in status_counts:
                            status_counts[status] = 0
                        status_counts[status] += 1
                    
                    for status, count in status_counts.items():
                        summary += f"- {status}: {count}\n"
                    
                    # List pods with issues
                    problem_pods = []
                    for pod in result:
                        issues = []
                        if pod.get("status") != "Running":
                            issues.append(pod.get("status", "Unknown status"))
                        
                        for container in pod.get("containers", []):
                            if not container.get("ready", True):
                                issues.append("container not ready")
                            if container.get("restart_count", 0) > 0:
                                issues.append(f"{container.get('restart_count')} restarts")
                        
                        if issues:
                            problem_pods.append(f"- {pod.get('name')}: {', '.join(issues)}")
                    
                    if problem_pods:
                        summary += "\nPods with issues:\n"
                        summary += "\n".join(problem_pods)
            
            elif tool_name == "get_nodes":
                summary += f"\nNode Status Summary:\n"
                if not result:
                    summary += "- No nodes found in the cluster.\n"
                else:
                    summary += f"- Total nodes: {len(result)}\n"
                    for node in result:
                        ready_status = "Ready" if node.get("status", {}).get("Ready", {}).get("status") == "True" else "Not Ready"
                        summary += f"- {node.get('name')}: {ready_status}\n"
            
            elif tool_name == "get_deployments":
                summary += f"\nDeployment Status Summary:\n"
                if not result:
                    summary += "- No deployments found in the specified namespace.\n"
                else:
                    summary += f"- Total deployments: {len(result)}\n"
                    for dep in result:
                        replicas = dep.get("replicas", 0)
                        ready = dep.get("ready_replicas", 0) or 0
                        summary += f"- {dep.get('name')}: {ready}/{replicas} ready\n"
            
            elif tool_name == "get_services":
                summary += f"\nService Status Summary:\n"
                if not result:
                    summary += "- No services found in the specified namespace.\n"
                else:
                    summary += f"- Total services: {len(result)}\n"
                    for svc in result:
                        summary += f"- {svc.get('name')}: {svc.get('type')} (ClusterIP: {svc.get('cluster_ip')})\n"
            
            elif tool_name == "get_namespaces":
                summary += f"\nNamespace Status Summary:\n"
                if not result:
                    summary += "- No namespaces found in the cluster.\n"
                else:
                    summary += f"- Total namespaces: {len(result)}\n"
                    for ns in result:
                        summary += f"- {ns.get('name')}: {ns.get('status')}\n"
            
            elif tool_name == "get_cluster_info":
                summary += f"\nCluster Information:\n"
                if not result:
                    summary += "- Failed to retrieve cluster information.\n"
                else:
                    for key, value in result.items():
                        if key != "api_versions":  # Skip verbose API versions list
                            summary += f"- {key}: {value}\n"
            
            elif tool_name == "get_pod_logs":
                summary += f"\nPod Logs Summary:\n"
                if not result or isinstance(result, str) and "Error" in result:
                    summary += f"- {result}\n"
                else:
                    log_lines = result.split("\n")
                    summary += f"- Retrieved {len(log_lines)} log lines\n"
                    if len(log_lines) > 5:
                        summary += "- Last 5 log entries:\n"
                        for line in log_lines[-5:]:
                            summary += f"  {line}\n"
                    else:
                        summary += "- Log entries:\n"
                        for line in log_lines:
                            summary += f"  {line}\n"
        
        summary += "\n--- Analysis & Recommendations ---\n"
        return summary

    def retrieve_context(self, user_input: str):
        """
        Use hybrid RAG retrieval pipeline:
        1. Retrieve relevant chunks from the knowledge base using hybrid search
        2. Apply cross-encoder reranking
        3. Format the context for the LLM
        """
        try:
            # Get the collection
            client = get_chroma_client()
            collection = get_or_create_collection(client)
            
            # Use enhanced hybrid search
            context_chunks = hybrid_search(
                collection=collection,
                query_text=user_input,
                n_results=5,
                rerank_top_n=10
            )
            
            if self.debug:
                print(f"Retrieved {len(context_chunks)} context chunks")
                for i, chunk in enumerate(context_chunks):
                    print(f"Chunk {i+1}: {chunk['metadata'].get('source', 'unknown')} | {chunk['metadata'].get('heading', 'unknown')}")
                    print(f"Score: {chunk.get('cross_score', chunk.get('rrf_score', 0)):.4f}")
            
            return context_chunks
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def format_llm_input(self, user_input: str, context_chunks: list, chat_history: str, tool_results: list):
        """Format the input for the LLM."""
        prompt = f"{SYSTEM_PROMPT}\n\nUser Query: {user_input}"
        
        # Add chat history if available
        if chat_history:
            prompt += f"\n\nChat History:\n{chat_history}"
        
        # Add context chunks if available
        if context_chunks:
            prompt += f"\n\nRelevant Context from Knowledge Base:\n"
            for i, chunk in enumerate(context_chunks):
                source = chunk['metadata'].get('source', 'Unknown Source')
                heading = chunk['metadata'].get('heading', 'No Heading')
                content = chunk['document']
                score = chunk.get('cross_score', chunk.get('rrf_score', 0))
                prompt += f"\n---\nChunk {i+1} [Source: {source} | Section: {heading} | Relevance: {score:.2f}]\n{content}\n"
        
        # Add tool results if available
        if tool_results:
            for tr in tool_results:
                request = tr.get("request", {})
                result = tr.get("result", {})
                error = tr.get("error", None)
                
                tool_name = request.get("tool", "unknown_tool")
                tool_args = request.get("args", {})
                
                prompt += f"\n\nTOOL_REQUEST: {json.dumps(request)}"
                
                if error:
                    prompt += f"\nTOOL_ERROR: {error}"
                else:
                    prompt += f"\nTOOL_RESULT: {json.dumps(result, indent=2)}"
        
        return prompt

    def llm_generate(self, llm_input: str):
        if self.llm:
            try:
                return self.llm.generate(llm_input)
            except Exception as e:
                logger.error(f"Error in llm_generate: {e}")
                return "Sorry, I encountered an error while generating my response."
        else:
            return llm_input

    def parse_tool_request(self, llm_output: str):
        """Extract a tool request from the LLM response."""
        try:
            # Look for the tool request pattern
            tool_request_pattern = r"TOOL_REQUEST:\s*({.*?})"
            match = re.search(tool_request_pattern, llm_output, re.DOTALL)
            
            if match:
                tool_request_json = match.group(1).strip()
                
                # Clean up the JSON string
                # Replace newlines and extra whitespace
                tool_request_json = re.sub(r'\s+', ' ', tool_request_json)
                
                # Fix common JSON formatting issues
                if tool_request_json.endswith('"args": {') or tool_request_json.endswith('"args":{'): 
                    tool_request_json += '}'
                
                if not tool_request_json.endswith('}'):
                    tool_request_json += '}'
                
                # Try to parse the JSON
                try:
                    tool_request = json.loads(tool_request_json)
                    return tool_request
                except json.JSONDecodeError as e:
                    logger.error(f"Error parsing JSON: {e}")
                    logger.error(f"JSON string: {tool_request_json}")
                    
                    # Try to extract just the tool name and args
                    tool_name_match = re.search(r'"tool":\s*"([^"]+)"', tool_request_json)
                    if tool_name_match:
                        tool_name = tool_name_match.group(1)
                        
                        # Extract namespace if present
                        namespace_match = re.search(r'"namespace":\s*"([^"]+)"', tool_request_json)
                        namespace = namespace_match.group(1) if namespace_match else "default"
                        
                        return {
                            "tool": tool_name,
                            "args": {"namespace": namespace}
                        }
            
            return None
        except Exception as e:
            logger.error(f"Error extracting tool request: {e}")
            return None

    def process_llm_response(self, response, user_input, tool_results):
        """Process the LLM response, checking if tool calls were made and ensuring data is shown."""
        try:
            # Get the content from the response (response is already a string)
            content = response
            
            # Check if the response has the expected sections
            has_data_section = "Real-Time Kubernetes Data" in content
            has_analysis_section = "Analysis & Recommendations" in content
            
            # If the response doesn't have the expected sections and we have tool results,
            # apply a fallback formatter to ensure data is shown to the user
            if (not has_data_section or not has_analysis_section) and tool_results:
                logger.info("Applying fallback formatter to ensure data is shown")
                return self.apply_fallback_formatter(content, tool_results)
            
            return content
        
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return response
    
    def apply_fallback_formatter(self, response_content, tool_results):
        """Apply a fallback formatter to ensure data is shown to the user."""
        try:
            # Check if we have tool results to format
            if not tool_results:
                return response_content
            
            # Format the tool results
            formatted_data = self.format_tool_results(tool_results)
            
            # Create a structured response with sections
            structured_response = f"""
## Real-Time Kubernetes Data
{formatted_data}

## Analysis & Recommendations
{response_content}
"""
            return structured_response
        
        except Exception as e:
            logger.error(f"Error in fallback formatter: {e}")
            return response_content
    
    def format_tool_results(self, tool_results):
        """Format tool results into a readable format."""
        try:
            # Check if we have tool results
            if not tool_results:
                return "No data available."
            
            # Format based on the data type
            if isinstance(tool_results, list):
                # Check if it's a list of dictionaries (e.g., pods, nodes, etc.)
                if all(isinstance(item, dict) for item in tool_results):
                    # Get the keys from the first item
                    if tool_results and len(tool_results) > 0:
                        keys = list(tool_results[0].keys())
                        
                        # Format as a table
                        result = "| " + " | ".join(keys) + " |\n"
                        result += "| " + " | ".join(["---" for _ in keys]) + " |\n"
                        
                        for item in tool_results:
                            row = []
                            for key in keys:
                                value = item.get(key, "")
                                # Handle nested structures
                                if isinstance(value, (dict, list)):
                                    value = str(value)
                                row.append(str(value))
                            result += "| " + " | ".join(row) + " |\n"
                        
                        return result
                    else:
                        return "No items found."
                else:
                    # Simple list
                    return "\n".join([f"- {item}" for item in tool_results])
            elif isinstance(tool_results, dict):
                # Format dictionary
                return "\n".join([f"- **{key}**: {value}" for key, value in tool_results.items()])
            else:
                # String or other type
                return str(tool_results)
        
        except Exception as e:
            logger.error(f"Error formatting tool results: {e}")
            return "Error formatting tool results."

    def is_k8s_resource_query(self, query: str) -> bool:
        """Check if the query is about Kubernetes resources."""
        k8s_resource_keywords = [
            "pod", "pods", "node", "nodes", "deployment", "deployments",
            "service", "services", "namespace", "namespaces", "cluster",
            "get", "list", "show", "describe", "fetch", "status"
        ]
        
        query_lower = query.lower()
        for keyword in k8s_resource_keywords:
            if keyword in query_lower:
                return True
        
        return False

    def execute_tool(self, tool_name: str, tool_args: dict) -> any:
        """Execute a tool and return the results."""
        try:
            # Map tool names to functions
            tool_map = {
                "get_pods": self.get_pods,
                "get_nodes": self.get_nodes,
                "get_deployments": self.get_deployments,
                "get_services": self.get_services,
                "get_cluster_info": self.get_cluster_info,
                "get_cluster_status": self.get_cluster_status,
                "get_logs": self.get_logs
            }
            
            # Check if the tool exists
            if tool_name not in tool_map:
                logger.error(f"Unknown tool: {tool_name}")
                return None
            
            # Execute the tool
            tool_function = tool_map[tool_name]
            return tool_function(**tool_args)
        
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return None

    def get_pods(self, namespace: str = "default") -> list:
        """Get pods in a namespace."""
        try:
            # Initialize the Kubernetes client
            api = initialize_kubernetes_client()
            
            # Get pods in the namespace
            pods = api.list_namespaced_pod(namespace=namespace)
            
            # Format the results
            results = []
            for pod in pods.items:
                containers = []
                for container in pod.spec.containers:
                    container_status = next((s for s in pod.status.container_statuses if s.name == container.name), None)
                    containers.append({
                        "name": container.name,
                        "ready": container_status.ready if container_status else False,
                        "restart_count": container_status.restart_count if container_status else 0
                    })
                
                results.append({
                    "name": pod.metadata.name,
                    "namespace": pod.metadata.namespace,
                    "status": pod.status.phase,
                    "node": pod.spec.node_name,
                    "ip": pod.status.pod_ip,
                    "containers": containers
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting pods: {e}")
            return []

    def get_nodes(self) -> list:
        """Get nodes in the cluster."""
        try:
            # Initialize the Kubernetes client
            api = initialize_kubernetes_client()
            
            # Get nodes
            nodes = api.list_node()
            
            # Format the results
            results = []
            for node in nodes.items:
                # Determine if the node is ready
                ready_condition = next((c for c in node.status.conditions if c.type == "Ready"), None)
                status = "Ready" if ready_condition and ready_condition.status == "True" else "NotReady"
                
                # Determine the node role
                role = "worker"
                for label in node.metadata.labels:
                    if "node-role.kubernetes.io" in label:
                        role = label.split("/")[1]
                        break
                
                # Calculate age
                age = "unknown"
                if node.metadata.creation_timestamp:
                    age_delta = datetime.now(timezone.utc) - node.metadata.creation_timestamp
                    age = f"{age_delta.days}d"
                
                results.append({
                    "name": node.metadata.name,
                    "status": status,
                    "role": role,
                    "age": age
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting nodes: {e}")
            return []

    def get_deployments(self, namespace: str = "default") -> list:
        """Get deployments in a namespace."""
        try:
            # Initialize the Kubernetes client
            api = initialize_kubernetes_client(api_type="apps")
            
            # Get deployments
            deployments = api.list_namespaced_deployment(namespace=namespace)
            
            # Format the results
            results = []
            for deployment in deployments.items:
                # Calculate age
                age = "unknown"
                if deployment.metadata.creation_timestamp:
                    age_delta = datetime.now(timezone.utc) - deployment.metadata.creation_timestamp
                    age = f"{age_delta.days}d"
                
                results.append({
                    "name": deployment.metadata.name,
                    "namespace": deployment.metadata.namespace,
                    "replicas": deployment.spec.replicas,
                    "ready_replicas": deployment.status.ready_replicas or 0,
                    "available_replicas": deployment.status.available_replicas or 0,
                    "updated_replicas": deployment.status.updated_replicas or 0,
                    "age": age
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting deployments: {e}")
            return []

    def get_services(self, namespace: str = "default") -> list:
        """Get services in a namespace."""
        try:
            # Initialize the Kubernetes client
            api = initialize_kubernetes_client()
            
            # Get services
            services = api.list_namespaced_service(namespace=namespace)
            
            # Format the results
            results = []
            for service in services.items:
                # Calculate age
                age = "unknown"
                if service.metadata.creation_timestamp:
                    age_delta = datetime.now(timezone.utc) - service.metadata.creation_timestamp
                    age = f"{age_delta.days}d"
                
                # Get ports
                ports = []
                if service.spec.ports:
                    for port in service.spec.ports:
                        ports.append({
                            "name": port.name,
                            "port": port.port,
                            "target_port": port.target_port,
                            "protocol": port.protocol
                        })
                
                results.append({
                    "name": service.metadata.name,
                    "namespace": service.metadata.namespace,
                    "type": service.spec.type,
                    "cluster_ip": service.spec.cluster_ip,
                    "external_ip": service.spec.external_i_ps[0] if service.spec.external_i_ps else None,
                    "ports": ports,
                    "age": age
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error getting services: {e}")
            return []

    def get_logs(self, pod_name: str, namespace: str = "default", container: str = None, tail_lines: int = 100) -> str:
        """Get logs for a pod."""
        try:
            # Initialize the Kubernetes client
            api = initialize_kubernetes_client()
            
            # Get logs
            logs = api.read_namespaced_pod_log(
                name=pod_name,
                namespace=namespace,
                container=container,
                tail_lines=tail_lines
            )
            
            return logs
        
        except Exception as e:
            logger.error(f"Error getting logs: {e}")
            return ""

    def get_cluster_info(self) -> dict:
        """Get cluster info."""
        try:
            # Initialize the Kubernetes client
            api = initialize_kubernetes_client()
            
            # Get nodes
            nodes = api.list_node()
            
            # Get pods across all namespaces
            pods = api.list_pod_for_all_namespaces()
            
            # Get deployments across all namespaces
            apps_api = initialize_kubernetes_client(api_type="apps")
            deployments = apps_api.list_deployment_for_all_namespaces()
            
            # Get services across all namespaces
            services = api.list_service_for_all_namespaces()
            
            # Get persistent volumes
            pv_api = initialize_kubernetes_client(api_type="custom")
            persistent_volumes = pv_api.list_persistent_volume()
            
            # Return counts
            return {
                "nodes": len(nodes.items),
                "pods": len(pods.items),
                "deployments": len(deployments.items),
                "services": len(services.items),
                "persistent_volumes": len(persistent_volumes.items)
            }
        
        except Exception as e:
            logger.error(f"Error getting cluster info: {e}")
            return {
                "nodes": 0,
                "pods": 0,
                "deployments": 0,
                "services": 0,
                "persistent_volumes": 0
            }

    def get_cluster_status(self) -> dict:
        """Get detailed cluster status."""
        try:
            # Get nodes
            nodes = self.get_nodes()
            
            # Get pods in default namespace
            pods = self.get_pods(namespace="default")
            
            # Get deployments in default namespace
            deployments = self.get_deployments(namespace="default")
            
            # Return detailed status
            return {
                "nodes": nodes,
                "pods": pods,
                "deployments": deployments
            }
        
        except Exception as e:
            logger.error(f"Error getting cluster status: {e}")
            return {
                "nodes": [],
                "pods": [],
                "deployments": []
            }

    def get_llm_response(self, prompt: str):
        """Get a response from the LLM."""
        if self.llm:
            try:
                return self.llm.generate(prompt)
            except Exception as e:
                logger.error(f"Error in get_llm_response: {e}")
                raise
        else:
            logger.error("LLM not initialized")
            raise Exception("LLM not initialized")

def print_welcome_message(is_minikube=False, k8s_fetcher_available=False):
    """Print a welcome message for the CLI."""
    print(f"{Fore.CYAN}\nKubernetes Agentic RAG CLI Chat Interface{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}")
    print("Welcome to the Kubernetes Agentic RAG system!")
    print("Ask questions about Kubernetes concepts, troubleshooting, or best practices.")
    
    if is_minikube:
        print(f"{Fore.GREEN}Minikube environment detected! Responses will be tailored for Minikube.")
        print(f"{Fore.GREEN}For Minikube setup help, ask about 'minikube setup' or 'minikube addons'.")
        
        if k8s_fetcher_available:
            print(f"{Fore.GREEN}Real-time Kubernetes information fetching is enabled!")
            print(f"{Fore.GREEN}You can ask about your current Minikube cluster, such as:")
            print(f"{Fore.GREEN}  - 'Show me the pods in my cluster'")
            print(f"{Fore.GREEN}  - 'What services are running?'")
            print(f"{Fore.GREEN}  - 'Display node information'")
    
    print("Type 'exit', 'quit', or 'q' to end the session.")
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}\n")

def main():
    """Main function for the CLI."""
    parser = argparse.ArgumentParser(description="Kubernetes RAG CLI")
    parser.add_argument("--rebuild", action="store_true", help="Rebuild the knowledge base")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Initialize the RAG system
    rag_system = KubernetesAgenticRAG(rebuild_kb=args.rebuild, debug=args.debug)
    
    # Check if we have access to Kubernetes
    is_minikube = rag_system.is_minikube
    k8s_fetcher_available = rag_system.k8s_fetcher_available
    
    # Print welcome message
    print_welcome_message(is_minikube, k8s_fetcher_available)
    
    # Interactive chat loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n{Fore.GREEN}You:{Style.RESET_ALL} ")
            
            # Check for exit command
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\n{Fore.BLUE}Koda:{Style.RESET_ALL} Goodbye!")
                break
            
            # Process the query and get response
            print(f"\n{Fore.BLUE}Koda:{Style.RESET_ALL} Thinking...")
            response = rag_system.chat(user_input)
            
            # Print the response
            print(f"\n{Fore.BLUE}Koda:{Style.RESET_ALL} {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\n{Fore.RED}Error:{Style.RESET_ALL} {str(e)}")
            if args.debug:
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    main()
