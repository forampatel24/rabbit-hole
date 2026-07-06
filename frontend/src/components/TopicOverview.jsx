import React, { useState, useContext } from 'react'
import { GraphContext } from '../context/GraphContext'
import { AuthContext } from '../context/AuthContext'
import {
  FiBook, FiBarChart2, FiClock, FiTrendingUp,
  FiStar, FiGrid, FiSave, FiCheck
} from 'react-icons/fi'

const difficultyColors = {
  Beginner: 'bg-accent-green/20 text-accent-green border-accent-green/30',
  Intermediate: 'bg-accent-yellow/20 text-accent-yellow border-accent-yellow/30',
  Advanced: 'bg-accent-red/20 text-accent-red border-accent-red/30',
}

export default function TopicOverview() {
  const { overview, savedGraphId, saveGraph, notes, completions, graph } = useContext(GraphContext)
  const { user } = useContext(AuthContext)
  const [saveMsg, setSaveMsg] = useState('')
  if (!overview) return null

  const cards = [
    { label: 'Domain', value: overview.domain, icon: FiBook },
    { label: 'Difficulty', value: overview.difficulty, icon: FiBarChart2, badge: difficultyColors[overview.difficulty] || difficultyColors.Intermediate },
    { label: 'Popularity', value: overview.popularity, icon: FiTrendingUp },
    { label: 'Time', value: overview.estimated_learning_time, icon: FiClock },
    { label: 'Importance', value: overview.importance_level, icon: FiStar },
  ]

  const totalNodes = graph?.nodes?.length || 0
  const completedCount = Object.values(completions).filter(Boolean).length
  const progressPct = totalNodes > 0 ? Math.round((completedCount / totalNodes) * 100) : 0

  return (
    <div className="mt-4 animate-fadeIn">
      <div className="glass-card rounded-2xl p-5">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-text-primary tracking-tight">{overview.topic}</h2>
            <p className="text-sm text-text-secondary mt-1 max-w-2xl leading-relaxed">{overview.summary}</p>
          </div>

          <div className="flex items-center gap-2 shrink-0 ml-4">
            {savedGraphId && (
              <div className="flex items-center gap-2 text-xs text-accent-green bg-accent-green/10 px-2.5 py-1 rounded-full">
                <FiCheck size={12} />
                Saved
              </div>
            )}
            {user && (
              <button
                onClick={async () => {
                  await saveGraph()
                  setSaveMsg('Saved!')
                  setTimeout(() => setSaveMsg(''), 2000)
                }}
                className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-xs font-medium hover:opacity-90 transition-opacity flex items-center gap-1.5"
              >
                <FiSave size={12} />
                {saveMsg || 'Save Graph'}
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-5 gap-3 mb-4">
          {cards.map((card) => (
            <div key={card.label} className="bg-deep-800/50 rounded-xl p-3 border border-surface-600/10">
              <div className="flex items-center gap-2 mb-1.5">
                <card.icon className="text-text-muted text-xs" />
                <span className="text-xs text-text-muted">{card.label}</span>
              </div>
              {card.badge ? (
                <span className={`inline-block text-xs font-medium px-2 py-0.5 rounded-full border ${card.badge}`}>
                  {card.value}
                </span>
              ) : (
                <p className="text-sm font-medium text-text-primary truncate">{card.value}</p>
              )}
            </div>
          ))}
        </div>

        {savedGraphId && totalNodes > 0 && (
          <div className="mb-3">
            <div className="flex items-center justify-between text-xs text-text-muted mb-1">
              <span>Progress</span>
              <span>{completedCount} / {totalNodes} concepts ({progressPct}%)</span>
            </div>
            <div className="w-full h-2 bg-deep-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-accent-blue to-accent-green rounded-full transition-all duration-500"
                style={{ width: `${progressPct}%` }}
              />
            </div>
          </div>
        )}

        {overview.applications?.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap">
            <FiGrid className="text-text-muted text-xs" />
            <span className="text-xs text-text-muted mr-1">Applications:</span>
            {overview.applications.map((app, i) => (
              <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-accent-blue/10 text-accent-blue border border-accent-blue/20">
                {app}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
