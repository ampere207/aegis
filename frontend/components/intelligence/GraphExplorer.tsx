'use client';

import React, { useCallback, useMemo, useEffect } from 'react';
import { useParams } from 'next/navigation';
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

export default function GraphExplorer() {
  const params = useParams();
  const repoId = Number(params.id);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [loading, setLoading] = React.useState(true);

  useEffect(() => {
    const fetchGraph = async () => {
      if (!repoId) return;
      setLoading(true);
      try {
        const res = await fetch(`/api/repos/${repoId}/graph`, { credentials: 'include' });
        if (res.ok) {
          const data = await res.json();
          
          // Layout the nodes roughly in a grid or circle if no position provided
          const mappedNodes = data.nodes.map((n: any, i: number) => ({
            id: n.id,
            position: { x: (i % 3) * 250, y: Math.floor(i / 3) * 150 },
            data: { label: n.label },
            type: n.type === 'API_ROUTE' ? 'input' : n.type === 'DATABASE_OPERATION' ? 'output' : 'default',
            style: {
               background: n.type === 'API_ROUTE' ? '#3b82f6' : n.type === 'DATABASE_OPERATION' ? '#10b981' : '#1f2937',
               color: '#fff',
               borderRadius: '8px',
               padding: '10px',
               fontSize: '12px',
               fontWeight: 'bold',
               border: '1px solid rgba(255,255,255,0.1)'
            }
          }));

          setNodes(mappedNodes);
          setEdges(data.edges.map((e: any) => ({
            ...e,
            animated: true,
            style: { stroke: '#6366f1' },
            labelStyle: { fill: '#94a3b8', fontSize: 10 }
          })));
        }
      } catch (e) {
        console.error('Failed to fetch graph:', e);
      } finally {
        setLoading(false);
      }
    };
    fetchGraph();
  }, [repoId, setNodes, setEdges]);

  const onConnect: OnConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  if (loading) {
    return (
      <div className="h-[600px] w-full flex items-center justify-center bg-card rounded-xl border border-border">
        <div className="flex flex-col items-center gap-2">
          <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Mapping security architecture...</p>
        </div>
      </div>
    );
  }

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
