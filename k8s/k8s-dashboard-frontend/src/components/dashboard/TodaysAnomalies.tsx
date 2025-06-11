import React, { useState, useEffect } from "react";
import { Anomaly } from "@/api/types";
import { getAnomalies, updateAnomalyStatus } from "@/api/services/anomalies";
import AnomalyCard from "./AnomalyCard";

interface TodaysAnomaliesProps {
  limit?: number;
  onAnomalyClick?: (anomaly: Anomaly) => void;
}

const TodaysAnomalies: React.FC<TodaysAnomaliesProps> = ({
  limit = 3,
  onAnomalyClick,
}) => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnomalies = async () => {
      try {
        setLoading(true);
        const data = await getAnomalies();

        // Filter for today's anomalies
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        const todaysAnomalies = data.filter((anomaly) => {
          const anomalyDate = new Date(anomaly.timestamp);
          return anomalyDate >= today;
        });

        // Sort by timestamp (newest first)
        const sortedAnomalies = todaysAnomalies
          .sort(
            (a, b) =>
              new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          )
          .slice(0, limit);

        setAnomalies(sortedAnomalies);
        setError(null);
      } catch (err) {
        console.error("Error fetching anomalies:", err);
        setError("Failed to load anomalies. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchAnomalies();
  }, [limit]);

  const handleAnomalyClick = (anomaly: Anomaly) => {
    if (onAnomalyClick) {
      onAnomalyClick(anomaly);
    }
  };

  const handleRemediate = async (remediatedAnomaly: Anomaly) => {
    try {
      // Update the anomaly status in the backend
      await updateAnomalyStatus(remediatedAnomaly.id, "resolved");

      // Update the local state
      setAnomalies((prevAnomalies) =>
        prevAnomalies.map((anomaly) =>
          anomaly.id === remediatedAnomaly.id
            ? { ...anomaly, status: "resolved" }
            : anomaly
        )
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
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-gray-800">
          Today's Anomalies
        </h2>
        <span className="text-sm text-blue-600 hover:text-blue-800 cursor-pointer">
          View All
        </span>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="text-center text-red-500 py-4">{error}</div>
      ) : anomalies.length === 0 ? (
        <div className="text-center text-gray-500 py-8">
          <p>No anomalies detected today.</p>
          <p className="text-sm mt-2">All systems are running normally.</p>
        </div>
      ) : (
        <div>
          {anomalies.map((anomaly) => (
            <AnomalyCard
              key={anomaly.id}
              anomaly={anomaly}
              onClick={handleAnomalyClick}
              onRemediate={handleRemediate}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default TodaysAnomalies;
