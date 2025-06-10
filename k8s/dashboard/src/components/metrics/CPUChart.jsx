import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';
import { formatPercentage } from '../../utils/formatters';

const CPUChart = ({ metrics }) => {
  const chartRef = useRef();
  
  useEffect(() => {
    if (!metrics || !chartRef.current) return;
    
    // Clear previous chart
    d3.select(chartRef.current).selectAll('*').remove();
    
    const margin = { top: 20, right: 30, bottom: 40, left: 50 };
    const width = chartRef.current.clientWidth - margin.left - margin.right;
    const height = 300 - margin.top - margin.bottom;
    
    const svg = d3.select(chartRef.current)
      .append('svg')
      .attr('width', width + margin.left + margin.right)
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);
    
    // Prepare data
    const data = metrics.map(pod => ({
      name: pod.name,
      cpu: parseFloat(pod.cpu || 0)
    }));
    
    // Sort data by CPU usage
    data.sort((a, b) => b.cpu - a.cpu);
    
    // X and Y scales
    const x = d3.scaleBand()
      .domain(data.map(d => d.name))
      .range([0, width])
      .padding(0.1);
    
    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.cpu) * 1.1])
      .nice()
      .range([height, 0]);
    
    // Add X axis
    svg.append('g')
      .attr('transform', `translate(0,${height})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('transform', 'translate(-10,0)rotate(-45)')
      .style('text-anchor', 'end');
    
    // Add Y axis
    svg.append('g')
      .call(d3.axisLeft(y).tickFormat(d => `${d}%`));
    
    // Add bars
    svg.selectAll('.bar')
      .data(data)
      .enter()
      .append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.name))
      .attr('y', d => y(d.cpu))
      .attr('width', x.bandwidth())
      .attr('height', d => height - y(d.cpu))
      .attr('fill', d => d.cpu > 80 ? '#ef4444' : d.cpu > 60 ? '#f59e0b' : '#10b981')
      .append('title')
      .text(d => `${d.name}: ${formatPercentage(d.cpu)}`);
    
    // Add title
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', 0 - margin.top / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .text('CPU Usage by Pod');
    
  }, [metrics]);
  
  return <div ref={chartRef} className="w-full h-[300px]"></div>;
};

export default CPUChart;