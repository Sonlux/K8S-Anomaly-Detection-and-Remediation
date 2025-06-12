import { NextResponse } from 'next/server';
import { fetchAnomalyData, getMockAnomalyData } from '@/lib/anomalyDataService';

/**
 * API route for fetching anomaly data
 * In a production environment, this would connect to your Kubernetes API
 * or metrics database to fetch real-time data
 */
export async function GET() {
  try {
    // Try to fetch data from the CSV file first
    try {
      const data = await fetchAnomalyData();
      return NextResponse.json(data);
    } catch (csvError) {
      console.warn('Failed to fetch CSV data, falling back to mock data:', csvError);
      // If CSV fetch fails, fall back to mock data
      const data = getMockAnomalyData();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error fetching anomaly data:', error);
    return NextResponse.json(
      { error: 'Failed to fetch anomaly data' },
      { status: 500 }
    );
  }
}