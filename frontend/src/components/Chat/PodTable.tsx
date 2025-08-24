import React from "react";

interface Container {
  name: string;
  ready: boolean;
  restart_count: number;
}

interface Pod {
  name: string;
  namespace: string;
  status: string;
  node: string;
  ip: string;
  containers: Container[];
}

export default function PodTable({ pods }: { pods: Pod[] }) {
  if (!pods || pods.length === 0) return null;
  return (
    <div className="overflow-x-auto mt-2">
      <table className="min-w-full text-xs text-left text-slate-200">
        <thead>
          <tr>
            <th className="px-2 py-1">Name</th>
            <th className="px-2 py-1">Namespace</th>
            <th className="px-2 py-1">Status</th>
            <th className="px-2 py-1">Node</th>
            <th className="px-2 py-1">IP</th>
            <th className="px-2 py-1">Containers</th>
          </tr>
        </thead>
        <tbody>
          {pods.map((pod) => (
            <tr key={pod.name + pod.namespace}>
              <td className="px-2 py-1">{pod.name}</td>
              <td className="px-2 py-1">{pod.namespace}</td>
              <td className="px-2 py-1">{pod.status}</td>
              <td className="px-2 py-1">{pod.node}</td>
              <td className="px-2 py-1">{pod.ip}</td>
              <td className="px-2 py-1">
                {pod.containers
                  ?.map(
                    (c: Container) =>
                      `${c.name} (${
                        c.ready ? "Ready" : "Not Ready"
                      }, Restarts: ${c.restart_count})`
                  )
                  .join(", ")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
