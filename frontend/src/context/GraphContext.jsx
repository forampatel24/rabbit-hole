import React, { createContext, useState, useCallback, useRef } from 'react'
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

  const [savedGraphId, setSavedGraphId] = useState(null)
  const [notes, setNotes] = useState('')
  const [completions, setCompletions] = useState({})
  const [resources, setResources] = useState({})
  const [resourceLoading, setResourceLoading] = useState({})

  const expandedNodes = useRef(new Set())

  const generateGraph = useCallback(async (topic) => {
    if (!topic) return
    setLoading(true)
    setError(null)
    expandedNodes.current = new Set()
    setSavedGraphId(null)
    setNotes('')
    setCompletions({})
    try {
      const res = await api.post('/generate-graph', { topic })
      setOverview(res.data.overview)
      setGraph(res.data.graph)
      setNodeDetails(res.data.node_details || {})
      setSelectedNodeId(null)
      setGapResult(null)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to generate graph')
    } finally {
      setLoading(false)
    }
  }, [])

  const openNodePanel = useCallback((id) => {
    setSelectedNodeId(id)
  }, [])

  const closePanel = useCallback(() => setSelectedNodeId(null), [])

  const expandNode = useCallback(async (nodeId) => {
    if (expandedNodes.current.has(nodeId)) return
    expandedNodes.current.add(nodeId)

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
      expandedNodes.current.delete(nodeId)
      console.error(e)
      setError(e.response?.data?.detail || 'Failed to expand node')
    } finally {
      setLoading(false)
    }
  }, [nodeDetails])

  const analyzeKnowledgeGap = useCallback(async (known_concepts, target_topic) => {
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
  }, [])

  const saveGraph = useCallback(async () => {
    if (!overview) return
    setLoading(true)
    setError(null)
    try {
      const payload = {
        topic: overview.topic,
        overview,
        graph,
        node_details: nodeDetails,
      }
      let res
      if (savedGraphId) {
        res = await api.put(`/graphs/${savedGraphId}`, payload)
      } else {
        res = await api.post('/graphs/save', payload)
        setSavedGraphId(res.data.id)
      }
      if (notes.trim()) {
        await api.put(`/graphs/${res.data.id || savedGraphId}/notes`, { content: notes })
      }
      return res.data
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to save graph')
    } finally {
      setLoading(false)
    }
  }, [overview, graph, nodeDetails, notes, savedGraphId])

  const deleteGraph = useCallback(async (graphId) => {
    setLoading(true)
    setError(null)
    try {
      await api.delete(`/graphs/${graphId}`)
      if (savedGraphId === graphId) {
        setSavedGraphId(null)
      }
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to delete graph')
    } finally {
      setLoading(false)
    }
  }, [savedGraphId])

  const loadSavedGraph = useCallback(async (id) => {
    setLoading(true)
    setError(null)
    expandedNodes.current = new Set()
    try {
      const res = await api.get(`/graphs/open/${id}`)
      setSavedGraphId(res.data.id)
      setOverview(res.data.overview)
      setGraph(res.data.graph)
      setNodeDetails(res.data.node_details)
      setNotes(res.data.notes || '')
      setCompletions(res.data.completions || {})
      setSelectedNodeId(null)
      setGapResult(null)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail || 'Failed to load graph')
    } finally {
      setLoading(false)
    }
  }, [])

  const saveNotes = useCallback(async (content) => {
    if (!savedGraphId) return
    try {
      await api.put(`/graphs/${savedGraphId}/notes`, { content })
      setNotes(content)
    } catch (err) {
      console.error(err)
    }
  }, [savedGraphId])

  const fetchResources = useCallback(async (conceptName) => {
    if (!conceptName) return
    if (resources[conceptName]) return

    setResourceLoading(prev => ({ ...prev, [conceptName]: true }))
    try {
      const res = await api.get(`/resources/${encodeURIComponent(conceptName)}`)
      setResources(prev => ({ ...prev, [conceptName]: res.data }))
    } catch (err) {
      console.error('Failed to fetch resources:', err)
      setResources(prev => ({ ...prev, [conceptName]: { youtube: [], courses: [], papers: [], github: [] } }))
    } finally {
      setResourceLoading(prev => ({ ...prev, [conceptName]: false }))
    }
  }, [resources])

  const toggleCompletion = useCallback(async (nodeId) => {
    if (!savedGraphId) return
    const current = completions[nodeId] || false
    const newState = !current
    try {
      const res = await api.put(`/graphs/${savedGraphId}/completion`, {
        node_id: nodeId,
        completed: newState,
      })
      setCompletions(prev => ({ ...prev, [nodeId]: newState }))
    } catch (err) {
      console.error(err)
    }
  }, [savedGraphId, completions])

  return (
    <GraphContext.Provider value={{
      overview,
      graph,
      nodeDetails,
      selectedNodeId,
      gapResult,
      loading,
      error,
      savedGraphId,
      notes,
      completions,
      resources,
      resourceLoading,
      generateGraph,
      fetchResources,
      openNodePanel,
      closePanel,
      expandNode,
      analyzeKnowledgeGap,
      setGraph,
      setError,
      saveGraph,
      loadSavedGraph,
      deleteGraph,
      saveNotes,
      toggleCompletion,
      setNotes,
    }}>
      {children}
    </GraphContext.Provider>
  )
}
