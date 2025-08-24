
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AlertTriangle, CheckCircle, XCircle, Clock } from 'lucide-react';

interface Anomaly {
  id: string;
  type: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  timestamp: string;
  resolved: boolean;
}

const AnomaliesPanel = () => {
  const [anomalies, setAnomalies] = useState<Anomaly[]>([
    {
      id: '1',
      type: 'critical',
      title: 'High Memory Usage Detected',
      description: 'Node worker-03 memory usage exceeded 90% threshold',
      timestamp: '2 minutes ago',
      resolved: false
    },
    {
      id: '2',
      type: 'warning',
      title: 'Pod Restart Loop',
      description: 'Pod frontend-app-xyz has restarted 5 times in 10 minutes',
      timestamp: '5 minutes ago',
      resolved: false
    },
    {
      id: '3',
      type: 'info',
      title: 'Scaling Event Completed',
      description: 'Successfully scaled deployment api-service from 3 to 5 replicas',
      timestamp: '8 minutes ago',
      resolved: true
    }
  ]);

  const getIcon = (type: string, resolved: boolean) => {
    if (resolved) return <CheckCircle className="w-5 h-5 text-green-400" />;
    
    switch (type) {
      case 'critical':
        return <XCircle className="w-5 h-5 text-red-400" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5 text-yellow-400" />;
      default:
        return <Clock className="w-5 h-5 text-blue-400" />;
    }
  };

  const getColorClasses = (type: string, resolved: boolean) => {
    if (resolved) return 'border-green-500/30 bg-green-500/10';
    
    switch (type) {
      case 'critical':
        return 'border-red-500/30 bg-red-500/10';
      case 'warning':
        return 'border-yellow-500/30 bg-yellow-500/10';
      default:
        return 'border-blue-500/30 bg-blue-500/10';
    }
  };

  const resolveAnomaly = (id: string) => {
    setAnomalies(prev => 
      prev.map(anomaly => 
        anomaly.id === id ? { ...anomaly, resolved: true } : anomaly
      )
    );
  };

  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate new anomalies
      if (Math.random() > 0.8) {
        const newAnomaly: Anomaly = {
          id: Date.now().toString(),
          type: Math.random() > 0.7 ? 'critical' : Math.random() > 0.5 ? 'warning' : 'info',
          title: 'New Anomaly Detected',
          description: 'System detected unusual behavior in cluster metrics',
          timestamp: 'Just now',
          resolved: false
        };
        
        setAnomalies(prev => [newAnomaly, ...prev.slice(0, 4)]);
      }
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <AlertTriangle className="w-5 h-5 text-red-400" />
          <span>Anomaly Detection</span>
          <motion.div 
            className="ml-auto px-2 py-1 bg-red-500/20 rounded-full text-red-400 text-sm"
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
          >
            {anomalies.filter(a => !a.resolved).length} Active
          </motion.div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          <AnimatePresence>
            {anomalies.map((anomaly) => (
              <motion.div
                key={anomaly.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={`p-4 rounded-lg border ${getColorClasses(anomaly.type, anomaly.resolved)} transition-all duration-300`}
              >
                <div className="flex items-start space-x-3">
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.1 }}
                  >
                    {getIcon(anomaly.type, anomaly.resolved)}
                  </motion.div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-white font-medium">{anomaly.title}</h4>
                    <p className="text-slate-400 text-sm mt-1">{anomaly.description}</p>
                    <p className="text-slate-500 text-xs mt-2">{anomaly.timestamp}</p>
                  </div>
                  {!anomaly.resolved && (
                    <motion.div
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => resolveAnomaly(anomaly.id)}
                        className="text-xs bg-transparent border-slate-600 text-slate-300 hover:bg-slate-700"
                      >
                        Resolve
                      </Button>
                    </motion.div>
                  )}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
};

export default AnomaliesPanel;
