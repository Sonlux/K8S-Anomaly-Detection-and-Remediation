"use client";

import { useEffect, useState } from "react";
import { getRemediations } from "@/api/services/remediation";
import RemediationList from "@/components/dashboard/RemediationList";
import { Remediation } from "@/api/types";

const RemediationsPage = () => {
  const [remediations, setRemediations] = useState<Remediation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const remediationsData = await getRemediations();
        setRemediations(remediationsData);
      } catch (err) {
        setError("Failed to fetch remediations.");
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
        <p>Loading remediations...</p>
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
        <h1 className="text-2xl font-bold text-gray-800">Remediations</h1>
      </header>
      <main className="p-4">
        <RemediationList remediations={remediations} />
      </main>
    </div>
  );
};

export default RemediationsPage;
