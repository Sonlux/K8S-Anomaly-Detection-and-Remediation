import { useEffect, useState } from "react";

export default function NODES() {
  const [nodes, setNodes] = useState([]);

  useEffect(() => {
    fetch("http://localhost:4000/api/nodes/metrics")
      .then((res) => res.json())
      .then(setNodes)
      .catch(console.error);
  }, []);

  return (
    <div className="p-6 space-y-4">
      <h1 className="text-2xl font-bold text-gray-800">Node Metrics</h1>
      {nodes.length === 0 ? (
        <p className="text-gray-500">Loading node data...</p>
      ) : (
        <table className="w-full text-sm border">
          <thead className="bg-gray-100">
            <tr className="text-left">
              <th className="p-2">Node</th>
              <th className="p-2">CPU</th>
              <th className="p-2">CPU %</th>
              <th className="p-2">Memory</th>
              <th className="p-2">Memory %</th>
            </tr>
          </thead>
          <tbody>
            {nodes.map((n, i) => (
              <tr key={i} className="border-t hover:bg-gray-50">
                <td className="p-2">{n.name}</td>
                <td className="p-2">{n.cpu}</td>
                <td className="p-2">{n.cpuPerc}</td>
                <td className="p-2">{n.mem}</td>
                <td className="p-2">{n.memPerc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
