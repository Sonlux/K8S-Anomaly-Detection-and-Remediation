'use client';

import { useState } from 'react';
import { 
  CubeTransparentIcon, 
  PlusIcon,
  FunnelIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import WorkloadCard from '@/components/dashboard/WorkloadCard';

interface Workload {
  id: string;
  name: string;
  type: 'deployment' | 'statefulset' | 'daemonset' | 'job' | 'cronjob';
  namespace: string;
  status: 'running' | 'pending' | 'failed' | 'completed' | 'suspended';
  replicas: {
    current: number;
    desired: number;
  };
  cpu: {
    used: string;
    limit: string;
  };
  memory: {
    used: string;
    limit: string;
  };
  age: string;
}

export default function WorkloadsPage() {
  const [workloads, setWorkloads] = useState<Workload[]>([
    {
      id: 'workload-1',
      name: 'frontend-app',
      type: 'deployment',
      namespace: 'web',
      status: 'running',
      replicas: {
        current: 3,
        desired: 3,
      },
      cpu: {
        used: '250m',
        limit: '500m',
      },
      memory: {
        used: '256Mi',
        limit: '512Mi',
      },
      age: '3d',
    },
    {
      id: 'workload-2',
      name: 'api-server',
      type: 'deployment',
      namespace: 'backend',
      status: 'running',
      replicas: {
        current: 2,
        desired: 2,
      },
      cpu: {
        used: '350m',
        limit: '1000m',
      },
      memory: {
        used: '512Mi',
        limit: '1Gi',
      },
      age: '5d',
    },
    {
      id: 'workload-3',
      name: 'postgres-db',
      type: 'statefulset',
      namespace: 'database',
      status: 'running',
      replicas: {
        current: 1,
        desired: 1,
      },
      cpu: {
        used: '500m',
        limit: '2000m',
      },
      memory: {
        used: '1.5Gi',
        limit: '4Gi',
      },
      age: '7d',
    },
    {
      id: 'workload-4',
      name: 'redis-cache',
      type: 'statefulset',
      namespace: 'cache',
      status: 'running',
      replicas: {
        current: 3,
        desired: 3,
      },
      cpu: {
        used: '200m',
        limit: '500m',
      },
      memory: {
        used: '512Mi',
        limit: '1Gi',
      },
      age: '2d',
    },
    {
      id: 'workload-5',
      name: 'log-collector',
      type: 'daemonset',
      namespace: 'monitoring',
      status: 'running',
      replicas: {
        current: 5,
        desired: 5,
      },
      cpu: {
        used: '100m',
        limit: '200m',
      },
      memory: {
        used: '128Mi',
        limit: '256Mi',
      },
      age: '10d',
    },
    {
      id: 'workload-6',
      name: 'backup-job',
      type: 'cronjob',
      namespace: 'backup',
      status: 'completed',
      replicas: {
        current: 0,
        desired: 0,
      },
      cpu: {
        used: '0m',
        limit: '500m',
      },
      memory: {
        used: '0Mi',
        limit: '1Gi',
      },
      age: '1d',
    },
    {
      id: 'workload-7',
      name: 'data-processor',
      type: 'job',
      namespace: 'batch',
      status: 'pending',
      replicas: {
        current: 1,
        desired: 1,
      },
      cpu: {
        used: '300m',
        limit: '1000m',
      },
      memory: {
        used: '512Mi',
        limit: '2Gi',
      },
      age: '5h',
    },
    {
      id: 'workload-8',
      name: 'maintenance-job',
      type: 'job',
      namespace: 'system',
      status: 'failed',
      replicas: {
        current: 0,
        desired: 1,
      },
      cpu: {
        used: '0m',
        limit: '500m',
      },
      memory: {
        used: '0Mi',
        limit: '1Gi',
      },
      age: '2h',
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNamespace, setSelectedNamespace] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedStatus, setSelectedStatus] = useState('all');

  const namespaces = ['all', ...new Set(workloads.map(w => w.namespace))];
  const types = ['all', ...new Set(workloads.map(w => w.type))];
  const statuses = ['all', ...new Set(workloads.map(w => w.status))];

  const filteredWorkloads = workloads.filter(workload => {
    const matchesSearch = workload.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesNamespace = selectedNamespace === 'all' || workload.namespace === selectedNamespace;
    const matchesType = selectedType === 'all' || workload.type === selectedType;
    const matchesStatus = selectedStatus === 'all' || workload.status === selectedStatus;
    
    return matchesSearch && matchesNamespace && matchesType && matchesStatus;
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Workloads</h1>
        
        <div className="mt-4 sm:mt-0 flex space-x-2">
          <button className="btn btn-outline flex items-center">
            <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
            Refresh
          </button>
          <button className="btn btn-primary flex items-center">
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            Create
          </button>
        </div>
      </div>

      <div className="card p-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-6 space-y-4 md:space-y-0">
          <div className="relative w-full md:w-64">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white dark:bg-gray-700 dark:border-gray-600 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm transition duration-150 ease-in-out"
              placeholder="Search workloads"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="flex flex-wrap gap-2">
            <div className="relative">
              <select
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                value={selectedNamespace}
                onChange={(e) => setSelectedNamespace(e.target.value)}
              >
                {namespaces.map((namespace) => (
                  <option key={namespace} value={namespace}>
                    {namespace === 'all' ? 'All Namespaces' : namespace}
                  </option>
                ))}
              </select>
            </div>

            <div className="relative">
              <select
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
              >
                {types.map((type) => (
                  <option key={type} value={type}>
                    {type === 'all' ? 'All Types' : type.charAt(0).toUpperCase() + type.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <div className="relative">
              <select
                className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
              >
                {statuses.map((status) => (
                  <option key={status} value={status}>
                    {status === 'all' ? 'All Statuses' : status.charAt(0).toUpperCase() + status.slice(1)}
                  </option>
                ))}
              </select>
            </div>

            <button
              type="button"
              className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:hover:bg-gray-600"
              onClick={() => {
                setSearchTerm('');
                setSelectedNamespace('all');
                setSelectedType('all');
                setSelectedStatus('all');
              }}
            >
              Clear Filters
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredWorkloads.length > 0 ? (
            filteredWorkloads.map((workload) => (
              <WorkloadCard key={workload.id} workload={workload} />
            ))
          ) : (
            <div className="col-span-full flex flex-col items-center justify-center py-12">
              <CubeTransparentIcon className="h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No workloads found</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Try adjusting your search or filter criteria.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}