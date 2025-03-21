import React, { useCallback, useEffect, useRef, useState } from 'react';
import { FiInfo, FiLock, FiMaximize2, FiMinimize2, FiUnlock } from 'react-icons/fi';
import { useInView } from 'react-intersection-observer';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  useEdgesState,
  useNodesState,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';

import { cn } from '@/lib/utils';

// Custom node styles
const nodeStyles = {
  padding: '10px',
  borderRadius: '8px',
  border: '1px solid #ddd',
  fontSize: '12px',
  width: 180,
  textAlign: 'center',
};

const DAGVisualizationWidget = ({ id, data: rawData, content, error }) => {
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [selectedNode, setSelectedNode] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isLocked, setIsLocked] = useState(false);
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const plotContainerRef = useRef(null);
  const [showMiniMap, setShowMiniMap] = useState(false);

  const { ref: inViewRef, inView } = useInView({
    threshold: 0.1,
    triggerOnce: true,
  });

  // Set refs for both intersection observer and plot container
  const setRefs = useCallback(
    (node) => {
      plotContainerRef.current = node;
      inViewRef(node);
    },
    [inViewRef]
  );

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-gray-200 text-gray-700',
      running: 'bg-blue-500 text-white',
      completed: 'bg-teal-500 text-white',
      failed: 'bg-red-500 text-white',
      retry: 'bg-orange-400 text-white',
      skipped: 'bg-purple-400 text-white',
      not_executed: 'bg-gray-300 text-gray-700',
    };
    return colors[status] || colors.not_executed;
  };

  const getStatusBgColor = (status) => {
    const colors = {
      pending: '#E8E8E8',
      running: '#72B0DD',
      completed: '#72B7B7',
      failed: '#B76E79',
      retry: '#FFB347',
      skipped: '#D7BDE2',
      not_executed: '#C8C8C8',
    };
    return colors[status] || colors.not_executed;
  };

  // Transform Plotly data to ReactFlow format
  useEffect(() => {
    if (rawData?.data) {
      const plotlyNodes = rawData.data.find((trace) => trace.type === 'scatter');
      const nodeData = plotlyNodes?.customdata || [];
      const positions = plotlyNodes?.node?.positions || [];

      // Create nodes
      const flowNodes = nodeData.map((data, index) => ({
        id: data.name,
        position: positions[index] || { x: index * 200, y: index * 100 },
        data: {
          label: data.name,
          status: data.status,
          executionTime: data.execution_time,
          attempts: data.attempts,
          error: data.error,
          dependencies: data.dependencies,
        },
        style: {
          ...nodeStyles,
          background: getStatusBgColor(data.status),
          color: data.status === 'pending' ? '#666' : '#fff',
        },
      }));

      // Create edges from dependencies
      const flowEdges = [];
      nodeData.forEach((node) => {
        if (node.dependencies) {
          node.dependencies.forEach((dep) => {
            flowEdges.push({
              id: `${dep}-${node.name}`,
              source: dep,
              target: node.name,
              type: 'smoothstep',
              animated: node.status === 'running',
              style: { stroke: '#4a5568', strokeWidth: 2 },
              markerEnd: {
                type: MarkerType.ArrowClosed,
                width: 20,
                height: 20,
                color: '#4a5568',
              },
            });
          });
        }
      });

      setNodes(flowNodes);
      setEdges(flowEdges);
      setIsLoading(false);
    }
  }, [rawData]);

  const handleNodeClick = useCallback((_, node) => {
    setSelectedNode(node.data);
  }, []);

  const toggleFullscreen = useCallback(() => {
    setIsFullscreen((prev) => !prev);
  }, []);

  const toggleLock = useCallback(() => {
    setIsLocked((prev) => !prev);
  }, []);

  if (error) {
    return (
      <Card className="dag-visualizer-error-card">
        <CardHeader>
          <CardTitle className="dag-visualizer-error-title">Error Loading DAG</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="dag-visualizer-error-text">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn('dag-visualizer-container', isFullscreen && 'dag-visualizer-fullscreen')}
      ref={setRefs}
    >
      {/* Header Controls */}
      <div className="dag-visualizer-controls">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => setShowMiniMap((prev) => !prev)}>
                <FiInfo className="dag-visualizer-tooltip-trigger" />
              </Button>
            </TooltipTrigger>
            <TooltipContent className="dag-visualizer-tooltip-content">
              Toggle MiniMap
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={toggleLock}>
                {isLocked ? (
                  <FiLock className="dag-visualizer-tooltip-trigger" />
                ) : (
                  <FiUnlock className="dag-visualizer-tooltip-trigger" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent className="dag-visualizer-tooltip-content">
              {isLocked ? 'Unlock Nodes' : 'Lock Nodes'}
            </TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={toggleFullscreen}>
                {isFullscreen ? (
                  <FiMinimize2 className="dag-visualizer-tooltip-trigger" />
                ) : (
                  <FiMaximize2 className="dag-visualizer-tooltip-trigger" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent className="dag-visualizer-tooltip-content">
              {isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* Main Content */}
      <CardContent
        className={cn(
          'dag-visualizer-content',
          isFullscreen ? 'dag-visualizer-content-fullscreen' : 'dag-visualizer-content-default'
        )}
      >
        {isLoading ? (
          <div className="dag-visualizer-loading">
            <div className="dag-visualizer-spinner"></div>
          </div>
        ) : (
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={isLocked ? undefined : onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={handleNodeClick}
            fitView
            attributionPosition="bottom-right"
          >
            {showMiniMap && (
              <MiniMap
                nodeStrokeColor={(n) => getStatusBgColor(n.data?.status)}
                nodeColor={(n) => getStatusBgColor(n.data?.status)}
                nodeBorderRadius={8}
              />
            )}
            <Controls />
            <Background color="#aaa" gap={16} />
          </ReactFlow>
        )}
      </CardContent>

      {/* Node Details Panel */}
      {selectedNode && (
        <Card
          className={cn(
            'dag-visualizer-node-panel',
            selectedNode ? 'dag-visualizer-node-panel-visible' : 'dag-visualizer-node-panel-hidden'
          )}
        >
          <CardHeader className="dag-visualizer-node-header">
            <div className="flex justify-between items-center">
              <CardTitle className="dag-visualizer-node-title">{selectedNode.label}</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setSelectedNode(null)}>
                <span className="dag-visualizer-node-close">Close</span>×
              </Button>
            </div>
          </CardHeader>
          <CardContent className="dag-visualizer-node-details">
            <div className="dag-visualizer-node-status">
              <span className="dag-visualizer-node-status-label">Status:</span>
              <Badge variant="secondary" className={getStatusColor(selectedNode.status)}>
                {selectedNode.status}
              </Badge>
            </div>
            <div>
              <span className="dag-visualizer-node-status-label">Execution Time:</span>
              <span className="ml-2 text-sm">{selectedNode.executionTime}</span>
            </div>
            <div>
              <span className="dag-visualizer-node-status-label">Attempts:</span>
              <span className="ml-2 text-sm">{selectedNode.attempts}</span>
            </div>
            {selectedNode.error && (
              <div>
                <span className="dag-visualizer-node-error-label">Error:</span>
                <p className="dag-visualizer-node-error-text">{selectedNode.error}</p>
              </div>
            )}
            {selectedNode.dependencies?.length > 0 && (
              <div>
                <span className="dag-visualizer-node-status-label">Dependencies:</span>
                <div className="dag-visualizer-node-dependencies">
                  {selectedNode.dependencies.map((dep) => (
                    <Badge key={dep} variant="outline" className="text-xs">
                      {dep}
                    </Badge>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </Card>
  );
};

export default DAGVisualizationWidget;
