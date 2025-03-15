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
      <Card className="border-red-200 bg-red-50">
        <CardHeader>
          <CardTitle className="text-red-700">Error Loading DAG</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-red-600">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      className={cn(
        'relative transition-all duration-300',
        isFullscreen ? 'fixed inset-0 z-50 m-4' : ''
      )}
      ref={setRefs}
    >
      {/* Header Controls */}
      <div className="absolute top-2 right-2 z-10 flex items-center gap-2">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={() => setShowMiniMap((prev) => !prev)}>
                <FiInfo className="h-4 w-4" />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Toggle MiniMap</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={toggleLock}>
                {isLocked ? <FiLock className="h-4 w-4" /> : <FiUnlock className="h-4 w-4" />}
              </Button>
            </TooltipTrigger>
            <TooltipContent>{isLocked ? 'Unlock Nodes' : 'Lock Nodes'}</TooltipContent>
          </Tooltip>

          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="ghost" size="icon" onClick={toggleFullscreen}>
                {isFullscreen ? (
                  <FiMinimize2 className="h-4 w-4" />
                ) : (
                  <FiMaximize2 className="h-4 w-4" />
                )}
              </Button>
            </TooltipTrigger>
            <TooltipContent>{isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}</TooltipContent>
          </Tooltip>
        </TooltipProvider>
      </div>

      {/* Main Content */}
      <CardContent className={cn('p-0', isFullscreen ? 'h-full' : 'h-[600px]')}>
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
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
            'absolute bottom-4 left-4 right-4 max-w-md mx-auto transition-all duration-300',
            selectedNode ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-5'
          )}
        >
          <CardHeader className="pb-2">
            <div className="flex justify-between items-center">
              <CardTitle className="text-lg">{selectedNode.label}</CardTitle>
              <Button variant="ghost" size="icon" onClick={() => setSelectedNode(null)}>
                <span className="sr-only">Close</span>×
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-muted-foreground">Status:</span>
              <Badge variant="secondary" className={getStatusColor(selectedNode.status)}>
                {selectedNode.status}
              </Badge>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">Execution Time:</span>
              <span className="ml-2 text-sm">{selectedNode.executionTime}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-muted-foreground">Attempts:</span>
              <span className="ml-2 text-sm">{selectedNode.attempts}</span>
            </div>
            {selectedNode.error && (
              <div>
                <span className="text-sm font-medium text-red-500">Error:</span>
                <p className="mt-1 text-sm text-red-600 bg-red-50 p-2 rounded">
                  {selectedNode.error}
                </p>
              </div>
            )}
            {selectedNode.dependencies?.length > 0 && (
              <div>
                <span className="text-sm font-medium text-muted-foreground">Dependencies:</span>
                <div className="mt-1 flex flex-wrap gap-1">
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
