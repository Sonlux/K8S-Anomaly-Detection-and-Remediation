#!/usr/bin/env python3
"""
Script to load Kubernetes knowledge base data from JSON into ChromaDB.

This script loads the Kubernetes documentation and troubleshooting data
from a JSON file into the ChromaDB vector database for use with the
Kubernetes Agentic RAG system.

Usage:
    python load_knowledge_base.py
"""

import os
import sys
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import RAG utilities
from rag_utils import (
    get_chroma_client,
    get_or_create_collection,
    load_documents_from_json,
    add_documents_to_knowledge_base
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function to load the knowledge base data."""
    # Path to the knowledge base JSON file
    json_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'k8s_knowledge.json')
    
    # Initialize ChromaDB client and collection
    try:
        client = get_chroma_client()
        collection = get_or_create_collection(client)
        
        # Load documents from JSON file
        documents, metadatas, ids = load_documents_from_json(json_file_path)
        
        if not documents:
            logger.error("No documents loaded from JSON file.")
            sys.exit(1)
        
        # Add documents to the knowledge base
        add_documents_to_knowledge_base(collection, documents, metadatas, ids)
        
        logger.info(f"Successfully loaded {len(documents)} documents into the knowledge base.")
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()