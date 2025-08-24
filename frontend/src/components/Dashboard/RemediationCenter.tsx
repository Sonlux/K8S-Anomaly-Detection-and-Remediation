
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Wrench, Play, RotateCcw, Scale, Trash2 } from 'lucide-react';
import { toast } from 'sonner';

interface RemediationAction {
  id: string;
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high';
  icon: React.ReactNode;
  action: () => void;
}

const RemediationCenter = () => {
  const [isExecuting, setIsExecuting] = useState<string | null>(null);

  const executeAction = async (action: RemediationAction) => {
    setIsExecuting(action.id);
    
    // Simulate action execution
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    action.action();
    setIsExecuting(null);
    
    toast.success(`${action.title} completed successfully!`, {
      description: action.description
    });
  };

  const actions: RemediationAction[] = [
    {
      id: 'restart-pods',
      title: 'Restart Failed Pods',
      description: 'Restart all pods in CrashLoopBackOff state',
      severity: 'high',
      icon: <RotateCcw className="w-4 h-4" />,
      action: () => console.log('Restarting failed pods...')
    },
    {
      id: 'scale-deployment',
      title: 'Auto-Scale Deployment',
      description: 'Scale high-load deployments automatically',
      severity: 'medium',
      icon: <Scale className="w-4 h-4" />,
      action: () => console.log('Scaling deployment...')
    },
    {
      id: 'cleanup-resources',
      title: 'Cleanup Unused Resources',
      description: 'Remove orphaned ConfigMaps and Secrets',
      severity: 'low',
      icon: <Trash2 className="w-4 h-4" />,
      action: () => console.log('Cleaning up resources...')
    },
    {
      id: 'health-check',
      title: 'Run Health Checks',
      description: 'Execute comprehensive cluster health validation',
      severity: 'medium',
      icon: <Play className="w-4 h-4" />,
      action: () => console.log('Running health checks...')
    }
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'medium':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      default:
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
    }
  };

  return (
    <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50">
      <CardHeader>
        <CardTitle className="text-white flex items-center space-x-2">
          <Wrench className="w-5 h-5 text-blue-400" />
          <span>Remediation Center</span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {actions.map((action, index) => (
            <motion.div
              key={action.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="p-4 rounded-lg bg-slate-700/30 border border-slate-600/30 hover:border-slate-500/50 transition-all duration-300"
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3">
                  <motion.div
                    className="p-2 bg-blue-500/20 rounded-lg"
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                  >
                    {action.icon}
                  </motion.div>
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-1">
                      <h4 className="text-white font-medium">{action.title}</h4>
                      <Badge className={`text-xs ${getSeverityColor(action.severity)}`}>
                        {action.severity}
                      </Badge>
                    </div>
                    <p className="text-slate-400 text-sm">{action.description}</p>
                  </div>
                </div>
                
                <motion.div
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <Button
                    size="sm"
                    onClick={() => executeAction(action)}
                    disabled={isExecuting === action.id}
                    className="bg-blue-600 hover:bg-blue-700 text-white"
                  >
                    {isExecuting === action.id ? (
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-4 h-4 border-2 border-white border-t-transparent rounded-full"
                      />
                    ) : (
                      'Execute'
                    )}
                  </Button>
                </motion.div>
              </div>
            </motion.div>
          ))}
        </div>
        
        <motion.div 
          className="mt-6 p-4 bg-gradient-to-r from-blue-500/10 to-purple-500/10 rounded-lg border border-blue-500/20"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
        >
          <h5 className="text-white font-medium mb-2">Quick Actions</h5>
          <div className="flex space-x-2">
            <Button size="sm" variant="outline" className="text-xs">
              Emergency Stop
            </Button>
            <Button size="sm" variant="outline" className="text-xs">
              Rollback
            </Button>
            <Button size="sm" variant="outline" className="text-xs">
              Backup
            </Button>
          </div>
        </motion.div>
      </CardContent>
    </Card>
  );
};

export default RemediationCenter;
