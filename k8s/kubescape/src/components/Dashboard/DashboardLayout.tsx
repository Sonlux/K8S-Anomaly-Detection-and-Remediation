
import React from 'react';
import { motion } from 'framer-motion';
import Header from './Header';
import MetricsOverview from './MetricsOverview';
import ResourceQuotas from './ResourceQuotas';
import ChartsGrid from './ChartsGrid';
import NamespaceOverview from './NamespaceOverview';
import AnomaliesPanel from './AnomaliesPanel';
import RemediationCenter from './RemediationCenter';
import ChatButton from '../Chat/ChatButton';

const DashboardLayout = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      <Header />
      
      <motion.main 
        className="container mx-auto px-4 py-6 space-y-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        {/* Main Metrics Overview */}
        <MetricsOverview />

        {/* Resource Quotas */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
            <motion.div 
              className="w-2 h-2 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span>Resource Quotas & Usage</span>
          </h2>
          <ResourceQuotas />
        </motion.section>

        {/* Charts Grid */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
            <motion.div 
              className="w-2 h-2 bg-gradient-to-r from-purple-400 to-pink-500 rounded-full"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 1 }}
            />
            <span>Performance Analytics</span>
          </h2>
          <ChartsGrid />
        </motion.section>

        {/* Namespace Overview */}
        <motion.section
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.6 }}
        >
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center space-x-2">
            <motion.div 
              className="w-2 h-2 bg-gradient-to-r from-green-400 to-emerald-500 rounded-full"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 2, repeat: Infinity, delay: 2 }}
            />
            <span>Namespace Management</span>
          </h2>
          <NamespaceOverview />
        </motion.section>
        
        {/* Anomalies and Remediation */}
        <motion.div 
          className="grid grid-cols-1 xl:grid-cols-2 gap-6"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.8 }}
        >
          <motion.div
            whileHover={{ scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <AnomaliesPanel />
          </motion.div>
          <motion.div
            whileHover={{ scale: 1.01 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <RemediationCenter />
          </motion.div>
        </motion.div>
      </motion.main>

      {/* Floating Chat Button */}
      <ChatButton />
    </div>
  );
};

export default DashboardLayout;
