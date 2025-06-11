"use client";

import { useEffect, useState } from "react";
import { getClusters } from "@/api/services/clusters";
import ClusterList from "@/components/dashboard/ClusterList";
import { Cluster } from "@/api/types";

const ClustersPage = () => {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const clustersData = await getClusters();
        setClusters(clustersData);
      } catch (err) {
        setError("Failed to fetch clusters.");
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
        <p>Loading clusters...</p>
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
        <h1 className="text-2xl font-bold text-gray-800">Clusters</h1>
      </header>
      <main className="p-4">
        <ClusterList clusters={clusters} />
      </main>
    </div>
  );
};

export default ClustersPage;
