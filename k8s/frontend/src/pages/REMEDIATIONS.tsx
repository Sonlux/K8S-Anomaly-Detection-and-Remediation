import { useEffect, useState } from "react";

export default function REMEDIATIONS() {
  const [remediated, setRemediated] = useState([]);
  const [filter, setFilter] = useState(
    () => localStorage.getItem("remediation-filter") || "All"
  );
  const [search, setSearch] = useState(
    () => localStorage.getItem("remediation-search") || ""
  );
  const [dateFilter, setDateFilter] = useState(
    () => localStorage.getItem("remediation-date") || ""
  );

  useEffect(() => {
    fetch("http://localhost:4000/api/remediations")
      .then((res) => res.json())
      .then((data) => setRemediated(data))
      .catch((err) => console.error("Failed to fetch remediations", err));
  }, []);

  useEffect(() => {
    localStorage.setItem("remediation-filter", filter);
  }, [filter]);

  useEffect(() => {
    localStorage.setItem("remediation-search", search);
  }, [search]);

  useEffect(() => {
    localStorage.setItem("remediation-date", dateFilter);
  }, [dateFilter]);

  const filteredData = remediated.filter((item) => {
    const matchesSeverity = filter === "All" || item.severity === filter;
    const matchesSearch =
      item.pod.toLowerCase().includes(search.toLowerCase()) ||
      item.cause.toLowerCase().includes(search.toLowerCase());
    const matchesDate = !dateFilter || item.time.startsWith(dateFilter);
    return matchesSeverity && matchesSearch && matchesDate;
  });

  const handleExport = () => {
    const csv = [
      ["Pod", "Cause", "Severity", "Remediated At"],
      ...filteredData.map((item) => [
        item.pod,
        item.cause,
        item.severity,
        item.time,
      ]),
    ]
      .map((row) => row.join(","))
      .join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "remediations.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getSeverityIcon = (level) => {
    switch (level) {
      case "Critical":
        return "🚨";
      case "Warning":
        return "⚠️";
      case "Moderate":
        return "🔶";
      default:
        return "ℹ️";
    }
  };

  const postRemediation = (item) => {
    fetch("http://localhost:4000/api/remediations", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(item),
    })
      .then((res) => res.json())
      .then(() => {
        setRemediated((prev) => [...prev, item]);
      })
      .catch((err) => console.error("Failed to save remediation", err));
  };

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">Remediation History</h1>

      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex space-x-2">
          <label className="text-sm">Severity:</label>
          <select
            className="border px-2 py-1 rounded text-sm"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          >
            <option value="All">All</option>
            <option value="Critical">Critical</option>
            <option value="Warning">Warning</option>
            <option value="Moderate">Moderate</option>
          </select>

          <label className="text-sm">Date:</label>
          <input
            type="date"
            className="border px-2 py-1 rounded text-sm"
            value={dateFilter}
            onChange={(e) => setDateFilter(e.target.value)}
          />
        </div>

        <div className="flex-grow">
          <input
            type="text"
            placeholder="Search pod or cause..."
            className="border px-3 py-1 rounded text-sm w-full"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <button
          onClick={handleExport}
          className="bg-blue-500 text-white px-4 py-1 rounded hover:bg-blue-600 text-sm"
        >
          Export CSV
        </button>
      </div>

      {filteredData.length === 0 ? (
        <p className="text-gray-500">
          No remediations match the selected filters.
        </p>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left text-gray-500 border-b">
              <th className="py-2">#</th>
              <th className="py-2">Pod</th>
              <th className="py-2">Cause</th>
              <th className="py-2">Severity</th>
              <th className="py-2">Remediated At</th>
            </tr>
          </thead>
          <tbody>
            {filteredData.map((item, index) => (
              <tr key={item.id || index} className="border-b">
                <td className="py-2">{index + 1}</td>
                <td className="py-2">{item.pod}</td>
                <td className="py-2">{item.cause}</td>
                <td className="py-2 font-semibold">
                  <span className="mr-1">{getSeverityIcon(item.severity)}</span>
                  {item.severity}
                </td>
                <td className="py-2 text-green-600">{item.time}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
