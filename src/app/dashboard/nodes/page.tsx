'use client';

import { useState } from 'react';
import { 
  ServerIcon, 
  MagnifyingGlassIcon,
  ArrowPathIcon,
  EllipsisVerticalIcon,
  ArrowsRightLeftIcon,
  BoltIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
  ComputerDesktopIcon,
  CpuChipIcon,
  BeakerIcon
} from '@heroicons/react/24/outline';

interface Node {
  id: string;
  name: string;
  status: 'Ready' | 'NotReady' | 'SchedulingDisabled';
  roles: string[];
  version: string;
  internalIP: string;
  externalIP: string;
  age: string;
  cpu: {
    capacity: string;
    allocatable: string;
    used: string;
    percentage: number;
  };
  memory: {
    capacity: string;
    allocatable: string;
    used: string;
    percentage: number;
  };
  pods: {
    capacity: number;
    used: number;
    percentage: number;
  };
  conditions: {
    type: string;
    status: 'True' | 'False' | 'Unknown';
    lastTransitionTime: string;
    reason: string;
    message: string;
  }[];
  taints: {
    key: string;
    value: string;
    effect: 'NoSchedule' | 'PreferNoSchedule' | 'NoExecute';
  }[];
  labels: Record<string, string>;
}

export default function NodesPage() {
  const [nodes, setNodes] = useState<Node[]>([
    {
      id: 'node-1',
      name: 'master-node-1',
      status: 'Ready',
      roles: ['control-plane', 'master'],
      version: 'v1.25.4',
      internalIP: '10.0.0.10',
      externalIP: '203.0.113.10',
      age: '120d',
      cpu: {
        capacity: '4',
        allocatable: '3.8',
        used: '1.2',
        percentage: 31.6,
      },
      memory: {
        capacity: '16Gi',
        allocatable: '14.5Gi',
        used: '8.2Gi',
        percentage: 56.6,
      },
      pods: {
        capacity: 110,
        used: 32,
        percentage: 29.1,
      },
      conditions: [
        {
          type: 'Ready',
          status: 'True',
          lastTransitionTime: '2023-06-15T10:20:30Z',
          reason: 'KubeletReady',
          message: 'kubelet is posting ready status',
        },
        {
          type: 'DiskPressure',
          status: 'False',
          lastTransitionTime: '2023-06-15T10:20:30Z',
          reason: 'KubeletHasSufficientDisk',
          message: 'kubelet has sufficient disk space available',
        },
        {
          type: 'MemoryPressure',
          status: 'False',
          lastTransitionTime: '2023-06-15T10:20:30Z',
          reason: 'KubeletHasSufficientMemory',
          message: 'kubelet has sufficient memory available',
        },
        {
          type: 'PIDPressure',
          status: 'False',
          lastTransitionTime: '2023-06-15T10:20:30Z',
          reason: 'KubeletHasSufficientPID',
          message: 'kubelet has sufficient PID available',
        },
      ],
      taints: [
        {
          key: 'node-role.kubernetes.io/master',
          value: '',
          effect: 'NoSchedule',
        },
      ],
      labels: {
        'kubernetes.io/hostname': 'master-node-1',
        'node-role.kubernetes.io/control-plane': '',
        'node-role.kubernetes.io/master': '',
        'beta.kubernetes.io/arch': 'amd64',
        'beta.kubernetes.io/os': 'linux',
      },
    },
    {
      id: 'node-2',
      name: 'worker-node-1',
      status: 'Ready',
      roles: ['worker'],
      version: 'v1.25.4',
      internalIP: '10.0.0.11',
      externalIP: '203.0.113.11',
      age: '115d',
      cpu: {
        capacity: '8',
        allocatable: '7.8',
        used: '5.4',
        percentage: 69.2,
      },
      memory: {
        capacity: '32Gi',
        allocatable: '30.5Gi',
        used: '24.8Gi',
        percentage: 81.3,
      },
      pods: {
        capacity: 110,
        used: 78,
        percentage: 70.9,
      },
      conditions: [
        {
          type: 'Ready',
          status: 'True',
          lastTransitionTime: '2023-06-20T08:15:45Z',
          reason: 'KubeletReady',
          message: 'kubelet is posting ready status',
        },
        {
          type: 'DiskPressure',
          status: 'False',
          lastTransitionTime: '2023-06-20T08:15:45Z',
          reason: 'KubeletHasSufficientDisk',
          message: 'kubelet has sufficient disk space available',
        },
        {
          type: 'MemoryPressure',
          status: 'False',
          lastTransitionTime: '2023-06-20T08:15:45Z',
          reason: 'KubeletHasSufficientMemory',
          message: 'kubelet has sufficient memory available',
        },
        {
          type: 'PIDPressure',
          status: 'False',
          lastTransitionTime: '2023-06-20T08:15:45Z',
          reason: 'KubeletHasSufficientPID',
          message: 'kubelet has sufficient PID available',
        },
      ],
      taints: [],
      labels: {
        'kubernetes.io/hostname': 'worker-node-1',
        'node-role.kubernetes.io/worker': '',
        'beta.kubernetes.io/arch': 'amd64',
        'beta.kubernetes.io/os': 'linux',
        'failure-domain.beta.kubernetes.io/zone': 'us-east-1a',
      },
    },
    {
      id: 'node-3',
      name: 'worker-node-2',
      status: 'Ready',
      roles: ['worker'],
      version: 'v1.25.4',
      internalIP: '10.0.0.12',
      externalIP: '203.0.113.12',
      age: '115d',
      cpu: {
        capacity: '8',
        allocatable: '7.8',
        used: '4.2',
        percentage: 53.8,
      },
      memory: {
        capacity: '32Gi',
        allocatable: '30.5Gi',
        used: '18.3Gi',
        percentage: 60.0,
      },
      pods: {
        capacity: 110,
        used: 65,
        percentage: 59.1,
      },
      conditions: [
        {
          type: 'Ready',
          status: 'True',
          lastTransitionTime: '2023-06-20T08:16:12Z',
          reason: 'KubeletReady',
          message: 'kubelet is posting ready status',
        },
        {
          type: 'DiskPressure',
          status: 'False',
          lastTransitionTime: '2023-06-20T08:16:12Z',
          reason: 'KubeletHasSufficientDisk',
          message: 'kubelet has sufficient disk space available',
        },
        {
          type: 'MemoryPressure',
          status: 'False',
          lastTransitionTime: '2023-06-20T08:16:12Z',
          reason: 'KubeletHasSufficientMemory',
          message: 'kubelet has sufficient memory available',
        },
        {
          type: 'PIDPressure',
          status: 'False',
          lastTransitionTime: '2023-06-20T08:16:12Z',
          reason: 'KubeletHasSufficientPID',
          message: 'kubelet has sufficient PID available',
        },
      ],
      taints: [],
      labels: {
        'kubernetes.io/hostname': 'worker-node-2',
        'node-role.kubernetes.io/worker': '',
        'beta.kubernetes.io/arch': 'amd64',
        'beta.kubernetes.io/os': 'linux',
        'failure-domain.beta.kubernetes.io/zone': 'us-east-1b',
      },
    },
    {
      id: 'node-4',
      name: 'worker-node-3',
      status: 'NotReady',
      roles: ['worker'],
      version: 'v1.25.4',
      internalIP: '10.0.0.13',
      externalIP: '203.0.113.13',
      age: '90d',
      cpu: {
        capacity: '8',
        allocatable: '7.8',
        used: '0.1',
        percentage: 1.3,
      },
      memory: {
        capacity: '32Gi',
        allocatable: '30.5Gi',
        used: '2.1Gi',
        percentage: 6.9,
      },
      pods: {
        capacity: 110,
        used: 5,
        percentage: 4.5,
      },
      conditions: [
        {
          type: 'Ready',
          status: 'False',
          lastTransitionTime: '2023-10-05T14:30:22Z',
          reason: 'KubeletNotReady',
          message: 'PLEG is not healthy: pleg was last seen active 15m ago',
        },
        {
          type: 'DiskPressure',
          status: 'False',
          lastTransitionTime: '2023-09-25T08:16:12Z',
          reason: 'KubeletHasSufficientDisk',
          message: 'kubelet has sufficient disk space available',
        },
        {
          type: 'MemoryPressure',
          status: 'False',
          lastTransitionTime: '2023-09-25T08:16:12Z',
          reason: 'KubeletHasSufficientMemory',
          message: 'kubelet has sufficient memory available',
        },
        {
          type: 'PIDPressure',
          status: 'False',
          lastTransitionTime: '2023-09-25T08:16:12Z',
          reason: 'KubeletHasSufficientPID',
          message: 'kubelet has sufficient PID available',
        },
      ],
      taints: [
        {
          key: 'node.kubernetes.io/unreachable',
          value: '',
          effect: 'NoExecute',
        },
        {
          key: 'node.kubernetes.io/not-ready',
          value: '',
          effect: 'NoExecute',
        },
      ],
      labels: {
        'kubernetes.io/hostname': 'worker-node-3',
        'node-role.kubernetes.io/worker': '',
        'beta.kubernetes.io/arch': 'amd64',
        'beta.kubernetes.io/os': 'linux',
        'failure-domain.beta.kubernetes.io/zone': 'us-east-1c',
      },
    },
    {
      id: 'node-5',
      name: 'worker-node-4',
      status: 'SchedulingDisabled',
      roles: ['worker'],
      version: 'v1.25.4',
      internalIP: '10.0.0.14',
      externalIP: '203.0.113.14',
      age: '90d',
      cpu: {
        capacity: '8',
        allocatable: '7.8',
        used: '2.3',
        percentage: 29.5,
      },
      memory: {
        capacity: '32Gi',
        allocatable: '30.5Gi',
        used: '12.8Gi',
        percentage: 42.0,
      },
      pods: {
        capacity: 110,
        used: 45,
        percentage: 40.9,
      },
      conditions: [
        {
          type: 'Ready',
          status: 'True',
          lastTransitionTime: '2023-09-25T08:16:12Z',
          reason: 'KubeletReady',
          message: 'kubelet is posting ready status',
        },
        {
          type: 'DiskPressure',
          status: 'False',
          lastTransitionTime: '2023-09-25T08:16:12Z',
          reason: 'KubeletHasSufficientDisk',
          message: 'kubelet has sufficient disk space available',
        },
        {
          type: 'MemoryPressure',
          status: 'False',
          lastTransitionTime: '2023-09-25T08:16:12Z',
          reason: 'KubeletHasSufficientMemory',
          message: 'kubelet has sufficient memory available',
        },
        {
          type: 'PIDPressure',
          status: 'False',
          lastTransitionTime: '2023-09-25T08:16:12Z',
          reason: 'KubeletHasSufficientPID',
          message: 'kubelet has sufficient PID available',
        },
      ],
      taints: [
        {
          key: 'node.kubernetes.io/unschedulable',
          value: '',
          effect: 'NoSchedule',
        },
      ],
      labels: {
        'kubernetes.io/hostname': 'worker-node-4',
        'node-role.kubernetes.io/worker': '',
        'beta.kubernetes.io/arch': 'amd64',
        'beta.kubernetes.io/os': 'linux',
        'failure-domain.beta.kubernetes.io/zone': 'us-east-1a',
        'maintenance': 'scheduled',
      },
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [expandedNode, setExpandedNode] = useState<string | null>(null);
  const [dropdownOpen, setDropdownOpen] = useState<string | null>(null);

  const filteredNodes = nodes.filter(node => 
    node.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    node.roles.some(role => role.toLowerCase().includes(searchTerm.toLowerCase())) ||
    node.status.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleNodeExpand = (id: string) => {
    if (expandedNode === id) {
      setExpandedNode(null);
    } else {
      setExpandedNode(id);
    }
  };

  const toggleDropdown = (id: string) => {
    if (dropdownOpen === id) {
      setDropdownOpen(null);
    } else {
      setDropdownOpen(id);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Ready':
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case 'NotReady':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'SchedulingDisabled':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200';
    }
  };

  const getConditionIcon = (status: 'True' | 'False' | 'Unknown') => {
    switch (status) {
      case 'True':
        return <CheckCircleIcon className="h-5 w-5 text-green-500" />;
      case 'False':
        return <XCircleIcon className="h-5 w-5 text-red-500" />;
      case 'Unknown':
        return <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />;
    }
  };

  const getUsageColor = (percentage: number) => {
    if (percentage >= 80) return 'text-red-500 dark:text-red-400';
    if (percentage >= 60) return 'text-yellow-500 dark:text-yellow-400';
    return 'text-green-500 dark:text-green-400';
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Nodes</h1>
        
        <div className="mt-4 sm:mt-0 flex space-x-2">
          <button className="btn btn-outline flex items-center">
            <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
            Refresh
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
              placeholder="Search nodes by name, role, or status"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <div className="flex items-center">
              <div className="h-3 w-3 rounded-full bg-green-500 mr-1"></div>
              <span>Ready</span>
            </div>
            <div className="flex items-center">
              <div className="h-3 w-3 rounded-full bg-red-500 mr-1"></div>
              <span>NotReady</span>
            </div>
            <div className="flex items-center">
              <div className="h-3 w-3 rounded-full bg-yellow-500 mr-1"></div>
              <span>SchedulingDisabled</span>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          {filteredNodes.map((node) => (
            <div key={node.id} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
              <div 
                className={`bg-white dark:bg-gray-800 px-6 py-4 cursor-pointer ${expandedNode === node.id ? 'border-b border-gray-200 dark:border-gray-700' : ''}`}
                onClick={() => toggleNodeExpand(node.id)}
              >
                <div className="flex flex-col md:flex-row md:items-center md:justify-between">
                  <div className="flex items-center">
                    <ServerIcon className="h-6 w-6 text-gray-500 dark:text-gray-400" />
                    <div className="ml-4">
                      <div className="flex items-center">
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white">{node.name}</h3>
                        <span className={`ml-2 inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(node.status)}`}>
                          {node.status}
                        </span>
                      </div>
                      <div className="mt-1 flex flex-wrap items-center text-sm text-gray-500 dark:text-gray-400">
                        <span className="mr-4">Version: {node.version}</span>
                        <span className="mr-4">Internal IP: {node.internalIP}</span>
                        <span>Age: {node.age}</span>
                      </div>
                    </div>
                  </div>
                  
                  <div className="mt-4 md:mt-0 flex flex-wrap gap-2">
                    {node.roles.map((role) => (
                      <span 
                        key={role} 
                        className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                      >
                        {role}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex flex-col">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">CPU</span>
                      <span className={`text-sm font-medium ${getUsageColor(node.cpu.percentage)}`}>
                        {node.cpu.used}/{node.cpu.capacity} ({node.cpu.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${node.cpu.percentage >= 80 ? 'bg-red-600' : node.cpu.percentage >= 60 ? 'bg-yellow-400' : 'bg-green-500'}`} 
                        style={{ width: `${node.cpu.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Memory</span>
                      <span className={`text-sm font-medium ${getUsageColor(node.memory.percentage)}`}>
                        {node.memory.used}/{node.memory.capacity} ({node.memory.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${node.memory.percentage >= 80 ? 'bg-red-600' : node.memory.percentage >= 60 ? 'bg-yellow-400' : 'bg-green-500'}`} 
                        style={{ width: `${node.memory.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  
                  <div className="flex flex-col">
                    <div className="flex justify-between items-center mb-1">
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Pods</span>
                      <span className={`text-sm font-medium ${getUsageColor(node.pods.percentage)}`}>
                        {node.pods.used}/{node.pods.capacity} ({node.pods.percentage.toFixed(1)}%)
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${node.pods.percentage >= 80 ? 'bg-red-600' : node.pods.percentage >= 60 ? 'bg-yellow-400' : 'bg-green-500'}`} 
                        style={{ width: `${node.pods.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
              </div>

              {expandedNode === node.id && (
                <div className="bg-gray-50 dark:bg-gray-900 px-6 py-4">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Conditions</h4>
                      <div className="space-y-3">
                        {node.conditions.map((condition, index) => (
                          <div key={index} className="flex items-start">
                            {getConditionIcon(condition.status)}
                            <div className="ml-3">
                              <div className="text-sm font-medium text-gray-900 dark:text-white">{condition.type}</div>
                              <div className="text-sm text-gray-500 dark:text-gray-400">{condition.message}</div>
                              <div className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                                <span>{condition.reason}</span>
                                <span className="mx-1">•</span>
                                <span>Last transition: {new Date(condition.lastTransitionTime).toLocaleString()}</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-6">
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Taints</h4>
                        {node.taints.length > 0 ? (
                          <div className="space-y-2">
                            {node.taints.map((taint, index) => (
                              <div key={index} className="flex items-center">
                                <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500" />
                                <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                                  {taint.key}{taint.value ? `=${taint.value}` : ''}: {taint.effect}
                                </span>
                              </div>
                            ))}
                          </div>
                        ) : (
                          <div className="text-sm text-gray-500 dark:text-gray-400">No taints</div>
                        )}
                      </div>

                      <div>
                        <h4 className="text-sm font-medium text-gray-900 dark:text-white mb-3">Labels</h4>
                        <div className="flex flex-wrap gap-2">
                          {Object.entries(node.labels).map(([key, value]) => (
                            <span 
                              key={key} 
                              className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                              title={`${key}: ${value}`}
                            >
                              {key.split('/').pop()}: {value || 'true'}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-6 flex justify-end">
                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          toggleDropdown(node.id);
                        }}
                        className="btn btn-outline flex items-center"
                      >
                        Actions
                        <EllipsisVerticalIcon className="ml-2 h-5 w-5" />
                      </button>
                      {dropdownOpen === node.id && (
                        <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                            onClick={(e) => e.preventDefault()}
                          >
                            <ComputerDesktopIcon className="mr-3 h-5 w-5 text-gray-400" />
                            View Details
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                            onClick={(e) => e.preventDefault()}
                          >
                            <ArrowsRightLeftIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Cordon/Uncordon
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                            onClick={(e) => e.preventDefault()}
                          >
                            <BoltIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Drain
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                            onClick={(e) => e.preventDefault()}
                          >
                            <CpuChipIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Edit Labels
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                            onClick={(e) => e.preventDefault()}
                          >
                            <BeakerIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Edit Taints
                          </a>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}

          {filteredNodes.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12">
              <ServerIcon className="h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No nodes found</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                Try adjusting your search criteria.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}