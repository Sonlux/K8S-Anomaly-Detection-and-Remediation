import React from "react";
import { Remediation } from "@/api/types";

interface RemediationListProps {
  remediations: Remediation[];
  onRemediationClick: (remediation: Remediation) => void;
}

const RemediationList: React.FC<RemediationListProps> = ({
  remediations,
  onRemediationClick,
}) => {
  return (
    <div className="bg-gray-800 p-6 rounded-lg shadow-xl">
      <h2 className="text-2xl font-semibold text-indigo-300 mb-6">
        Remediation Progress
      </h2>
      {remediations.length === 0 ? (
        <p className="text-gray-400">No remediations in progress.</p>
      ) : (
        <ul className="space-y-4">
          {remediations.map((remediation) => (
            <li
              key={remediation.id}
              className="bg-gray-700 p-4 rounded-md shadow-md hover:bg-gray-600 transition duration-300 ease-in-out cursor-pointer border border-gray-600"
              onClick={() => onRemediationClick(remediation)}
            >
              <div className="flex justify-between items-center mb-2">
                <span className="text-lg font-medium text-white">
                  {remediation.action}
                </span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-semibold ${
                    remediation.status === "Completed"
                      ? "bg-green-500 text-white"
                      : remediation.status === "In Progress"
                      ? "bg-blue-500 text-white"
                      : "bg-red-500 text-white"
                  }`}
                >
                  {remediation.status}
                </span>
              </div>
              <p className="text-gray-300 text-sm mb-2">
                Anomaly ID: {remediation.anomalyId}
              </p>
              <p className="text-gray-400 text-xs">{remediation.details}</p>
              <div className="flex justify-between text-gray-400 text-xs mt-2">
                <span>{new Date(remediation.timestamp).toLocaleString()}</span>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default RemediationList;
