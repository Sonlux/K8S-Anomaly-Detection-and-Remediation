import React from 'react';

const Sidebar = () => {
  return (
    <div className="w-64 bg-blue-800 text-white p-4">
      <h1 className="text-xl font-bold mb-6">K8s Dashboard</h1>
      <nav>
        <ul>
          <li className="mb-2">
            <a href="#" className="block p-2 hover:bg-blue-700 rounded">Overview</a>
          </li>
          <li className="mb-2">
            <a href="#" className="block p-2 hover:bg-blue-700 rounded">Metrics</a>
          </li>
          <li className="mb-2">
            <a href="#" className="block p-2 hover:bg-blue-700 rounded">Anomalies</a>
          </li>
          <li className="mb-2">
            <a href="#" className="block p-2 hover:bg-blue-700 rounded">Remediation</a>
          </li>
        </ul>
      </nav>
    </div>
  );
};

export default Sidebar;