'use client';

import { useState, useEffect } from 'react';
import { 
  ArrowPathIcon,
  ChartBarIcon,
  ClockIcon,
  ExclamationTriangleIcon,
  ServerIcon,
  CpuChipIcon,
  CircleStackIcon,
  CloudIcon,
  CubeIcon,
  CubeTransparentIcon,
  ShieldCheckIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from '@heroicons/react/24/outline';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';

interface MetricData {
  name: string;
  value: number;
  time: string;
}

interface TimeSeriesData {
  time: string;
  cpu: number;
  memory: number;
  pods: number;
  network: number;
}

interface NodeMetric {
  nodeName: string;
  status: 'healthy' | 'warning' | 'critical';
  cpu: number;
  memory: number;
  pods: number;
  disk: number;
  network: number;
}

export default function MonitoringPage() {
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h');
  const [refreshInterval, setRefreshInterval] = useState<number>(30);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [clusterHealth, setClusterHealth] = useState<'healthy' | 'warning' | 'critical'>('healthy');
  
  // Mock time series data
  const [timeSeriesData, setTimeSeriesData] = useState<TimeSeriesData[]>([]);
  const [nodeMetrics, setNodeMetrics] = useState<NodeMetric[]>([]);

  // Generate mock time series data
  useEffect(() => {
    setIsLoading(true);
    
    // Generate mock data based on time range
    const generateMockData = () => {
      const now = new Date();
      const data: TimeSeriesData[] = [];
      const dataPoints = timeRange === '1h' ? 60 : 
                        timeRange === '6h' ? 72 : 
                        timeRange === '24h' ? 96 : 168;
      
      const timeIncrement = timeRange === '1h' ? 60000 : 
                           timeRange === '6h' ? 300000 : 
                           timeRange === '24h' ? 900000 : 3600000;
      
      for (let i = dataPoints; i >= 0; i--) {
        const time = new Date(now.getTime() - (i * timeIncrement));
        const baseValue = Math.sin(i / 10) * 10 + 70; // Base oscillating value
        
        data.push({
          time: time.toISOString(),
          cpu: Math.max(10, Math.min(95, baseValue + Math.random() * 20)),
          memory: Math.max(20, Math.min(90, baseValue - 5 + Math.random() * 15)),
          pods: Math.max(30, Math.min(85, 60 + Math.random() * 25)),
          network: Math.max(5, Math.min(100, 40 + Math.random() * 60)),
        });
      }
      
      return data;
    };
    
    // Generate mock node metrics
    const generateNodeMetrics = () => {
      const nodes: NodeMetric[] = [
        {
          nodeName: 'master-1',
          status: 'healthy',
          cpu: 45 + Math.random() * 10,
          memory: 60 + Math.random() * 15,
          pods: 28 + Math.random() * 5,
          disk: 35 + Math.random() * 10,
          network: 50 + Math.random() * 20,
        },
        {
          nodeName: 'worker-1',
          status: 'healthy',
          cpu: 65 + Math.random() * 10,
          memory: 70 + Math.random() * 10,
          pods: 42 + Math.random() * 5,
          disk: 55 + Math.random() * 10,
          network: 60 + Math.random() * 15,
        },
        {
          nodeName: 'worker-2',
          status: 'warning',
          cpu: 85 + Math.random() * 10,
          memory: 75 + Math.random() * 10,
          pods: 38 + Math.random() * 5,
          disk: 65 + Math.random() * 10,
          network: 70 + Math.random() * 15,
        },
        {
          nodeName: 'worker-3',
          status: 'healthy',
          cpu: 55 + Math.random() * 10,
          memory: 65 + Math.random() * 10,
          pods: 32 + Math.random() * 5,
          disk: 45 + Math.random() * 10,
          network: 55 + Math.random() * 15,
        },
        {
          nodeName: 'worker-4',
          status: 'critical',
          cpu: 95 + Math.random() * 5,
          memory: 90 + Math.random() * 5,
          pods: 45 + Math.random() * 3,
          disk: 85 + Math.random() * 10,
          network: 80 + Math.random() * 10,
        },
      ];
      
      return nodes;
    };
    
    const data = generateMockData();
    const nodes = generateNodeMetrics();
    
    setTimeSeriesData(data);
    setNodeMetrics(nodes);
    
    // Determine cluster health based on node metrics
    if (nodes.some(node => node.status === 'critical')) {
      setClusterHealth('critical');
    } else if (nodes.some(node => node.status === 'warning')) {
      setClusterHealth('warning');
    } else {
      setClusterHealth('healthy');
    }
    
    setLastUpdated(new Date());
    setIsLoading(false);
  }, [timeRange]);
  
  // Auto-refresh effect
  useEffect(() => {
    if (refreshInterval <= 0) return;
    
    const intervalId = setInterval(() => {
      // Simulate data refresh
      const updatedNodes = nodeMetrics.map(node => ({
        ...node,
        cpu: Math.max(10, Math.min(100, node.cpu + (Math.random() * 10 - 5))),
        memory: Math.max(10, Math.min(100, node.memory + (Math.random() * 10 - 5))),
        pods: Math.max(10, Math.min(50, node.pods + (Math.random() * 4 - 2))),
        disk: Math.max(10, Math.min(100, node.disk + (Math.random() * 5 - 2.5))),
        network: Math.max(10, Math.min(100, node.network + (Math.random() * 15 - 7.5))),
      }));
      
      // Update the last data point in time series
      const updatedTimeSeries = [...timeSeriesData];
      if (updatedTimeSeries.length > 0) {
        const lastIndex = updatedTimeSeries.length - 1;
        updatedTimeSeries[lastIndex] = {
          ...updatedTimeSeries[lastIndex],
          cpu: Math.max(10, Math.min(95, updatedTimeSeries[lastIndex].cpu + (Math.random() * 10 - 5))),
          memory: Math.max(20, Math.min(90, updatedTimeSeries[lastIndex].memory + (Math.random() * 8 - 4))),
          pods: Math.max(30, Math.min(85, updatedTimeSeries[lastIndex].pods + (Math.random() * 6 - 3))),
          network: Math.max(5, Math.min(100, updatedTimeSeries[lastIndex].network + (Math.random() * 12 - 6))),
        };
      }
      
      setNodeMetrics(updatedNodes);
      setTimeSeriesData(updatedTimeSeries);
      setLastUpdated(new Date());
      
      // Determine cluster health based on updated node metrics
      if (updatedNodes.some(node => node.status === 'critical')) {
        setClusterHealth('critical');
      } else if (updatedNodes.some(node => node.status === 'warning')) {
        setClusterHealth('warning');
      } else {
        setClusterHealth('healthy');
      }
    }, refreshInterval * 1000);
    
    return () => clearInterval(intervalId);
  }, [refreshInterval, nodeMetrics, timeSeriesData]);
  
  // Format time for display
  const formatTime = (isoString: string) => {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };
  
  // Format date for display
  const formatDate = (date: Date) => {
    return date.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  // Get status color
  const getStatusColor = (status: 'healthy' | 'warning' | 'critical') => {
    switch (status) {
      case 'healthy':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'critical':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };
  
  // Get status background color
  const getStatusBgColor = (status: 'healthy' | 'warning' | 'critical') => {
    switch (status) {
      case 'healthy':
        return 'bg-green-100 dark:bg-green-900/20';
      case 'warning':
        return 'bg-yellow-100 dark:bg-yellow-900/20';
      case 'critical':
        return 'bg-red-100 dark:bg-red-900/20';
      default:
        return 'bg-gray-100 dark:bg-gray-800';
    }
  };
  
  // Get usage color based on percentage
  const getUsageColor = (percentage: number) => {
    if (percentage >= 90) return 'text-red-500';
    if (percentage >= 75) return 'text-yellow-500';
    return 'text-green-500';
  };
  
  // Get usage background color based on percentage
  const getUsageBgColor = (percentage: number) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Cluster Monitoring</h1>
        
        <div className="mt-4 sm:mt-0 flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <ClockIcon className="h-5 w-5 text-gray-400" />
            <span className="text-sm text-gray-500 dark:text-gray-400">
              Last updated: {formatDate(lastUpdated)}
            </span>
          </div>
          
          <button 
            onClick={() => {
              setIsLoading(true);
              setTimeout(() => {
                // Simulate refresh
                const data = timeSeriesData.map(item => ({
                  ...item,
                  cpu: Math.max(10, Math.min(95, item.cpu + (Math.random() * 10 - 5))),
                  memory: Math.max(20, Math.min(90, item.memory + (Math.random() * 8 - 4))),
                  pods: Math.max(30, Math.min(85, item.pods + (Math.random() * 6 - 3))),
                  network: Math.max(5, Math.min(100, item.network + (Math.random() * 12 - 6))),
                }));
                setTimeSeriesData(data);
                setLastUpdated(new Date());
                setIsLoading(false);
              }, 500);
            }}
            className="inline-flex items-center px-3 py-1.5 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200 dark:hover:bg-gray-700"
          >
            <ArrowPathIcon className={`-ml-1 mr-2 h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </button>
        </div>
      </div>
      
      {/* Cluster Health Overview */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h2 className="text-lg font-medium">Cluster Health</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">Overall health and resource utilization</p>
          </div>
          
          <div className="mt-4 md:mt-0 flex items-center space-x-2">
            <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBgColor(clusterHealth)} ${getStatusColor(clusterHealth)}`}>
              {clusterHealth === 'healthy' && 'Healthy'}
              {clusterHealth === 'warning' && 'Warning'}
              {clusterHealth === 'critical' && 'Critical'}
            </div>
            
            <select
              id="refresh-interval"
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="block w-full pl-3 pr-10 py-1.5 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            >
              <option value="0">Manual refresh</option>
              <option value="10">10 seconds</option>
              <option value="30">30 seconds</option>
              <option value="60">1 minute</option>
              <option value="300">5 minutes</option>
            </select>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* CPU Usage */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CpuChipIcon className="h-8 w-8 text-primary-500" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium">CPU Usage</h3>
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold">
                      {Math.round(timeSeriesData[timeSeriesData.length - 1]?.cpu || 0)}%
                    </span>
                    <span className="ml-2 flex items-center text-sm font-medium text-green-500">
                      <ArrowTrendingDownIcon className="self-center flex-shrink-0 h-4 w-4 text-green-500" aria-hidden="true" />
                      <span className="sr-only">Decreased by</span>
                      2.5%
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getUsageBgColor(timeSeriesData[timeSeriesData.length - 1]?.cpu || 0)}`}
                style={{ width: `${timeSeriesData[timeSeriesData.length - 1]?.cpu || 0}%` }}
              ></div>
            </div>
          </div>
          
          {/* Memory Usage */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CircleStackIcon className="h-8 w-8 text-primary-500" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium">Memory Usage</h3>
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold">
                      {Math.round(timeSeriesData[timeSeriesData.length - 1]?.memory || 0)}%
                    </span>
                    <span className="ml-2 flex items-center text-sm font-medium text-red-500">
                      <ArrowTrendingUpIcon className="self-center flex-shrink-0 h-4 w-4 text-red-500" aria-hidden="true" />
                      <span className="sr-only">Increased by</span>
                      4.3%
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getUsageBgColor(timeSeriesData[timeSeriesData.length - 1]?.memory || 0)}`}
                style={{ width: `${timeSeriesData[timeSeriesData.length - 1]?.memory || 0}%` }}
              ></div>
            </div>
          </div>
          
          {/* Pod Usage */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CubeIcon className="h-8 w-8 text-primary-500" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium">Pod Usage</h3>
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold">
                      {Math.round(timeSeriesData[timeSeriesData.length - 1]?.pods || 0)}%
                    </span>
                    <span className="ml-2 flex items-center text-sm font-medium text-green-500">
                      <ArrowTrendingDownIcon className="self-center flex-shrink-0 h-4 w-4 text-green-500" aria-hidden="true" />
                      <span className="sr-only">Decreased by</span>
                      1.2%
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getUsageBgColor(timeSeriesData[timeSeriesData.length - 1]?.pods || 0)}`}
                style={{ width: `${timeSeriesData[timeSeriesData.length - 1]?.pods || 0}%` }}
              ></div>
            </div>
          </div>
          
          {/* Network Usage */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <CloudIcon className="h-8 w-8 text-primary-500" />
                <div className="ml-3">
                  <h3 className="text-sm font-medium">Network Usage</h3>
                  <div className="flex items-center">
                    <span className="text-2xl font-semibold">
                      {Math.round(timeSeriesData[timeSeriesData.length - 1]?.network || 0)}%
                    </span>
                    <span className="ml-2 flex items-center text-sm font-medium text-yellow-500">
                      <ArrowTrendingUpIcon className="self-center flex-shrink-0 h-4 w-4 text-yellow-500" aria-hidden="true" />
                      <span className="sr-only">Increased by</span>
                      3.7%
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div className="mt-4 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div 
                className={`h-full ${getUsageBgColor(timeSeriesData[timeSeriesData.length - 1]?.network || 0)}`}
                style={{ width: `${timeSeriesData[timeSeriesData.length - 1]?.network || 0}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Time Series Charts */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h2 className="text-lg font-medium">Resource Utilization</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">Historical resource usage over time</p>
          </div>
          
          <div className="mt-4 md:mt-0">
            <div className="inline-flex rounded-md shadow-sm">
              <button
                type="button"
                onClick={() => setTimeRange('1h')}
                className={`relative inline-flex items-center px-3 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium ${timeRange === '1h' ? 'text-primary-600 bg-primary-50 border-primary-500 z-10' : 'text-gray-700 hover:bg-gray-50'} focus:z-10 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200 ${timeRange === '1h' ? 'dark:bg-primary-900/20 dark:border-primary-500' : 'dark:hover:bg-gray-700'}`}
              >
                1H
              </button>
              <button
                type="button"
                onClick={() => setTimeRange('6h')}
                className={`relative inline-flex items-center px-3 py-2 border border-gray-300 bg-white text-sm font-medium ${timeRange === '6h' ? 'text-primary-600 bg-primary-50 border-primary-500 z-10' : 'text-gray-700 hover:bg-gray-50'} focus:z-10 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 -ml-px dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200 ${timeRange === '6h' ? 'dark:bg-primary-900/20 dark:border-primary-500' : 'dark:hover:bg-gray-700'}`}
              >
                6H
              </button>
              <button
                type="button"
                onClick={() => setTimeRange('24h')}
                className={`relative inline-flex items-center px-3 py-2 border border-gray-300 bg-white text-sm font-medium ${timeRange === '24h' ? 'text-primary-600 bg-primary-50 border-primary-500 z-10' : 'text-gray-700 hover:bg-gray-50'} focus:z-10 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 -ml-px dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200 ${timeRange === '24h' ? 'dark:bg-primary-900/20 dark:border-primary-500' : 'dark:hover:bg-gray-700'}`}
              >
                24H
              </button>
              <button
                type="button"
                onClick={() => setTimeRange('7d')}
                className={`relative inline-flex items-center px-3 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium ${timeRange === '7d' ? 'text-primary-600 bg-primary-50 border-primary-500 z-10' : 'text-gray-700 hover:bg-gray-50'} focus:z-10 focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500 -ml-px dark:bg-gray-800 dark:border-gray-700 dark:text-gray-200 ${timeRange === '7d' ? 'dark:bg-primary-900/20 dark:border-primary-500' : 'dark:hover:bg-gray-700'}`}
              >
                7D
              </button>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* CPU Usage Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h3 className="text-sm font-medium mb-4">CPU Utilization</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={timeSeriesData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis 
                    dataKey="time" 
                    tickFormatter={formatTime} 
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <YAxis 
                    tickFormatter={(value) => `${value}%`}
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'CPU Usage']}
                    labelFormatter={(label) => formatTime(label)}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="cpu" 
                    stroke="#3B82F6" 
                    fill="#3B82F6" 
                    fillOpacity={0.2} 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Memory Usage Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h3 className="text-sm font-medium mb-4">Memory Utilization</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={timeSeriesData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis 
                    dataKey="time" 
                    tickFormatter={formatTime} 
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <YAxis 
                    tickFormatter={(value) => `${value}%`}
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Memory Usage']}
                    labelFormatter={(label) => formatTime(label)}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="memory" 
                    stroke="#EC4899" 
                    fill="#EC4899" 
                    fillOpacity={0.2} 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Pod Usage Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h3 className="text-sm font-medium mb-4">Pod Utilization</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={timeSeriesData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis 
                    dataKey="time" 
                    tickFormatter={formatTime} 
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <YAxis 
                    tickFormatter={(value) => `${value}%`}
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Pod Usage']}
                    labelFormatter={(label) => formatTime(label)}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="pods" 
                    stroke="#10B981" 
                    fill="#10B981" 
                    fillOpacity={0.2} 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
          
          {/* Network Usage Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
            <h3 className="text-sm font-medium mb-4">Network Utilization</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={timeSeriesData}
                  margin={{ top: 5, right: 5, left: 5, bottom: 5 }}
                >
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                  <XAxis 
                    dataKey="time" 
                    tickFormatter={formatTime} 
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <YAxis 
                    tickFormatter={(value) => `${value}%`}
                    domain={[0, 100]}
                    tick={{ fontSize: 12 }}
                    stroke="#6B7280"
                  />
                  <Tooltip 
                    formatter={(value) => [`${value}%`, 'Network Usage']}
                    labelFormatter={(label) => formatTime(label)}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="network" 
                    stroke="#F59E0B" 
                    fill="#F59E0B" 
                    fillOpacity={0.2} 
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>
      
      {/* Node Metrics */}
      <div className="card">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
          <div>
            <h2 className="text-lg font-medium">Node Metrics</h2>
            <p className="text-sm text-gray-500 dark:text-gray-400">Resource utilization by node</p>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Node
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  CPU
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Memory
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Pods
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Disk
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Network
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
              {nodeMetrics.map((node, index) => (
                <tr key={node.nodeName} className={index % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800/50'}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                    <div className="flex items-center">
                      <ServerIcon className="h-5 w-5 text-gray-500 dark:text-gray-400 mr-2" />
                      {node.nodeName}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusBgColor(node.status)} ${getStatusColor(node.status)}`}>
                      {node.status === 'healthy' && 'Healthy'}
                      {node.status === 'warning' && 'Warning'}
                      {node.status === 'critical' && 'Critical'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center">
                      <span className={`mr-2 ${getUsageColor(node.cpu)}`}>{Math.round(node.cpu)}%</span>
                      <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getUsageBgColor(node.cpu)}`}
                          style={{ width: `${node.cpu}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center">
                      <span className={`mr-2 ${getUsageColor(node.memory)}`}>{Math.round(node.memory)}%</span>
                      <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getUsageBgColor(node.memory)}`}
                          style={{ width: `${node.memory}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center">
                      <span className={`mr-2 ${getUsageColor(node.pods * 2)}`}>{Math.round(node.pods)}</span>
                      <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getUsageBgColor(node.pods * 2)}`}
                          style={{ width: `${node.pods * 2}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center">
                      <span className={`mr-2 ${getUsageColor(node.disk)}`}>{Math.round(node.disk)}%</span>
                      <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getUsageBgColor(node.disk)}`}
                          style={{ width: `${node.disk}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <div className="flex items-center">
                      <span className={`mr-2 ${getUsageColor(node.network)}`}>{Math.round(node.network)}%</span>
                      <div className="w-24 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                        <div 
                          className={`h-full ${getUsageBgColor(node.network)}`}
                          style={{ width: `${node.network}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}