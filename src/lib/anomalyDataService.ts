import { parse } from 'papaparse';

export interface AnomalyDataPoint {
  timestamp: string;
  podName: string;
  cpuUsage: number;
  memoryUsage: number;
  networkTraffic: number;
  podStatus: string;
  podReason: string;
  podRestarts: number;
  errorMessage: string;
  latestEventReason: string;
  podEventType: string;
  podEventMessage: string;
  nodeName: string;
  isAnomaly: boolean;
}

/**
 * Fetches and parses anomaly data from the CSV file
 */
export async function fetchAnomalyData(): Promise<AnomalyDataPoint[]> {
  try {
    // In a real application, this would be an API call to your backend
    // For now, we'll fetch the CSV file directly from the public directory
    const response = await fetch('/data/dataSynthetic.csv');
    if (!response.ok) {
      throw new Error(`Failed to fetch data: ${response.status} ${response.statusText}`);
    }
    
    const csvText = await response.text();
    const { data } = parse(csvText, { header: true, skipEmptyLines: true });
    
    // Transform the CSV data into our expected format
    return data.map((row: any) => {
      // Determine if this is an anomaly based on various indicators
      const isAnomaly = (
        row['Pod Status'] !== 'Running' ||
        row['Pod Reason'] !== '' ||
        row['Pod Restarts'] > 2 ||
        row['Error Message'] !== '' ||
        row['Latest Event Reason'] === 'OOMKilled' ||
        row['Latest Event Reason'] === 'BackOff' ||
        row['Pod Event Type'] === 'Warning'
      );
      
      return {
        timestamp: row['Timestamp'],
        podName: row['Pod Name'],
        cpuUsage: parseFloat(row['CPU Usage (%)']) || 0,
        memoryUsage: parseFloat(row['Memory Usage (%)']) || 0,
        networkTraffic: parseFloat(row['Network Traffic (B/s)']) || 0,
        podStatus: row['Pod Status'],
        podReason: row['Pod Reason'],
        podRestarts: parseInt(row['Pod Restarts']) || 0,
        errorMessage: row['Error Message'],
        latestEventReason: row['Latest Event Reason'],
        podEventType: row['Pod Event Type'],
        podEventMessage: row['Pod Event Message'],
        nodeName: row['Node Name'],
        isAnomaly
      };
    });
  } catch (error) {
    console.error('Error fetching anomaly data:', error);
    return [];
  }
}

/**
 * Fetches mock anomaly data for development/testing
 */
export function getMockAnomalyData(): AnomalyDataPoint[] {
  // Generate timestamps for the last 24 hours, every 5 minutes
  const now = new Date();
  const data: AnomalyDataPoint[] = [];
  
  // Sample pod names
  const pods = [
    { name: 'frontend-app-1', node: 'worker-1' },
    { name: 'backend-api-1', node: 'worker-2' },
    { name: 'database-0', node: 'worker-3' },
    { name: 'cache-redis-0', node: 'worker-1' },
    { name: 'monitoring-agent-1', node: 'worker-2' },
    { name: 'logging-fluentd-2', node: 'worker-3' }
  ];
  
  // Generate data for each pod
  pods.forEach(pod => {
    // Generate data points for the last 24 hours (288 points at 5-minute intervals)
    for (let i = 0; i < 288; i++) {
      const timestamp = new Date(now.getTime() - (i * 5 * 60 * 1000));
      
      // Base values with some randomness
      let cpuUsage = 30 + Math.random() * 40; // 30-70%
      let memoryUsage = 40 + Math.random() * 30; // 40-70%
      let networkTraffic = 500 + Math.random() * 1000; // 500-1500 B/s
      let podStatus = 'Running';
      let podReason = '';
      let podRestarts = 0;
      let errorMessage = '';
      let latestEventReason = '';
      let podEventType = 'Normal';
      let podEventMessage = '';
      
      // Introduce anomalies randomly (about 5% of the time)
      const isAnomalyPoint = Math.random() < 0.05;
      
      if (isAnomalyPoint) {
        // Choose a random anomaly type
        const anomalyType = Math.floor(Math.random() * 4);
        
        switch (anomalyType) {
          case 0: // CPU spike
            cpuUsage = 85 + Math.random() * 15; // 85-100%
            break;
          case 1: // Memory leak
            memoryUsage = 85 + Math.random() * 15; // 85-100%
            latestEventReason = 'OOMKilled';
            podEventType = 'Warning';
            podEventMessage = 'Container was OOM killed';
            break;
          case 2: // Pod restart
            podRestarts = 3 + Math.floor(Math.random() * 5); // 3-7 restarts
            latestEventReason = 'BackOff';
            podEventType = 'Warning';
            podEventMessage = 'Back-off restarting failed container';
            break;
          case 3: // Pod failure
            podStatus = 'Failed';
            podReason = 'Error';
            errorMessage = 'Container exited with non-zero status code';
            podEventType = 'Warning';
            break;
        }
      }
      
      // Determine if this is an anomaly based on the indicators
      const isAnomaly = (
        podStatus !== 'Running' ||
        podReason !== '' ||
        podRestarts > 2 ||
        errorMessage !== '' ||
        latestEventReason === 'OOMKilled' ||
        latestEventReason === 'BackOff' ||
        podEventType === 'Warning'
      );
      
      data.push({
        timestamp: timestamp.toISOString(),
        podName: pod.name,
        cpuUsage,
        memoryUsage,
        networkTraffic,
        podStatus,
        podReason,
        podRestarts,
        errorMessage,
        latestEventReason,
        podEventType,
        podEventMessage,
        nodeName: pod.node,
        isAnomaly
      });
    }
  });
  
  // Sort by timestamp (newest first)
  return data.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}