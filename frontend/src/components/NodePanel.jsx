import React, {useContext} from 'react'
import { GraphContext } from '../context/GraphContext'

export default function NodePanel(){
  const { selectedNodeId, nodeDetails, closePanel } = useContext(GraphContext)
  if(!selectedNodeId) return null
  const node = nodeDetails[selectedNodeId]
  if(!node) return null
  return (
    <aside className="w-96 bg-[#061226] text-[#F8FAFC] p-4 border-l border-[#0F172A]">
      <div className="flex justify-between items-center">
        <h3 className="text-lg font-semibold">{node.name}</h3>
        <button onClick={closePanel} className="text-[#94A3B8]">Close</button>
      </div>
      <p className="mt-2 text-sm text-[#94A3B8]">{node.description}</p>
      <div className="mt-3 text-sm">
        <div><strong>Difficulty:</strong> {node.difficulty}</div>
        <div><strong>Importance:</strong> {node.importance_score}</div>
        <div><strong>Estimate:</strong> {node.estimated_learning_time}</div>
        <div><strong>Prerequisites:</strong> {node.prerequisites?.join(', ')}</div>
        <div><strong>Unlocks:</strong> {node.unlocks?.join(', ')}</div>
        <div><strong>Applications:</strong> {node.applications?.join(', ')}</div>
      </div>
    </aside>
  )
}
