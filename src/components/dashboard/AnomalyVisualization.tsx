'use client';

import { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  ZAxis,
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  Sector
} from 'recharts';
import { ExclamationTriangleIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { AnomalyDataPoint } from '@/lib/anomalyDataService';

// Interface already defined in anomalyDataService.ts
/*interface AnomalyDataPoint {
  timestamp: string;
  podName: string;
  cpuUsage: number;
  memoryUsage: number;
  networkTraffic: number;
  podStatus: string;
  podReason: string;
  podRestarts: number;
  errorMessage: string;
  latestEventReason: string;
  podEventType: string;
  podEventMessage: string;
  nodeName: string;
  isAnomaly: boolean;
}*/

interface AnomalyVisualizationProps {
  data: AnomalyDataPoint[];
  isLoading: boolean;
  onRefresh: () => void;
}
const AnomalyVisualization: React.FC<AnomalyVisualizationProps> = ({ data, isLoading, onRefresh }) => {
  const [selectedMetric, setSelectedMetric] = useState<'cpuUsage' | 'memoryUsage' | 'networkTraffic' | 'podRestarts'>('cpuUsage');
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h'>('1h');
  
  // Format timestamp for display
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  // Get color based on anomaly status
  const getAnomalyColor = (isAnomaly: boolean) => {
    return isAnomaly ? '#ef4444' : '#22c55e';
  };

  // Get metric value based on selected metric
  const getMetricValue = (dataPoint: AnomalyDataPoint) => {
    return dataPoint[selectedMetric];
  };

  // Get metric label based on selected metric
  const getMetricLabel = () => {
    switch (selectedMetric) {
      case 'cpuUsage':
        return 'CPU Usage (%)';
      case 'memoryUsage':
        return 'Memory Usage (%)';
      case 'networkTraffic':
        return 'Network Traffic (B/s)';
      case 'podRestarts':
        return 'Pod Restarts';
      default:
        return 'Value';
    }
  };

  // Prepare data for scatter plot (anomaly detection visualization)
  const scatterData = data.map(point => ({
    x: getMetricValue(point),
    y: point.podRestarts,
    z: point.isAnomaly ? 100 : 30,
    name: point.podName,
    status: point.podStatus,
    reason: point.podReason || point.latestEventReason,
    message: point.errorMessage || point.podEventMessage,
    isAnomaly: point.isAnomaly,
    timestamp: point.timestamp,
    nodeName: point.nodeName,
    cpuUsage: point.cpuUsage,
    memoryUsage: point.memoryUsage,
    networkTraffic: point.networkTraffic
  }));

  // Group data by pod name for line chart
  const podNames = Array.from(new Set(data.map(d => d.podName)));
  
  return (
    <div className="card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
        <div className="flex items-center mb-4 sm:mb-0">
          <ExclamationTriangleIcon className="h-6 w-6 text-warning-500 mr-2" />
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Anomaly Visualization</h2>
        </div>
        
        <div className="flex flex-col sm:flex-row sm:items-center space-y-2 sm:space-y-0">
          <div className="flex space-x-2 mr-4">
            <button
              className={`px-3 py-1 text-xs font-medium rounded-md ${selectedMetric === 'cpuUsage' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
              onClick={() => setSelectedMetric('cpuUsage')}
            >
              CPU
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium rounded-md ${selectedMetric === 'memoryUsage' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
              onClick={() => setSelectedMetric('memoryUsage')}
            >
              Memory
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium rounded-md ${selectedMetric === 'networkTraffic' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
              onClick={() => setSelectedMetric('networkTraffic')}
            >
              Network
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium rounded-md ${selectedMetric === 'podRestarts' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
              onClick={() => setSelectedMetric('podRestarts')}
            >
              Restarts
            </button>
          </div>
          
          <div className="flex space-x-2">
            <button
              className={`px-3 py-1 text-xs font-medium rounded-md ${timeRange === '1h' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
              onClick={() => setTimeRange('1h')}
            >
              1H
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium rounded-md ${timeRange === '6h' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
              onClick={() => setTimeRange('6h')}
            >
              6H
            </button>
            <button
              className={`px-3 py-1 text-xs font-medium rounded-md ${timeRange === '24h' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
              onClick={() => setTimeRange('24h')}
            >
              24H
            </button>
            <button 
              className="ml-2 p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
              onClick={onRefresh}
              disabled={isLoading}
            >
              <ArrowPathIcon className={`h-5 w-5 text-gray-500 ${isLoading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Time Series Chart */}
        <div className="card p-4 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            {getMetricLabel()} Over Time
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart
                data={data}
                margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                <XAxis 
                  dataKey="timestamp" 
                  tickFormatter={formatTimestamp}
                  tick={{ fontSize: 12 }}
                  stroke="#6B7280"
                />
                <YAxis 
                  tick={{ fontSize: 12 }}
                  stroke="#6B7280"
                  domain={selectedMetric === 'networkTraffic' ? ['auto', 'auto'] : 
                          selectedMetric === 'podRestarts' ? [0, 'auto'] : [0, 100]}
                />
                <Tooltip 
                  formatter={(value, name) => {
                    if (selectedMetric === 'networkTraffic') {
                      return [`${value} B/s`, name];
                    } else if (selectedMetric === 'podRestarts') {
                      return [`${value}`, name];
                    } else {
                      return [`${value}%`, name];
                    }
                  }}
                  labelFormatter={(label) => new Date(label).toLocaleString()}
                />
                <Legend />
                {/* Line for each pod */}
                {Array.from(new Set(data.map(d => d.podName))).map((podName, index) => (
                  <Line
                    key={`${podName}-${index}`}
                    type="monotone"
                    dataKey={(entry) => {
                      const point = data.find(d => d.podName === podName && d.timestamp === entry.timestamp);
                      return point ? point[selectedMetric] : null;
                    }}
                    name={podName}
                    stroke={`hsl(${index * 40}, 70%, 50%)`}
                    strokeWidth={2}
                    dot={false}
                    activeDot={{ r: 6, stroke: 'white', strokeWidth: 2 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Anomaly Scatter Plot */}
        <div className="card p-4 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            Anomaly Detection ({getMetricLabel()} vs Pod Restarts)
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart
                margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                <XAxis 
                  type="number" 
                  dataKey="x" 
                  name={getMetricLabel()}
                  tick={{ fontSize: 12 }}
                  stroke="#6B7280"
                  domain={selectedMetric === 'networkTraffic' ? ['auto', 'auto'] : 
                          selectedMetric === 'podRestarts' ? [0, 'auto'] : [0, 100]}
                />
                <YAxis 
                  type="number" 
                  dataKey="y" 
                  name="Pod Restarts"
                  tick={{ fontSize: 12 }}
                  stroke="#6B7280"
                />
                <ZAxis 
                  type="number" 
                  dataKey="z" 
                  range={[30, 200]} 
                />
                <Tooltip 
                  cursor={{ strokeDasharray: '3 3' }}
                  formatter={(value, name, props) => {
                    if (name === 'x') {
                      if (selectedMetric === 'networkTraffic') {
                        return [`${value} B/s`, getMetricLabel()];
                      } else if (selectedMetric === 'podRestarts') {
                        return [`${value}`, getMetricLabel()];
                      } else {
                        return [`${value}%`, getMetricLabel()];
                      }
                    }
                    if (name === 'y') return [value, 'Pod Restarts'];
                    return [value, name];
                  }}
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0].payload;
                      let metricValue;
                      if (selectedMetric === 'networkTraffic') {
                        metricValue = `${data.x} B/s`;
                      } else if (selectedMetric === 'podRestarts') {
                        metricValue = `${data.x}`;
                      } else {
                        metricValue = `${data.x}%`;
                      }
                      return (
                        <div className="bg-white dark:bg-gray-800 p-2 border border-gray-200 dark:border-gray-700 rounded shadow-md">
                          <p className="font-medium">{data.name}</p>
                          <p className="text-xs">{new Date(data.timestamp).toLocaleString()}</p>
                          <p className="text-xs">{`${getMetricLabel()}: ${metricValue}`}</p>
                          <p className="text-xs">{`Pod Restarts: ${data.y}`}</p>
                          <p className="text-xs">{`Status: ${data.status}`}</p>
                          {data.reason && <p className="text-xs">{`Reason: ${data.reason}`}</p>}
                          {data.message && <p className="text-xs">{`Message: ${data.message}`}</p>}
                          <p className="text-xs font-medium" style={{ color: data.isAnomaly ? '#ef4444' : '#22c55e' }}>
                            {data.isAnomaly ? 'Anomaly Detected' : 'Normal'}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter 
                  name="Pods" 
                  data={scatterData} 
                  fill={(entry) => getAnomalyColor(entry.isAnomaly)}
                />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Pod Status Distribution */}
      <div className="mt-6">
        <div className="card p-4 border border-gray-200 dark:border-gray-700">
          <h3 className="text-sm font-medium text-gray-900 dark:text-white mb-4">
            Pod Status Distribution by Node
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {Array.from(new Set(data.map(d => d.nodeName))).map(nodeName => {
              const nodeData = data.filter(d => d.nodeName === nodeName);
              const totalPods = nodeData.length;
              const anomalousPods = nodeData.filter(d => d.isAnomaly).length;
              const normalPods = totalPods - anomalousPods;
              
              return (
                <div key={nodeName} className="bg-gray-50 dark:bg-gray-750 p-3 rounded-lg">
                  <h4 className="text-sm font-medium mb-2">{nodeName}</h4>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">Normal:</span>
                    <span className="text-xs font-medium text-success-500">{normalPods}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                    <div 
                      className="bg-success-500 h-2 rounded-full" 
                      style={{ width: `${(normalPods / totalPods) * 100}%` }}
                    ></div>
                  </div>
                  
                  <div className="flex items-center justify-between mb-1 mt-2">
                    <span className="text-xs text-gray-500 dark:text-gray-400">Anomalous:</span>
                    <span className="text-xs font-medium text-danger-500">{anomalousPods}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2 dark:bg-gray-700">
                    <div 
                      className="bg-danger-500 h-2 rounded-full" 
                      style={{ width: `${(anomalousPods / totalPods) * 100}%` }}
                    ></div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnomalyVisualization;