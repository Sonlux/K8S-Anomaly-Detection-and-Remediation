import { Cluster } from "../types";

const API_BASE_URL = "http://localhost:5000/api";

export async function getClusters(): Promise<Cluster[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/clusters`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching clusters:", error);

    // If it's a network error, return mock data
    if (error instanceof TypeError) {
      console.log("Using mock cluster data due to API unavailability");
      return getMockClusters();
    }

    throw error;
  }
}

// Mock data function to use when API is unavailable
const getMockClusters = (): Cluster[] => {
  return [
    {
      id: "c1",
      name: "production-cluster",
      status: "healthy",
      region: "us-west-2",
      nodeCount: 5,
      kubernetesVersion: "v1.27.3",
      cpuUtilization: 65,
      memoryUtilization: 72,
    },
    {
      id: "c2",
      name: "staging-cluster",
      status: "degraded",
      region: "us-east-1",
      nodeCount: 3,
      kubernetesVersion: "v1.26.5",
      cpuUtilization: 45,
      memoryUtilization: 38,
    },
  ];
};

export const getClusterById = async (
  id: string
): Promise<Cluster | undefined> => {
  console.warn("getClusterById is not fully implemented for real-time data.");
  return undefined;
};
