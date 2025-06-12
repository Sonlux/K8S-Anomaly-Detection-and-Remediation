'use client';

import { useState } from 'react';
import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface MetricData {
  id: string;
  name: string;
  value: number;
  unit: string;
  change: number;
  status: 'normal' | 'warning' | 'critical';
  history: Array<{ time: string; value: number }>;
}

interface MetricsGridProps {
  data: MetricData[];
}

const MetricsGrid: React.FC<MetricsGridProps> = ({ data }) => {
  const [timeRange, setTimeRange] = useState('1h');

  const getStatusColor = (status: 'normal' | 'warning' | 'critical') => {
    switch (status) {
      case 'normal':
        return 'text-success-500';
      case 'warning':
        return 'text-warning-500';
      case 'critical':
        return 'text-danger-500';
      default:
        return 'text-gray-500';
    }
  };

  const getChangeColor = (change: number) => {
    if (change > 0) return 'text-danger-500';
    if (change < 0) return 'text-success-500';
    return 'text-gray-500';
  };

  const getChartColor = (status: 'normal' | 'warning' | 'critical') => {
    switch (status) {
      case 'normal':
        return '#22c55e';
      case 'warning':
        return '#f59e0b';
      case 'critical':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white">Key Metrics</h2>
        
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
            className={`px-3 py-1 text-xs font-medium rounded-md ${timeRange === '7d' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
            onClick={() => setTimeRange('7d')}
          >
            7D
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.map((metric) => (
          <div key={metric.id} className="card p-4 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">{metric.name}</h3>
              <span className={`text-xs font-medium ${getStatusColor(metric.status)} capitalize`}>
                {metric.status}
              </span>
            </div>
            
            <div className="flex items-baseline">
              <span className="text-2xl font-semibold text-gray-900 dark:text-white">{metric.value}</span>
              <span className="ml-1 text-sm text-gray-500 dark:text-gray-400">{metric.unit}</span>
              
              <div className="ml-2 flex items-center">
                {metric.change !== 0 && (
                  <>
                    {metric.change > 0 ? (
                      <ArrowUpIcon className="h-3 w-3 text-danger-500" />
                    ) : (
                      <ArrowDownIcon className="h-3 w-3 text-success-500" />
                    )}
                  </>
                )}
                <span className={`text-xs font-medium ${getChangeColor(metric.change)}`}>
                  {Math.abs(metric.change)}%
                </span>
              </div>
            </div>
            
            <div className="mt-3 h-16">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={metric.history}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                  <XAxis dataKey="time" hide={true} />
                  <YAxis hide={true} />
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: '#ffffff', 
                      borderColor: '#e5e7eb',
                      borderRadius: '0.375rem',
                      fontSize: '0.75rem'
                    }} 
                    formatter={(value: number) => [`${value} ${metric.unit}`, metric.name]}
                    labelFormatter={() => ''}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="value" 
                    stroke={getChartColor(metric.status)} 
                    strokeWidth={2} 
                    dot={false} 
                    activeDot={{ r: 4 }} 
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MetricsGrid;