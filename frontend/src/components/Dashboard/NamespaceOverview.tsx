
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Activity, AlertCircle, CheckCircle } from 'lucide-react';

interface Namespace {
  name: string;
  pods: number;
  services: number;
  status: 'healthy' | 'warning' | 'error';
  cpuUsage: number;
  memoryUsage: number;
}

const NamespaceOverview = () => {
  const [namespaces, setNamespaces] = useState<Namespace[]>([
    { name: 'default', pods: 12, services: 4, status: 'healthy', cpuUsage: 45, memoryUsage: 60 },
    { name: 'kube-system', pods: 8, services: 6, status: 'healthy', cpuUsage: 30, memoryUsage: 40 },
    { name: 'monitoring', pods: 5, services: 3, status: 'warning', cpuUsage: 75, memoryUsage: 80 },
    { name: 'production', pods: 25, services: 8, status: 'healthy', cpuUsage: 55, memoryUsage: 65 },
    { name: 'staging', pods: 15, services: 5, status: 'healthy', cpuUsage: 35, memoryUsage: 45 },
    { name: 'development', pods: 10, services: 4, status: 'error', cpuUsage: 20, memoryUsage: 25 }
  ]);

  useEffect(() => {
    const interval = setInterval(() => {
      setNamespaces(prev => 
        prev.map(ns => {
          const newCpuUsage = Math.max(10, Math.min(90, ns.cpuUsage + (Math.random() - 0.5) * 10));
          const newMemoryUsage = Math.max(15, Math.min(95, ns.memoryUsage + (Math.random() - 0.5) * 8));
          
          let status: 'healthy' | 'warning' | 'error' = 'healthy';
          if (newCpuUsage > 80 || newMemoryUsage > 85) status = 'warning';
          if (newCpuUsage > 90 || newMemoryUsage > 95) status = 'error';
          
          return {
            ...ns,
            cpuUsage: newCpuUsage,
            memoryUsage: newMemoryUsage,
            status,
            pods: Math.max(1, ns.pods + Math.floor((Math.random() - 0.5) * 2))
          };
        })
      );
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="w-4 h-4 text-green-400" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-400" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-400" />;
      default: return <Activity className="w-4 h-4 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500/20 text-green-400 border-green-500/50';
      case 'warning': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50';
      case 'error': return 'bg-red-500/20 text-red-400 border-red-500/50';
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/50';
    }
  };

  return (
    <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <div className="w-3 h-3 bg-cyan-400 rounded-full"></div>
          <span>Namespace Overview</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <AnimatePresence>
            {namespaces.map((namespace, index) => (
              <motion.div
                key={namespace.name}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3, delay: index * 0.1 }}
                whileHover={{ scale: 1.02, y: -2 }}
                className="p-4 bg-slate-700/30 rounded-lg border border-slate-600/50 hover:border-slate-500/50 transition-all duration-300"
              >
                <div className="flex items-center justify-between mb-3">
                  <h4 className="text-white font-medium">{namespace.name}</h4>
                  <Badge className={getStatusColor(namespace.status)}>
                    {getStatusIcon(namespace.status)}
                    <span className="ml-1 capitalize">{namespace.status}</span>
                  </Badge>
                </div>
                
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Pods:</span>
                    <span className="text-white">{namespace.pods}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Services:</span>
                    <span className="text-white">{namespace.services}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">CPU:</span>
                    <span className={`${namespace.cpuUsage > 70 ? 'text-yellow-400' : 'text-green-400'}`}>
                      {namespace.cpuUsage.toFixed(1)}%
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-400">Memory:</span>
                    <span className={`${namespace.memoryUsage > 75 ? 'text-yellow-400' : 'text-blue-400'}`}>
                      {namespace.memoryUsage.toFixed(1)}%
                    </span>
                  </div>
                </div>
                
                <div className="mt-3 flex space-x-2">
                  <div className="flex-1 bg-slate-600/50 rounded-full h-2 overflow-hidden">
                    <motion.div 
                      className={`h-full ${namespace.cpuUsage > 70 ? 'bg-yellow-400' : 'bg-green-400'}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${namespace.cpuUsage}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                  <div className="flex-1 bg-slate-600/50 rounded-full h-2 overflow-hidden">
                    <motion.div 
                      className={`h-full ${namespace.memoryUsage > 75 ? 'bg-yellow-400' : 'bg-blue-400'}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${namespace.memoryUsage}%` }}
                      transition={{ duration: 0.5, delay: 0.1 }}
                    />
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
};

export default NamespaceOverview;
