import React, { useContext, useMemo } from 'react'
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow'
import 'reactflow/dist/style.css'
import { GraphContext } from '../context/GraphContext'

const nodeTypeColors = {
  prerequisite: '#3B82F6',
  core_concept: '#10B981',
  advanced_concept: '#8B5CF6',
  application: '#F59E0B',
  framework: '#EF4444',
  tool: '#06B6D4',
  mathematical_foundation: '#EC4899',
  related_concept: '#94A3B8',
}

function layoutNodes(nodes, edges) {
  if (nodes.length === 0) return nodes

  const depths = {}
  const adjacency = {}
  const reverseAdj = {}

  nodes.forEach(n => {
    depths[n.id] = n.depth ?? 0
    adjacency[n.id] = []
    reverseAdj[n.id] = []
  })

  edges.forEach(e => {
    if (adjacency[e.source]) adjacency[e.source].push(e.target)
    if (reverseAdj[e.target]) reverseAdj[e.target].push(e.source)
  })

  const levelMap = {}
  nodes.forEach(n => {
    const d = n.depth ?? 0
    if (!levelMap[d]) levelMap[d] = []
    levelMap[d].push(n.id)
  })

  const xSpacing = 280
  const ySpacing = 120
  const levels = Object.keys(levelMap).sort((a, b) => Number(a) - Number(b))

  levels.forEach((level, li) => {
    const ids = levelMap[level]
    const totalWidth = (ids.length - 1) * xSpacing
    ids.forEach((id, i) => {
      const node = nodes.find(n => n.id === id)
      if (node) {
        node.position = {
          x: -totalWidth / 2 + i * xSpacing,
          y: li * 220 + 40,
        }
      }
    })
  })

  return nodes
}

export default function GraphView() {
  const { graph, openNodePanel } = useContext(GraphContext)

  const { rfNodes, rfEdges } = useMemo(() => {
    const nodes = (graph?.nodes || []).map(n => ({
      id: n.id,
      type: 'default',
      data: {
        label: n.name,
      },
      style: {
        background: nodeTypeColors[n.type] || '#3B82F6',
        color: '#F8FAFC',
        border: 'none',
        borderRadius: '8px',
        padding: '10px 16px',
        fontSize: '13px',
        fontWeight: 600,
        minWidth: '120px',
        textAlign: 'center',
        boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
      },
      position: n.position || { x: 0, y: 0 },
    }))

    const laidOut = layoutNodes(nodes, graph?.edges || [])

    const edges = (graph?.edges || []).map(e => ({
      id: e.id || `${e.source}-${e.target}`,
      source: e.source,
      target: e.target,
      label: e.relationship,
      style: { stroke: '#475569', strokeWidth: 2 },
      labelStyle: { fill: '#94A3B8', fontSize: 10 },
      markerEnd: {
        type: MarkerType.ArrowClosed,
        color: '#475569',
        width: 20,
        height: 20,
      },
    }))

    return { rfNodes: laidOut, rfEdges: edges }
  }, [graph])

  if (!graph?.nodes?.length) {
    return (
      <div className="flex-1 bg-[#071127] rounded flex items-center justify-center" style={{ height: '600px' }}>
        <p className="text-[#94A3B8] text-lg">Enter a topic to generate a knowledge universe</p>
      </div>
    )
  }

  return (
    <div className="flex-1 bg-[#071127] rounded overflow-hidden" style={{ height: '600px' }}>
      <ReactFlow
        nodes={rfNodes}
        edges={rfEdges}
        onNodeClick={(e, node) => openNodePanel(node.id)}
        fitView
        fitViewOptions={{ padding: 0.3 }}
        style={{ width: '100%', height: '100%' }}
        nodesDraggable={true}
        nodesConnectable={false}
      >
        <Background color="#1E293B" gap={20} />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}
