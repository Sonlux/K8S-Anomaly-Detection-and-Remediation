# NVIDIA API Integration for Kubernetes Multi-Agent System

This document provides information about the NVIDIA API integration for the Kubernetes Multi-Agent System, which enables enhanced LLM capabilities for anomaly detection, remediation, and analysis.

## Overview

The system integrates with NVIDIA's API to leverage the Llama 3.3 70B Instruct model for advanced natural language processing tasks. This integration is implemented in two ways:

1. **Direct OpenAI Client**: Using the `openai` Python package to directly interact with NVIDIA's API
2. **LangChain Integration**: Using the `langchain-nvidia-ai-endpoints` package for a more abstracted interface

## Implementation Details

### NvidiaLLM Class

The `NvidiaLLM` class in `src/agents/nvidia_llm.py` provides a wrapper for NVIDIA's LLM API using the Llama 3.3 70B Instruct model. It includes methods for:

- Generating text responses
- Analyzing Kubernetes metrics
- Streaming responses

### LlamaLLM Class

The `LlamaLLM` class in `src/agents/k8s_multi_agent_system.py` provides a more general wrapper that can work with different LLM providers, including NVIDIA. It automatically detects NVIDIA API keys and adjusts the base URL and model accordingly.

## Setup and Testing

### Requirements

The following packages are required for the NVIDIA API integration:

```
openai>=1.3.5
langchain>=0.0.267
langchain-openai>=0.0.2
langchain-nvidia-ai-endpoints>=0.0.1 (optional)
```

### Setup Script

A PowerShell script `setup_and_test_nvidia_api.ps1` is provided to set up the environment and test the NVIDIA API integration. It performs the following steps:

1. Creates a virtual environment (if it doesn't exist)
2. Activates the virtual environment
3. Installs the required dependencies
4. Runs the test script
5. Deactivates the virtual environment

### Test Script

The test script `tests/test_nvidia_api.py` demonstrates both the direct OpenAI client and LangChain approaches for interacting with NVIDIA's API. It includes examples of:

- Non-streaming responses
- Streaming responses
- Different prompts and parameters

## Usage

### Environment Variables

The following environment variables can be used to configure the NVIDIA API integration:

- `NVIDIA_API_KEY`: Your NVIDIA API key (should start with `nvapi-`)
- `LLAMA_API_KEY`: Can also be set to a NVIDIA API key for compatibility
- `LLAMA_API_URL`: Base URL for the API (defaults to NVIDIA's URL when using a NVIDIA key)

### Example Usage

```python
# Using NvidiaLLM
from nvidia_llm import NvidiaLLM

api_key = "nvapi-your-key-here"
llm = NvidiaLLM(api_key=api_key)

# Generate a response
response = llm.generate("What is Kubernetes?")
print(response)

# Stream a response
for chunk in llm.generate("Explain pod scheduling in Kubernetes.", stream=True):
    print(chunk, end="")
```

## Integration with Multi-Agent System

The NVIDIA API integration is used in the Kubernetes Multi-Agent System for:

1. **Anomaly Detection**: Analyzing metrics and providing insights
2. **Remediation**: Generating remediation plans for detected issues
3. **User Interaction**: Providing natural language responses to user queries

## Troubleshooting

- If you encounter authentication errors, ensure your API key is correct and has the necessary permissions
- If you experience timeout errors, try adjusting the `max_tokens` parameter to a lower value
- For other issues, check the logs for detailed error messages