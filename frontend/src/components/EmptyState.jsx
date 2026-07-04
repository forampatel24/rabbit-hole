import React, { useContext, useState } from 'react'
import { GraphContext } from '../context/GraphContext'
import { FiHexagon, FiZap, FiBook, FiCpu, FiTrendingUp, FiGlobe } from 'react-icons/fi'

const suggestions = [
  { label: 'Transformers', icon: FiZap },
  { label: 'Machine Learning', icon: FiCpu },
  { label: 'Neural Networks', icon: FiBook },
  { label: 'Quantum Computing', icon: FiTrendingUp },
  { label: 'Ancient History', icon: FiGlobe },
]

export default function EmptyState() {
  const { generateGraph, loading, error } = useContext(GraphContext)
  const [value, setValue] = useState('')

  const handleSubmit = (topic) => {
    const searchTopic = topic || value.trim()
    if (!searchTopic) return
    generateGraph(searchTopic)
  }

  return (
    <div className="flex-1 flex items-center justify-center px-6">
      <div className="max-w-lg w-full text-center animate-fadeIn">
        <div className="w-16 h-16 mx-auto mb-6 rounded-2xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center shadow-lg shadow-accent-blue/20">
          <FiHexagon className="text-white text-2xl" />
        </div>

        <h1 className="text-4xl font-bold tracking-tight text-text-primary mb-3">
          RabbitHole
        </h1>
        <p className="text-lg text-text-secondary mb-8 leading-relaxed">
          Explore Knowledge.<br />
          Discover Dependencies.<br />
          Follow Curiosity.
        </p>

        {error && (
          <div className="mb-4 text-sm text-accent-red bg-accent-red/10 border border-accent-red/20 rounded-lg px-4 py-2.5 text-left">
            {error}
          </div>
        )}

        <div className="relative mb-6">
          <input
            className="w-full px-5 py-3.5 rounded-xl bg-deep-800 border border-surface-600/30 text-text-primary placeholder-text-muted text-base focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/20 transition-all duration-200"
            placeholder="Enter any topic..."
            value={value}
            onChange={e => setValue(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && handleSubmit()}
          />
          <button
            onClick={() => handleSubmit()}
            disabled={loading || !value.trim()}
            className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            {loading ? 'Generating...' : 'Explore'}
          </button>
        </div>

        <div>
          <p className="text-xs text-text-muted mb-3 uppercase tracking-widest">Try Exploring</p>
          <div className="flex flex-wrap justify-center gap-2">
            {suggestions.map((s) => (
              <button
                key={s.label}
                onClick={() => handleSubmit(s.label)}
                disabled={loading}
                className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-lg bg-deep-800/50 border border-surface-600/20 text-text-secondary text-sm hover:bg-deep-700/50 hover:text-text-primary hover:border-accent-blue/30 transition-all duration-200 disabled:opacity-40"
              >
                <s.icon className="text-xs" />
                {s.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
