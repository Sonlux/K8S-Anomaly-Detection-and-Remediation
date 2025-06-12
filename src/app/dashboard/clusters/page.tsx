'use client';

import { useState } from 'react';
import { 
  ServerIcon, 
  PlusIcon,
  EllipsisVerticalIcon,
  ArrowPathIcon,
  TrashIcon,
  PencilSquareIcon,
  ChartBarIcon
} from '@heroicons/react/24/outline';

interface Cluster {
  id: string;
  name: string;
  status: 'healthy' | 'warning' | 'critical' | 'offline';
  version: string;
  provider: string;
  region: string;
  nodes: number;
  lastUpdated: string;
}

export default function ClustersPage() {
  const [clusters, setClusters] = useState<Cluster[]>([
    {
      id: 'cluster-1',
      name: 'Production Cluster',
      status: 'healthy',
      version: '1.26.5',
      provider: 'AWS',
      region: 'us-west-2',
      nodes: 5,
      lastUpdated: '10 minutes ago',
    },
    {
      id: 'cluster-2',
      name: 'Staging Cluster',
      status: 'warning',
      version: '1.25.9',
      provider: 'GCP',
      region: 'us-central1',
      nodes: 3,
      lastUpdated: '25 minutes ago',
    },
    {
      id: 'cluster-3',
      name: 'Development Cluster',
      status: 'healthy',
      version: '1.26.3',
      provider: 'Azure',
      region: 'eastus',
      nodes: 2,
      lastUpdated: '1 hour ago',
    },
    {
      id: 'cluster-4',
      name: 'Test Cluster',
      status: 'offline',
      version: '1.24.12',
      provider: 'Digital Ocean',
      region: 'nyc1',
      nodes: 1,
      lastUpdated: '3 days ago',
    },
  ]);

  const [showDropdown, setShowDropdown] = useState<string | null>(null);

  const toggleDropdown = (clusterId: string) => {
    if (showDropdown === clusterId) {
      setShowDropdown(null);
    } else {
      setShowDropdown(clusterId);
    }
  };

  const getStatusColor = (status: Cluster['status']) => {
    switch (status) {
      case 'healthy':
        return 'bg-success-500';
      case 'warning':
        return 'bg-warning-500';
      case 'critical':
        return 'bg-danger-500';
      case 'offline':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = (status: Cluster['status']) => {
    switch (status) {
      case 'healthy':
        return 'text-success-500';
      case 'warning':
        return 'text-warning-500';
      case 'critical':
        return 'text-danger-500';
      case 'offline':
        return 'text-gray-500';
      default:
        return 'text-gray-500';
    }
  };

  const getProviderIcon = (provider: string) => {
    // In a real application, you would use actual provider logos
    return <ServerIcon className="h-5 w-5 text-gray-400" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Kubernetes Clusters</h1>
        
        <div className="mt-4 sm:mt-0 flex space-x-2">
          <button className="btn btn-outline flex items-center">
            <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
            Refresh
          </button>
          <button className="btn btn-primary flex items-center">
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            Add Cluster
          </button>
        </div>
      </div>

      <div className="card p-6">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead>
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Cluster
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Version
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Provider
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Nodes
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Last Updated
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              {clusters.map((cluster) => (
                <tr key={cluster.id} className="hover:bg-gray-50 dark:hover:bg-gray-750">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-md bg-primary-100 dark:bg-primary-900">
                        <ServerIcon className="h-6 w-6 text-primary-600 dark:text-primary-400" />
                      </div>
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {cluster.name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {cluster.region}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className={`flex-shrink-0 h-2.5 w-2.5 rounded-full ${getStatusColor(cluster.status)} mr-2`}></div>
                      <span className={`text-sm font-medium ${getStatusText(cluster.status)} capitalize`}>
                        {cluster.status}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    v{cluster.version}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getProviderIcon(cluster.provider)}
                      <span className="ml-2 text-sm text-gray-500 dark:text-gray-400">{cluster.provider}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {cluster.nodes}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {cluster.lastUpdated}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="relative inline-block text-left">
                      <button
                        type="button"
                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                        onClick={() => toggleDropdown(cluster.id)}
                      >
                        <EllipsisVerticalIcon className="h-5 w-5" />
                      </button>
                      
                      {showDropdown === cluster.id && (
                        <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                          <div className="py-1">
                            <button
                              className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                              onClick={() => {}}
                            >
                              <ChartBarIcon className="mr-3 h-5 w-5 text-gray-400" />
                              View Details
                            </button>
                            <button
                              className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                              onClick={() => {}}
                            >
                              <PencilSquareIcon className="mr-3 h-5 w-5 text-gray-400" />
                              Edit
                            </button>
                            <button
                              className="flex items-center w-full text-left px-4 py-2 text-sm text-danger-700 hover:bg-gray-100 dark:text-danger-300 dark:hover:bg-gray-700"
                              onClick={() => {}}
                            >
                              <TrashIcon className="mr-3 h-5 w-5 text-danger-400" />
                              Delete
                            </button>
                          </div>
                        </div>
                      )}
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