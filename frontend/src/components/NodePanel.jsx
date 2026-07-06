import React, { useContext } from 'react'
import { GraphContext } from '../context/GraphContext'
import { AuthContext } from '../context/AuthContext'
import {
  FiX, FiBook, FiBarChart2, FiClock, FiStar,
  FiArrowRight, FiGrid, FiHeart, FiExternalLink,
  FiChevronRight, FiZap, FiLayers, FiCheckCircle, FiCircle
} from 'react-icons/fi'

const difficultyColors = {
  Beginner: 'text-accent-green bg-accent-green/10',
  Intermediate: 'text-accent-yellow bg-accent-yellow/10',
  Advanced: 'text-accent-red bg-accent-red/10',
}

export default function NodePanel() {
  const { selectedNodeId, nodeDetails, closePanel, expandNode, savedGraphId, completions, toggleCompletion } = useContext(GraphContext)
  const { user } = useContext(AuthContext)
  if (!selectedNodeId) return null
  const node = nodeDetails[selectedNodeId]
  if (!node) return null

  const badgeColor = difficultyColors[node.difficulty] || difficultyColors.Intermediate
  const isCompleted = completions?.[selectedNodeId] || false

  return (
    <div className="glass-card rounded-2xl h-full overflow-hidden flex flex-col">
      <div className="p-5 border-b border-surface-700/20">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-text-primary tracking-tight truncate">{node.name}</h3>
            <div className="flex items-center gap-2 mt-1.5">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeColor}`}>
                {node.difficulty}
              </span>
              <span className="text-xs text-text-muted">
                <FiStar className="inline mr-0.5 text-accent-yellow" />
                {node.importance_score}/10
              </span>
            </div>
          </div>
          <button onClick={closePanel} className="p-1.5 rounded-lg hover:bg-surface-700/30 text-text-muted hover:text-text-primary transition-colors">
            <FiX size={16} />
          </button>
        </div>

        {savedGraphId && user && (
          <button
            onClick={() => toggleCompletion(selectedNodeId)}
            className={`mt-3 w-full px-3 py-2 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all ${
              isCompleted
                ? 'bg-accent-green/10 text-accent-green border border-accent-green/30'
                : 'bg-deep-700/50 text-text-muted border border-surface-600/20 hover:border-accent-green/30 hover:text-accent-green'
            }`}
          >
            {isCompleted ? (
              <><FiCheckCircle size={14} /> Completed</>
            ) : (
              <><FiCircle size={14} /> Mark as Completed</>
            )}
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        <Section icon={FiBook} title="Overview">
          <p className="text-sm text-text-secondary leading-relaxed">{node.description}</p>
          <div className="flex items-center gap-2 mt-2 text-xs text-text-muted">
            <FiClock className="shrink-0" />
            <span>{node.estimated_learning_time}</span>
          </div>
        </Section>

        {node.prerequisites?.length > 0 && (
          <Section icon={FiArrowRight} title="Prerequisites" accent="text-accent-yellow">
            <ul className="space-y-1.5">
              {node.prerequisites.map((p, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-text-secondary">
                  <FiChevronRight className="text-accent-yellow shrink-0 text-xs" />
                  {p}
                </li>
              ))}
            </ul>
          </Section>
        )}

        {node.unlocks?.length > 0 && (
          <Section icon={FiZap} title="Unlocks" accent="text-accent-green">
            <ul className="space-y-1.5">
              {node.unlocks.map((u, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-text-secondary">
                  <FiChevronRight className="text-accent-green shrink-0 text-xs" />
                  {u}
                </li>
              ))}
            </ul>
          </Section>
        )}

        {node.applications?.length > 0 && (
          <Section icon={FiGrid} title="Applications" accent="text-accent-blue">
            <div className="flex flex-wrap gap-1.5">
              {node.applications.map((a, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-accent-blue/10 text-accent-blue border border-accent-blue/20">
                  {a}
                </span>
              ))}
            </div>
          </Section>
        )}

        {node.why_it_matters && (
          <Section icon={FiHeart} title="Why It Matters" accent="text-accent-pink">
            <p className="text-sm text-text-secondary leading-relaxed">{node.why_it_matters}</p>
          </Section>
        )}

        {node.resources && Object.keys(node.resources).length > 0 && (
          <Section icon={FiExternalLink} title="Resources" accent="text-accent-cyan">
            {Object.entries(node.resources).map(([key, val]) => (
              <div key={key} className="flex items-center gap-2 text-sm text-accent-cyan">
                <FiExternalLink className="shrink-0 text-xs" />
                <span className="truncate">{String(val)}</span>
              </div>
            ))}
          </Section>
        )}
      </div>

      <div className="p-4 border-t border-surface-700/20 space-y-2">
        <button
          onClick={() => expandNode(node.id)}
          className="w-full px-4 py-2.5 rounded-xl bg-gradient-to-r from-accent-blue to-accent-purple text-white text-sm font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
        >
          <FiLayers />
          Expand Concept
        </button>
      </div>
    </div>
  )
}

function Section({ icon: Icon, title, children, accent = 'text-text-muted' }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`${accent} text-sm`} />
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-muted">{title}</h4>
      </div>
      {children}
    </div>
  )
}
