import React from 'react';
import { formatPercentage, formatMemory, formatDate } from '../../utils/formatters';

const CombinedMetricsView = ({ metrics }) => {
  if (!metrics || metrics.length === 0) {
    return <div className="text-center p-4">No metrics data available</div>;
  }
  
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white">
        <thead className="bg-gray-100">
          <tr>
            <th className="py-2 px-4 border-b text-left">Pod Name</th>
            <th className="py-2 px-4 border-b text-left">CPU</th>
            <th className="py-2 px-4 border-b text-left">Memory</th>
            <th className="py-2 px-4 border-b text-left">Status</th>
            <th className="py-2 px-4 border-b text-left">Last Updated</th>
          </tr>
        </thead>
        <tbody>
          {metrics.map((pod, index) => (
            <tr key={index} className={index % 2 === 0 ? 'bg-gray-50' : 'bg-white'}>
              <td className="py-2 px-4 border-b">{pod.name}</td>
              <td className="py-2 px-4 border-b">
                <div className="flex items-center">
                  <div className="w-16">{formatPercentage(pod.cpu || 0)}</div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 ml-2">
                    <div 
                      className="bg-blue-600 h-2.5 rounded-full" 
                      style={{ width: `${Math.min((pod.cpu || 0) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </td>
              <td className="py-2 px-4 border-b">
                <div className="flex items-center">
                  <div className="w-16">{formatMemory(pod.memory || 0)}</div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 ml-2">
                    <div 
                      className="bg-purple-600 h-2.5 rounded-full" 
                      style={{ width: `${Math.min((pod.memory / (pod.memoryLimit || 1)) * 100, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </td>
              <td className="py-2 px-4 border-b">
                <span className={`px-2 py-1 rounded-full text-xs ${pod.status === 'Running' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                  {pod.status || 'Unknown'}
                </span>
              </td>
              <td className="py-2 px-4 border-b">{formatDate(pod.timestamp || new Date())}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default CombinedMetricsView;