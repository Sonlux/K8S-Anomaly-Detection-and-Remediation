import React, { useState, useEffect } from "react";
import { getAnomalies } from "@/api/services/anomalies";
import { Anomaly } from "@/api/types";
import AnomalyCard from "./AnomalyCard";

interface RemediatedPodsProps {
  limit?: number;
}

const RemediatedPods: React.FC<RemediatedPodsProps> = ({ limit = 5 }) => {
  const [remediatedAnomalies, setRemediatedAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchRemediatedAnomalies = async () => {
    try {
      setLoading(true);
      const data = await getAnomalies();

      // Filter for resolved anomalies
      const resolvedAnomalies = data.filter(
        (anomaly) => anomaly.status === "resolved"
      );

      // Sort by timestamp (newest first)
      const sortedAnomalies = resolvedAnomalies
        .sort(
          (a, b) =>
            new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        )
        .slice(0, limit);

      setRemediatedAnomalies(sortedAnomalies);
      setError(null);
    } catch (err) {
      console.error("Error fetching remediated anomalies:", err);
      setError("Failed to load remediated pods");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRemediatedAnomalies();

    // Listen for remediation events from other components
    const handleRemediationEvent = (event: CustomEvent) => {
      fetchRemediatedAnomalies();
    };

    window.addEventListener(
      "anomalyRemediated",
      handleRemediationEvent as EventListener
    );

    return () => {
      window.removeEventListener(
        "anomalyRemediated",
        handleRemediationEvent as EventListener
      );
    };
  }, [limit]);

  const handleAnomalyClick = (anomaly: Anomaly) => {
    console.log("Remediated anomaly clicked:", anomaly);
    // Handle click event (e.g., show details, navigate to details page)
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Remediated Pods</h2>

      {loading ? (
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 p-4 rounded-md">{error}</div>
      ) : remediatedAnomalies.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No remediated pods</p>
          <p className="text-sm mt-2">No pods have been remediated yet</p>
        </div>
      ) : (
        remediatedAnomalies.map((anomaly) => (
          <AnomalyCard
            key={anomaly.id}
            anomaly={anomaly}
            onClick={handleAnomalyClick}
          />
        ))
      )}
    </div>
  );
};

export default RemediatedPods;
