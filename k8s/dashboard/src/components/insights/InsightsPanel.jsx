import React from 'react';

const InsightsPanel = () => {
  // Mock data for insights
  const insights = [
    {
      id: 1,
      title: 'Resource Optimization',
      description: 'Consider reducing CPU limits for underutilized pods in the default namespace',
      impact: 'medium',
      timestamp: new Date().toISOString(),
    },
    {
      id: 2,
      title: 'Scaling Recommendation',
      description: 'The api-gateway deployment would benefit from horizontal scaling based on current traffic patterns',
      impact: 'high',
      timestamp: new Date(Date.now() - 7200000).toISOString(),
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-semibold mb-4">Insights</h2>
      {insights.length === 0 ? (
        <div className="text-center p-4 text-gray-500">No insights available</div>
      ) : (
        <div className="space-y-4">
          {insights.map((insight) => (
            <div key={insight.id} className="border-l-4 border-blue-500 pl-4 py-2">
              <h3 className="font-medium">{insight.title}</h3>
              <p className="text-gray-600 text-sm">{insight.description}</p>
              <div className="flex justify-between mt-2 text-xs text-gray-500">
                <span className={`px-2 py-1 rounded-full ${insight.impact === 'high' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {insight.impact.charAt(0).toUpperCase() + insight.impact.slice(1)} Impact
                </span>
                <span>{new Date(insight.timestamp).toLocaleString()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InsightsPanel;