import React, { useEffect, useState } from 'react';
import ReactFlow, { MarkerType, useEdgesState, useNodesState } from 'reactflow';
import 'reactflow/dist/style.css';

// Simple card components without shadcn
const Card = ({ className = '', children, ...props }) => (
  <div
    className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}
    {...props}
  >
    {children}
  </div>
);

const CardContent = ({ className = '', children, ...props }) => (
  <div className={`p-6 ${className}`} {...props}>
    {children}
  </div>
);

// Tailwind dark mode status classes
const getStatusClasses = (status) => {
  switch (status) {
    case 'pending':
      return 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900';
    case 'running':
      return 'border-blue-600 bg-blue-50 dark:border-blue-400 dark:bg-blue-900';
    case 'completed':
      return 'border-green-600 bg-green-50 dark:border-green-400 dark:bg-green-900';
    case 'failed':
      return 'border-red-600 bg-red-50 dark:border-red-400 dark:bg-red-900';
    case 'retry':
      return 'border-amber-600 bg-amber-50 dark:border-amber-400 dark:bg-amber-900';
    case 'skipped':
      return 'border-gray-500 bg-gray-100 dark:border-gray-400 dark:bg-gray-800';
    case 'not_executed':
    default:
      return 'border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900';
  }
};

const DAGVisualizationWidget = ({ id, data: rawData, error, className = '' }) => {
  const [nodes, setNodes] = useNodesState([]);
  const [edges, setEdges] = useEdgesState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (rawData?.data) {
      const plotlyNodes = rawData.data.find((trace) => trace.type === 'scatter');
      const nodeData = plotlyNodes?.customdata || [];
      const positions = plotlyNodes?.node?.positions || [];

      const flowNodes = nodeData.map((data, index) => ({
        id: data.name,
        position: positions[index] || { x: index * 150, y: index * 60 },
        data: {
          label: data.name,
          status: data.status,
        },
        className: `p-2 px-3 text-foreground text-[13px] font-medium min-w-[120px] rounded-md transition-all duration-150 border ${getStatusClasses(data.status)}`,
      }));

      const flowEdges = nodeData.flatMap((node) =>
        (node.dependencies || []).map((dep) => ({
          id: `${dep}-${node.name}`,
          source: dep,
          target: node.name,
          type: 'smoothstep',
          animated: node.status === 'running',
          style: {
            stroke: 'var(--tw-prose-invert-borders, #64748b)',
            strokeWidth: 1,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 12,
            height: 12,
            color: 'var(--tw-prose-invert-borders, #64748b)',
          },
        }))
      );

      setNodes(flowNodes);
      setEdges(flowEdges);
      setIsLoading(false);
    }
  }, [rawData]);

  if (error) {
    return (
      <Card id={id} className={className}>
        <CardContent>
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 dark:border-red-700 dark:bg-red-950">
            <h4 className="text-sm font-medium text-red-800 mb-1 dark:text-red-200">Error</h4>
            <p className="text-sm text-red-600 dark:text-red-300">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card id={id} className={className}>
        <CardContent>
          <div className="h-4 w-48 bg-gray-100 rounded animate-pulse mb-4 dark:bg-gray-800" />
          <div className="h-[200px] w-full bg-gray-100 rounded animate-pulse dark:bg-gray-800" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card id={id} className={className}>
      <div className="h-[300px] overflow-hidden">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          panOnDrag={false}
          zoomOnScroll={false}
          zoomOnPinch={false}
          zoomOnDoubleClick={false}
          nodesDraggable={false}
          nodesConnectable={false}
          elementsSelectable={false}
          className="bg-background"
        />
      </div>
    </Card>
  );
};

export default DAGVisualizationWidget;
