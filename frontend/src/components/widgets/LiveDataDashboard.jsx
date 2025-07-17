/**
 * Live Data Dashboard Widget
 *
 * @author Topgyal Gurung
 * @created 2025-06-12
 * @description Real-time data streaming dashboard with animated visualizations.
 *              Features live metrics cards, interactive play/pause controls,
 *              connection status monitoring, and smooth chart animations.
 *              Simulates realistic streaming data with configurable update intervals.
 */
import {
  Activity,
  Clock,
  DollarSign,
  Pause,
  Play,
  TrendingUp,
  Users,
  Wifi,
  WifiOff,
} from 'lucide-react';
import PropTypes from 'prop-types';

import React, { useCallback, useEffect, useRef, useState } from 'react';
import Plot from 'react-plotly.js';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Switch } from '@/components/ui/switch';

import { cn } from '@/lib/utils';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7c7c', '#8dd1e1', '#d084d0'];

const LiveDataDashboard = ({
  id,
  title = 'Live Data Dashboard',
  className,
  updateInterval = 1000,
  maxDataPoints = 50,
  metrics = ['sales', 'users', 'revenue', 'performance'],
}) => {
  const [isStreaming, setIsStreaming] = useState(true);
  const [data, setData] = useState([]);
  const [liveMetrics, setLiveMetrics] = useState({});
  const [connectionStatus, setConnectionStatus] = useState('connected');
  const intervalRef = useRef(null);
  const animationRef = useRef(null);

  // Generate realistic streaming data
  const generateDataPoint = useCallback(() => {
    const timestamp = new Date();
    const baseValues = {
      sales: 150,
      users: 320,
      revenue: 2500,
      performance: 85,
    };

    const newPoint = {
      timestamp,
      sales: baseValues.sales + Math.sin(Date.now() / 10000) * 30 + (Math.random() - 0.5) * 20,
      users: baseValues.users + Math.cos(Date.now() / 8000) * 50 + (Math.random() - 0.5) * 40,
      revenue:
        baseValues.revenue + Math.sin(Date.now() / 12000) * 400 + (Math.random() - 0.5) * 200,
      performance: Math.max(
        0,
        Math.min(
          100,
          baseValues.performance + Math.sin(Date.now() / 15000) * 10 + (Math.random() - 0.5) * 15
        )
      ),
    };

    return newPoint;
  }, []);

  // Calculate live metrics
  const calculateMetrics = useCallback((dataPoints) => {
    if (dataPoints.length === 0) return {};

    const latest = dataPoints[dataPoints.length - 1];
    const previous = dataPoints.length > 1 ? dataPoints[dataPoints.length - 2] : latest;

    return {
      sales: {
        current: Math.round(latest.sales * 10) / 10,
        change: (((latest.sales - previous.sales) / previous.sales) * 100).toFixed(1),
        trend: latest.sales > previous.sales ? 'up' : 'down',
      },
      users: {
        current: Math.round(latest.users),
        change: (((latest.users - previous.users) / previous.users) * 100).toFixed(1),
        trend: latest.users > previous.users ? 'up' : 'down',
      },
      revenue: {
        current: `$${latest.revenue.toFixed(0)}`,
        change: (((latest.revenue - previous.revenue) / previous.revenue) * 100).toFixed(1),
        trend: latest.revenue > previous.revenue ? 'up' : 'down',
      },
      performance: {
        current: `${latest.performance.toFixed(1)}%`,
        change: (latest.performance - previous.performance).toFixed(1),
        trend: latest.performance > previous.performance ? 'up' : 'down',
      },
    };
  }, []);

  // Start/stop streaming
  const toggleStreaming = useCallback(() => {
    setIsStreaming((prev) => !prev);
  }, []);

  // Update data with animation
  const updateData = useCallback(() => {
    if (!isStreaming) return;

    setData((prevData) => {
      const newPoint = generateDataPoint();
      const newData = [...prevData, newPoint];

      // Keep only the latest maxDataPoints
      if (newData.length > maxDataPoints) {
        newData.shift();
      }

      // Update metrics
      setLiveMetrics(calculateMetrics(newData));

      return newData;
    });

    // Simulate occasional connection issues for realism
    if (Math.random() < 0.02) {
      setConnectionStatus('reconnecting');
      setTimeout(() => setConnectionStatus('connected'), 2000);
    }
  }, [isStreaming, generateDataPoint, calculateMetrics, maxDataPoints]);

  // Setup streaming interval
  useEffect(() => {
    if (isStreaming) {
      intervalRef.current = setInterval(updateData, updateInterval);
    } else {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    }

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isStreaming, updateData, updateInterval]);

  // Initialize with some data
  useEffect(() => {
    const initialData = [];
    for (let i = 0; i < 20; i++) {
      initialData.push(generateDataPoint());
    }
    setData(initialData);
    setLiveMetrics(calculateMetrics(initialData));
  }, [generateDataPoint, calculateMetrics]);

  // Prepare chart data
  const chartData = metrics.map((metric, index) => ({
    x: data.map((d) => d.timestamp),
    y: data.map((d) => d[metric]),
    type: 'scatter',
    mode: 'lines+markers',
    name: metric.charAt(0).toUpperCase() + metric.slice(1),
    line: {
      color: COLORS[index % COLORS.length],
      width: 3,
      shape: 'spline',
    },
    marker: {
      size: 6,
      color: COLORS[index % COLORS.length],
      symbol: 'circle',
    },
    connectgaps: false,
    hovertemplate:
      `<b>%{fullData.name}</b><br>` + `Value: %{y:.2f}<br>` + `Time: %{x}<br>` + `<extra></extra>`,
  }));

  const metricCards = [
    { key: 'sales', label: 'Sales Rate', icon: TrendingUp, unit: '/min', color: 'blue' },
    { key: 'users', label: 'Active Users', icon: Users, unit: '', color: 'green' },
    { key: 'revenue', label: 'Revenue', icon: DollarSign, unit: '', color: 'purple' },
    { key: 'performance', label: 'Performance', icon: Activity, unit: '', color: 'orange' },
  ];

  return (
    <Card id={id} className={cn('w-full', className)}>
      <CardHeader className="pb-4">
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Activity className={cn('h-5 w-5', isStreaming && 'animate-pulse text-green-500')} />
            {title}
          </CardTitle>

          <div className="flex items-center gap-4">
            {/* Connection Status */}
            <div className="flex items-center gap-2">
              {connectionStatus === 'connected' ? (
                <Wifi className="h-4 w-4 text-green-500" />
              ) : (
                <WifiOff className="h-4 w-4 text-orange-500" />
              )}
              <Badge variant={connectionStatus === 'connected' ? 'success' : 'warning'}>
                {connectionStatus}
              </Badge>
            </div>

            {/* Streaming Toggle */}
            <div className="flex items-center gap-2">
              <Switch checked={isStreaming} onCheckedChange={toggleStreaming} />
              <Button variant="outline" size="sm" onClick={toggleStreaming}>
                {isStreaming ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              </Button>
            </div>
          </div>
        </div>

        {/* Live indicator */}
        {isStreaming && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="h-2 w-2 bg-red-500 rounded-full animate-pulse" />
            <span>LIVE</span>
            <Clock className="h-3 w-3" />
            <span>Updated every {updateInterval}ms</span>
          </div>
        )}
      </CardHeader>

      <CardContent className="space-y-6">
        {/* Real-time Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {metricCards.map((card) => {
            const metric = liveMetrics[card.key];
            if (!metric) return null;

            return (
              <Card key={card.key} className="p-4 relative overflow-hidden">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        'p-2 rounded-lg',
                        card.color === 'blue' && 'bg-blue-100 text-blue-600',
                        card.color === 'green' && 'bg-green-100 text-green-600',
                        card.color === 'purple' && 'bg-purple-100 text-purple-600',
                        card.color === 'orange' && 'bg-orange-100 text-orange-600'
                      )}
                    >
                      <card.icon className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold">
                        {metric.current}
                        {card.unit}
                      </p>
                      <p className="text-xs text-muted-foreground">{card.label}</p>
                    </div>
                  </div>

                  <div className="text-right">
                    <div
                      className={cn(
                        'flex items-center gap-1 text-sm font-medium',
                        metric.trend === 'up' ? 'text-green-600' : 'text-red-600'
                      )}
                    >
                      <TrendingUp
                        className={cn('h-3 w-3', metric.trend === 'down' && 'rotate-180')}
                      />
                      {Math.abs(parseFloat(metric.change))}%
                    </div>
                  </div>
                </div>

                {/* Animated background indicator */}
                {isStreaming && (
                  <div
                    className={cn(
                      'absolute inset-0 opacity-5',
                      card.color === 'blue' && 'bg-blue-500',
                      card.color === 'green' && 'bg-green-500',
                      card.color === 'purple' && 'bg-purple-500',
                      card.color === 'orange' && 'bg-orange-500',
                      'animate-pulse'
                    )}
                  />
                )}
              </Card>
            );
          })}
        </div>

        {/* Real-time Chart */}
        <Card className="p-4">
          <div className="h-96">
            <Plot
              data={chartData}
              layout={{
                title: {
                  text: 'Real-time Data Stream',
                  font: { size: 16, family: 'Inter, system-ui, sans-serif' },
                },
                xaxis: {
                  title: 'Time',
                  type: 'date',
                  tickformat: '%H:%M:%S',
                  showgrid: true,
                  gridcolor: '#f0f0f0',
                  range:
                    data.length > 0
                      ? [new Date(Date.now() - maxDataPoints * updateInterval), new Date()]
                      : undefined,
                },
                yaxis: {
                  title: 'Values',
                  showgrid: true,
                  gridcolor: '#f0f0f0',
                },
                margin: { t: 50, r: 50, l: 60, b: 50 },
                paper_bgcolor: 'transparent',
                plot_bgcolor: 'transparent',
                showlegend: true,
                legend: {
                  orientation: 'h',
                  x: 0,
                  y: -0.2,
                },
                hovermode: 'x unified',
                transition: {
                  duration: updateInterval * 0.8,
                  easing: 'cubic-in-out',
                },
              }}
              config={{
                responsive: true,
                displayModeBar: false,
                doubleClick: false,
                scrollZoom: false,
              }}
              style={{ width: '100%', height: '100%' }}
              useResizeHandler={true}
              animate={isStreaming}
            />
          </div>
        </Card>

        {/* Data Summary */}
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            Data Points: {data.length}/{maxDataPoints}
          </span>
          <span>Update Rate: {updateInterval}ms</span>
          <span>Status: {isStreaming ? 'Streaming' : 'Paused'}</span>
        </div>
      </CardContent>
    </Card>
  );
};

LiveDataDashboard.propTypes = {
  id: PropTypes.string,
  title: PropTypes.string,
  className: PropTypes.string,
  updateInterval: PropTypes.number,
  maxDataPoints: PropTypes.number,
  metrics: PropTypes.arrayOf(PropTypes.string),
};

LiveDataDashboard.defaultProps = {
  id: undefined,
  title: 'Live Data Dashboard',
  className: '',
  updateInterval: 1000,
  maxDataPoints: 50,
  metrics: ['sales', 'users', 'revenue', 'performance'],
};

export default LiveDataDashboard;
