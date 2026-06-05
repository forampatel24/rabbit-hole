import React, {createContext, useState} from 'react'
import api from '../services/api'

export const GraphContext = createContext()

export function GraphProvider({children}){
  const [overview,setOverview] = useState(null)
  const [graph,setGraph] = useState({nodes:[], edges:[]})
  const [nodeDetails,setNodeDetails] = useState({})
  const [selectedNodeId, setSelectedNodeId] = useState(null)
  const [gapResult, setGapResult] = useState(null)

  const generateGraph = async (topic)=>{
    if(!topic) return
    try{
      const res = await api.post('/generate-graph', {topic})
      setOverview(res.data.overview)
      setGraph(res.data.graph)
      setNodeDetails(res.data.node_details || {})
    }catch(err){
      console.error(err)
      alert('Failed to generate graph')
    }
  }

  const openNodePanel = (id)=>{
    setSelectedNodeId(id)
  }
  const closePanel = ()=> setSelectedNodeId(null)

  const expandNode = async (nodeId)=>{
    try{
      const res = await api.post('/expand-node', {node_id: nodeId, current_depth: 1})
      const {new_nodes, new_edges, new_node_details} = res.data
      // merge
      setGraph(prev=>({nodes: [...prev.nodes, ...new_nodes], edges: [...prev.edges, ...new_edges]}))
      setNodeDetails(prev=>({...prev, ...new_node_details}))
    }catch(e){console.error(e)}
  }

  const analyzeKnowledgeGap = async (known_concepts, target_topic)=>{
    try{
      const res = await api.post('/knowledge-gap', {known_concepts, target_topic})
      setGapResult(res.data)
    }catch(e){console.error(e); alert('Knowledge gap analysis failed')}
  }

  return (
    <GraphContext.Provider value={{overview, graph, nodeDetails, selectedNodeId, gapResult, generateGraph, openNodePanel, closePanel, expandNode, analyzeKnowledgeGap, setGraph}}>
      {children}
    </GraphContext.Provider>
  )
}
