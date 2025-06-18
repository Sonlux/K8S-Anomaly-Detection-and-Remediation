
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const PodChart = () => {
  const [data, setData] = useState([
    { name: 'Running', value: 120, color: '#10B981' },
    { name: 'Pending', value: 8, color: '#F59E0B' },
    { name: 'Failed', value: 3, color: '#EF4444' },
    { name: 'Succeeded', value: 25, color: '#3B82F6' }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prevData => [
        { ...prevData[0], value: Math.max(100, Math.min(150, prevData[0].value + Math.floor((Math.random() - 0.5) * 10))) },
        { ...prevData[1], value: Math.max(0, Math.min(20, prevData[1].value + Math.floor((Math.random() - 0.5) * 4))) },
        { ...prevData[2], value: Math.max(0, Math.min(10, prevData[2].value + Math.floor((Math.random() - 0.5) * 2))) },
        { ...prevData[3], value: Math.max(15, Math.min(40, prevData[3].value + Math.floor((Math.random() - 0.5) * 6))) }
      ]);
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const currentData = payload[0].payload;
      const total = data.reduce((sum, item) => sum + item.value, 0);
      const percentage = ((currentData.value / total) * 100).toFixed(1);
      
      return (
        <motion.div 
          className="bg-slate-800/90 backdrop-blur-lg p-3 rounded-lg border border-slate-700/50"
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
        >
          <p className="text-slate-300">{`Status: ${currentData.name}`}</p>
          <p style={{ color: currentData.color }}>{`Count: ${currentData.value}`}</p>
          <p className="text-slate-400">{`${percentage}%`}</p>
        </motion.div>
      );
    }
    return null;
  };

  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
    if (percent < 0.05) return null; // Don't show labels for slices smaller than 5%
    
    const RADIAN = Math.PI / 180;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);

    return (
      <text 
        x={x} 
        y={y} 
        fill="white" 
        textAnchor={x > cx ? 'start' : 'end'} 
        dominantBaseline="central"
        fontSize={12}
        fontWeight="bold"
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomLabel}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            animationBegin={0}
            animationDuration={800}
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            formatter={(value, entry: any) => (
              <span style={{ color: entry.color }}>{value}</span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PodChart;
