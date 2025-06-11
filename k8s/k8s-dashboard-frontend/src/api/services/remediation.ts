import { Remediation } from "@/api/types";

const API_BASE_URL = "http://localhost:5000/api";

export const getRemediations = async (): Promise<Remediation[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/remediations`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error fetching remediations:", error);
    return [];
  }
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
