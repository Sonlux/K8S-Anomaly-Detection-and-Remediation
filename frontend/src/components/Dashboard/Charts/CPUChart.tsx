
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const CPUChart = () => {
  const [data, setData] = useState(() => {
    const initialData = [];
    for (let i = 0; i < 20; i++) {
      initialData.push({
        time: new Date(Date.now() - (19 - i) * 30000).toLocaleTimeString('en-US', { 
          hour12: false, 
          minute: '2-digit', 
          second: '2-digit' 
        }),
        cpu: Math.random() * 40 + 30,
        threshold: 80
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
            minute: '2-digit', 
            second: '2-digit' 
          }),
          cpu: Math.random() * 40 + 30 + (Math.sin(Date.now() / 10000) * 20),
          threshold: 80
        });
        return newData;
      });
    }, 2000);

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
          <p className="text-green-400">{`CPU: ${payload[0].value.toFixed(1)}%`}</p>
        </motion.div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="time" 
            stroke="#9CA3AF"
            fontSize={12}
            interval="preserveStartEnd"
          />
          <YAxis 
            stroke="#9CA3AF"
            fontSize={12}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Line 
            type="monotone" 
            dataKey="cpu" 
            stroke="#10B981" 
            strokeWidth={3}
            dot={false}
            activeDot={{ r: 6, fill: '#10B981' }}
          />
          <Line 
            type="monotone" 
            dataKey="threshold" 
            stroke="#EF4444" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CPUChart;
