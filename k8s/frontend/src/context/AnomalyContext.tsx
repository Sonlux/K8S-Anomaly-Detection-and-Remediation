// src/context/AnomalyContext.tsx
import { createContext, useContext, useState } from "react";

const AnomalyContext = createContext();

export function AnomalyProvider({ children }) {
  const [anomalies, setAnomalies] = useState([
    {
      id: 1,
      pod: "test-anomaly-deployment-7d47d87969-btddc",
      cause: "High CPU Usage",
      severity: "Critical",
    },
    {
      id: 2,
      pod: "memory-leak-demo-6f6bbdfd5b-482gn",
      cause: "Memory leak detected",
      severity: "Warning",
    },
    {
      id: 3,
      pod: "crash-deployment-57b4487979-tmjp8",
      cause: "Frequent restarts",
      severity: "Moderate",
    },
  ]);

  const [remediated, setRemediated] = useState([]);

  function remediate(id) {
    const found = anomalies.find((a) => a.id === id);
    if (found) {
      setAnomalies((prev) => prev.filter((a) => a.id !== id));
      setRemediated((prev) => [
        ...prev,
        { ...found, time: new Date().toLocaleString() },
      ]);
    }
  }

  return (
    <AnomalyContext.Provider value={{ anomalies, remediated, remediate }}>
      {children}
    </AnomalyContext.Provider>
  );
}

export function useAnomalies() {
  return useContext(AnomalyContext);
}
