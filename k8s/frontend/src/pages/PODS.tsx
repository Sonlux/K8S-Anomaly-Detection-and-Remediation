import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { useEffect, useState } from "react";

export default function PODS() {
  const [podData, setPodData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortKey, setSortKey] = useState("cpuVal");

  useEffect(() => {
    fetch("http://localhost:4000/api/pods/metrics")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch pod metrics");
        return res.json();
      })
      .then((data) => {
        const parsed = data.map((item, index) => {
          const cpuVal = parseInt(item.cpu.replace("m", "")) || 0;
          const memoryVal = parseInt(item.memory.replace("Mi", "")) || 0;
          return {
            id: index + 1,
            name: item.name,
            cpu: item.cpu,
            memory: item.memory,
            cpuVal,
            memoryVal,
            isAnomaly: cpuVal > 300 || memoryVal > 140,
          };
        });
        setPodData(parsed);
        setLoading(false);
      })
      .catch((err) => {
        console.error(err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const sortedPods = [...podData].sort((a, b) => b[sortKey] - a[sortKey]);

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Pod CPU Usage (mCPU)</h1>
      {loading && <p className="text-gray-500">Loading metrics...</p>}
      {error && <p className="text-red-500">Error: {error}</p>}

      {!loading && !error && (
        <>
          <div className="bg-white rounded-2xl shadow p-4">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={sortedPods}
                margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
              >
                <XAxis
                  dataKey="name"
                  interval={0}
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="cpuVal" fill="#60A5FA" name="CPU (m)" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-2xl shadow p-4">
            <h2 className="text-lg font-semibold mb-4">Pod Details</h2>
            <div className="mb-2">
              <label className="text-sm mr-2">Sort by:</label>
              <select
                className="border rounded px-2 py-1 text-sm"
                value={sortKey}
                onChange={(e) => setSortKey(e.target.value)}
              >
                <option value="cpuVal">CPU Usage</option>
                <option value="memoryVal">Memory Usage</option>
              </select>
            </div>
            <table className="w-full text-sm">
              <thead>
                <tr className="text-left text-gray-500 border-b">
                  <th className="py-2">#</th>
                  <th className="py-2">Pod Name</th>
                  <th className="py-2">CPU Usage</th>
                  <th className="py-2">Memory Usage</th>
                  <th className="py-2">Status</th>
                </tr>
              </thead>
              <tbody>
                {sortedPods.map((pod) => (
                  <tr
                    key={pod.name}
                    className="border-b hover:bg-gray-50 group cursor-pointer"
                    title={`Cluster Info: ${pod.name.split("-")[0]} | CPU: ${
                      pod.cpu
                    } | Memory: ${pod.memory}`}
                  >
                    <td className="py-2">{pod.id}</td>
                    <td className="py-2">{pod.name}</td>
                    <td
                      className={`py-2 ${
                        pod.cpuVal > 300 ? "text-red-600 font-semibold" : ""
                      }`}
                    >
                      {pod.cpu}
                    </td>
                    <td
                      className={`py-2 ${
                        pod.memoryVal > 140 ? "text-red-600 font-semibold" : ""
                      }`}
                    >
                      {pod.memory}
                    </td>
                    <td className="py-2">
                      {pod.isAnomaly ? (
                        <span className="text-red-500 font-semibold">
                          Anomaly
                        </span>
                      ) : (
                        <span className="text-green-600">Normal</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
