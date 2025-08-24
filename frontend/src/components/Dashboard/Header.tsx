
import React from 'react';
import { motion } from 'framer-motion';
import { Activity, Server, AlertTriangle } from 'lucide-react';

const Header = () => {
  return (
    <motion.header 
      className="bg-slate-800/50 backdrop-blur-lg border-b border-slate-700/50"
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
    >
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <motion.div
              className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <Server className="w-6 h-6 text-white" />
            </motion.div>
            <div>
              <h1 className="text-2xl font-bold text-white">Kubernetes Dashboard</h1>
              <p className="text-slate-400">Production Cluster Monitoring</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <motion.div 
              className="flex items-center space-x-2 px-3 py-2 bg-green-500/20 rounded-lg border border-green-500/30"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3 }}
            >
              <Activity className="w-4 h-4 text-green-400" />
              <span className="text-green-400 font-medium">Healthy</span>
            </motion.div>
            
            <motion.div 
              className="text-slate-400"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              Last updated: {new Date().toLocaleTimeString()}
            </motion.div>
          </div>
        </div>
      </div>
    </motion.header>
  );
};

export default Header;
