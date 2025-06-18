
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const NodeHealthChart = () => {
  const [data, setData] = useState(() => {
    return Array.from({ length: 12 }, (_, i) => ({
      node: `node-${i + 1}`,
      cpu: Math.random() * 80 + 10,
      memory: Math.random() * 80 + 10,
      status: Math.random() > 0.9 ? 'warning' : 'healthy'
    }));
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prevData => 
        prevData.map(node => ({
          ...node,
          cpu: Math.max(5, Math.min(95, node.cpu + (Math.random() - 0.5) * 10)),
          memory: Math.max(5, Math.min(95, node.memory + (Math.random() - 0.5) * 10)),
          status: node.cpu > 80 || node.memory > 80 ? 'warning' : 'healthy'
        }))
      );
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <motion.div 
          className="bg-slate-800/90 backdrop-blur-lg p-3 rounded-lg border border-slate-700/50"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <p className="text-slate-300">{`Node: ${data.node}`}</p>
          <p className="text-blue-400">{`CPU: ${data.cpu.toFixed(1)}%`}</p>
          <p className="text-purple-400">{`Memory: ${data.memory.toFixed(1)}%`}</p>
          <p className={`${data.status === 'healthy' ? 'text-green-400' : 'text-yellow-400'}`}>
            {`Status: ${data.status}`}
          </p>
        </motion.div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            type="number" 
            dataKey="cpu" 
            domain={[0, 100]}
            stroke="#9CA3AF"
            fontSize={12}
            name="CPU %"
          />
          <YAxis 
            type="number" 
            dataKey="memory" 
            domain={[0, 100]}
            stroke="#9CA3AF"
            fontSize={12}
            name="Memory %"
          />
          <Tooltip content={<CustomTooltip />} />
          <Scatter data={data} fill="#8884d8">
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.status === 'healthy' ? '#10B981' : '#F59E0B'} 
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default NodeHealthChart;
