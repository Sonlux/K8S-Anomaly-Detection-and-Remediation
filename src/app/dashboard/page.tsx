'use client';

import { useState, useEffect } from 'react';
import ClusterOverview from '@/components/dashboard/ClusterOverview';
import MetricsGrid from '@/components/dashboard/MetricsGrid';
import AnomalyDetection from '@/components/dashboard/AnomalyDetection';
import AnomalyVisualization from '@/components/dashboard/AnomalyVisualization';
import RecentActivity from '@/components/dashboard/RecentActivity';
import { mockClusterData, mockMetricsData, mockAnomalies, mockActivities } from '@/lib/mockData';
import { AnomalyDataPoint, getMockAnomalyData } from '@/lib/anomalyDataService';

export default function Dashboard() {
  const [clusterData, setClusterData] = useState(mockClusterData);
  const [metricsData, setMetricsData] = useState(mockMetricsData);
  const [anomalies, setAnomalies] = useState(mockAnomalies);
  const [activities, setActivities] = useState(mockActivities);
  const [anomalyData, setAnomalyData] = useState<AnomalyDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isAnomalyDataLoading, setIsAnomalyDataLoading] = useState(true);

  useEffect(() => {
    // Simulate data loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    // Load anomaly data
    loadAnomalyData();

    return () => clearTimeout(timer);
  }, []);
  
  const loadAnomalyData = async () => {
    setIsAnomalyDataLoading(true);
    try {
      // Fetch data from our API endpoint
      const response = await fetch('/api/anomaly-data');
      if (!response.ok) {
        throw new Error(`Failed to fetch anomaly data: ${response.status}`);
      }
      const data = await response.json();
      setAnomalyData(data);
    } catch (error) {
      console.error('Error loading anomaly data:', error);
    } finally {
      setIsAnomalyDataLoading(false);
    }
  };


  // In a real application, you would fetch data from your backend here
  // useEffect(() => {
  //   const fetchData = async () => {
  //     try {
  //       setIsLoading(true);
  //       const [clusterResponse, metricsResponse, anomaliesResponse, activitiesResponse, anomalyDataResponse] = await Promise.all([
  //         fetch('/api/clusters'),
  //         fetch('/api/metrics'),
  //         fetch('/api/anomalies'),
  //         fetch('/api/activities'),
  //         fetch('/api/anomaly-data')
  //       ]);
  //       
  //       const clusterData = await clusterResponse.json();
  //       const metricsData = await metricsResponse.json();
  //       const anomaliesData = await anomaliesResponse.json();
  //       const activitiesData = await activitiesResponse.json();
  //       const anomalyData = await anomalyDataResponse.json();
  //       
  //       setClusterData(clusterData);
  //       setMetricsData(metricsData);
  //       setAnomalies(anomaliesData);
  //       setActivities(activitiesData);
  //       setAnomalyData(anomalyData);
  //     } catch (error) {
  //       console.error('Error fetching dashboard data:', error);
  //     } finally {
  //       setIsLoading(false);
  //       setIsAnomalyDataLoading(false);
  //     }
  //   };
  //   
  //   fetchData();
  // }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold">Dashboard Overview</h1>
      
      <ClusterOverview data={clusterData} />
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <MetricsGrid data={metricsData} />
          <AnomalyVisualization 
            data={anomalyData} 
            isLoading={isAnomalyDataLoading} 
            onRefresh={loadAnomalyData} 
          />
          <AnomalyDetection anomalies={anomalies} />
        </div>
        
        <div className="space-y-6">
          <RecentActivity activities={activities} />
        </div>
      </div>
    </div>
  );
}