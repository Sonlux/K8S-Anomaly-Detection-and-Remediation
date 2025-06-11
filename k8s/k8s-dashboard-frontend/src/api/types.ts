// TypeScript interfaces for API responses

// Chat interfaces for LLaMA API integration
export interface ChatMessage {
  role: "system" | "user" | "assistant";
  content: string;
  timestamp?: string;
}

export interface ChatResponse {
  message: ChatMessage;
  context?: {
    clusterInfo?: string;
    relatedResources?: string[];
    confidence?: number;
  };
}

export interface Anomaly {
  id: string;
  type: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  timestamp: string;
  status: "detected" | "investigating" | "resolved";
  resource?: string;
  namespace?: string;
}

export interface Remediation {
  id: string;
  anomalyId: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  action: string;
  timestamp: string;
  details?: string;
}

export interface Cluster {
  id: string;
  name: string;
  status: "healthy" | "degraded" | "unreachable";
  region: string;
  nodeCount: number;
  kubernetesVersion: string;
  cpuUtilization: number;
  memoryUtilization: number;
}
