import 'reactflow/dist/style.css';

import { FiInfo, FiLock, FiMaximize2, FiMinimize2, FiUnlock } from 'react-icons/fi';
import React, { useCallback, useEffect, useRef, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MarkerType,
  MiniMap,
  useEdgesState,
  useNodesState,
} from 'reactflow';

import { Tooltip } from '../common/Tooltip';
import { useInView } from 'react-intersection-observer';

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
      const plotlyNodes = rawData.data.find(trace => trace.type === 'scatter');
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
          background: getStatusColor(data.status),
          color: data.status === 'pending' ? '#666' : '#fff',
        },
      }));

      // Create edges from dependencies
      const flowEdges = [];
      nodeData.forEach(node => {
        if (node.dependencies) {
          node.dependencies.forEach(dep => {
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
    setIsFullscreen(prev => !prev);
  }, []);

  const toggleLock = useCallback(() => {
    setIsLocked(prev => !prev);
  }, []);

  if (error) {
    return (
      <div className="p-4 bg-red-50 text-red-700 rounded-lg">
        <h3 className="font-semibold">Error Loading DAG</h3>
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div
      className={`relative rounded-lg bg-white transition-all duration-300 ${
        isFullscreen ? 'fixed inset-0 z-50 m-4' : ''
      }`}
      ref={setRefs}
    >
      {/* Header Controls */}
      <div className="absolute top-2 right-2 z-10 flex items-center gap-2">
        <Tooltip content="Toggle MiniMap">
          <button
            onClick={() => setShowMiniMap(prev => !prev)}
            className="p-2 rounded-full hover:bg-gray-100"
          >
            <FiInfo className="w-5 h-5" />
          </button>
        </Tooltip>
        <Tooltip content={isLocked ? "Unlock Nodes" : "Lock Nodes"}>
          <button
            onClick={toggleLock}
            className="p-2 rounded-full hover:bg-gray-100"
          >
            {isLocked ? (
              <FiLock className="w-5 h-5" />
            ) : (
              <FiUnlock className="w-5 h-5" />
            )}
          </button>
        </Tooltip>
        <Tooltip content={isFullscreen ? "Exit Fullscreen" : "Enter Fullscreen"}>
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-full hover:bg-gray-100"
          >
            {isFullscreen ? (
              <FiMinimize2 className="w-5 h-5" />
            ) : (
              <FiMaximize2 className="w-5 h-5" />
            )}
          </button>
        </Tooltip>
      </div>

      {/* Main Content */}
      <div className={`w-full ${isFullscreen ? 'h-full' : 'h-[600px]'}`}>
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
                nodeStrokeColor={(n) => getStatusColor(n.data?.status)}
                nodeColor={(n) => getStatusColor(n.data?.status)}
                nodeBorderRadius={8}
              />
            )}
            <Controls />
            <Background color="#aaa" gap={16} />
          </ReactFlow>
        )}
      </div>

      {/* Node Details Panel */}
      {selectedNode && (
        <div
          className="absolute bottom-4 left-4 right-4 bg-white rounded-lg p-4 max-w-md mx-auto shadow-lg transition-all duration-300 opacity-100 translate-y-0"
          style={{
            transform: selectedNode ? 'translateY(0)' : 'translateY(20px)',
            opacity: selectedNode ? 1 : 0,
          }}
        >
          <div className="flex justify-between items-start">
            <h3 className="text-lg font-semibold">{selectedNode.label}</h3>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          <div className="mt-2 space-y-2">
            <div className="flex items-center gap-2">
              <span className="text-sm font-medium text-gray-500">Status:</span>
              <span
                className="px-2 py-1 rounded-full text-xs"
                style={{
                  backgroundColor: getStatusColor(selectedNode.status),
                  color: selectedNode.status === 'pending' ? '#666' : '#fff',
                }}
              >
                {selectedNode.status}
              </span>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Execution Time:</span>
              <span className="ml-2 text-sm">{selectedNode.executionTime}</span>
            </div>
            <div>
              <span className="text-sm font-medium text-gray-500">Attempts:</span>
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
                <span className="text-sm font-medium text-gray-500">Dependencies:</span>
                <div className="mt-1 flex flex-wrap gap-1">
                  {selectedNode.dependencies.map((dep) => (
                    <span
                      key={dep}
                      className="px-2 py-1 bg-gray-100 rounded-full text-xs text-gray-700"
                    >
                      {dep}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default DAGVisualizationWidget; 