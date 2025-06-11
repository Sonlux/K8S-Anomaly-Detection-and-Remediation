import React from "react";
import { MetricCard } from "./MetricCard";

interface ResourceCardProps {
  title: string;
  value: string;
  description: string;
  icon?: React.ReactNode;
  onClick?: () => void;
}

const ResourceCard: React.FC<ResourceCardProps> = ({
  title,
  value,
  description,
  icon,
  onClick,
}) => {
  return (
    <div
      className="bg-white rounded-lg shadow p-6 flex items-center space-x-4 cursor-pointer hover:shadow-md transition-shadow duration-300"
      onClick={onClick}
    >
      {icon && (
        <div className="bg-gray-100 rounded-full p-4 flex items-center justify-center">
          {icon}
        </div>
      )}
      <div>
        <h3 className="text-gray-500 text-sm font-medium mb-1">{title}</h3>
        <p className="text-3xl font-bold text-gray-800 mb-1">{value}</p>
        <p className="text-xs text-gray-500">{description}</p>
      </div>
    </div>
  );
};

interface ResourceMetricsCardsProps {
  metrics: {
    totalPods: number;
    restartedPods: number;
    failedPods: number;
    cpuUsage: number;
    memoryUsage: number;
    networkTraffic: number;
  };
  onMetricClick?: (metricType: string) => void;
}

const ResourceMetricsCards: React.FC<ResourceMetricsCardsProps> = ({
  metrics,
  onMetricClick = () => {},
}) => {
  // Icons for each metric card
  const renderPodIcon = () => (
    <div className="p-2 rounded-full bg-blue-100 dark:bg-blue-900">
      <svg
        className="w-6 h-6 text-blue-600 dark:text-blue-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
        />
      </svg>
    </div>
  );

  const renderCpuIcon = () => (
    <div className="p-2 rounded-full bg-green-100 dark:bg-green-900">
      <svg
        className="w-6 h-6 text-green-600 dark:text-green-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"
        />
      </svg>
    </div>
  );

  const renderMemoryIcon = () => (
    <div className="p-2 rounded-full bg-purple-100 dark:bg-purple-900">
      <svg
        className="w-6 h-6 text-purple-600 dark:text-purple-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      </svg>
    </div>
  );

  const renderNetworkIcon = () => (
    <div className="p-2 rounded-full bg-indigo-100 dark:bg-indigo-900">
      <svg
        className="w-6 h-6 text-indigo-600 dark:text-indigo-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4"
        />
      </svg>
    </div>
  );

  const renderRestartIcon = () => (
    <div className="p-2 rounded-full bg-yellow-100 dark:bg-yellow-900">
      <svg
        className="w-6 h-6 text-yellow-600 dark:text-yellow-300"
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
    </div>
  );

  const renderFailedIcon = () => (
    <div className="p-2 rounded-full bg-red-100 dark:bg-red-900">
      <svg
        className="w-6 h-6 text-red-600 dark:text-red-300"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
    </div>
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div className="md:col-span-3">
        <h2 className="text-xl font-semibold text-gray-800 dark:text-white mb-4">
          Resource Metrics
        </h2>
      </div>

      <ResourceCard
        title="Total Pods"
        value={`${metrics.totalPods}`}
        description="All clusters"
        icon={renderPodIcon()}
        onClick={() => onMetricClick("pods")}
      />

      <ResourceCard
        title="CPU Usage"
        value={`${metrics.cpuUsage}%`}
        description={metrics.cpuUsage > 70 ? "High" : "Normal"}
        icon={renderCpuIcon()}
        onClick={() => onMetricClick("cpu")}
      />

      <ResourceCard
        title="Memory Usage"
        value={`${metrics.memoryUsage}%`}
        description={metrics.memoryUsage > 80 ? "High" : "Normal"}
        icon={renderMemoryIcon()}
        onClick={() => onMetricClick("memory")}
      />

      <ResourceCard
        title="Network Traffic"
        value={`${metrics.networkTraffic} MB/s`}
        description="Last minute"
        icon={renderNetworkIcon()}
        onClick={() => onMetricClick("network")}
      />

      <ResourceCard
        title="Restarted Pods"
        value={`${metrics.restartedPods}`}
        description={metrics.restartedPods > 5 ? "Investigate" : "Normal"}
        icon={renderRestartIcon()}
        onClick={() => onMetricClick("restarts")}
      />

      <ResourceCard
        title="Failed Pods"
        value={`${metrics.failedPods}`}
        description={metrics.failedPods > 0 ? "Alert" : "Healthy"}
        icon={renderFailedIcon()}
        onClick={() => onMetricClick("failed")}
      />
    </div>
  );
};

export default ResourceMetricsCards;
