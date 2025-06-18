
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Cpu, HardDrive, Zap, Database } from 'lucide-react';

interface QuotaCardProps {
  title: string;
  used: number;
  total: number;
  unit: string;
  icon: React.ReactNode;
  color: string;
  delay: number;
}

const QuotaCard = ({ title, used, total, unit, icon, color, delay }: QuotaCardProps) => {
  const percentage = (used / total) * 100;
  
  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.6, delay }}
      whileHover={{ scale: 1.02 }}
    >
      <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
        <CardHeader className="pb-2">
          <CardTitle className="text-white flex items-center space-x-2 text-sm">
            <motion.div 
              className={`p-2 rounded-lg ${color}`}
              whileHover={{ rotate: 10 }}
            >
              {icon}
            </motion.div>
            <span>{title}</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">
                {used.toFixed(1)} {unit} / {total} {unit}
              </span>
              <span className={`font-medium ${percentage > 80 ? 'text-red-400' : percentage > 60 ? 'text-yellow-400' : 'text-green-400'}`}>
                {percentage.toFixed(1)}%
              </span>
            </div>
            <Progress 
              value={percentage} 
              className="h-2"
              style={{
                '--progress-foreground': percentage > 80 ? '#EF4444' : percentage > 60 ? '#F59E0B' : '#10B981'
              } as React.CSSProperties}
            />
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
};

const ResourceQuotas = () => {
  const [quotas, setQuotas] = useState({
    cpu: { used: 45.5, total: 64 },
    memory: { used: 128.3, total: 256 },
    storage: { used: 1.2, total: 5 },
    pods: { used: 156, total: 250 }
  });

  useEffect(() => {
    const interval = setInterval(() => {
      setQuotas(prev => ({
        cpu: { 
          ...prev.cpu, 
          used: Math.max(20, Math.min(60, prev.cpu.used + (Math.random() - 0.5) * 5)) 
        },
        memory: { 
          ...prev.memory, 
          used: Math.max(80, Math.min(240, prev.memory.used + (Math.random() - 0.5) * 10)) 
        },
        storage: { 
          ...prev.storage, 
          used: Math.max(0.5, Math.min(4, prev.storage.used + (Math.random() - 0.5) * 0.2)) 
        },
        pods: { 
          ...prev.pods, 
          used: Math.max(100, Math.min(200, prev.pods.used + Math.floor((Math.random() - 0.5) * 10))) 
        }
      }));
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <QuotaCard
        title="CPU Cores"
        used={quotas.cpu.used}
        total={quotas.cpu.total}
        unit="cores"
        icon={<Cpu className="w-4 h-4 text-blue-400" />}
        color="bg-blue-500/20"
        delay={0}
      />
      <QuotaCard
        title="Memory"
        used={quotas.memory.used}
        total={quotas.memory.total}
        unit="GB"
        icon={<HardDrive className="w-4 h-4 text-green-400" />}
        color="bg-green-500/20"
        delay={0.1}
      />
      <QuotaCard
        title="Storage"
        used={quotas.storage.used}
        total={quotas.storage.total}
        unit="TB"
        icon={<Database className="w-4 h-4 text-purple-400" />}
        color="bg-purple-500/20"
        delay={0.2}
      />
      <QuotaCard
        title="Pod Limit"
        used={quotas.pods.used}
        total={quotas.pods.total}
        unit="pods"
        icon={<Zap className="w-4 h-4 text-yellow-400" />}
        color="bg-yellow-500/20"
        delay={0.3}
      />
    </div>
  );
};

export default ResourceQuotas;
