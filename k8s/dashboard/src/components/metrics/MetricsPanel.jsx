import React, { useState } from 'react';
import CPUChart from './CPUChart';
import MemoryChart from './MemoryChart';
import CombinedMetricsView from './CombinedMetricsView';
import { useMetrics } from '../../hooks/useMetrics';

const MetricsPanel = () => {
  const [activeTab, setActiveTab] = useState('cpu');
  const { metrics, loading, error } = useMetrics();
  
  // Pass an empty array for metrics if loading or error, and filter out any null/undefined pods
  const displayMetrics = loading || error 
    ? [] 
    : metrics.filter(pod => pod !== null && typeof pod !== 'undefined');

  if (loading) return <div className="bg-white rounded-lg shadow p-4">Loading metrics...</div>;
  if (error) return <div className="bg-white rounded-lg shadow p-4 text-red-500">Error loading metrics: {error}</div>;
  
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <h2 className="text-xl font-semibold mb-4">Cluster Metrics</h2>
      <div className="flex border-b mb-4">
        <button 
          className={`py-2 px-4 ${activeTab === 'cpu' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('cpu')}
        >
          CPU Usage
        </button>
        <button 
          className={`py-2 px-4 ${activeTab === 'memory' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('memory')}
        >
          Memory Usage
        </button>
        <button 
          className={`py-2 px-4 ${activeTab === 'combined' ? 'border-b-2 border-blue-500 text-blue-500' : 'text-gray-500'}`}
          onClick={() => setActiveTab('combined')}
        >
          Combined View
        </button>
      </div>
      <div className="mt-4">
        {activeTab === 'cpu' && <CPUChart metrics={displayMetrics} />}
        {activeTab === 'memory' && <MemoryChart metrics={displayMetrics} />}
        {activeTab === 'combined' && <CombinedMetricsView metrics={displayMetrics} />}
      </div>
    </div>
  );
};

export default MetricsPanel;