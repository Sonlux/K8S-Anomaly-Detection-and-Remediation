import React from "react";
import { Cluster } from "@/api/types";

interface ClusterListProps {
  clusters: Cluster[];
  onClusterClick: (cluster: Cluster) => void;
}

const ClusterList: React.FC<ClusterListProps> = ({
  clusters,
  onClusterClick,
}) => {
  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-xl">
      <h2 className="text-2xl font-semibold text-indigo-300 mb-6">
        Monitored Clusters
      </h2>
      {clusters.length === 0 ? (
        <p className="text-gray-400">No clusters found.</p>
      ) : (
        <ul className="space-y-4">
          {clusters.map((cluster) => (
            <li
              key={cluster.id}
              className="bg-gray-700 p-4 rounded-md shadow-md hover:bg-gray-600 transition duration-300 ease-in-out cursor-pointer border border-gray-600"
              onClick={() => onClusterClick(cluster)}
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-lg font-medium text-white">
                  {cluster.name}
                </span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    cluster.status === "Healthy"
                      ? "bg-green-500 text-white"
                      : "bg-red-500 text-white"
                  }`}
                >
                  {cluster.status}
                </span>
              </div>
              <div className="text-gray-300 text-sm mb-2">
                <p>Region: {cluster.region}</p>
                <p>Nodes: {cluster.nodeCount}</p>
                <p>Version: {cluster.kubernetesVersion}</p>
              </div>
              <div className="flex justify-between text-gray-400 text-xs">
                <span>CPU Util: {cluster.cpuUtilization}%</span>
                <span>Memory Util: {cluster.memoryUtilization}%</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default ClusterList;
