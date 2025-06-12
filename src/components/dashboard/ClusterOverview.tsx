'use client';

import { useState } from 'react';
import { 
  ServerIcon, 
  CpuChipIcon, 
  CircleStackIcon,
  CubeTransparentIcon
} from '@heroicons/react/24/outline';

interface ClusterData {
  name: string;
  status: 'healthy' | 'warning' | 'critical';
  version: string;
  nodes: number;
  pods: number;
  deployments: number;
  services: number;
  cpu: {
    used: number;
    total: number;
    percentage: number;
  };
  memory: {
    used: number;
    total: number;
    percentage: number;
  };
  storage: {
    used: number;
    total: number;
    percentage: number;
  };
}

interface ClusterOverviewProps {
  data: ClusterData;
}

const ClusterOverview: React.FC<ClusterOverviewProps> = ({ data }) => {
  const [selectedTab, setSelectedTab] = useState('overview');

  const getStatusColor = (status: 'healthy' | 'warning' | 'critical') => {
    switch (status) {
      case 'healthy':
        return 'text-success-500';
      case 'warning':
        return 'text-warning-500';
      case 'critical':
        return 'text-danger-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusBg = (status: 'healthy' | 'warning' | 'critical') => {
    switch (status) {
      case 'healthy':
        return 'bg-success-100 dark:bg-success-900';
      case 'warning':
        return 'bg-warning-100 dark:bg-warning-900';
      case 'critical':
        return 'bg-danger-100 dark:bg-danger-900';
      default:
        return 'bg-gray-100 dark:bg-gray-800';
    }
  };

  const formatStorage = (gb: number) => {
    if (gb >= 1024) {
      return `${(gb / 1024).toFixed(1)} TB`;
    }
    return `${gb.toFixed(1)} GB`;
  };

  return (
    <div className="card p-6">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6">
        <div className="flex items-center">
          <ServerIcon className="h-8 w-8 text-primary-500 mr-3" />
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">{data.name}</h2>
            <div className="flex items-center mt-1">
              <span className={`inline-block h-2.5 w-2.5 rounded-full ${getStatusBg(data.status)} mr-2`}></span>
              <span className={`text-sm font-medium ${getStatusColor(data.status)} capitalize`}>{data.status}</span>
              <span className="text-sm text-gray-500 dark:text-gray-400 ml-3">Kubernetes v{data.version}</span>
            </div>
          </div>
        </div>

        <div className="mt-4 md:mt-0 flex space-x-2">
          <button className="btn btn-primary">Refresh</button>
          <button className="btn btn-outline">Actions</button>
        </div>
      </div>

      <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
        <nav className="-mb-px flex space-x-6">
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${selectedTab === 'overview'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            onClick={() => setSelectedTab('overview')}
          >
            Overview
          </button>
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${selectedTab === 'nodes'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            onClick={() => setSelectedTab('nodes')}
          >
            Nodes
          </button>
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${selectedTab === 'workloads'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            onClick={() => setSelectedTab('workloads')}
          >
            Workloads
          </button>
          <button
            className={`pb-4 px-1 border-b-2 font-medium text-sm ${selectedTab === 'services'
              ? 'border-primary-500 text-primary-600 dark:text-primary-400'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            onClick={() => setSelectedTab('services')}
          >
            Services
          </button>
        </nav>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="card p-4 bg-gray-50 dark:bg-gray-750 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-primary-100 dark:bg-primary-900 text-primary-600 dark:text-primary-400 mr-4">
              <ServerIcon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Nodes</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{data.nodes}</p>
            </div>
          </div>
        </div>

        <div className="card p-4 bg-gray-50 dark:bg-gray-750 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-secondary-100 dark:bg-secondary-900 text-secondary-600 dark:text-secondary-400 mr-4">
              <CubeTransparentIcon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Pods</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{data.pods}</p>
            </div>
          </div>
        </div>

        <div className="card p-4 bg-gray-50 dark:bg-gray-750 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-success-100 dark:bg-success-900 text-success-600 dark:text-success-400 mr-4">
              <CubeTransparentIcon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Deployments</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{data.deployments}</p>
            </div>
          </div>
        </div>

        <div className="card p-4 bg-gray-50 dark:bg-gray-750 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-warning-100 dark:bg-warning-900 text-warning-600 dark:text-warning-400 mr-4">
              <CubeTransparentIcon className="h-6 w-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Services</p>
              <p className="text-2xl font-semibold text-gray-900 dark:text-white">{data.services}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <CpuChipIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">CPU Usage</h3>
            </div>
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {data.cpu.used} / {data.cpu.total} cores
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-1">
            <div 
              className={`h-2.5 rounded-full ${data.cpu.percentage > 80 ? 'bg-danger-500' : data.cpu.percentage > 60 ? 'bg-warning-500' : 'bg-success-500'}`} 
              style={{ width: `${data.cpu.percentage}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">{data.cpu.percentage}% used</p>
        </div>

        <div className="card p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <CircleStackIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">Memory Usage</h3>
            </div>
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {data.memory.used} / {data.memory.total} GB
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-1">
            <div 
              className={`h-2.5 rounded-full ${data.memory.percentage > 80 ? 'bg-danger-500' : data.memory.percentage > 60 ? 'bg-warning-500' : 'bg-success-500'}`} 
              style={{ width: `${data.memory.percentage}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">{data.memory.percentage}% used</p>
        </div>

        <div className="card p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center">
              <CircleStackIcon className="h-5 w-5 text-gray-400 mr-2" />
              <h3 className="text-sm font-medium text-gray-900 dark:text-white">Storage Usage</h3>
            </div>
            <span className="text-sm font-medium text-gray-500 dark:text-gray-400">
              {formatStorage(data.storage.used)} / {formatStorage(data.storage.total)}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700 mb-1">
            <div 
              className={`h-2.5 rounded-full ${data.storage.percentage > 80 ? 'bg-danger-500' : data.storage.percentage > 60 ? 'bg-warning-500' : 'bg-success-500'}`} 
              style={{ width: `${data.storage.percentage}%` }}
            ></div>
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400">{data.storage.percentage}% used</p>
        </div>
      </div>
    </div>
  );
};

export default ClusterOverview;