'use client';

import { useState } from 'react';
import { 
  TagIcon, 
  PlusIcon,
  MagnifyingGlassIcon,
  ArrowPathIcon,
  EllipsisVerticalIcon,
  TrashIcon,
  PencilSquareIcon,
  DocumentDuplicateIcon,
  LockClosedIcon,
  ShieldCheckIcon
} from '@heroicons/react/24/outline';

interface Namespace {
  id: string;
  name: string;
  status: 'active' | 'terminating';
  phase: string;
  age: string;
  labels: Record<string, string>;
  resourceQuota: {
    cpu: {
      used: string;
      limit: string;
    };
    memory: {
      used: string;
      limit: string;
    };
    pods: {
      used: number;
      limit: number;
    };
  };
  podCount: number;
  serviceCount: number;
  deploymentCount: number;
}

export default function NamespacesPage() {
  const [namespaces, setNamespaces] = useState<Namespace[]>([
    {
      id: 'ns-1',
      name: 'default',
      status: 'active',
      phase: 'Active',
      age: '120d',
      labels: {
        'kubernetes.io/metadata.name': 'default'
      },
      resourceQuota: {
        cpu: {
          used: '1.2',
          limit: '4',
        },
        memory: {
          used: '2.5Gi',
          limit: '8Gi',
        },
        pods: {
          used: 8,
          limit: 20,
        },
      },
      podCount: 8,
      serviceCount: 3,
      deploymentCount: 2,
    },
    {
      id: 'ns-2',
      name: 'kube-system',
      status: 'active',
      phase: 'Active',
      age: '120d',
      labels: {
        'kubernetes.io/metadata.name': 'kube-system',
        'control-plane': 'true'
      },
      resourceQuota: {
        cpu: {
          used: '0.8',
          limit: '2',
        },
        memory: {
          used: '1.2Gi',
          limit: '4Gi',
        },
        pods: {
          used: 12,
          limit: 30,
        },
      },
      podCount: 12,
      serviceCount: 5,
      deploymentCount: 6,
    },
    {
      id: 'ns-3',
      name: 'monitoring',
      status: 'active',
      phase: 'Active',
      age: '45d',
      labels: {
        'kubernetes.io/metadata.name': 'monitoring',
        'app.kubernetes.io/part-of': 'monitoring-stack',
        'app.kubernetes.io/managed-by': 'prometheus-operator'
      },
      resourceQuota: {
        cpu: {
          used: '1.5',
          limit: '4',
        },
        memory: {
          used: '3.2Gi',
          limit: '8Gi',
        },
        pods: {
          used: 15,
          limit: 25,
        },
      },
      podCount: 15,
      serviceCount: 8,
      deploymentCount: 5,
    },
    {
      id: 'ns-4',
      name: 'app-production',
      status: 'active',
      phase: 'Active',
      age: '30d',
      labels: {
        'kubernetes.io/metadata.name': 'app-production',
        'environment': 'production',
        'team': 'backend'
      },
      resourceQuota: {
        cpu: {
          used: '3.2',
          limit: '8',
        },
        memory: {
          used: '6.5Gi',
          limit: '16Gi',
        },
        pods: {
          used: 18,
          limit: 40,
        },
      },
      podCount: 18,
      serviceCount: 7,
      deploymentCount: 9,
    },
    {
      id: 'ns-5',
      name: 'app-staging',
      status: 'active',
      phase: 'Active',
      age: '30d',
      labels: {
        'kubernetes.io/metadata.name': 'app-staging',
        'environment': 'staging',
        'team': 'backend'
      },
      resourceQuota: {
        cpu: {
          used: '1.8',
          limit: '4',
        },
        memory: {
          used: '3.5Gi',
          limit: '8Gi',
        },
        pods: {
          used: 12,
          limit: 25,
        },
      },
      podCount: 12,
      serviceCount: 5,
      deploymentCount: 6,
    },
    {
      id: 'ns-6',
      name: 'database',
      status: 'active',
      phase: 'Active',
      age: '60d',
      labels: {
        'kubernetes.io/metadata.name': 'database',
        'app.kubernetes.io/part-of': 'data-layer',
        'team': 'dba'
      },
      resourceQuota: {
        cpu: {
          used: '2.5',
          limit: '6',
        },
        memory: {
          used: '8Gi',
          limit: '16Gi',
        },
        pods: {
          used: 6,
          limit: 10,
        },
      },
      podCount: 6,
      serviceCount: 3,
      deploymentCount: 2,
    },
    {
      id: 'ns-7',
      name: 'test-namespace',
      status: 'terminating',
      phase: 'Terminating',
      age: '5d',
      labels: {
        'kubernetes.io/metadata.name': 'test-namespace',
        'environment': 'test',
        'temporary': 'true'
      },
      resourceQuota: {
        cpu: {
          used: '0.2',
          limit: '1',
        },
        memory: {
          used: '0.5Gi',
          limit: '2Gi',
        },
        pods: {
          used: 2,
          limit: 10,
        },
      },
      podCount: 2,
      serviceCount: 1,
      deploymentCount: 1,
    },
  ]);

  const [searchTerm, setSearchTerm] = useState('');
  const [dropdownOpen, setDropdownOpen] = useState<string | null>(null);

  const filteredNamespaces = namespaces.filter(namespace => 
    namespace.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const toggleDropdown = (id: string) => {
    if (dropdownOpen === id) {
      setDropdownOpen(null);
    } else {
      setDropdownOpen(id);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
        <h1 className="text-2xl font-bold">Namespaces</h1>
        
        <div className="mt-4 sm:mt-0 flex space-x-2">
          <button className="btn btn-outline flex items-center">
            <ArrowPathIcon className="-ml-1 mr-2 h-5 w-5" />
            Refresh
          </button>
          <button className="btn btn-primary flex items-center">
            <PlusIcon className="-ml-1 mr-2 h-5 w-5" />
            Create Namespace
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
              placeholder="Search namespaces"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-800">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Name
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Age
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Resource Usage
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Workloads
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                  Labels
                </th>
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-gray-900 divide-y divide-gray-200 dark:divide-gray-800">
              {filteredNamespaces.map((namespace) => (
                <tr key={namespace.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <TagIcon className="flex-shrink-0 h-5 w-5 text-gray-500 dark:text-gray-400" />
                      <div className="ml-4">
                        <div className="text-sm font-medium text-gray-900 dark:text-white">
                          {namespace.name}
                        </div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${namespace.status === 'active' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'}`}>
                      {namespace.phase}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {namespace.age}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="space-y-1">
                      <div className="flex items-center">
                        <span className="text-xs text-gray-500 dark:text-gray-400 w-12">CPU:</span>
                        <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 ml-2">
                          <div 
                            className="bg-blue-600 h-2.5 rounded-full" 
                            style={{ width: `${(parseFloat(namespace.resourceQuota.cpu.used) / parseFloat(namespace.resourceQuota.cpu.limit)) * 100}%` }}
                          ></div>
                        </div>
                        <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                          {namespace.resourceQuota.cpu.used}/{namespace.resourceQuota.cpu.limit}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <span className="text-xs text-gray-500 dark:text-gray-400 w-12">Memory:</span>
                        <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 ml-2">
                          <div 
                            className="bg-purple-600 h-2.5 rounded-full" 
                            style={{ width: `${(parseFloat(namespace.resourceQuota.memory.used.replace('Gi', '')) / parseFloat(namespace.resourceQuota.memory.limit.replace('Gi', ''))) * 100}%` }}
                          ></div>
                        </div>
                        <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                          {namespace.resourceQuota.memory.used}/{namespace.resourceQuota.memory.limit}
                        </span>
                      </div>
                      <div className="flex items-center">
                        <span className="text-xs text-gray-500 dark:text-gray-400 w-12">Pods:</span>
                        <div className="w-32 bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 ml-2">
                          <div 
                            className="bg-green-600 h-2.5 rounded-full" 
                            style={{ width: `${(namespace.resourceQuota.pods.used / namespace.resourceQuota.pods.limit) * 100}%` }}
                          ></div>
                        </div>
                        <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                          {namespace.resourceQuota.pods.used}/{namespace.resourceQuota.pods.limit}
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900 dark:text-white">
                      <div className="flex space-x-2">
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                          {namespace.podCount} Pods
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
                          {namespace.serviceCount} Services
                        </span>
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                          {namespace.deploymentCount} Deployments
                        </span>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    <div className="flex flex-wrap gap-1">
                      {Object.entries(namespace.labels).map(([key, value]) => (
                        <span 
                          key={key} 
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200"
                          title={`${key}: ${value}`}
                        >
                          {key.split('/').pop()}: {value.length > 10 ? `${value.substring(0, 10)}...` : value}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div className="relative">
                      <button
                        onClick={() => toggleDropdown(namespace.id)}
                        className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
                      >
                        <EllipsisVerticalIcon className="h-5 w-5" />
                      </button>
                      {dropdownOpen === namespace.id && (
                        <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg py-1 bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 focus:outline-none z-10">
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                          >
                            <PencilSquareIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Edit
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                          >
                            <DocumentDuplicateIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Clone
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                          >
                            <ShieldCheckIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Manage RBAC
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                          >
                            <LockClosedIcon className="mr-3 h-5 w-5 text-gray-400" />
                            Network Policies
                          </a>
                          <a
                            href="#"
                            className="block px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center"
                          >
                            <TrashIcon className="mr-3 h-5 w-5 text-red-500" />
                            Delete
                          </a>
                        </div>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredNamespaces.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12">
            <TagIcon className="h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No namespaces found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              Try adjusting your search criteria.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}