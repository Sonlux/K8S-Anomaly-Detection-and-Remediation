// Mock data for the dashboard

// Cluster Overview Data
export const mockClusterData = {
  name: 'Production Cluster',
  status: 'healthy',
  version: '1.26.5',
  nodes: 5,
  pods: 48,
  deployments: 12,
  services: 15,
  cpu: {
    used: 12.5,
    total: 32,
    percentage: 39,
  },
  memory: {
    used: 45.2,
    total: 64,
    percentage: 71,
  },
  storage: {
    used: 256,
    total: 512,
    percentage: 50,
  },
};

// Metrics Data
export const mockMetricsData = [
  {
    id: 'cpu-usage',
    name: 'CPU Usage',
    value: 39,
    unit: '%',
    change: 5.2,
    status: 'normal',
    history: [
      { time: '00:00', value: 32 },
      { time: '01:00', value: 28 },
      { time: '02:00', value: 30 },
      { time: '03:00', value: 35 },
      { time: '04:00', value: 37 },
      { time: '05:00', value: 39 },
    ],
  },
  {
    id: 'memory-usage',
    name: 'Memory Usage',
    value: 71,
    unit: '%',
    change: 3.8,
    status: 'warning',
    history: [
      { time: '00:00', value: 65 },
      { time: '01:00', value: 62 },
      { time: '02:00', value: 68 },
      { time: '03:00', value: 70 },
      { time: '04:00', value: 72 },
      { time: '05:00', value: 71 },
    ],
  },
  {
    id: 'network-in',
    name: 'Network In',
    value: 42.5,
    unit: 'MB/s',
    change: -2.1,
    status: 'normal',
    history: [
      { time: '00:00', value: 45 },
      { time: '01:00', value: 48 },
      { time: '02:00', value: 47 },
      { time: '03:00', value: 44 },
      { time: '04:00', value: 43 },
      { time: '05:00', value: 42.5 },
    ],
  },
  {
    id: 'network-out',
    name: 'Network Out',
    value: 38.2,
    unit: 'MB/s',
    change: 1.5,
    status: 'normal',
    history: [
      { time: '00:00', value: 35 },
      { time: '01:00', value: 36 },
      { time: '02:00', value: 38 },
      { time: '03:00', value: 37 },
      { time: '04:00', value: 37.5 },
      { time: '05:00', value: 38.2 },
    ],
  },
  {
    id: 'pod-restarts',
    name: 'Pod Restarts',
    value: 3,
    unit: '',
    change: 200,
    status: 'warning',
    history: [
      { time: '00:00', value: 0 },
      { time: '01:00', value: 0 },
      { time: '02:00', value: 1 },
      { time: '03:00', value: 1 },
      { time: '04:00', value: 2 },
      { time: '05:00', value: 3 },
    ],
  },
  {
    id: 'disk-io',
    name: 'Disk I/O',
    value: 15.8,
    unit: 'MB/s',
    change: -5.4,
    status: 'normal',
    history: [
      { time: '00:00', value: 18 },
      { time: '01:00', value: 17.5 },
      { time: '02:00', value: 16.8 },
      { time: '03:00', value: 16.2 },
      { time: '04:00', value: 16 },
      { time: '05:00', value: 15.8 },
    ],
  },
];

// Anomaly Detection Data
export const mockAnomalies = [
  {
    id: 'anomaly-1',
    title: 'High Memory Usage in Database Pod',
    description: 'The database pod is consuming more memory than usual, currently at 92% of its limit. This might lead to OOM kills if not addressed.',
    severity: 'high',
    timestamp: '10 minutes ago',
    resource: {
      type: 'Pod',
      name: 'postgres-db-0',
      namespace: 'database',
    },
    status: 'active',
    remediation: 'Consider increasing the memory limit for this pod or investigate potential memory leaks in the application.',
  },
  {
    id: 'anomaly-2',
    title: 'Frequent Pod Restarts',
    description: 'The frontend pod has restarted 5 times in the last hour. This indicates potential stability issues with the application.',
    severity: 'medium',
    timestamp: '35 minutes ago',
    resource: {
      type: 'Pod',
      name: 'frontend-app-7d8f9b7c5-2xvz4',
      namespace: 'web',
    },
    status: 'acknowledged',
    remediation: 'Check the pod logs for error messages and investigate the cause of the crashes.',
  },
  {
    id: 'anomaly-3',
    title: 'Node Disk Space Running Low',
    description: 'Worker node 3 is running low on disk space (85% used). This could affect the ability to schedule new pods on this node.',
    severity: 'medium',
    timestamp: '2 hours ago',
    resource: {
      type: 'Node',
      name: 'worker-node-3',
      namespace: '',
    },
    status: 'active',
    remediation: 'Clean up unused images and volumes, or consider adding more storage to the node.',
  },
  {
    id: 'anomaly-4',
    title: 'Network Latency Spike',
    description: 'Detected unusual network latency between services in the application namespace. Average request time increased by 300%.',
    severity: 'low',
    timestamp: '3 hours ago',
    resource: {
      type: 'Service',
      name: 'api-gateway',
      namespace: 'application',
    },
    status: 'resolved',
    remediation: 'The issue was resolved automatically when the network congestion cleared.',
  },
];

// Recent Activity Data
export const mockActivities = [
  {
    id: 'activity-1',
    type: 'scaling',
    message: 'Horizontal Pod Autoscaler increased replicas',
    timestamp: '5 minutes ago',
    resource: {
      type: 'Deployment',
      name: 'frontend-app',
      namespace: 'web',
    },
  },
  {
    id: 'activity-2',
    type: 'alert',
    message: 'High CPU usage alert triggered',
    timestamp: '15 minutes ago',
    resource: {
      type: 'Pod',
      name: 'api-server-5d7f8c6b95-xvz42',
      namespace: 'backend',
    },
  },
  {
    id: 'activity-3',
    type: 'deployment',
    message: 'New version deployed successfully',
    timestamp: '45 minutes ago',
    user: 'jenkins-ci',
    resource: {
      type: 'Deployment',
      name: 'payment-service',
      namespace: 'financial',
    },
  },
  {
    id: 'activity-4',
    type: 'creation',
    message: 'New ConfigMap created',
    timestamp: '1 hour ago',
    user: 'admin@example.com',
    resource: {
      type: 'ConfigMap',
      name: 'app-settings',
      namespace: 'web',
    },
  },
  {
    id: 'activity-5',
    type: 'maintenance',
    message: 'Node cordoned for maintenance',
    timestamp: '2 hours ago',
    user: 'system-admin',
    resource: {
      type: 'Node',
      name: 'worker-node-2',
      namespace: '',
    },
  },
];