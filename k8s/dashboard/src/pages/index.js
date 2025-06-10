import React from 'react';
import DashboardLayout from '../components/layouts/DashboardLayout';
import MetricsPanel from '../components/metrics/MetricsPanel';
import ClusterTopology from '../components/topology/ClusterTopology';
import AnomalyPanel from '../components/anomalies/AnomalyPanel';
import InsightsPanel from '../components/insights/InsightsPanel';
import RemediationHistory from '../components/remediation/RemediationHistory';

export default function Dashboard() {
  return (
    <DashboardLayout>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <MetricsPanel />
        <ClusterTopology />
      </div>
      <div className="grid grid-cols-1 gap-4 mb-4">
        <AnomalyPanel />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <InsightsPanel />
        <RemediationHistory />
      </div>
    </DashboardLayout>
  );
}