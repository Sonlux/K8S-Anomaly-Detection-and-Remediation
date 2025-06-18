
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const MemoryChart = () => {
  const [data, setData] = useState(() => {
    const initialData = [];
    for (let i = 0; i < 20; i++) {
      initialData.push({
        time: new Date(Date.now() - (19 - i) * 30000).toLocaleTimeString('en-US', { 
          hour12: false, 
          minute: '2-digit', 
          second: '2-digit' 
        }),
        memory: Math.random() * 30 + 50,
        available: Math.random() * 20 + 20
      });
    }
    return initialData;
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prevData => {
        const newData = [...prevData.slice(1)];
        const memUsage = Math.random() * 30 + 50 + (Math.cos(Date.now() / 8000) * 15);
        newData.push({
          time: new Date().toLocaleTimeString('en-US', { 
            hour12: false, 
            minute: '2-digit', 
            second: '2-digit' 
          }),
          memory: memUsage,
          available: 100 - memUsage
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
          <p className="text-blue-400">{`Used: ${payload[0].value.toFixed(1)}%`}</p>
          <p className="text-cyan-400">{`Available: ${payload[1].value.toFixed(1)}%`}</p>
        </motion.div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <defs>
            <linearGradient id="memoryGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#3B82F6" stopOpacity={0.1}/>
            </linearGradient>
            <linearGradient id="availableGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#06B6D4" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#06B6D4" stopOpacity={0.1}/>
            </linearGradient>
          </defs>
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
          <Area
            type="monotone"
            dataKey="memory"
            stackId="1"
            stroke="#3B82F6"
            fill="url(#memoryGradient)"
          />
          <Area
            type="monotone"
            dataKey="available"
            stackId="1"
            stroke="#06B6D4"
            fill="url(#availableGradient)"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};

export default MemoryChart;
