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
from datetime import datetime
import colorama
from colorama import Fore, Style
# Add this import near the top of your agentic_rag_cli.py file, with your other imports
from k8s_client_utils import initialize_kubernetes_client, get_cluster_info


# Initialize colorama for cross-platform colored terminal output
colorama.init(autoreset=True)

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RAG utilities
from rag_utils import (
    get_chroma_client,
    get_or_create_collection,
    query_knowledge_base,
    load_documents_from_json
)

# Import Kubernetes knowledge fetcher
# Import Kubernetes knowledge fetcher
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
You are Koda, a Kubernetes Anomaly Remediation Agent. Your job is to identify issues in Kubernetes clusters, 
explain them clearly, and suggest safe, practical resolutions.

You have access to a knowledge base of Kubernetes documentation, errors, and best practices.

When answering questions:
1. Analyze the query to understand what Kubernetes concept or issue is being asked about
2. Use the retrieved context from the knowledge base to inform your answer
3. Provide a clear, step-by-step explanation with a chain of thought
4. Include practical examples or kubectl commands when relevant
5. If you're unsure or the knowledge base doesn't contain relevant information, acknowledge this

Minikube-specific knowledge:
- Minikube runs a single-node Kubernetes cluster locally for development and testing
- Common Minikube commands include: minikube start, minikube stop, minikube dashboard
- Minikube addons can be enabled with: minikube addons enable <addon-name>
- For metrics collection in Minikube, the metrics-server addon must be enabled
- Prometheus can be accessed in Minikube via port-forwarding from the monitoring namespace
- To access Prometheus in Minikube: kubectl port-forward -n monitoring service/prometheus-server 9090:80
- Minikube has resource limitations compared to production clusters, so resource-intensive applications may need configuration adjustments
- Common Minikube troubleshooting includes checking VM driver compatibility, ensuring sufficient resources, and verifying addon status
- For persistent storage in Minikube, use the 'storage-provisioner' addon and PersistentVolumeClaims
- Minikube networking differs from production clusters; use 'minikube service' to access NodePort services

When detecting Minikube-specific issues:
1. Check if required addons are enabled (metrics-server, dashboard, etc.)
2. Verify resource allocation is sufficient for the workload
3. Consider Minikube's single-node architecture when diagnosing cluster-wide problems
4. Recommend Minikube-specific commands and approaches

Always prioritize accuracy over completeness. If you don't know something, say so.
"""

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
    
    def __init__(self, debug: bool = False):
        """Initialize the RAG system.
        
        Args:
            debug: Whether to enable debug logging.
        """
        self.debug = debug
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Initialize chat history
        self.chat_history: List[ChatMessage] = []
        
        # Initialize the knowledge base
        self.initialize_knowledge_base()
        
        # Initialize the LLM
        self.initialize_llm()
    
    def initialize_knowledge_base(self):
        """Initialize the ChromaDB knowledge base."""
        logger.info("Initializing knowledge base...")
        try:
            self.client = get_chroma_client()
            self.collection = get_or_create_collection(self.client)
            
            # Check if we have Minikube-specific knowledge in the collection
            # This is a simple check to see if we have any documents with 'minikube' in their content
            try:
                minikube_results = self.collection.query(
                    query_texts=["minikube"],
                    n_results=1
                )
                if minikube_results and minikube_results['documents'] and minikube_results['documents'][0]:
                    logger.info("Found Minikube-related knowledge in the knowledge base.")
                else:
                    logger.info("No Minikube-specific knowledge found. Consider adding Minikube documentation.")
            except Exception as query_err:
                logger.warning(f"Could not query for Minikube knowledge: {query_err}")
            
            # Check if running in a Minikube environment
            self.is_minikube = self.detect_minikube_environment()
            if self.is_minikube:
                logger.info("Detected Minikube environment - adapting responses accordingly")
                
            logger.info("Knowledge base initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            sys.exit(1)
            
    def detect_minikube_environment(self):
        """Detect if the system is running in a Minikube environment."""
        try:
            # Use the k8s_knowledge_fetcher if available
            if k8s_fetcher_available:
                try:
                    return is_minikube_available()
                except Exception as e:
                    logger.warning(f"Error using k8s_knowledge_fetcher: {e}")
            
            # Fallback: Try to import and use k8s_client_utils directly
            try:
                from k8s_client_utils import initialize_kubernetes_client, get_cluster_info
                if initialize_kubernetes_client():
                    cluster_info = get_cluster_info()
                    if cluster_info.get("is_minikube", False):
                        logger.info("Minikube detected via cluster info")
                        return True
            except Exception as e:
                logger.warning(f"Error using k8s_client_utils: {e}")
            
            # Method: Check via subprocess
            import subprocess
            try:
                result = subprocess.run(
                    ["minikube", "status"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    check=False
                )
                if result.returncode == 0 and "host: Running" in result.stdout:
                    logger.info("Minikube detected via status command")
                    return True
            except (subprocess.SubprocessError, FileNotFoundError):
                logger.warning("Could not run minikube status command")
            
            return False
            
        except Exception as e:
            logger.warning(f"Error detecting Minikube environment: {e}")
            return False



    
    def initialize_llm(self):
        """Initialize the LLM for generating responses."""
        if not llm_available:
            logger.warning("LLM modules not available. Running in retrieval-only mode.")
            self.llm = None
            return
        
        logger.info("Initializing LLM...")
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
                raise ValueError("NVIDIA_API_KEY not set in environment or .env file.")
            self.llm = NvidiaLLM(api_key=nvidia_api_key)
            logger.info("LLM initialized successfully with NVIDIA API.")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            logger.warning("Running in retrieval-only mode.")
            self.llm = None
    
    def add_message(self, role: str, content: str):
        """Add a message to the chat history.
        
        Args:
            role: The role of the message sender (user or assistant).
            content: The content of the message.
        """
        message = ChatMessage(role, content)
        self.chat_history.append(message)
    
    def get_chat_history_as_text(self) -> str:
        """Get the chat history as a formatted text string.
        
        Returns:
            The formatted chat history.
        """
        history_text = ""
        for msg in self.chat_history:
            if msg.role == "user":
                history_text += f"User: {msg.content}\n"
            else:
                history_text += f"Assistant: {msg.content}\n"
        return history_text
    
    def query(self, user_input: str) -> str:
        """Process a user query and generate a response.
        
        Args:
            user_input: The user's query text.
            
        Returns:
            The generated response.
        """
        # Add the user message to chat history
        self.add_message("user", user_input)

        # DEBUG: Log the query and minikube/k8s fetcher status
        logger.info(f"[DEBUG] User query: {user_input}")
        logger.info(f"[DEBUG] k8s_fetcher_available: {k8s_fetcher_available}, is_minikube: {getattr(self, 'is_minikube', None)}")

        # Check if the query is asking for real-time Kubernetes information
        k8s_info = None
        # Always try real-time fetch if k8s_fetcher_available, regardless of is_minikube
        if self._is_k8s_info_query(user_input) and k8s_fetcher_available:
            try:
                logger.info("[DEBUG] Attempting to fetch real-time Kubernetes information from cluster...")
                k8s_info = fetch_k8s_info(user_input)
                logger.info(f"[DEBUG] fetch_k8s_info result: {str(k8s_info)[:200]}")
            except Exception as e:
                logger.error(f"[DEBUG] Error fetching Kubernetes information: {e}")

        # Query the knowledge base
        try:
            results = query_knowledge_base(self.collection, user_input, n_results=3)
            retrieved_docs = results['documents'][0] if results['documents'] else []
            retrieved_metadatas = results['metadatas'][0] if results['metadatas'] else []
            
            if self.debug:
                logger.debug(f"Retrieved {len(retrieved_docs)} documents from knowledge base")
                for i, (doc, meta) in enumerate(zip(retrieved_docs, retrieved_metadatas)):
                    logger.debug(f"Document {i+1}: {doc[:100]}...")
                    logger.debug(f"Metadata {i+1}: {meta}")
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            retrieved_docs = []
            retrieved_metadatas = []
        
        # Format the context from retrieved documents
        context = "\n\n".join([f"Document {i+1} (Source: {meta.get('source', 'Unknown')}):\n{doc}" 
                              for i, (doc, meta) in enumerate(zip(retrieved_docs, retrieved_metadatas))])
        
        # If no documents were retrieved
        if not context:
            context = "No relevant information found in the knowledge base."
            
        # Add real-time Kubernetes information to the context if available
        if k8s_info:
            context = f"Real-time Kubernetes Information from Minikube:\n{k8s_info}\n\n" + context
        
        # Generate response using LLM if available
        if self.llm:
            # Prepare the prompt with system instructions, chat history, and retrieved context
            chat_history = self.get_chat_history_as_text()
            
            # Base prompt
            prompt = SYSTEM_PROMPT
            
            # Add Minikube-specific instruction if in Minikube environment
            if hasattr(self, 'is_minikube') and self.is_minikube:
                prompt += "\n\nIMPORTANT: You are currently analyzing a Minikube environment. Tailor your responses accordingly."
            
            # Complete the prompt with chat history, context and user input
            prompt += f"\n\nChat History:\n{chat_history}\n\nRelevant Context from Knowledge Base:\n{context}\n\nUser Query: {user_input}\n\nPlease provide a detailed response with chain-of-thought reasoning:"
            
            try:
                response = self.llm.generate(prompt)
            except Exception as e:
                logger.error(f"Error generating response from LLM: {e}")
                response = self._fallback_response(user_input, context)
        else:
            # Fallback to a simple response if LLM is not available
            response = self._fallback_response(user_input, context)
        
        # Add the assistant's response to chat history
        self.add_message("assistant", response)
        # Always show real-time Kubernetes info if available
        if k8s_info:
            combined = (
                f"--- Real-Time Kubernetes Data ---\n"
                f"{k8s_info}\n"
                f"--- LLM Reasoning & Guidance ---\n"
                f"{response}"
            )
            return combined
        else:
            return response
    
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
    """Main function to run the CLI chat interface."""
    parser = argparse.ArgumentParser(description="Kubernetes Agentic RAG CLI Chat Interface")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Initialize the RAG system
    try:
        rag_system = KubernetesAgenticRAG(debug=args.debug)
    except Exception as e:
        logger.error(f"Failed to initialize the RAG system: {e}")
        sys.exit(1)
    
    # Print welcome message with Minikube detection status and k8s fetcher availability
    is_minikube = hasattr(rag_system, 'is_minikube') and rag_system.is_minikube
    print_welcome_message(is_minikube, k8s_fetcher_available)
    
    # Main chat loop
    while True:
        try:
            # Get user input
            user_input = input(f"{Fore.GREEN}You:{Style.RESET_ALL} ")
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"\n{Fore.YELLOW}Thank you for using the Kubernetes Agentic RAG system. Goodbye!{Style.RESET_ALL}")
                break
            
            # Process the query and get response
            print(f"\n{Fore.BLUE}Koda:{Style.RESET_ALL} Thinking...")
            response = rag_system.query(user_input)
            
            # Print the response
            print(f"\n{Fore.BLUE}Koda:{Style.RESET_ALL} {response}\n")
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}Session interrupted. Exiting...{Style.RESET_ALL}")
            break
        except Exception as e:
            logger.error(f"Error in chat loop: {e}")
            print(f"\n{Fore.RED}An error occurred: {str(e)}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
