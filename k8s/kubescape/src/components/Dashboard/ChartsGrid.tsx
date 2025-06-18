
import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import CPUChart from './Charts/CPUChart';
import MemoryChart from './Charts/MemoryChart';
import NetworkChart from './Charts/NetworkChart';
import PodChart from './Charts/PodChart';
import ServiceStatusChart from './Charts/ServiceStatusChart';
import NodeHealthChart from './Charts/NodeHealthChart';

const ChartsGrid = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 }
  };

  return (
    <motion.div 
      className="space-y-6"
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      {/* First row - Main metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <motion.div 
                  className="w-3 h-3 bg-green-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
                <span>CPU Usage Trends</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CPUChart />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <motion.div 
                  className="w-3 h-3 bg-blue-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.5 }}
                />
                <span>Memory Utilization</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <MemoryChart />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Second row - Network and Pods */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <motion.div 
                  className="w-3 h-3 bg-purple-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 1 }}
                />
                <span>Network Traffic</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <NetworkChart />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <motion.div 
                  className="w-3 h-3 bg-yellow-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 1.5 }}
                />
                <span>Pod Distribution</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <PodChart />
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Third row - Services and Node Health */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div variants={itemVariants}>
          <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <motion.div 
                  className="w-3 h-3 bg-cyan-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 2 }}
                />
                <span>Service Health Status</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ServiceStatusChart />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div variants={itemVariants}>
          <Card className="bg-slate-800/50 backdrop-blur-lg border-slate-700/50 hover:border-slate-600/50 transition-all duration-300">
            <CardHeader>
              <CardTitle className="text-white flex items-center space-x-2">
                <motion.div 
                  className="w-3 h-3 bg-pink-400 rounded-full"
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 2.5 }}
                />
                <span>Node Health Matrix</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <NodeHealthChart />
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </motion.div>
  );
};

export default ChartsGrid;
