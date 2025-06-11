// LLaMA API service for chatbot interactions
import { ChatMessage, ChatResponse } from "../types";

/**
 * Sends a message to the LLaMA API and returns the response
 * @param messages Array of chat messages representing the conversation history
 * @returns Promise with the LLaMA API response
 */
export const sendChatMessage = async (
  messages: ChatMessage[]
): Promise<ChatResponse> => {
  try {
    const response = await fetch("/api/llama/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ messages }),
    });

    if (!response.ok) {
      // Handle specific error status codes
      if (response.status === 503) {
        throw new Error(
          `API error: ${response.status} - Service Unavailable. The LLaMA API service is currently unavailable.`
        );
      } else {
        const errorData = await response.json().catch(() => null);
        const errorMessage =
          errorData?.error || `API error: ${response.status}`;
        throw new Error(errorMessage);
      }
    }

    return await response.json();
  } catch (error) {
    console.error("Error sending message to LLaMA API:", error);
    throw error;
  }
};

/**
 * Analyzes Kubernetes resources using the LLaMA API
 * @param resourceType Type of resource to analyze (pod, deployment, service, etc.)
 * @param resourceName Name of the resource
 * @param namespace Kubernetes namespace
 * @returns Promise with the analysis response
 */
export const analyzeResource = async (
  resourceType: string,
  resourceName: string,
  namespace: string
): Promise<ChatResponse> => {
  try {
    const response = await fetch("/api/llama/analyze", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ resourceType, resourceName, namespace }),
    });

    if (!response.ok) {
      // Handle specific error status codes
      if (response.status === 503) {
        throw new Error(
          `API error: ${response.status} - Service Unavailable. The LLaMA API service is currently unavailable.`
        );
      } else {
        const errorData = await response.json().catch(() => null);
        const errorMessage =
          errorData?.error || `API error: ${response.status}`;
        throw new Error(errorMessage);
      }
    }

    return await response.json();
  } catch (error) {
    console.error("Error analyzing resource with LLaMA API:", error);
    throw error;
  }
};
