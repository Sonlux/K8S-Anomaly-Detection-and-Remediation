import { useEffect, useState } from "react";
import { Monitor, Server, AlertTriangle, Wrench } from "lucide-react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid,
  Legend,
} from "recharts";

export default function DASHBOARD() {
  const [podStats, setPodStats] = useState([]);
  const [loading, setLoading] = useState(true);
  const [anomaliesCount, setAnomaliesCount] = useState(0);
  const [trendData, setTrendData] = useState([]);

  useEffect(() => {
    fetch("http://localhost:4000/api/pods/metrics")
      .then((res) => res.json())
      .then((data) => {
        const formatted = data.map((p) => ({
          name: p.name,
          cpu: parseInt(p.cpu.replace("m", "")) || 0,
          memory: parseInt(p.memory.replace("Mi", "")) || 0,
        }));
        setPodStats(formatted);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    fetch("http://localhost:4000/api/anomalies")
      .then((res) => res.json())
      .then((data) => setAnomaliesCount(data.length || 0))
      .catch(() => setAnomaliesCount(0));
  }, []);

  useEffect(() => {
    fetch("http://localhost:4000/api/pods/trend")
      .then((res) => res.json())
      .then((data) => setTrendData(data))
      .catch(() => setTrendData([]));
  }, []);

  const colors = [
    "#6366F1",
    "#10B981",
    "#F59E0B",
    "#EF4444",
    "#3B82F6",
    "#8B5CF6",
  ];
  const uniquePods = [...new Set(trendData.map((d) => d.pod))];
  const chartAxisColor = "currentColor";
  const chartGridColor = "#e5e7eb";

  return (
    <div className="space-y-6 text-gray-900 dark:text-white">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard icon={<Monitor />} label="Total Clusters" value="1" />
        <MetricCard
          icon={<Server />}
          label="Active Pods"
          value={podStats.length}
        />
        <MetricCard
          icon={<AlertTriangle />}
          label="Live Anomalies"
          value={anomaliesCount}
        />
        <MetricCard icon={<Wrench />} label="Remediated" value="5" />
      </div>

      <ChartCard title="Pod CPU Usage">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={podStats}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              interval={0}
              angle={-45}
              textAnchor="end"
              height={100}
              stroke={chartAxisColor}
            />
            <YAxis stroke={chartAxisColor} />
            <Tooltip />
            <Bar dataKey="cpu" fill="#60A5FA" name="CPU (m)" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Pod Memory Usage">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={podStats}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="name"
              interval={0}
              angle={-45}
              textAnchor="end"
              height={100}
              stroke={chartAxisColor}
            />
            <YAxis stroke={chartAxisColor} />
            <Tooltip />
            <Bar dataKey="memory" fill="#34D399" name="Memory (Mi)" />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <ChartCard title="Pod CPU & Memory Trends">
        {trendData.length > 0 ? (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={trendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                angle={-25}
                textAnchor="end"
                height={60}
                stroke={chartAxisColor}
              />
              <YAxis stroke={chartAxisColor} />
              <Tooltip />
              <Legend />
              {uniquePods.map((pod, index) => (
                <Line
                  key={`${pod}-cpu`}
                  type="monotone"
                  dataKey={(d) => (d.pod === pod ? d.cpu : null)}
                  name={`${pod} CPU`}
                  stroke={colors[index % colors.length]}
                  dot={false}
                />
              ))}
              {uniquePods.map((pod, index) => (
                <Line
                  key={`${pod}-mem`}
                  type="monotone"
                  dataKey={(d) => (d.pod === pod ? d.memory : null)}
                  name={`${pod} Mem`}
                  stroke={colors[(index + 2) % colors.length]}
                  strokeDasharray="4 2"
                  dot={false}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-sm text-gray-500">No trend data available.</p>
        )}
      </ChartCard>
    </div>
  );
}

function MetricCard({ icon, label, value }) {
  return (
    <div className="bg-white dark:bg-gray-800 rounded-2xl p-4 shadow flex items-center space-x-4">
      <div className="text-blue-500 dark:text-blue-400">{icon}</div>
      <div>
        <div className="text-gray-600 dark:text-gray-300 text-sm">{label}</div>
        <div className="font-bold text-xl">{value}</div>
      </div>
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <div className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow">
      <h2 className="text-lg font-semibold mb-4">{title}</h2>
      {children}
    </div>
  );
}
