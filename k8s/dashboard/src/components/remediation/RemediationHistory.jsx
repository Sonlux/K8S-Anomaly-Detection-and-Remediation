import React from 'react';

const RemediationHistory = () => {
  // Mock data for remediation history
  const remediations = [
    {
      id: 1,
      podName: 'api-gateway-5d8b9f7c9b-2xvqz',
      namespace: 'default',
      action: 'scale-deployment',
      details: 'Scaled deployment api-gateway from 2 to 3 replicas',
      status: 'successful',
      timestamp: new Date().toISOString(),
    },
    {
      id: 2,
      podName: 'data-processor-6f7d8e5c4b-3yvxw',
      namespace: 'data-processing',
      action: 'restart-pod',
      details: 'Restarted pod to address memory leak',
      status: 'successful',
      timestamp: new Date(Date.now() - 86400000).toISOString(),
    },
    {
      id: 3,
      podName: 'auth-service-7e6d5c4b3a-8zxcv',
      namespace: 'security',
      action: 'increase-resource-limits',
      details: 'Increased memory limit from 256Mi to 512Mi',
      status: 'failed',
      timestamp: new Date(Date.now() - 172800000).toISOString(),
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-semibold mb-4">Remediation History</h2>
      {remediations.length === 0 ? (
        <div className="text-center p-4 text-gray-500">No remediation actions recorded</div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-gray-100">
                <th className="py-2 px-4 text-left">Time</th>
                <th className="py-2 px-4 text-left">Pod</th>
                <th className="py-2 px-4 text-left">Action</th>
                <th className="py-2 px-4 text-left">Status</th>
              </tr>
            </thead>
            <tbody>
              {remediations.map((item) => (
                <tr key={item.id} className="border-b">
                  <td className="py-2 px-4">{new Date(item.timestamp).toLocaleString()}</td>
                  <td className="py-2 px-4">{item.podName}</td>
                  <td className="py-2 px-4">{item.details}</td>
                  <td className="py-2 px-4">
                    <span className={`px-2 py-1 rounded-full text-xs ${item.status === 'successful' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default RemediationHistory;