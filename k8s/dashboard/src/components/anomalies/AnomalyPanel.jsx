import React from 'react';
import AnomalyCard from './AnomalyCard';

const AnomalyPanel = () => {
  // Mock data for anomalies
  const anomalies = [
    {
      id: 1,
      podName: 'api-gateway-5d8b9f7c9b-2xvqz',
      namespace: 'default',
      type: 'resource-exhaustion',
      severity: 'high',
      timestamp: new Date().toISOString(),
      description: 'CPU usage exceeding threshold for extended period',
    },
    {
      id: 2,
      podName: 'data-processor-6f7d8e5c4b-3yvxw',
      namespace: 'data-processing',
      type: 'oom-risk',
      severity: 'medium',
      timestamp: new Date(Date.now() - 3600000).toISOString(),
      description: 'Memory usage trending toward limit',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-semibold mb-4">Detected Anomalies</h2>
      {anomalies.length === 0 ? (
        <div className="text-center p-4 text-gray-500">No anomalies detected</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {anomalies.map((anomaly) => (
            <AnomalyCard key={anomaly.id} anomaly={anomaly} />
          ))}
        </div>
      )}
    </div>
  );
};

export default AnomalyPanel;