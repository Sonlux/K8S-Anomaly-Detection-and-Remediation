import { useState } from "react";
import { useAnomalies } from "../context/AnomalyContext";

export default function ANOMALIES() {
  const { anomalies, remediate } = useAnomalies();
  const [hovered, setHovered] = useState(null);

  const handleRemediate = (item) => {
    const time = new Date().toLocaleString();
    const record = { ...item, time };
    fetch("http://localhost:4000/api/remediations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(record),
    })
      .then(() => remediate(item.id))
      .catch(console.error);
  };

  return (
    <div className="p-6 space-y-6 relative">
      <h1 className="text-2xl font-bold text-gray-800">Active Anomalies</h1>
      {anomalies.length === 0 ? (
        <p className="text-green-600">✅ No anomalies detected</p>
      ) : (
        <table className="w-full text-sm relative">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="py-2">#</th>
              <th className="py-2">Pod</th>
              <th className="py-2">Cause</th>
              <th className="py-2">Severity</th>
              <th className="py-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {anomalies.map((a, index) => (
              <tr
                key={a.id}
                onMouseEnter={() => setHovered(a.id)}
                onMouseLeave={() => setHovered(null)}
                className="border-b group hover:bg-gray-50 relative"
              >
                <td className="py-2">{index + 1}</td>
                <td className="py-2">{a.pod}</td>
                <td className="py-2">{a.cause}</td>
                <td className="py-2 font-semibold text-red-600">
                  {a.severity}
                </td>
                <td className="py-2">
                  <button
                    onClick={() => handleRemediate(a)}
                    className="invisible group-hover:visible text-green-600 font-semibold hover:text-green-800 flex items-center space-x-1"
                  >
                    <span>Remediate</span>
                    <span>✅</span>
                  </button>
                </td>
                {hovered === a.id && (
                  <td
                    colSpan={5}
                    className="absolute z-10 bg-white border rounded shadow-lg p-4 top-full left-1/2 -translate-x-1/2 w-96"
                  >
                    <h3 className="font-bold text-lg mb-1">Pod: {a.pod}</h3>
                    <p className="text-sm text-gray-600 mb-1">
                      Cause: {a.cause}
                    </p>
                    <p className="text-sm text-gray-600 mb-2">
                      Severity: {a.severity}
                    </p>
                    <div className="flex justify-between items-center">
                      <button className="text-sm text-blue-600 hover:underline">
                        More Details
                      </button>
                      <button
                        className="bg-green-500 text-white px-3 py-1 rounded text-sm hover:bg-green-600"
                        onClick={() => handleRemediate(a)}
                      >
                        ✅ Remediate
                      </button>
                    </div>
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
