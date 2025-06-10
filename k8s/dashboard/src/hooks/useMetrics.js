import { useState, useEffect } from 'react';
import { fetchPodMetrics } from '../services/api';

export const useMetrics = () => {
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getMetrics = async () => {
      try {
        setLoading(true);
        const data = await fetchPodMetrics();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch metrics');
      } finally {
        setLoading(false);
      }
    };

    getMetrics();

    // Set up polling every 30 seconds
    const intervalId = setInterval(getMetrics, 30000);

    return () => clearInterval(intervalId);
  }, []);

  return { metrics, loading, error };
};