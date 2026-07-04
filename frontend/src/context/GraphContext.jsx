import React, { createContext, useState } from 'react'
import api from '../services/api'

export const GraphContext = createContext()

export function GraphProvider({ children }) {
  const [overview, setOverview] = useState(null)
  const [graph, setGraph] = useState({ nodes: [], edges: [] })
  const [nodeDetails, setNodeDetails] = useState({})
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const [gapResult, setGapResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const generateGraph = async (topic) => {
    if (!topic) return
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/generate-graph', { topic })
      setOverview(res.data.overview)
      setGraph(res.data.graph)
      setNodeDetails(res.data.node_details || {})
      setSelectedNodeId(null)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to generate graph')
    } finally {
      setLoading(false)
    }
  }

  const openNodePanel = (id) => {
    setSelectedNodeId(id)
  }

  const closePanel = () => setSelectedNodeId(null)

  const expandNode = async (nodeId) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/expand-node', {
        node_id: nodeId,
        current_depth: (nodeDetails[nodeId]?.depth || 0) + 1,
      })
      const { new_nodes, new_edges, new_node_details } = res.data
      setGraph(prev => ({
        nodes: [...prev.nodes, ...new_nodes],
        edges: [...prev.edges, ...new_edges],
      }))
      setNodeDetails(prev => ({ ...prev, ...new_node_details }))
    } catch (e) {
      console.error(e)
      setError(e.response?.data?.detail || 'Failed to expand node')
    } finally {
      setLoading(false)
    }
  }

  const analyzeKnowledgeGap = async (known_concepts, target_topic) => {
    setLoading(true)
    setError(null)
    try {
      const res = await api.post('/knowledge-gap', { known_concepts, target_topic })
      setGapResult(res.data)
    } catch (e) {
      console.error(e)
      setError(e.response?.data?.detail || 'Knowledge gap analysis failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <GraphContext.Provider value={{
      overview,
      graph,
      nodeDetails,
      selectedNodeId,
      gapResult,
      loading,
      error,
      generateGraph,
      openNodePanel,
      closePanel,
      expandNode,
      analyzeKnowledgeGap,
      setGraph,
      setError,
    }}>
      {children}
    </GraphContext.Provider>
  )
}
