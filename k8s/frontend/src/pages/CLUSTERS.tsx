import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

const mockClusterData = [
  { name: "minikube", cpu: 35, memory: 60 },
  { name: "worker-1", cpu: 45, memory: 70 },
  { name: "worker-2", cpu: 25, memory: 40 },
];

export default function CLUSTERS() {
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-gray-800">
        Cluster Resource Usage
      </h1>
      <div className="bg-white rounded-2xl shadow p-4">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={mockClusterData}
            margin={{ top: 20, right: 30, left: 0, bottom: 5 }}
          >
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="cpu" fill="#60A5FA" name="CPU Usage (%)" />
            <Bar dataKey="memory" fill="#F59E0B" name="Memory Usage (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
