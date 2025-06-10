import React, { useState } from 'react';
import useRemediation from '../../hooks/useRemediation';

const AnomalyCard = ({ anomaly }) => {
  const [selectedAction, setSelectedAction] = useState(anomaly.suggestedAction);
  const { executeRemediation, isExecuting, isCompleted } = useRemediation();
  
  const handleExecute = async () => {
    await executeRemediation(anomaly.podName, selectedAction);
  };
  
  // Define action options based on anomaly type
  const getActionOptions = (type) => {
    switch (type) {
      case 'resource_exhaustion':
        return [
          { value: 'increase_cpu', label: 'Increase CPU' },
          { value: 'increase_memory', label: 'Increase Memory' },
          { value: 'restart_pod', label: 'Restart Pod' }
        ];
      case 'oom_risk':
        return [
          { value: 'increase_memory', label: 'Increase Memory' },
          { value: 'optimize_memory', label: 'Optimize Memory Usage' },
          { value: 'restart_pod', label: 'Restart Pod' }
        ];
      case 'crash_loopback':
        return [
          { value: 'fix_configuration', label: 'Fix Configuration' },
          { value: 'restart_pod', label: 'Restart Pod' },
          { value: 'recreate_pod', label: 'Recreate Pod' }
        ];
      default:
        return [
          { value: 'restart_pod', label: 'Restart Pod' },
          { value: 'increase_resources', label: 'Increase Resources' },
          { value: 'investigate', label: 'Investigate Further' }
        ];
    }
  };
  
  const actionOptions = getActionOptions(anomaly.type);
  
  return (
    <div className="bg-white rounded-lg shadow p-4">
      <div className="flex justify-between items-start">
        <div>
          <h3 className="font-bold">{anomaly.podName}</h3>
          <div className="badge badge-warning mt-1">{anomaly.type.replace('_', ' ')}</div>
          <div className="mt-2">
            <p><span className="font-semibold">Confidence:</span> {anomaly.confidence}%</p>
            <p><span className="font-semibold">CPU:</span> {anomaly.metrics.cpu}%</p>
            <p><span className="font-semibold">Memory:</span> {anomaly.metrics.memory}%</p>
          </div>
        </div>
      </div>
      
      <div className="mt-4">
        <label className="font-semibold block mb-1">Remediation Action:</label>
        <select 
          className="w-full p-2 border border-gray-300 rounded"
          value={selectedAction}
          onChange={(e) => setSelectedAction(e.target.value)}
          disabled={isExecuting || isCompleted}
        >
          {actionOptions.map(option => (
            <option key={option.value} value={option.value}>{option.label}</option>
          ))}
        </select>
        
        {selectedAction !== anomaly.suggestedAction && (
          <p className="text-amber-600 text-sm mt-1">
            Warning: This is not the suggested action for this anomaly type.
          </p>
        )}
      </div>
      
      <div className="mt-4">
        {!isCompleted ? (
          <button 
            className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            onClick={handleExecute}
            disabled={isExecuting}
          >
            {isExecuting ? 'Executing...' : 'Execute'}
          </button>
        ) : (
          <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-2 rounded">
            Remediation completed successfully
          </div>
        )}
      </div>
    </div>
  );
};

export default AnomalyCard;