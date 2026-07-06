import React, { useContext, useState, useEffect, useRef, useCallback } from 'react'
import ReactFlow, {
  Background, Controls, MiniMap, ReactFlowProvider,
  MarkerType,
} from 'reactflow'
import 'reactflow/dist/style.css'
import dagre from 'dagre'
import { GraphContext } from '../context/GraphContext'
import CustomNode from './CustomNode'

const nodeTypes = { custom: CustomNode }
const NODE_W = 180
const NODE_H = 70

function dagreLayout(nodes, edges) {
  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'TB', nodesep: 80, ranksep: 120, marginx: 50, marginy: 50 })

  const ids = new Set(nodes.map(n => n.id))
  nodes.forEach(n => g.setNode(n.id, { width: NODE_W, height: NODE_H }))
  edges.forEach(e => {
    if (ids.has(e.source) && ids.has(e.target)) g.setEdge(e.source, e.target)
  })

  dagre.layout(g)

  return nodes.map(n => {
    const p = g.node(n.id)
    if (!p) return { ...n, position: { x: 0, y: 0 } }
    return { ...n, position: { x: p.x - NODE_W / 2, y: p.y - NODE_H / 2 } }
  })
}

function expansionLayout(newNodes, allEdges, frozen) {
  const frozenIds = Object.keys(frozen)
  if (frozenIds.length === 0) return newNodes

  const allIds = new Set([...frozenIds, ...newNodes.map(n => n.id)])

  const g = new dagre.graphlib.Graph()
  g.setDefaultEdgeLabel(() => ({}))
  g.setGraph({ rankdir: 'TB', nodesep: 80, ranksep: 120, marginx: 50, marginy: 50 })

  allIds.forEach(id => g.setNode(id, { width: NODE_W, height: NODE_H }))
  allEdges.forEach(e => {
    if (allIds.has(e.source) && allIds.has(e.target)) g.setEdge(e.source, e.target)
  })

  dagre.layout(g)

  return newNodes.map(n => {
    const dp = g.node(n.id)
    if (!dp) return { ...n, position: { x: 0, y: 0 } }
    const dagrePos = { x: dp.x - NODE_W / 2, y: dp.y - NODE_H / 2 }

    const pe = allEdges.find(e => e.target === n.id && frozen[e.source])
    if (pe && frozen[pe.source]) {
      const parentActual = frozen[pe.source]
      const parentDagre = g.node(pe.source)
      if (parentDagre) {
        const pdp = { x: parentDagre.x - NODE_W / 2, y: parentDagre.y - NODE_H / 2 }
        return {
          ...n,
          position: {
            x: dagrePos.x + (parentActual.x - pdp.x),
            y: dagrePos.y + (parentActual.y - pdp.y) + 20,
          },
        }
      }
    }
    return { ...n, position: dagrePos }
  })
}

function toRFNode(n, i, completions) {
  return {
    id: n.id,
    type: 'custom',
    data: {
      label: n.name,
      nodeType: n.type,
      difficulty: n.difficulty,
      importance: n.importance_score,
      completed: completions?.[n.id] || false,
    },
    position: { x: 0, y: 0 },
  }
}

function toRFEdge(e) {
  return {
    id: e.id || `${e.source}-${e.target}`,
    source: e.source,
    target: e.target,
    label: e.relationship,
    type: 'smoothstep',
    animated: true,
    style: { stroke: '#475569', strokeWidth: 2 },
    labelStyle: { fill: '#64748B', fontSize: 10, fontWeight: 500 },
    labelBgStyle: { fill: '#0B1225', opacity: 0.8 },
    labelBgPadding: [6, 3],
    labelBgBorderRadius: 4,
    markerEnd: { type: MarkerType.ArrowClosed, color: '#475569', width: 18, height: 18 },
  }
}

function GraphFlow() {
  const { graph, openNodePanel, completions } = useContext(GraphContext)
  const [renderNodes, setRenderNodes] = useState([])
  const [renderEdges, setRenderEdges] = useState([])
  const [generationKey, setGenerationKey] = useState(0)
  const frozenPositions = useRef({})
  const prevCount = useRef(0)
  const fitCalled = useRef(false)

  useEffect(() => {
    const nodes = graph?.nodes
    const edges = graph?.edges
    if (!nodes || nodes.length === 0) {
      setRenderNodes([])
      setRenderEdges([])
      frozenPositions.current = {}
      prevCount.current = 0
      return
    }

    const nCount = nodes.length
    const frozenIds = Object.keys(frozenPositions.current)
    const hasOverlap = frozenIds.length > 0 && nodes.some(n => frozenIds.includes(n.id))
    const isExpansion = frozenIds.length > 0 && nCount > prevCount.current && hasOverlap
    const rawEdges = edges.map(toRFEdge)

    let positionedNodes

    if (isExpansion) {
      const existingCount = prevCount.current
      const existingNodes = nodes.slice(0, existingCount)
      const newNodes = nodes.slice(existingCount)

      const existingRF = existingNodes.map((n, i) => {
        const saved = frozenPositions.current[n.id]
        const base = toRFNode(n, i, completions)
        return saved ? { ...base, position: { ...saved } } : base
      })

      const newRF = newNodes.map((n, i) => toRFNode(n, existingCount + i, completions))
      const positionedNew = expansionLayout(newRF, rawEdges, frozenPositions.current)

      positionedNew.forEach(n => { frozenPositions.current[n.id] = { ...n.position } })
      positionedNodes = [...existingRF, ...positionedNew]
    } else {
      const rawNodes = nodes.map((n, i) => toRFNode(n, i, completions))
      positionedNodes = dagreLayout(rawNodes, rawEdges)
      positionedNodes.forEach(n => { frozenPositions.current[n.id] = { ...n.position } })
    }

    prevCount.current = nCount
    setRenderNodes(positionedNodes)
    setRenderEdges(rawEdges)
    setGenerationKey(k => k + 1)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [graph, completions])

  const onNodeClick = useCallback((e, node) => openNodePanel(node.id), [openNodePanel])

  const onInit = useCallback((instance) => {
    if (fitCalled.current) return
    fitCalled.current = true
    requestAnimationFrame(() => {
      instance.fitView({ padding: 0.35, duration: 500 })
    })
  }, [])

  const hasNodes = renderNodes.length > 0

  return (
    <div className="w-full h-full relative" style={{ minHeight: '500px' }}>
      <ReactFlow
        key={generationKey || 'empty'}
        nodes={renderNodes}
        edges={renderEdges}
        nodeTypes={nodeTypes}
        onNodeClick={onNodeClick}
        onInit={onInit}
        fitView={false}
        nodesDraggable={true}
        nodesConnectable={false}
        minZoom={0.2}
        maxZoom={2.5}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
          style: { stroke: '#475569', strokeWidth: 2 },
        }}
      >
        <Background color="#1E293B" gap={24} size={1} />
        <Controls showInteractive={false} className="!bottom-4 !left-4 !shadow-none !space-y-1.5" />
        <MiniMap
          nodeColor={(n) => {
            if (n.data?.completed) return '#10B981'
            const colors = {
              prerequisite: '#3B82F6', core_concept: '#10B981', advanced_concept: '#8B5CF6',
              application: '#F59E0B', framework: '#EF4444', tool: '#06B6D4',
              mathematical_foundation: '#EC4899',
            }
            return colors[n.data?.nodeType] || '#64748B'
          }}
          maskColor="rgba(7, 11, 26, 0.7)"
          style={{ background: '#0B1225', borderRadius: 12, border: '1px solid rgba(51, 65, 85, 0.2)' }}
          className="!bottom-4 !right-4"
        />
      </ReactFlow>
      {!hasNodes && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none z-10">
          <p className="text-text-muted text-sm">Enter a topic to generate a knowledge universe</p>
        </div>
      )}
    </div>
  )
}

export default function GraphView() {
  return (
    <ReactFlowProvider>
      <GraphFlow />
    </ReactFlowProvider>
  )
}
