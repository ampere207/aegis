'use client';

import React, { useCallback, useMemo } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Panel,
  Node,
  Edge,
  OnConnect,
  Connection,
  BackgroundVariant,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

const initialNodes: Node[] = [
  { id: '1', position: { x: 0, y: 0 }, data: { label: 'Auth Service' }, type: 'input' },
  { id: '2', position: { x: 0, y: 100 }, data: { label: 'Billing API' } },
  { id: '3', position: { x: 200, y: 100 }, data: { label: 'Database' }, type: 'output' },
];

const initialEdges: Edge[] = [
  { id: 'e1-2', source: '1', target: '2', label: 'CALLS', animated: true },
  { id: 'e2-3', source: '2', target: '3', label: 'WRITES_TO' },
];

export default function GraphExplorer() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect: OnConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  return (
    <div className="h-[600px] w-full border border-border rounded-xl bg-card overflow-hidden shadow-2xl">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        fitView
        colorMode="dark"
      >
        <Controls />
        <MiniMap />
        <Background variant={BackgroundVariant.Dots} gap={12} size={1} />
        <Panel position="top-left" className="bg-background/80 backdrop-blur p-2 rounded border border-border text-sm font-medium">
          Security Knowledge Graph
        </Panel>
      </ReactFlow>
    </div>
  );
}
