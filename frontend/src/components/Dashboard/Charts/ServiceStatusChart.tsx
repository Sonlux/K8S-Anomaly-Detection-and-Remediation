
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const ServiceStatusChart = () => {
  const [data, setData] = useState([
    { name: 'API Gateway', healthy: 8, unhealthy: 0, color: '#10B981' },
    { name: 'Auth Service', healthy: 3, unhealthy: 1, color: '#F59E0B' },
    { name: 'Database', healthy: 5, unhealthy: 0, color: '#10B981' },
    { name: 'Cache', healthy: 2, unhealthy: 0, color: '#10B981' },
    { name: 'Worker', healthy: 4, unhealthy: 1, color: '#F59E0B' },
    { name: 'Frontend', healthy: 6, unhealthy: 0, color: '#10B981' }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setData(prevData => 
        prevData.map(service => ({
          ...service,
          healthy: Math.max(1, service.healthy + Math.floor((Math.random() - 0.5) * 2)),
          unhealthy: Math.max(0, Math.min(2, service.unhealthy + Math.floor((Math.random() - 0.5) * 2))),
          color: service.unhealthy > 0 ? '#F59E0B' : '#10B981'
        }))
      );
    }, 5000);

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
          <p className="text-slate-300">{`Service: ${label}`}</p>
          <p className="text-green-400">{`Healthy: ${payload[0]?.value || 0}`}</p>
          <p className="text-red-400">{`Unhealthy: ${payload[1]?.value || 0}`}</p>
        </motion.div>
      );
    }
    return null;
  };

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis 
            dataKey="name" 
            stroke="#9CA3AF"
            fontSize={12}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis stroke="#9CA3AF" fontSize={12} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="healthy" stackId="a" fill="#10B981" />
          <Bar dataKey="unhealthy" stackId="a" fill="#EF4444" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default ServiceStatusChart;
