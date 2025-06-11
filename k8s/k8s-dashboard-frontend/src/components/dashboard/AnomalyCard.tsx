import React, { useState, useEffect } from "react";
import { Anomaly } from "@/api/types";

interface PodDetail {
  name: string;
  namespace: string;
  status: string;
  creationTimestamp: string;
  restarts: number;
  cpu: string;
  memory: string;
  image: string;
}

interface AnomalyCardProps {
  anomaly: Anomaly;
  onClick?: (anomaly: Anomaly) => void;
  onRemediate?: (anomaly: Anomaly) => void;
}

const AnomalyCard: React.FC<AnomalyCardProps> = ({
  anomaly,
  onClick,
  onRemediate,
}) => {
  const [isExpanded, setIsExpanded] = useState<boolean>(false);
  const [isRemediating, setIsRemediating] = useState<boolean>(false);
  const [isRemediated, setIsRemediated] = useState<boolean>(
    anomaly.status === "resolved"
  );
  const [podDetails, setPodDetails] = useState<PodDetail[]>([]);
  const [isLoadingPods, setIsLoadingPods] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // Format the timestamp to a readable time
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  // Format the timestamp to a readable date
  const formatDate = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString([], {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  // Get severity class based on severity level
  const getSeverityClass = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "critical":
        return "text-red-600";
      case "high":
        return "text-orange-500";
      case "medium":
        return "text-yellow-500";
      case "low":
        return "text-green-500";
      default:
        return "text-blue-500";
    }
  };

  // Extract pod name from resource string (e.g., "pod/nginx-123" -> "nginx-123")
  const getPodName = (resource: string | undefined): string => {
    if (!resource) return "unknown-pod";
    const parts = resource.split("/");
    return parts.length > 1 ? parts[1] : resource;
  };

  // Calculate affected components based on resource
  const affectedComponents = anomaly.resource ? 1 : 0;
  const pendingComponents = isRemediating ? affectedComponents : 0;
  const notAffectedComponents = isRemediated ? affectedComponents : 0;

  // Handle card click to expand/collapse and fetch pod details
  const handleCardClick = async () => {
    setIsExpanded(!isExpanded);

    // Only fetch pod details if expanding and we don't have them yet
    if (!isExpanded && podDetails.length === 0 && !isLoadingPods) {
      setIsLoadingPods(true);
      setError(null);

      try {
        // Mock fetching pod details - in a real app, this would be an API call
        await new Promise((resolve) => setTimeout(resolve, 800));

        // Create mock pod details based on the anomaly resource
        const podName = getPodName(anomaly.resource);
        const mockPod: PodDetail = {
          name: podName,
          namespace: anomaly.namespace || "default",
          status: isRemediated ? "Running" : "Warning",
          creationTimestamp: new Date(
            Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000
          ).toISOString(),
          restarts: Math.floor(Math.random() * 5),
          cpu: `${(Math.random() * 100).toFixed(1)}m`,
          memory: `${(Math.random() * 256).toFixed(0)}Mi`,
          image: `kubernetes/${podName.split("-")[0]}:latest`,
        };

        setPodDetails([mockPod]);
      } catch (err) {
        console.error("Error fetching pod details:", err);
        setError("Failed to load pod details. Please try again.");
      } finally {
        setIsLoadingPods(false);
      }
    }

    // Call the onClick handler if provided
    if (onClick) {
      onClick(anomaly);
    }
  };

  // Handle remediation button click
  const handleRemediateClick = async (e: React.MouseEvent) => {
    e.stopPropagation(); // Prevent card expansion when clicking the button

    if (isRemediated) return;

    setIsRemediating(true);
    setError(null);

    try {
      // Mock API call for remediation
      await new Promise((resolve) => setTimeout(resolve, 2000));

      setIsRemediated(true);

      // Notify parent component about remediation
      if (onRemediate) {
        onRemediate({
          ...anomaly,
          status: "resolved",
        });
      }
    } catch (err) {
      console.error("Error remediating pod:", err);
      setError("Failed to remediate pod. Please try again.");
    } finally {
      setIsRemediating(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-4 hover:shadow-md transition-all duration-300">
      <div className="cursor-pointer" onClick={handleCardClick}>
        <div className="flex items-start mb-4">
          <div className="bg-gray-100 rounded-full p-3 mr-4">
            {/* Icon based on anomaly type */}
            <span className="text-xl">{isRemediated ? "✅" : "⚠️"}</span>
          </div>
          <div className="flex-1">
            <div className="flex justify-between">
              <h3 className="font-medium text-lg text-gray-800">
                {anomaly.type}
              </h3>
              {isRemediated && (
                <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full flex items-center">
                  <svg
                    className="w-3 h-3 mr-1"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                  Remediated
                </span>
              )}
            </div>
            <p className="text-gray-500 text-sm">
              {anomaly.resource || "Unknown resource"}
            </p>
            <p className="text-gray-700 mt-2">
              {formatTime(anomaly.timestamp)}
            </p>
          </div>
        </div>

        <div className="border-t border-gray-100 pt-4">
          <div className="flex justify-between items-center mb-2">
            <div>
              <span className="text-blue-500 mr-1">
                {affectedComponents} Pod{affectedComponents !== 1 ? "s" : ""}{" "}
                Affected
              </span>
              {!isRemediated && (
                <>
                  <span className="text-gray-400 mx-1">•</span>
                  <span
                    className={
                      isRemediating ? "text-blue-500" : "text-yellow-500"
                    }
                  >
                    {isRemediating ? "Remediating..." : "Needs Action"}
                  </span>
                </>
              )}
            </div>
            <span
              className={`font-medium ${getSeverityClass(anomaly.severity)}`}
            >
              {anomaly.severity.toUpperCase()}
            </span>
          </div>

          <div className="flex justify-between items-center mt-4">
            <p className="text-sm text-gray-600">{anomaly.description}</p>
            <div className="flex items-center">
              {!isRemediated && (
                <button
                  className={`mr-3 px-3 py-1 text-xs font-medium rounded-md focus:outline-none ${
                    isRemediating
                      ? "bg-blue-100 text-blue-800 cursor-wait"
                      : "bg-blue-500 text-white hover:bg-blue-600"
                  }`}
                  onClick={handleRemediateClick}
                  disabled={isRemediating}
                >
                  {isRemediating ? (
                    <span className="flex items-center">
                      <svg
                        className="animate-spin -ml-1 mr-2 h-3 w-3 text-blue-800"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Remediating
                    </span>
                  ) : (
                    "Remediate"
                  )}
                </button>
              )}
              <svg
                className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${
                  isExpanded ? "transform rotate-180" : ""
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 9l-7 7-7-7"
                ></path>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Expanded pod details section */}
      {isExpanded && (
        <div className="mt-4 pt-4 border-t border-gray-100">
          <h4 className="text-sm font-medium text-gray-700 mb-3">
            Pod Details
          </h4>

          {error && (
            <div className="bg-red-50 text-red-700 p-3 rounded-md text-sm mb-3">
              {error}
            </div>
          )}

          {isLoadingPods ? (
            <div className="flex justify-center items-center py-6">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            </div>
          ) : podDetails.length > 0 ? (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead>
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Pod Name
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Created
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Restarts
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      CPU
                    </th>
                    <th className="px-3 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Memory
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {podDetails.map((pod, index) => (
                    <tr key={index} className="hover:bg-gray-100">
                      <td className="px-3 py-2 whitespace-nowrap">
                        {pod.name}
                      </td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                            isRemediated
                              ? "bg-green-100 text-green-800"
                              : "bg-yellow-100 text-yellow-800"
                          }`}
                        >
                          {isRemediated ? "Running" : "Warning"}
                        </span>
                      </td>
                      <td
                        className="px-3 py-2 whitespace-nowrap"
                        title={new Date(pod.creationTimestamp).toLocaleString()}
                      >
                        {formatDate(pod.creationTimestamp)}
                      </td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        {pod.restarts}
                      </td>
                      <td className="px-3 py-2 whitespace-nowrap">{pod.cpu}</td>
                      <td className="px-3 py-2 whitespace-nowrap">
                        {pod.memory}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="text-center py-6 text-gray-500">
              No pod details available
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AnomalyCard;
