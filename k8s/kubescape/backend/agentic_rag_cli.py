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

You will be given context from a knowledge base containing Kubernetes documentation, best practices, and troubleshooting guides. This context is provided in chunks, each with a source and a section heading.

Your task is to follow these steps to construct your answer:
1.  **Analyze the User's Query**: Understand the core problem or question the user is asking.
2.  **Synthesize Information**: Review all the provided context chunks. Identify the most relevant pieces of information from each chunk that address the user's query.
3.  **Formulate a Chain of Thought**:
    *   Start by stating the primary issue or topic.
    *   Build a step-by-step explanation by combining information from the relevant chunks.
    *   When you use information from a chunk, reference its source and section (e.g., "[Source: k8s_docs | Section: Pod Lifecycle]").
    *   If multiple chunks contribute to a point, synthesize them into a coherent paragraph.
4.  **Provide Actionable Recommendations**: If the query is about a problem, offer clear, numbered steps for diagnosis and resolution. Include `kubectl` commands where appropriate.
5.  **Acknowledge Limitations**: If the provided context does not contain enough information to fully answer the query, state what's missing and suggest what the user could look for.

**Example of a good response:**
> The `CrashLoopBackOff` error you're seeing indicates that a container in your pod is starting and then repeatedly crashing.
>
> Here's a breakdown of how to troubleshoot this, based on the provided context:
> 1.  **Check Container Logs**: The first step is to inspect the logs of the crashing container to find out why it's failing. You can do this with the command `kubectl logs <pod-name> -c <container-name>` [Source: k8s_troubleshooting | Section: Debugging Pods].
> 2.  **Review Resource Limits**: Insufficient memory or CPU can also cause crashes. Ensure the pod has adequate resources defined in its manifest [Source: k8s_best_practices | Section: Resource Management].
> 3.  **Verify Liveness Probes**: An incorrectly configured liveness probe could be terminating your container prematurely. Check your deployment configuration for the probe's settings [Source: k8s_docs | Section: Liveness and Readiness Probes].

Always prioritize accuracy and clarity. Your goal is to be a helpful and trustworthy assistant.
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
        """Initialize the ChromaDB knowledge base."""
        logger.info("Initializing knowledge base...")
        try:
            self.client = get_chroma_client()
            self.collection = get_or_create_collection(self.client)

            if rebuild:
                self.clear_and_rebuild_collection()
            
            # Check if the collection is empty and may need initial population
            if self.collection.count() == 0:
                logger.info("Knowledge base is empty. Consider loading documents.")
                # You might want to automatically trigger a build process here
            
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
        real_time_data = None
        real_time_data_type = None
        pod_data = None
        
        # Always try real-time fetch if k8s_fetcher_available, regardless of is_minikube
        if self._is_k8s_info_query(user_input) and k8s_fetcher_available:
            try:
                logger.info("[DEBUG] Attempting to fetch real-time Kubernetes information from cluster...")
                k8s_info = fetch_k8s_info(user_input)
                logger.info(f"[DEBUG] fetch_k8s_info result: {str(k8s_info)[:200]}")

                # Determine the type of resource being queried
                lowered = user_input.lower()
                if "pod" in lowered:
                    real_time_data_type = "pods"
                    # Get structured pod data from k8s_client_utils
                    from k8s_client_utils import get_pod_info
                    if "all namespaces" in lowered or "--all-namespaces" in lowered:
                        from kubernetes import client
                        core_api = client.CoreV1Api()
                        pods = core_api.list_pod_for_all_namespaces().items
                        pod_data = []
                        for pod in pods:
                            containers = []
                            for c in pod.status.container_statuses or []:
                                container_info = {
                                    'name': c.name,
                                    'image': c.image,
                                    'ready': c.ready,
                                    'restart_count': c.restart_count,
                                    'state': list(c.state.to_dict().keys())[0] if c.state else None,
                                    'reason': getattr(c.state.waiting, 'reason', '') if c.state and c.state.waiting else ''
                                }
                                containers.append(container_info)
                            pod_data.append({
                                'name': pod.metadata.name,
                                'namespace': pod.metadata.namespace,
                                'status': pod.status.phase,
                                'node': pod.spec.node_name,
                                'ip': pod.status.pod_ip,
                                'containers': containers
                            })
                        real_time_data = pod_data
                    else:
                        namespace = 'default'
                        if 'namespace' in lowered:
                            import re
                            ns_match = re.search(r'namespace\s+([^\s]+)', lowered)
                            if ns_match:
                                namespace = ns_match.group(1)
                        pod_data = get_pod_info(namespace)
                        real_time_data = pod_data
                elif "node" in lowered:
                    real_time_data_type = "nodes"
                    from k8s_client_utils import get_node_info
                    real_time_data = get_node_info()
                elif "deployment" in lowered:
                    real_time_data_type = "deployments"
                    from k8s_client_utils import get_deployment_info
                    namespace = 'default'
                    if 'namespace' in lowered:
                        import re
                        ns_match = re.search(r'namespace\s+([^\s]+)', lowered)
                        if ns_match:
                            namespace = ns_match.group(1)
                    real_time_data = get_deployment_info(namespace)
                elif "service" in lowered:
                    real_time_data_type = "services"
                    from k8s_client_utils import get_service_info
                    namespace = 'default'
                    if 'namespace' in lowered:
                        import re
                        ns_match = re.search(r'namespace\s+([^\s]+)', lowered)
                        if ns_match:
                            namespace = ns_match.group(1)
                    real_time_data = get_service_info(namespace)
                elif "namespace" in lowered:
                    real_time_data_type = "namespaces"
                    from k8s_client_utils import get_namespace_info
                    real_time_data = get_namespace_info()
                elif any(word in lowered for word in ['status', 'cluster', 'overview', 'health']):
                    real_time_data_type = "cluster"
                    from k8s_client_utils import get_cluster_info
                    real_time_data = get_cluster_info()
                else:
                    real_time_data_type = None
                    real_time_data = None
            except Exception as e:
                logger.error(f"[DEBUG] Error fetching Kubernetes information: {e}")
                real_time_data = None
                real_time_data_type = None

        # Query the knowledge base
        try:
            results = query_knowledge_base(self.collection, user_input, n_results=3)
            retrieved_docs = results['documents'][0] if results['documents'] else []
            retrieved_metadatas = results['metadatas'][0] if results['metadatas'] else []
            retrieved_distances = results['distances'][0] if results['distances'] else []
            
            if self.debug:
                logger.debug(f"Retrieved {len(retrieved_docs)} document chunks from knowledge base")
                for i, (doc, meta, dist) in enumerate(zip(retrieved_docs, retrieved_metadatas, retrieved_distances)):
                    logger.debug(f"  Chunk {i+1}: (Distance: {dist:.4f}) Source: {meta.get('source')} | Heading: {meta.get('heading')}")
                    logger.debug(f"    Content: {doc[:100]}...")
        except Exception as e:
            logger.error(f"Error querying knowledge base: {e}")
            retrieved_docs = []
            retrieved_metadatas = []
        
        # Format the context from retrieved chunks with metadata
        context_chunks = []
        for i, (doc, meta) in enumerate(zip(retrieved_docs, retrieved_metadatas)):
            source = meta.get('source', 'Unknown Source')
            heading = meta.get('heading', 'No Heading')
            chunk_content = f"Source: {source} | Section: {heading}\nContent: {doc}"
            context_chunks.append(chunk_content)
        
        context = "\n---\n".join(context_chunks)
        
        # If no documents were retrieved
        if not context:
            context = "No relevant information found in the knowledge base."
        
        # Generate response using LLM if available
        if self.llm:
            # Prepare the prompt with system instructions, chat history, and retrieved context
            chat_history = self.get_chat_history_as_text()
            
            # Base prompt
            prompt = SYSTEM_PROMPT
            
            # Add Minikube-specific instruction if in Minikube environment
            if hasattr(self, 'is_minikube') and self.is_minikube:
                prompt += "\n\nIMPORTANT: You are currently analyzing a Minikube environment. Tailor your responses accordingly."
            
            # Add real-time data to the prompt if available
            if real_time_data is not None and real_time_data_type is not None:
                if real_time_data_type == "cluster":
                    prompt += (
                        "\n\nYou are given the following real-time Kubernetes cluster summary as a JSON object. "
                        "Your job is to:\n"
                        "1. Summarize the overall cluster health (is minikube, node count, pod count, namespace count, etc.).\n"
                        "2. Highlight any potential issues (e.g., only 1 node, high pod count, minikube limitations, etc.).\n"
                        "3. List the most important findings in bullet points.\n"
                        "4. Give specific, actionable recommendations for improving or monitoring the cluster.\n"
                        "5. If everything is healthy, say so clearly.\n"
                        "Example:\n"
                        "Cluster Data:\n"
                        "{'is_minikube': True, 'node_count': 1, 'namespace_count': 8, 'pod_count': 42, ...}\n"
                        "Summary:\n"
                        "- Minikube environment detected (single-node cluster).\n"
                        "- 1 node, 8 namespaces, 42 pods.\n"
                        "- No immediate issues detected, but single-node clusters are not highly available.\n"
                        "Recommendations:\n"
                        "1. Monitor pod and node health regularly.\n"
                        "2. For production, consider a multi-node cluster for high availability.\n"
                        "If no issues are found, say: 'Cluster is healthy and running as expected.'\n"
                        f"Cluster Data:\n{json.dumps(real_time_data, indent=2)}\n\n"
                    )
                else:
                    prompt += (
                        f"\n\nYou are given the following real-time Kubernetes {real_time_data_type} data as a JSON object or array. "
                        "Your job is to:\n"
                        "1. Summarize the overall state (e.g., how many are Running, Pending, Failed, etc.).\n"
                        f"2. Highlight any {real_time_data_type} with high restart counts, non-running states, or other issues.\n"
                        "3. List the most important issues in bullet points or a table.\n"
                        "4. Give specific, actionable recommendations for the issues you find (e.g., check logs, increase resources, fix image pull errors).\n"
                        "5. If everything is healthy, say so clearly.\n"
                        "Example:\n"
                        "Pod Data:\n"
                        "[{'name': 'my-app', 'status': 'CrashLoopBackOff', 'restart_count': 12}, ...]\n"
                        "Summary:\n"
                        "- 1 pod in CrashLoopBackOff (my-app)\n"
                        "- 2 pods Pending\n"
                        "- 5 pods Running\n"
                        "Issues:\n"
                        "- my-app is crashing repeatedly (12 restarts). Check logs for errors.\n"
                        "- pod xyz is Pending. Check for resource constraints.\n"
                        "Recommendations:\n"
                        "1. Run `kubectl logs my-app` to investigate crashes.\n"
                        "2. Check node resources for Pending pods.\n"
                        "If no issues are found, say: 'All pods are healthy and running.'\n"
                        f"{real_time_data_type.capitalize()} Data:\n{json.dumps(real_time_data, indent=2)}\n\n"
                    )
            
            # Complete the prompt with chat history, context and user input
            prompt += f"\n\nChat History:\n{chat_history}\n\nRelevant Context from Knowledge Base:\n{context}\n\nUser Query: {user_input}\n\nPlease provide a detailed response with chain-of-thought reasoning:"
            
            try:
                response = self.llm.generate(prompt)
                response = self._strip_pod_list_from_llm_output(response)
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
    parser.add_argument("--rebuild-kb", action="store_true", help="Clear and rebuild the knowledge base")
    args = parser.parse_args()
    
    # Initialize the RAG system
    try:
        rag_system = KubernetesAgenticRAG(debug=args.debug)
        if args.rebuild_kb:
            rag_system.clear_and_rebuild_collection()
            # After rebuilding, you might want to exit or continue
            print("Knowledge base has been rebuilt. Please restart the application.")
            sys.exit(0)

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
