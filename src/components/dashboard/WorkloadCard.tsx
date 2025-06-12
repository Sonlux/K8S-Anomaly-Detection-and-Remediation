'use client';

import { useState } from 'react';
import { 
  CubeTransparentIcon, 
  EllipsisVerticalIcon,
  ArrowPathIcon,
  TrashIcon,
  PencilSquareIcon,
  ChartBarIcon,
  PauseIcon,
  PlayIcon
} from '@heroicons/react/24/outline';

interface WorkloadCardProps {
  workload: {
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
  };
}

const WorkloadCard: React.FC<WorkloadCardProps> = ({ workload }) => {
  const [showDropdown, setShowDropdown] = useState(false);

  const toggleDropdown = () => {
    setShowDropdown(!showDropdown);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'bg-success-500';
      case 'pending':
        return 'bg-warning-500';
      case 'failed':
        return 'bg-danger-500';
      case 'completed':
        return 'bg-primary-500';
      case 'suspended':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'running':
        return 'text-success-500';
      case 'pending':
        return 'text-warning-500';
      case 'failed':
        return 'text-danger-500';
      case 'completed':
        return 'text-primary-500';
      case 'suspended':
        return 'text-gray-500';
      default:
        return 'text-gray-500';
    }
  };

  const getTypeIcon = (type: string) => {
    return <CubeTransparentIcon className="h-6 w-6 text-primary-600 dark:text-primary-400" />;
  };

  return (
    <div className="card p-4 border border-gray-200 dark:border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className="flex-shrink-0 h-10 w-10 flex items-center justify-center rounded-md bg-primary-100 dark:bg-primary-900">
            {getTypeIcon(workload.type)}
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-gray-900 dark:text-white">{workload.name}</h3>
            <div className="flex items-center mt-1">
              <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">{workload.type}</span>
              <span className="mx-1 text-gray-300 dark:text-gray-600">•</span>
              <span className="text-xs text-gray-500 dark:text-gray-400">{workload.namespace}</span>
            </div>
          </div>
        </div>

        <div className="relative">
          <button
            type="button"
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
            onClick={toggleDropdown}
          >
            <EllipsisVerticalIcon className="h-5 w-5" />
          </button>
          
          {showDropdown && (
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
                  <ArrowPathIcon className="mr-3 h-5 w-5 text-gray-400" />
                  Restart
                </button>
                {workload.status === 'running' ? (
                  <button
                    className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    onClick={() => {}}
                  >
                    <PauseIcon className="mr-3 h-5 w-5 text-gray-400" />
                    Pause
                  </button>
                ) : (
                  <button
                    className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700"
                    onClick={() => {}}
                  >
                    <PlayIcon className="mr-3 h-5 w-5 text-gray-400" />
                    Resume
                  </button>
                )}
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
      </div>

      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center">
          <div className={`h-2.5 w-2.5 rounded-full ${getStatusColor(workload.status)} mr-2`}></div>
          <span className={`text-xs font-medium ${getStatusText(workload.status)} capitalize`}>
            {workload.status}
          </span>
        </div>
        <span className="text-xs text-gray-500 dark:text-gray-400">
          Age: {workload.age}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-3">
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Replicas</p>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {workload.replicas.current} / {workload.replicas.desired}
          </p>
        </div>
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">CPU</p>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {workload.cpu.used} / {workload.cpu.limit}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4">
        <div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Memory</p>
          <p className="text-sm font-medium text-gray-900 dark:text-white">
            {workload.memory.used} / {workload.memory.limit}
          </p>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700 flex justify-between">
        <button className="text-xs text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 font-medium">
          View Logs
        </button>
        <button className="text-xs text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 font-medium">
          View Pods
        </button>
      </div>
    </div>
  );
};

export default WorkloadCard;