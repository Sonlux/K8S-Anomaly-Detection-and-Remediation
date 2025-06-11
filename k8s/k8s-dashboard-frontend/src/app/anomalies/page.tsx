"use client";

import { useEffect, useState } from "react";
import { getAnomalies } from "@/api/services/anomalies";
import AnomalyList from "@/components/dashboard/AnomalyList";
import { Anomaly } from "@/api/types";

const AnomaliesPage = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const anomaliesData = await getAnomalies();
        setAnomalies(anomaliesData);
      } catch (err) {
        setError("Failed to fetch anomalies.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <p>Loading anomalies...</p>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex min-h-screen flex-col items-center justify-center p-24">
        <p className="text-red-500">Error: {error}</p>
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow p-4">
        <h1 className="text-2xl font-bold text-gray-800">Anomalies</h1>
      </header>
      <main className="p-4">
        <AnomalyList anomalies={anomalies} />
      </main>
    </div>
  );
};

export default AnomaliesPage;
