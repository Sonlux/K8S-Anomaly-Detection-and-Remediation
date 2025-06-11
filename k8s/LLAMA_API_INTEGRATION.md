# LLaMA API Integration for Kubernetes Dashboard

## Overview

This document describes the integration of the LLaMA API with the Kubernetes Dashboard application. The LLaMA API provides intelligent responses to Kubernetes queries, anomaly analysis, and remediation suggestions.

## Architecture

The integration consists of the following components:

1. **Frontend Components**:

   - `Chatbot.tsx`: React component for user interaction
   - `llama.ts`: API service for communicating with the backend
   - Types and interfaces in `types.ts`
   - Endpoint definitions in `endpoints.ts`

2. **Backend Components**:
   - `llama_routes.py`: Flask routes for handling LLaMA API requests
   - `LlamaLLM` class in `k8s_multi_agent_system.py`: Wrapper for the LLaMA API

## API Endpoints

### Chat Endpoint

```
POST /api/llama/chat
```

**Request Body**:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are Koda, an intelligent Kubernetes anomaly detection and remediation specialist.",
      "timestamp": "2023-06-01T12:00:00Z"
    },
    {
      "role": "user",
      "content": "What could be causing high CPU usage in my cluster?",
      "timestamp": "2023-06-01T12:01:00Z"
    }
  ]
}
```

**Response**:

```json
{
  "message": {
    "role": "assistant",
    "content": "High CPU usage in your Kubernetes cluster could be caused by several factors...",
    "timestamp": "2023-06-01T12:01:05Z"
  },
  "context": {
    "confidence": 0.85,
    "relatedResources": ["deployment/resource-intensive-app", "node/worker-1"]
  }
}
```

### Analyze Endpoint

```
POST /api/llama/analyze
```

**Request Body**:

```json
{
  "resourceType": "deployment",
  "resourceName": "frontend-app",
  "namespace": "production"
}
```

**Response**:

```json
{
  "message": {
    "role": "assistant",
    "content": "Analysis of deployment 'frontend-app' in namespace 'production'...",
    "timestamp": "2023-06-01T12:05:00Z"
  },
  "context": {
    "confidence": 0.9,
    "clusterInfo": "Namespace: production",
    "relatedResources": ["deployment/frontend-app"]
  }
}
```

## Frontend Usage

### Sending a Chat Message

```typescript
import { sendChatMessage } from "../api/services/llama";
import { ChatMessage, ChatResponse } from "../api/types";

// Create chat history
const chatHistory: ChatMessage[] = [
  {
    role: "user",
    content: "What are the best practices for pod security?",
    timestamp: new Date().toISOString(),
  },
];

// Send message to LLaMA API
const response: ChatResponse = await sendChatMessage(chatHistory);

// Use the response
console.log(response.message.content);
```

### Analyzing a Resource

```typescript
import { analyzeResource } from "../api/services/llama";
import { ChatResponse } from "../api/types";

// Analyze a Kubernetes resource
const analysis: ChatResponse = await analyzeResource(
  "deployment",
  "api-server",
  "default"
);

// Use the analysis
console.log(analysis.message.content);
console.log(analysis.context.relatedResources);
```

## Backend Configuration

The LLaMA API integration requires the following environment variables:

- `LLAMA_API_KEY`: API key for the LLaMA service
- `LLAMA_API_BASE_URL`: Base URL for the LLaMA API (defaults to NVIDIA API if not provided)

If these variables are not provided, the system will fall back to the NVIDIA API with the default key.

## Error Handling

The frontend components include error handling for API failures, displaying appropriate error messages to the user. The backend routes also include error handling to return meaningful error responses.

## Future Enhancements

1. **Streaming Responses**: Implement streaming for long responses
2. **Context Awareness**: Enhance the system's awareness of cluster state
3. **Resource Suggestions**: Provide specific resource suggestions based on anomalies
4. **Integration with Metrics**: Use real-time metrics to inform responses
5. **Custom Prompts**: Allow users to customize the system prompt
