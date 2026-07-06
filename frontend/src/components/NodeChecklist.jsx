import React, { useContext } from 'react'
import { GraphContext } from '../context/GraphContext'
import { AuthContext } from '../context/AuthContext'
import { FiCheckSquare, FiSquare, FiBook, FiBarChart2 } from 'react-icons/fi'

const typeColors = {
  prerequisite: 'text-accent-blue',
  core_concept: 'text-accent-green',
  advanced_concept: 'text-accent-purple',
  application: 'text-accent-yellow',
  framework: 'text-accent-red',
  tool: 'text-accent-cyan',
  mathematical_foundation: 'text-accent-pink',
}

export default function NodeChecklist() {
  const { graph, savedGraphId, completions, toggleCompletion } = useContext(GraphContext)
  const { user } = useContext(AuthContext)

  if (!savedGraphId || !user) return null

  const nodes = graph?.nodes || []
  const totalCount = nodes.length
  const completedCount = Object.values(completions).filter(Boolean).length
  const pct = totalCount > 0 ? Math.round((completedCount / totalCount) * 100) : 0

  if (totalCount === 0) return null

  return (
    <div className="glass-card rounded-2xl p-5 animate-fadeIn">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <FiBarChart2 className="text-accent-blue text-sm" />
          <h4 className="text-sm font-semibold text-text-primary">Checklist</h4>
        </div>
        <span className="text-xs text-text-muted">
          {completedCount} / {totalCount} ({pct}%)
        </span>
      </div>

      <div className="w-full h-1.5 bg-deep-700 rounded-full mb-3 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-accent-blue to-accent-green rounded-full transition-all duration-500"
          style={{ width: `${pct}%` }}
        />
      </div>

      <div className="max-h-64 overflow-y-auto space-y-1">
        {nodes.map((node) => {
          const isCompleted = completions?.[node.id] || false
          const typeColor = typeColors[node.type] || 'text-text-muted'
          return (
            <button
              key={node.id}
              onClick={() => toggleCompletion(node.id)}
              className={`w-full flex items-center gap-2.5 px-3 py-2 rounded-xl text-left transition-all ${
                isCompleted
                  ? 'bg-accent-green/5 text-text-secondary'
                  : 'bg-deep-800/50 text-text-primary hover:bg-deep-700/50'
              }`}
            >
              {isCompleted ? (
                <FiCheckSquare className="text-accent-green shrink-0" size={16} />
              ) : (
                <FiSquare className="text-text-muted shrink-0" size={16} />
              )}
              <FiBook className={`${typeColor} shrink-0 text-xs`} />
              <span className={`text-sm truncate ${isCompleted ? 'line-through opacity-60' : ''}`}>
                {node.name}
              </span>
            </button>
          )
        })}
      </div>
    </div>
  )
}
