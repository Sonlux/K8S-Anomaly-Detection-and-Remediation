import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Add request interceptor for authentication if needed
api.interceptors.request.use(
  (config) => {
    // You can add auth tokens here if needed
    return config;
  },
  (error) => Promise.reject(error)
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Handle API errors globally
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const fetchPodMetrics = async () => {
  const response = await api.get('/metrics');
  return response.data;
};

export const fetchAnomalies = async () => {
  const response = await api.get('/anomalies');
  return response.data;
};

export const executeRemediation = async (podName, action) => {
  const response = await api.post('/remediate', { podName, action });
  return response.data;
};

export const fetchInsights = async () => {
  const response = await api.get('/insights');
  return response.data;
};

export const fetchClusterTopology = async () => {
  const response = await api.get('/topology');
  return response.data;
};

export const fetchRemediationHistory = async () => {
  const response = await api.get('/remediation-history');
  return response.data;
};

export default api;