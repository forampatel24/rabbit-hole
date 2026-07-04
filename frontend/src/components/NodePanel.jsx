import React, { useContext } from 'react'
import { GraphContext } from '../context/GraphContext'

export default function NodePanel() {
  const { selectedNodeId, nodeDetails, closePanel, expandNode } = useContext(GraphContext)
  if (!selectedNodeId) return null
  const node = nodeDetails[selectedNodeId]
  if (!node) return null

  return (
    <aside className="bg-[#061226] text-[#F8FAFC] p-4 border-l border-[#0F172A] h-full overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">{node.name}</h3>
        <button onClick={closePanel} className="text-[#94A3B8] hover:text-[#F8FAFC] text-sm">Close</button>
      </div>

      <div className="space-y-4 text-sm">
        <div>
          <p className="text-[#94A3B8] leading-relaxed">{node.description}</p>
        </div>

        <div className="border-t border-[#0F172A] pt-3">
          <div className="flex justify-between">
            <span className="text-[#94A3B8]">Difficulty</span>
            <span className="font-medium">{node.difficulty}</span>
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-[#94A3B8]">Importance</span>
            <span className="font-medium">{node.importance_score}/10</span>
          </div>
          <div className="flex justify-between mt-1">
            <span className="text-[#94A3B8]">Estimated Time</span>
            <span className="font-medium">{node.estimated_learning_time}</span>
          </div>
        </div>

        {node.prerequisites?.length > 0 && (
          <div className="border-t border-[#0F172A] pt-3">
            <h4 className="text-[#94A3B8] text-xs uppercase tracking-wide mb-2">Prerequisites</h4>
            <ul className="space-y-1">
              {node.prerequisites.map((p, i) => (
                <li key={i} className="text-[#F59E0B]">• {p}</li>
              ))}
            </ul>
          </div>
        )}

        {node.unlocks?.length > 0 && (
          <div className="border-t border-[#0F172A] pt-3">
            <h4 className="text-[#94A3B8] text-xs uppercase tracking-wide mb-2">Unlocks</h4>
            <ul className="space-y-1">
              {node.unlocks.map((u, i) => (
                <li key={i} className="text-[#10B981]">→ {u}</li>
              ))}
            </ul>
          </div>
        )}

        {node.applications?.length > 0 && (
          <div className="border-t border-[#0F172A] pt-3">
            <h4 className="text-[#94A3B8] text-xs uppercase tracking-wide mb-2">Applications</h4>
            <ul className="space-y-1">
              {node.applications.map((a, i) => (
                <li key={i} className="text-[#3B82F6]">▶ {a}</li>
              ))}
            </ul>
          </div>
        )}

        {node.why_it_matters && (
          <div className="border-t border-[#0F172A] pt-3">
            <h4 className="text-[#94A3B8] text-xs uppercase tracking-wide mb-2">Why It Matters</h4>
            <p className="text-[#F8FAFC] leading-relaxed">{node.why_it_matters}</p>
          </div>
        )}

        {node.resources && Object.keys(node.resources).length > 0 && (
          <div className="border-t border-[#0F172A] pt-3">
            <h4 className="text-[#94A3B8] text-xs uppercase tracking-wide mb-2">Resources</h4>
            {Object.entries(node.resources).map(([key, val]) => (
              <div key={key} className="text-sm text-[#3B82F6]">
                {key}: {val}
              </div>
            ))}
          </div>
        )}

        <div className="border-t border-[#0F172A] pt-3">
          <button
            onClick={() => expandNode(node.id)}
            className="w-full px-4 py-2 bg-[#8B5CF6] text-black font-medium rounded hover:bg-[#7C3AED] transition-colors"
          >
            Expand Concept
          </button>
        </div>
      </div>
    </aside>
  )
}
