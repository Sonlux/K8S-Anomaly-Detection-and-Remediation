import { Remediation } from "../types";

const API_BASE_URL = "http://localhost:5000/api";

export async function getRemediations(): Promise<Remediation[]> {
  try {
    const response = await fetch(`${API_BASE_URL}/remediations`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching remediations:", error);

    // If it's a network error, return mock data
    if (error instanceof TypeError) {
      console.log("Using mock remediation data due to API unavailability");
      return getMockRemediations();
    }

    throw error;
  }
}

// Mock data function to use when API is unavailable
const getMockRemediations = (): Remediation[] => {
  return [
    {
      id: "r1",
      anomalyId: "a1",
      status: "completed",
      action: "Scale Up Deployment",
      timestamp: new Date().toISOString(),
      details: "Increased replicas for 'api-service' from 2 to 4",
    },
    {
      id: "r2",
      anomalyId: "a2",
      status: "in_progress",
      action: "Restart Pod",
      timestamp: new Date().toISOString(),
      details: "Restarting 'data-processor' pod to clear memory leak",
    },
  ];
};

export const getRemediationById = async (
  id: string
): Promise<Remediation | undefined> => {
  console.warn(
    "getRemediationById is not fully implemented for real-time data."
  );
  return undefined;
};

export const updateRemediationStatus = async (
  id: string,
  status: Remediation["status"]
): Promise<Remediation | undefined> => {
  console.warn(
    "updateRemediationStatus is not fully implemented for real-time data."
  );
  return undefined;
};
