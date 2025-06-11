"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  ServerIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
  ShieldCheckIcon,
  ChartBarIcon,
  CpuChipIcon,
} from "@heroicons/react/24/outline";
import ResourceMetricsCards from "@/components/dashboard/ResourceMetricsCards";

// Define Kubernetes types
interface PodStatus {
  running: number;
  pending: number;
  failed: number;
  total: number;
}

interface ClusterMetrics {
  cpuUsage: number;
  memoryUsage: number;
  storageUsage: number;
  anomaliesDetected: number;
}

interface Anomaly {
  id: string;
  podName: string;
  namespace: string;
  severity: "critical" | "warning" | "info";
  type: string;
  timestamp: string;
  status: string;
  description: string;
}

const KodaDashboardPage = () => {
  const [loading, setLoading] = useState(false);
  const [podStatus, setPodStatus] = useState<PodStatus>({
    running: 78,
    pending: 5,
    failed: 3,
    total: 86,
  });

  const [clusterMetrics, setClusterMetrics] = useState<ClusterMetrics>({
    cpuUsage: 42,
    memoryUsage: 58,
    storageUsage: 37,
    anomaliesDetected: 7,
  });

  // Mock anomalies data
  const [anomalies, setAnomalies] = useState<Anomaly[]>([
    {
      id: "a001",
      podName: "api-gateway-7d8f9b7c5-2xvz4",
      namespace: "production",
      severity: "critical",
      type: "Memory Leak",
      timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(), // 30 mins ago
      status: "active",
      description:
        "Memory usage increasing steadily over time without corresponding traffic increase",
    },
    {
      id: "a002",
      podName: "data-processor-6b7d9c8e5-1qaz2",
      namespace: "data-pipeline",
      severity: "warning",
      type: "CPU Spike",
      timestamp: new Date(Date.now() - 1000 * 60 * 120).toISOString(), // 2 hours ago
      status: "active",
      description:
        "Periodic CPU spikes detected during batch processing operations",
    },
    {
      id: "a003",
      podName: "auth-service-5c6d7e8f9-3edc4",
      namespace: "security",
      severity: "critical",
      type: "Connection Timeout",
      timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(), // 45 mins ago
      status: "active",
      description: "Multiple connection timeouts to database service detected",
    },
    {
      id: "a004",
      podName: "frontend-9e8d7c6b5-5rfv6",
      namespace: "production",
      severity: "warning",
      type: "Slow Response",
      timestamp: new Date(Date.now() - 1000 * 60 * 180).toISOString(), // 3 hours ago
      status: "active",
      description: "API response times exceeding threshold during peak hours",
    },
    {
      id: "a005",
      podName: "cache-4d5e6f7g8-7ujm8",
      namespace: "data-pipeline",
      severity: "info",
      type: "Cache Miss Rate",
      timestamp: new Date(Date.now() - 1000 * 60 * 240).toISOString(), // 4 hours ago
      status: "active",
      description:
        "Increasing cache miss rate affecting application performance",
    },
  ]);

  // Simulate real-time updates
  useEffect(() => {
    const interval = setInterval(() => {
      // Randomly update some metrics to simulate real-time changes
      setClusterMetrics((prev) => ({
        ...prev,
        cpuUsage: Math.max(
          1,
          Math.min(
            100,
            prev.cpuUsage +
              (Math.random() > 0.5 ? 1 : -1) * Math.floor(Math.random() * 3)
          )
        ),
        memoryUsage: Math.max(
          1,
          Math.min(
            100,
            prev.memoryUsage +
              (Math.random() > 0.5 ? 1 : -1) * Math.floor(Math.random() * 2)
          )
        ),
        storageUsage: Math.max(
          1,
          Math.min(100, prev.storageUsage + (Math.random() > 0.6 ? 0.5 : -0.5))
        ),
      }));
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  // Get severity class for styling
  const getSeverityClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200";
      case "warning":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200";
      case "info":
        return "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200";
      default:
        return "bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200";
    }
  };

  // Format timestamp to readable format
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center p-6">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-indigo-500 border-t-transparent"></div>
          <p className="mt-2 text-gray-600 dark:text-gray-300">
            Loading dashboard data...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 h-full overflow-auto bg-gray-50 dark:bg-gray-800">
      <div className="mb-8">
        <h1 className="text-2xl font-bold mb-6 text-gray-800 dark:text-white">
          Cluster Overview
        </h1>

        {/* Resource Usage Metrics */}
        <div className="mb-8">
          <ResourceMetricsCards
            metrics={{
              totalPods: podStatus.total,
              restartedPods: podStatus.pending,
              failedPods: podStatus.failed,
              cpuUsage: clusterMetrics.cpuUsage,
              memoryUsage: clusterMetrics.memoryUsage,
              networkTraffic: Math.floor(Math.random() * 200) + 50, // Mock network traffic data
            }}
          />
        </div>

        {/* Pod Status Overview */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-700 rounded-lg shadow-sm p-6 col-span-1">
            <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">
              Pod Status
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  Running
                </span>
                <div className="flex items-center">
                  <div className="h-3 w-3 rounded-full bg-green-500 mr-2"></div>
                  <span className="text-sm font-medium">
                    {podStatus.running}
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  Pending
                </span>
                <div className="flex items-center">
                  <div className="h-3 w-3 rounded-full bg-yellow-500 mr-2"></div>
                  <span className="text-sm font-medium">
                    {podStatus.pending}
                  </span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600 dark:text-gray-300">
                  Failed
                </span>
                <div className="flex items-center">
                  <div className="h-3 w-3 rounded-full bg-red-500 mr-2"></div>
                  <span className="text-sm font-medium">
                    {podStatus.failed}
                  </span>
                </div>
              </div>
              <div className="pt-4 border-t border-gray-200 dark:border-gray-600">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                    Total Pods
                  </span>
                  <span className="text-lg font-semibold text-indigo-600 dark:text-indigo-400">
                    {podStatus.total}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Detected Anomalies */}
          <div className="bg-white dark:bg-gray-700 rounded-lg shadow-sm p-6 col-span-1 lg:col-span-3">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold text-gray-800 dark:text-white">
                Recent Anomalies
              </h2>
              <span className="px-2.5 py-1 text-xs font-medium rounded-full bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                {clusterMetrics.anomaliesDetected} Detected
              </span>
            </div>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-600">
                <thead>
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Severity
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Pod
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Time
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Status
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-700 divide-y divide-gray-200 dark:divide-gray-600">
                  {anomalies.slice(0, 4).map((anomaly) => (
                    <tr
                      key={anomaly.id}
                      className="hover:bg-gray-50 dark:hover:bg-gray-600 cursor-pointer"
                    >
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span
                          className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getSeverityClass(
                            anomaly.severity
                          )}`}
                        >
                          {anomaly.severity}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <div>
                          <div className="text-sm font-medium text-gray-900 dark:text-white">
                            {anomaly.podName}
                          </div>
                          <div className="text-xs text-gray-500 dark:text-gray-400">
                            {anomaly.namespace}
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-700 dark:text-gray-300">
                        {anomaly.type}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                        {formatTimestamp(anomaly.timestamp)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-200">
                          {anomaly.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 text-right">
              <button className="text-sm text-indigo-600 dark:text-indigo-400 hover:text-indigo-800 dark:hover:text-indigo-300 font-medium">
                View all anomalies →
              </button>
            </div>
          </div>
        </div>

        {/* Resource Utilization Chart */}
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow-sm p-6 mb-8">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">
            Resource Utilization
          </h2>
          <div className="h-64 flex items-center justify-center">
            <div className="text-center text-gray-500 dark:text-gray-400">
              <svg
                className="w-16 h-16 mx-auto mb-4 text-indigo-500"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                />
              </svg>
              <p className="text-sm">
                Resource utilization charts will be displayed here
              </p>
              <p className="text-xs mt-2">
                Connect to Prometheus metrics for real-time data visualization
              </p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-700 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4 text-gray-800 dark:text-white">
            Quick Actions
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button className="p-4 bg-indigo-50 dark:bg-indigo-900 rounded-lg flex flex-col items-center justify-center hover:bg-indigo-100 dark:hover:bg-indigo-800 transition-colors">
              <svg
                className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                Run Diagnostics
              </span>
            </button>
            <button className="p-4 bg-indigo-50 dark:bg-indigo-900 rounded-lg flex flex-col items-center justify-center hover:bg-indigo-100 dark:hover:bg-indigo-800 transition-colors">
              <svg
                className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                Restart Services
              </span>
            </button>
            <button className="p-4 bg-indigo-50 dark:bg-indigo-900 rounded-lg flex flex-col items-center justify-center hover:bg-indigo-100 dark:hover:bg-indigo-800 transition-colors">
              <svg
                className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"
                />
              </svg>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                Security Scan
              </span>
            </button>
            <button className="p-4 bg-indigo-50 dark:bg-indigo-900 rounded-lg flex flex-col items-center justify-center hover:bg-indigo-100 dark:hover:bg-indigo-800 transition-colors">
              <svg
                className="w-6 h-6 text-indigo-600 dark:text-indigo-400 mb-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-200">
                Settings
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default KodaDashboardPage;
