# Kubernetes Agentic RAG CLI

## Overview

The Kubernetes Agentic RAG CLI is an interactive command-line interface that allows you to query a knowledge base of Kubernetes documentation, troubleshooting guides, and best practices. It uses Retrieval Augmented Generation (RAG) to provide accurate, context-aware responses to your Kubernetes-related questions.

## Features

- **Interactive Chat Interface**: Engage in a conversational experience with the Kubernetes knowledge assistant
- **Chain of Thought Reasoning**: Get detailed explanations that show the reasoning process
- **Knowledge Base Integration**: Leverages ChromaDB and embeddings to retrieve relevant information
- **LLM-Powered Responses**: Uses the same LLM providers as the main Kubernetes multi-agent system
- **Context-Aware Answers**: Maintains chat history to provide coherent, contextual responses
- **Colored Output**: Easy-to-read terminal output with color-coded messages

## Prerequisites

- Python 3.9+
- Virtual environment with dependencies installed (see `requirements.txt`)
- Access to LLM API (optional, falls back to retrieval-only mode if not available)

## Installation

The CLI is already integrated with the Kubernetes project. All dependencies should be installed in the virtual environment.

## Usage

### Starting the CLI

#### Windows

```powershell
.\run_agentic_rag_cli.ps1
```

#### Linux/macOS

```bash
./run_agentic_rag_cli.sh
```

Or manually:

```bash
# Activate the virtual environment
.venv/scripts/activate  # Windows
source .venv/bin/activate  # Linux/macOS

# Run the CLI
python src/agentic_rag_cli.py
```

### Debug Mode

To run with debug logging enabled:

```bash
python src/agentic_rag_cli.py --debug
```

### Example Queries

Here are some example queries you can try:

- "What are Kubernetes Pods and how do they work?"
- "How do I troubleshoot a pod in CrashLoopBackOff state?"
- "What's the difference between a Deployment and a StatefulSet?"
- "How can I scale my application automatically in Kubernetes?"
- "What are best practices for securing a Kubernetes cluster?"

## How It Works

1. **Knowledge Base**: The system uses ChromaDB as a vector database to store and retrieve documents
2. **Embeddings**: Documents are converted to vector embeddings using the Sentence Transformers model
3. **Retrieval**: When you ask a question, the system finds the most relevant documents
4. **Generation**: The retrieved documents and your question are sent to an LLM to generate a comprehensive response
5. **Chain of Thought**: The LLM is prompted to show its reasoning process for complex questions

## Integration with Kubernetes Project

The Agentic RAG CLI integrates with the existing Kubernetes project in several ways:

- Uses the same `rag_utils.py` module for knowledge base operations
- Leverages the LLM initialization from the multi-agent system
- Accesses the same ChromaDB knowledge base
- Follows the same architectural patterns as the main project

## Extending the Knowledge Base

You can extend the knowledge base by adding more documents to the `k8s_knowledge.json` file in the `data` directory. The file should follow this format:

```json
[
  {
    "id": "unique-id",
    "content": "Document content goes here",
    "metadata": {
      "source": "Document source",
      "topic": "Document topic"
    }
  }
]
```

## Troubleshooting

- **LLM Not Available**: If the LLM initialization fails, the system will fall back to retrieval-only mode
- **Knowledge Base Issues**: Check that the ChromaDB directory exists and has permissions
- **Virtual Environment**: Ensure you're using the correct virtual environment with all dependencies

## License

This project is licensed under the same terms as the main Kubernetes project.