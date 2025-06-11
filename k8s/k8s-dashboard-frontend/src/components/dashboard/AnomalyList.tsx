import React, { useState, useEffect } from "react";
import { getAnomalies, updateAnomalyStatus } from "@/api/services/anomalies";
import { Anomaly } from "@/api/types";
import AnomalyCard from "./AnomalyCard";

interface AnomalyListProps {
  limit?: number;
}

const AnomalyList: React.FC<AnomalyListProps> = ({ limit = 5 }) => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true);
        const data = await getAnomalies();

        // Filter out resolved anomalies
        const activeAnomalies = data.filter(
          (anomaly) => anomaly.status !== "resolved"
        );

        // Sort by severity and timestamp
        const sortedAnomalies = activeAnomalies
          .sort((a, b) => {
            // First sort by severity (critical first)
            const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
            const severityA = severityOrder[a.severity.toLowerCase()] || 4;
            const severityB = severityOrder[b.severity.toLowerCase()] || 4;

            if (severityA !== severityB) {
              return severityA - severityB;
            }

            // Then by timestamp (newest first)
            return (
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
            );
          })
          .slice(0, limit);

        setAnomalies(sortedAnomalies);
        setError(null);
      } catch (err) {
        console.error("Error fetching anomalies:", err);
        setError("Failed to load anomalies");
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();

    // Listen for remediation events from other components
    const handleRemediationEvent = (event: CustomEvent) => {
      fetchAnomalies();
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
    console.log("Anomaly clicked:", anomaly);
    // Handle click event (e.g., show details, navigate to details page)
  };

  const handleRemediate = async (remediatedAnomaly: Anomaly) => {
    try {
      // Update the anomaly status in the backend
      await updateAnomalyStatus(remediatedAnomaly.id, "resolved");

      // Update the local state
      setAnomalies((prevAnomalies) =>
        prevAnomalies.filter((anomaly) => anomaly.id !== remediatedAnomaly.id)
      );

      console.log("Anomaly remediated:", remediatedAnomaly);

      // Emit a custom event that the page component can listen for
      const event = new CustomEvent("anomalyRemediated", {
        detail: { anomaly: remediatedAnomaly },
      });
      window.dispatchEvent(event);
    } catch (err) {
      console.error("Error remediating anomaly:", err);
      // You might want to show an error notification here
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold mb-4">Active Anomalies</h2>

      {loading ? (
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-50 text-red-700 p-4 rounded-md">{error}</div>
      ) : anomalies.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <p>No active anomalies</p>
          <p className="text-sm mt-2">All systems operating normally</p>
        </div>
      ) : (
        anomalies.map((anomaly) => (
          <AnomalyCard
            key={anomaly.id}
            anomaly={anomaly}
            onClick={handleAnomalyClick}
            onRemediate={handleRemediate}
          />
        ))
      )}
    </div>
  );
};

export default AnomalyList;
