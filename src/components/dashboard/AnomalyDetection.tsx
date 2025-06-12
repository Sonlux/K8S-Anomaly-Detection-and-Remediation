'use client';

import { useState } from 'react';
import { 
  ExclamationTriangleIcon, 
  ArrowTopRightOnSquareIcon,
  CheckCircleIcon,
  XCircleIcon
} from '@heroicons/react/24/outline';

interface Anomaly {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: string;
  resource: {
    type: string;
    name: string;
    namespace: string;
  };
  status: 'active' | 'resolved' | 'acknowledged';
  remediation?: string;
}

interface AnomalyDetectionProps {
  anomalies: Anomaly[];
}

const AnomalyDetection: React.FC<AnomalyDetectionProps> = ({ anomalies }) => {
  const [filter, setFilter] = useState('all');
  const [expandedAnomalyId, setExpandedAnomalyId] = useState<string | null>(null);

  const toggleExpand = (id: string) => {
    if (expandedAnomalyId === id) {
      setExpandedAnomalyId(null);
    } else {
      setExpandedAnomalyId(id);
    }
  };

  const getSeverityColor = (severity: 'low' | 'medium' | 'high' | 'critical') => {
    switch (severity) {
      case 'low':
        return 'bg-primary-100 text-primary-800 dark:bg-primary-900 dark:text-primary-300';
      case 'medium':
        return 'bg-warning-100 text-warning-800 dark:bg-warning-900 dark:text-warning-300';
      case 'high':
        return 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-300';
      case 'critical':
        return 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-300 border border-danger-500';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getStatusColor = (status: 'active' | 'resolved' | 'acknowledged') => {
    switch (status) {
      case 'active':
        return 'bg-danger-100 text-danger-800 dark:bg-danger-900 dark:text-danger-300';
      case 'resolved':
        return 'bg-success-100 text-success-800 dark:bg-success-900 dark:text-success-300';
      case 'acknowledged':
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300';
    }
  };

  const getStatusIcon = (status: 'active' | 'resolved' | 'acknowledged') => {
    switch (status) {
      case 'active':
        return <ExclamationTriangleIcon className="h-5 w-5 text-danger-500" />;
      case 'resolved':
        return <CheckCircleIcon className="h-5 w-5 text-success-500" />;
      case 'acknowledged':
        return <XCircleIcon className="h-5 w-5 text-gray-500" />;
      default:
        return null;
    }
  };

  const filteredAnomalies = filter === 'all' 
    ? anomalies 
    : anomalies.filter(anomaly => anomaly.status === filter);

  return (
    <div className="card p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
        <div className="flex items-center mb-4 sm:mb-0">
          <ExclamationTriangleIcon className="h-6 w-6 text-warning-500 mr-2" />
          <h2 className="text-lg font-bold text-gray-900 dark:text-white">Anomaly Detection</h2>
          <span className="ml-2 px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300">
            {anomalies.length}
          </span>
        </div>
        
        <div className="flex space-x-2">
          <button
            className={`px-3 py-1 text-xs font-medium rounded-md ${filter === 'all' ? 'bg-primary-100 text-primary-700 dark:bg-primary-900 dark:text-primary-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
            onClick={() => setFilter('all')}
          >
            All
          </button>
          <button
            className={`px-3 py-1 text-xs font-medium rounded-md ${filter === 'active' ? 'bg-danger-100 text-danger-700 dark:bg-danger-900 dark:text-danger-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
            onClick={() => setFilter('active')}
          >
            Active
          </button>
          <button
            className={`px-3 py-1 text-xs font-medium rounded-md ${filter === 'acknowledged' ? 'bg-gray-200 text-gray-700 dark:bg-gray-700 dark:text-gray-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
            onClick={() => setFilter('acknowledged')}
          >
            Acknowledged
          </button>
          <button
            className={`px-3 py-1 text-xs font-medium rounded-md ${filter === 'resolved' ? 'bg-success-100 text-success-700 dark:bg-success-900 dark:text-success-300' : 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300'}`}
            onClick={() => setFilter('resolved')}
          >
            Resolved
          </button>
        </div>
      </div>

      <div className="space-y-4">
        {filteredAnomalies.length > 0 ? (
          filteredAnomalies.map((anomaly) => (
            <div 
              key={anomaly.id} 
              className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden"
            >
              <div 
                className="p-4 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-750 flex items-center justify-between"
                onClick={() => toggleExpand(anomaly.id)}
              >
                <div className="flex items-center">
                  {getStatusIcon(anomaly.status)}
                  <div className="ml-3">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white">{anomaly.title}</h3>
                    <div className="flex items-center mt-1 space-x-2">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(anomaly.severity)}`}>
                        {anomaly.severity.toUpperCase()}
                      </span>
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(anomaly.status)}`}>
                        {anomaly.status}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        {anomaly.resource.type} | {anomaly.resource.namespace}/{anomaly.resource.name}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {anomaly.timestamp}
                </div>
              </div>
              
              {expandedAnomalyId === anomaly.id && (
                <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-750">
                  <p className="text-sm text-gray-700 dark:text-gray-300 mb-4">
                    {anomaly.description}
                  </p>
                  
                  {anomaly.remediation && (
                    <div className="mb-4">
                      <h4 className="text-xs font-medium text-gray-700 dark:text-gray-300 uppercase mb-2">Recommended Action</h4>
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        {anomaly.remediation}
                      </p>
                    </div>
                  )}
                  
                  <div className="flex justify-end space-x-2">
                    {anomaly.status === 'active' && (
                      <button className="btn btn-sm btn-outline">
                        Acknowledge
                      </button>
                    )}
                    <button className="btn btn-sm btn-primary flex items-center">
                      <span>View Details</span>
                      <ArrowTopRightOnSquareIcon className="ml-1 h-4 w-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="text-center py-6">
            <CheckCircleIcon className="mx-auto h-12 w-12 text-success-500" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No anomalies found</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              All systems are operating normally.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnomalyDetection;