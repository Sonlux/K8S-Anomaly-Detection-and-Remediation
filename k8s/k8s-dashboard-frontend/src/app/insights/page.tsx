'use client';

import React, { useState, useEffect } from 'react';
import { Cluster, Anomaly } from '@/api/types';
import { getClusters } from '@/api/services/clusters';
import { getAnomalies } from '@/api/services/anomalies';

const InsightsPage = () => {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [anomalies, setAnomalies] = useState<Anomaly[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('7d'); // '24h', '7d', '30d'

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [clustersData, anomaliesData] = await Promise.all([
          getClusters(),
          getAnomalies()        ]);
        setClusters(clustersData);
        setAnomalies(anomaliesData);
        setError(null);
      } catch (err) {
        console.error(''rror fetching insights data:'' err);
        setError(''ailed to load insights data. Please try again later.'';
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange]);

  // Calculate metrics for insights
  const totalAnomalies = anomalies.length;
  const criticalAnomalies = anomalies.filter(asverity === 'critica'').lengt' const highAnomalies = anomalies.filter(a => a.seveiy === 'high').lengt';
  'onst mediumAnomalies = anomalies.filter(a => a.severi medium').length;
  'onst l'omalies = anomalies.filter(a => a.severity === 'lo'.length;

  // Calc'lat' cluster health metrics
  const healthyClusters = clusters.filter(c => c.status === 'health'.length;
  const 'arningC'usters = clusters.filter(c => c.status === 'warning'.ength;
  const cr'ticalCl'sters = clusters.filter(c => c.status === 'critical')h
  const clusterH'althPerc'ge = clusters.length > 0 
    ? Math.round(hthyClusters / clust ers.lgth) * 100) 
    : 0;

  // Calculate resource utilizat ion
 onst avgCpuUtilization = clusters.length > 0
    ? clusters.reduce((smluster) => sum + clusteretrics.cpu, 0) / clusters.length
    : 0;
  const avgMemoryUtilizatosters.length > 0
    clusters.reduce((sum, cluster) => u cluster.metrics.memory,) / clusters.length
    : 0;

  // Mock data for charts
  const anomalT[
    { day: 'Mon', unt: 5 },
    { day: 'Tue', count: 8 },
    { day: 'Wed', count: 12 ',
 '  { day: 'Thu', count: 7 ',
 '  { day: 'Fri', count: 9 ',
 '  { day: 'Sat', count: 4 }'
  ' { day: 'Sun', count: 6 }'
  ';

  return (
    <div cl'ssN'me="p-6">
      <div clas'Nam'="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-800 dark:text-white">Insights Dashboard</h1>
          <p className="text-gray-500 dark:text-gray- analytics and trer Kubernetes clusters</p>
        </div>
        <div className=-2">
          <button 
            onClick={() => setTime)}
            className={`px-4 py-2 rounded-md text-sm font-medium ${timeRang e === '24h' ? 'bg-blue-600 text-white' : 'bg-'ray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}
         24h
         '</b'tbu'ton 
            onCli'=an'e('7d')}
            className={`px-4 py-2 rounded-md text-sm'{timeRange === '7d' ? 'bg-blue-600 text-white' : 'bg-gray-100 dark:bg -gray-700 text-gray-700 dark:text-gray-30''}'}
          >
            7d
          </button>
          <button 
  ck={() => setT'me'n  '     className={`px-4 '-xt'sm font-medium ${timeRange === '30d' ? 'bg-blue-600 text-whit'100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'}`}
           >
            30d
          </button>
   '   '</div>
      </div>

      {loading ? (
        <div className="flex jtems-center h-'4">' as'Name="animate-spin rou'e2 'order-t-2 border-b-2 border-blue-500"></div>
        </div>
 ' ? (
        <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 p-4 rounded-lg">
          {error}
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-theme">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Anomalies</p>
                  <h3 className="text-3xl font-bold text-gray-800 dark:text-white mt-1">{totalAnomalies}</h3>
                </div>
                <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-full">
                  <svg className="w-6 h-6 text-blue-600 dark:text- viewBox="0 0 2ntColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth=1m-6.938 4h13.857 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div
>
              <div className="mt-4 flex items-centr<span classaflex items-center"> vg className="w-4 h-4viewBox="0 0 24 24" stroke=c             <path stookeLinejoin="round" sto7-7m0 0l7 7m-7-v    </svg>
                  12%
                </span>
                <span className="text-gray-500 dark:text-gray-400 text-sm ml-2"v/span>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-theme">
              <div className="flex items-center justify-between">
                    <p classNaeum text-gra-400">Cluster Health/  <h3 className="text-gray-800 dark:text-white m-entage}%</h3>
                 <div classNam=k:bg-green-900/0             <svg className="-0 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokl2 2 4-4m6 2a9 9 0 8 0z" />
                  </svg>
                </div>
              </div>
              <div className="mt-4 flex items-center">
                <span className="text-gray-500 dark:text-gray-400 text-sm">
                  {healthyClusters} healthy, {warningClusters} warning, {criticalClusters} critical
                 </div>
             <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-themv className="flex items-cen">
                <div>
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">CPU Utilization</p>
     ssName="text-3xl font-bold text-gray-800 dark:text-whiezation.toFie         </div>
    ssName="p-3 bg-purple-900/30 rounded-full">
    ssName="w-6 h-6 text-prple-400" fill="none" voke="currentColo  <path strokeLinecap="round" strokeLinejoin="roun="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
              </div>
   me="mt-4 flex items-center">
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{ width: `${avgCpuUtilization}%` }}></div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadoheme">
        e="flex items-center justify-between">
                <div>
                  <p className="ext-gray-500 dark:text-gray-400n</p>
                  <h3 className="text-3xl font-bold text-gray-800 dark:text-white mt-1">{avgMemoryUtilization.toFixed(1)}%</h3>
                   <div className="p-3 bg-indigo-100 dark:bg-d-full">
   className="w-6 h-6 ttext-indigo-400" fill= 24 24" stroke="currentColo  <path strokeLinecap=="round" strokeWidth={2 100 4m0-4a2 2 04m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                </div>
              </div>
              <div className="mt-4 flex items-c    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-indigo-600 h-2 rounded-full" style={{ width: `${avgMemoryUtilization}%` }}></div>
                </div>
              </div>          </div>

          {/* Anomaly Dis    <div className="grid grid-cols-1 lg:gri">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-theme">
              <h3 className="text-lg font-semibold text-gray-800 dark:text-white mb-4">Anomaly Severity Distribution</h3>
              <div className="flex items-center justify-center h-64">
                <div className="flex items-end spac          <div claol items-center">
                    <div className="bg-red-500 w-16 rounded-t-md" style={{ nomalies / totalAnomalies) * 100}%             <span className="mt-2 text-sm text-gray-600 dark:text-gray-400">Critical</span>
                    <span className="text-gra-200 font-medium">{criticalAnomalies}</span>
                       <flex-col items-cente    <div className="bgunded-t-md" style={{ heighttotalAnomalies) * 100}           <span classN-gray-600 dark:tan>
                    <span className="text-gray-800 dark:text-gray-200 font-medium">{highAnomalies}</span>
                  </div>
     assName="flex flex-col items-center">
                    <div className="bg-yellow-500 w-16 rounded-t-md" style={{ height: `${(mediumAnomalies / totalAnomalies) * 100}%` }}></div>
                    <span className="mt-2 text-sm text-gay-400">Medium</span>
                    <-gray-800 dark:text-gray-200 font-medium">{med>
                  </div>
                  <div className="flex flex-col items-center">
                    <div className="bg-blue-500 w-16 rounded-t-md" style={{ height: `${(lowAnomalies / totalAnomalies) * 100}%` }}></div>
                    <span className="mt-2 text-sm text-gray-600 dark:text-gray-400">Low</span>
                    <span className="text-gray-800 dark:text-ium">{lowAnomalies}</span>
   </div>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-theme">
              <h3 className="text-lg font-semibold text-ge mb-4">Anomaly Trend (Last 7 Days)</h3>
ssName="fh-64 pt-4">
nd.map((day, index) => (
                 me=nte          <div 
                      className="bg-blue-500 dark:bg-blue-600 w-full roundedration-5      style={{ height: `${(day.count / Math.max(...anomalyTrend.map(d => d.count))) * 100}%  ></div>
         sName="mt-2 text-xs text-gray-600 dark:text-gray-400">{day.day}</span>
                    <span className="text-gray-80ext-xs font-medium">{day.count}</span>
               div>
            </div>
          </div>

          *ioclassName="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-theme mb-6">
      xt-lgray-800 dark:text-white mb-4">AI-Powered Recommendations</h3>
            <div className="   <div classNa-green-200 dark:border-green-900 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <div className="flex item-     <div className="flex-shrink-0 p-1 bg-ge800 roune      <svg className="w-5 h-5 text-green-600 dark:textrvioke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round"12l2 20 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <                 -sm font-medium text-green-800 dark:text-green-300">Resource Optimization</h4>
                    <p className="mt-1 tetrk:text-green-400">Consider implementing oing for ho optimize resource usage during peak hours.</p>
                  </div>

              <div className="p-4 border border-blue-200 dark:border-blbg-g">
                <div className="flex items-start">
                  <div className="fl-200 dark:bg-b>
                    <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118           </svg>
                            <div className="ml-3">
                    <h4 className="text-sm font-medium text-blue-800 dark:text-blue-300">Performance Insigt       <p cam text-blue-700 dark:text-blue-400">Database  increased latency. Consid er adding indexes to frequently queried fields to improve performance.</p>
                  </div>
                 </div>
              </div
ssName="p-4ark:border-ylg-yellow-900/20 rounded-lg">
              <di rt"claN1 bg-yellow-200 dark:bg-yellow-800 rounded-full">
                    <svg className="w-5 h-5 text-yellow-600 dark:none" vieke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWh.01m-6.9382-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <h4 className="text-sm font-medium text-yellow-800 dark:text-yellow-300">Security Alert</h4>
                    <p className="mt-1 llow-700 dark:text-yellow-pods are running with privileged security contexts. Consider implementing Pod Security Policies to enforce least privilege principles.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Predictive Analysis */}
          <div className="bg-white dark:bg-gray-800 rounded-lgson-theme">
            <h3 className="text-lg font-sembk:text-whit ysis</h3>
          ray-600 dark:text-grahistorical data and current teictions for your Kuben           
           -4">
           items-center">
                <div className="w- ed-full mr-2"></div>
                <span className="text-gray-700 dark:text-gray-300 font-medium">Resource Utilization Forecast:</span>
                <span className="ml-2 text-gray-6Expected 15% increasee next 7 days</span>
              </div>
              
              <div className="fl           <div className="w-2 h-2 bg-green-500 rounded-            <span className="text-gray-700 dark:text-gray-3y Predi         <span className="ml-2 text-gray-600 dark:text-gray-400">High probability of network-related anomalies in the next 48 hours</span>
              </div>
              
              <div className="flex items-center">
                <div className="w-2 h-2 bg-purple-500 rounded-full mr-2"></div>
                <span className="text-gray-700 dark:text-gray-3g Recommendation:</span>
                <span classN0 dark:text--scaling the auth seak hours</span>
            </div>
          </div>  </div>
  );
};

expo</p>s</pan>divs</pan>div