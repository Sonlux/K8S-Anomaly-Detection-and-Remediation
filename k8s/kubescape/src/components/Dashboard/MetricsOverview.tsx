
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Cpu, HardDrive, Activity, Users } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string;
  change: string;
  icon: React.ReactNode;
  color: string;
  delay: number;
}

const MetricCard = ({ title, value, change, icon, color, delay }: MetricCardProps) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay }}
    whileHover={{ y: -5 }}
  >
    <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
      <CardContent className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-slate-400 text-sm font-medium">{title}</p>
            <motion.p 
              className="text-2xl font-bold text-white mt-1"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: delay + 0.2, type: "spring" }}
            >
              {value}
            </motion.p>
            <p className={`text-sm mt-1 ${color}`}>{change}</p>
          </div>
          <motion.div 
            className={`p-3 rounded-lg bg-gradient-to-r ${color === 'text-green-400' ? 'from-green-500/20 to-emerald-500/20' : 
              color === 'text-blue-400' ? 'from-blue-500/20 to-cyan-500/20' : 
              color === 'text-yellow-400' ? 'from-yellow-500/20 to-orange-500/20' : 
              'from-purple-500/20 to-pink-500/20'}`}
            whileHover={{ scale: 1.1, rotate: 5 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            {icon}
          </motion.div>
        </div>
      </CardContent>
    </Card>
  </motion.div>
);

const MetricsOverview = () => {
  const [metrics, setMetrics] = useState({
    cpu: { value: 65, change: 2.3 },
    memory: { value: 78, change: -1.2 },
    nodes: { value: 12, change: 0 },
    pods: { value: 156, change: 8 }
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        cpu: { 
          value: Math.max(20, Math.min(95, prev.cpu.value + (Math.random() - 0.5) * 10)),
          change: (Math.random() - 0.5) * 5
        },
        memory: { 
          value: Math.max(30, Math.min(90, prev.memory.value + (Math.random() - 0.5) * 8)),
          change: (Math.random() - 0.5) * 4
        },
        nodes: { 
          value: prev.nodes.value,
          change: 0
        },
        pods: { 
          value: Math.max(100, Math.min(200, prev.pods.value + Math.floor((Math.random() - 0.5) * 20))),
          change: Math.floor((Math.random() - 0.5) * 15)
        }
      }));
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const formatChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(1)}%`;
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <MetricCard
        title="CPU Usage"
        value={`${metrics.cpu.value.toFixed(1)}%`}
        change={formatChange(metrics.cpu.change)}
        icon={<Cpu className="w-6 h-6 text-green-400" />}
        color="text-green-400"
        delay={0}
      />
      <MetricCard
        title="Memory Usage"
        value={`${metrics.memory.value.toFixed(1)}%`}
        change={formatChange(metrics.memory.change)}
        icon={<HardDrive className="w-6 h-6 text-blue-400" />}
        color="text-blue-400"
        delay={0.1}
      />
      <MetricCard
        title="Active Nodes"
        value={metrics.nodes.value.toString()}
        change="All healthy"
        icon={<Activity className="w-6 h-6 text-yellow-400" />}
        color="text-yellow-400"
        delay={0.2}
      />
      <MetricCard
        title="Running Pods"
        value={metrics.pods.value.toString()}
        change={`${metrics.pods.change >= 0 ? '+' : ''}${metrics.pods.change}`}
        icon={<Users className="w-6 h-6 text-purple-400" />}
        color="text-purple-400"
        delay={0.3}
      />
    </div>
  );
};

export default MetricsOverview;
