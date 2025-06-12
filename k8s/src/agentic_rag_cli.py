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

Usage:
    python agentic_rag_cli.py
"""

import os
import sys
import logging
import argparse
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import colorama
from colorama import Fore, Style

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
            logger.info("Knowledge base initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize knowledge base: {e}")
            sys.exit(1)
    
    def initialize_llm(self):
        """Initialize the LLM for generating responses."""
        if not llm_available:
            logger.warning("LLM modules not available. Running in retrieval-only mode.")
            self.llm = None
            return
        
        logger.info("Initializing LLM...")
        try:
            # Use the NVIDIA API key provided by the user
            nvidia_api_key = "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"
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
        
        # Generate response using LLM if available
        if self.llm:
            # Prepare the prompt with system instructions, chat history, and retrieved context
            chat_history = self.get_chat_history_as_text()
            
            prompt = f"{SYSTEM_PROMPT}\n\nChat History:\n{chat_history}\n\nRelevant Context from Knowledge Base:\n{context}\n\nUser Query: {user_input}\n\nPlease provide a detailed response with chain-of-thought reasoning:"
            
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
        
        return response
    
    def _fallback_response(self, query: str, context: str) -> str:
        """Generate a fallback response when LLM is not available.
        
        Args:
            query: The user's query.
            context: The retrieved context.
            
        Returns:
            A fallback response.
        """
        return f"I found the following information that might help with your query about '{query}':\n\n{context}\n\nUnfortunately, I'm currently running in retrieval-only mode and cannot generate a detailed analysis. Please check the documentation or try again later when the LLM service is available."

def print_welcome_message():
    """Print a welcome message for the CLI."""
    print(f"{Fore.CYAN}\nKubernetes Agentic RAG CLI Chat Interface{Style.RESET_ALL}")
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}")
    print("Welcome to the Kubernetes Agentic RAG system!")
    print("Ask questions about Kubernetes concepts, troubleshooting, or best practices.")
    print("Type 'exit', 'quit', or 'q' to end the session.")
    print(f"{Fore.CYAN}=========================================={Style.RESET_ALL}\n")

def main():
    """Main function to run the CLI chat interface."""
    parser = argparse.ArgumentParser(description="Kubernetes Agentic RAG CLI Chat Interface")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()
    
    # Print welcome message
    print_welcome_message()
    
    # Initialize the RAG system
    try:
        rag_system = KubernetesAgenticRAG(debug=args.debug)
    except Exception as e:
        logger.error(f"Failed to initialize the RAG system: {e}")
        sys.exit(1)
    
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