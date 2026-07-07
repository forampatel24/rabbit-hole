import React, { useContext, useState, useRef, useEffect } from 'react'
import { GraphContext } from '../context/GraphContext'
import { FiHexagon, FiZap, FiBook, FiCpu, FiTrendingUp, FiGlobe, FiChevronDown } from 'react-icons/fi'

const modes = [
  { value: 'learn', label: 'Learn', icon: '📚' },
  { value: 'interview', label: 'Interview Preparation', icon: '💼' },
  { value: 'project', label: 'Project Building', icon: '🛠' },
  { value: 'research', label: 'Research', icon: '🔬' },
  { value: 'quick', label: 'Quick Overview', icon: '⚡' },
]

const suggestions = [
  { label: 'Transformers', icon: FiZap },
  { label: 'Machine Learning', icon: FiCpu },
  { label: 'Neural Networks', icon: FiBook },
  { label: 'Quantum Computing', icon: FiTrendingUp },
  { label: 'Ancient History', icon: FiGlobe },
]

export default function EmptyState() {
  const { generateGraph, loading, error, mode, setMode } = useContext(GraphContext)
  const [value, setValue] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef(null)

  useEffect(() => {
    function handleClick(e) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  const currentMode = modes.find(m => m.value === mode) || modes[0]

  const handleSubmit = (topic) => {
    const searchTopic = topic || value.trim()
    if (!searchTopic) return
    generateGraph(searchTopic, mode)
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

        <div className="flex items-center gap-2 mb-3 justify-start">
          <div className="relative z-[100]" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="flex items-center gap-1.5 text-xs text-text-muted bg-deep-800/80 border border-surface-600/20 rounded-lg px-3 py-1.5 hover:border-accent-blue/30 hover:text-text-primary transition-all"
            >
              <span>{currentMode.icon}</span>
              <span>{currentMode.label}</span>
              <FiChevronDown size={12} className={`transition-transform ${dropdownOpen ? 'rotate-180' : ''}`} />
            </button>
            {dropdownOpen && (
              <div className="absolute top-full left-0 mt-1 w-52 bg-deep-800 rounded-xl border border-surface-600/40 shadow-xl z-50 overflow-hidden">
                {modes.map(m => (
                  <button
                    key={m.value}
                    onClick={() => { setMode(m.value); setDropdownOpen(false) }}
                    className={`w-full flex items-center gap-2 px-3 py-2 text-sm text-left transition-colors ${
                      mode === m.value
                        ? 'text-accent-blue bg-accent-blue/10'
                        : 'text-text-secondary hover:bg-deep-700/50 hover:text-text-primary'
                    }`}
                  >
                    <span>{m.icon}</span>
                    <span>{m.label}</span>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

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
