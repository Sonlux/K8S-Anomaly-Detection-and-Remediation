
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const NetworkChart = () => {
  const [data, setData] = useState(() => {
    const initialData = [];
    for (let i = 0; i < 15; i++) {
      initialData.push({
        time: new Date(Date.now() - (14 - i) * 60000).toLocaleTimeString('en-US', { 
          hour12: false, 
          hour: '2-digit',
          minute: '2-digit'
        }),
        ingress: Math.random() * 100 + 50,
        egress: Math.random() * 80 + 30,
        latency: Math.random() * 20 + 10
      });
    }
    return initialData;
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prevData => {
        const newData = [...prevData.slice(1)];
        newData.push({
          time: new Date().toLocaleTimeString('en-US', { 
            hour12: false, 
            hour: '2-digit',
            minute: '2-digit'
          }),
          ingress: Math.random() * 100 + 50 + (Math.sin(Date.now() / 15000) * 30),
          egress: Math.random() * 80 + 30 + (Math.cos(Date.now() / 12000) * 25),
          latency: Math.random() * 20 + 10
        });
        return newData;
      });
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <motion.div 
          className="bg-slate-800/90 backdrop-blur-lg p-3 rounded-lg border border-slate-700/50"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <p className="text-slate-300">{`Time: ${label}`}</p>
          <p className="text-purple-400">{`Ingress: ${payload[0]?.value?.toFixed(1)} MB/s`}</p>
          <p className="text-pink-400">{`Egress: ${payload[1]?.value?.toFixed(1)} MB/s`}</p>
          <p className="text-yellow-400">{`Latency: ${payload[2]?.value?.toFixed(1)} ms`}</p>
        </motion.div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            fontSize={12}
            interval="preserveStartEnd"
          />
          <YAxis 
            yAxisId="left"
            stroke="#9CA3AF"
            fontSize={12}
          />
          <YAxis 
            yAxisId="right" 
            orientation="right"
            stroke="#9CA3AF"
            fontSize={12}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            yAxisId="left"
            dataKey="ingress" 
            fill="#8B5CF6" 
            opacity={0.8}
          />
          <Bar 
            yAxisId="left"
            dataKey="egress" 
            fill="#EC4899" 
            opacity={0.8}
          />
          <Line 
            yAxisId="right"
            type="monotone" 
            dataKey="latency" 
            stroke="#F59E0B" 
            strokeWidth={3}
            dot={false}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};

export default NetworkChart;
