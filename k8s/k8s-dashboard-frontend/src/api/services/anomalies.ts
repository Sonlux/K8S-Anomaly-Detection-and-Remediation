// src/api/services/anomalies.ts
import { Anomaly } from "../types";

const API_BASE_URL = "http://localhost:5000/api";

export async function getAnomalies(): Promise<Anomaly[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/metrics`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return transformMetricsToAnomalies(data);
  } catch (error) {
    console.error("Error fetching anomalies:", error);

    // If it's a network error, return mock data
    if (error instanceof TypeError) {
      console.log("Using mock anomaly data due to API unavailability");
      return getMockAnomalies();
    }

    throw error;
  }
}

// Transform metrics data into Anomaly objects
function transformMetricsToAnomalies(data: any[]): Anomaly[] {
  return data.map((item: any, index: number) => ({
    id: `a${index + 1}`,
    type: `Metrics for ${item.pod_name}`,
    severity: "medium", // Default severity, can be determined by metrics later
    description: `CPU: ${item.metrics["CPU Usage (%)"]?.toFixed(
      2
    )}%, Memory: ${item.metrics["Memory Usage (MB)"]?.toFixed(2)}MB`,
    timestamp: new Date().toISOString(),
    status: "detected",
    resource: `pod/${item.pod_name}`,
    namespace: item.namespace || "default",
  }));
}

// Mock data function to use when API is unavailable
const getMockAnomalies = (): Anomaly[] => {
  return [
    {
      id: "a1",
      type: "High CPU Usage",
      severity: "medium",
      description: "CPU: 85.5%, Memory: 512MB",
      timestamp: new Date().toISOString(),
      status: "detected",
      resource: "pod/api-service",
      namespace: "default",
    },
    {
      id: "a2",
      type: "Memory Leak",
      severity: "high",
      description: "CPU: 45.2%, Memory: 1024MB",
      timestamp: new Date().toISOString(),
      status: "investigating",
      resource: "pod/data-processor",
      namespace: "backend",
    },
  ];
};

export const getAnomalyById = async (
  id: string
): Promise<Anomaly | undefined> => {
  // This mock implementation will not work with real-time data without a backend change
  // For now, it will return undefined as we don't have a specific anomaly ID endpoint
  console.warn("getAnomalyById is not fully implemented for real-time data.");
  return undefined;
};

export const updateAnomalyStatus = async (
  id: string,
  status: Anomaly["status"]
): Promise<Anomaly | undefined> => {
  // This mock implementation will not work with real-time data without a backend change
  console.warn(
    "updateAnomalyStatus is not fully implemented for real-time data."
  );
  return undefined;
};
