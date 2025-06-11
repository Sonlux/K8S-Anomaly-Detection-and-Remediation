// API endpoint definitions

// Base API URL
const API_BASE = "/api";

// Anomaly endpoints
export const ANOMALIES_ENDPOINT = `${API_BASE}/anomalies`;
export const ANOMALY_BY_ID_ENDPOINT = (id: string) =>
  `${API_BASE}/anomalies/${id}`;
export const UPDATE_ANOMALY_STATUS_ENDPOINT = (id: string) =>
  `${API_BASE}/anomalies/${id}/status`;

// Remediation endpoints
export const REMEDIATIONS_ENDPOINT = `${API_BASE}/remediations`;
export const REMEDIATION_BY_ID_ENDPOINT = (id: string) =>
  `${API_BASE}/remediations/${id}`;

// Cluster endpoints
export const CLUSTERS_ENDPOINT = `${API_BASE}/clusters`;
export const CLUSTER_BY_ID_ENDPOINT = (id: string) =>
  `${API_BASE}/clusters/${id}`;

// Metrics endpoints
export const METRICS_ENDPOINT = `${API_BASE}/metrics`;

// LLaMA API endpoints
export const LLAMA_CHAT_ENDPOINT = `${API_BASE}/llama/chat`;
export const LLAMA_ANALYZE_ENDPOINT = `${API_BASE}/llama/analyze`;
