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

const nodeStyles = {
  padding: '8px 12px',
  fontSize: '13px',
  fontWeight: 500,
  width: 'auto',
  minWidth: '120px',
  borderWidth: '1px',
  borderStyle: 'solid',
  borderRadius: '6px',
  transition: 'all 150ms ease',
};

const statusStyles = {
  pending: {
    border: '1px solid #e5e5e5',
    background: '#fafafa',
  },
  running: {
    border: '1px solid #2563eb',
    background: '#eff6ff',
  },
  completed: {
    border: '1px solid #16a34a',
    background: '#f0fdf4',
  },
  failed: {
    border: '1px solid #dc2626',
    background: '#fef2f2',
  },
  retry: {
    border: '1px solid #d97706',
    background: '#fffbeb',
  },
  skipped: {
    border: '1px solid #6b7280',
    background: '#f9fafb',
  },
  not_executed: {
    border: '1px solid #e5e5e5',
    background: '#fafafa',
  },
};

const getStatusStyles = (status) => {
  const style = statusStyles[status] || statusStyles.not_executed;
  return {
    ...nodeStyles,
    ...style,
  };
};

const DAGVisualizationWidget = ({ data: rawData, error, className = '' }) => {
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
        style: getStatusStyles(data.status),
      }));

      const flowEdges = nodeData.flatMap((node) =>
        (node.dependencies || []).map((dep) => ({
          id: `${dep}-${node.name}`,
          source: dep,
          target: node.name,
          type: 'smoothstep',
          animated: node.status === 'running',
          style: {
            stroke: '#64748b',
            strokeWidth: 1,
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            width: 12,
            height: 12,
            color: '#64748b',
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
      <Card className={className}>
        <CardContent>
          <div className="rounded-lg border border-red-200 bg-red-50 p-4">
            <h4 className="text-sm font-medium text-red-800 mb-1">Error</h4>
            <p className="text-sm text-red-600">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (isLoading) {
    return (
      <Card className={className}>
        <CardContent>
          <div className="h-4 w-48 bg-gray-100 rounded animate-pulse mb-4" />
          <div className="h-[200px] w-full bg-gray-100 rounded animate-pulse" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
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
          className="bg-white"
        />
      </div>
    </Card>
  );
};

export default DAGVisualizationWidget;
