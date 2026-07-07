import React, { useState, useContext, useRef, useEffect } from 'react'
import { GraphContext } from '../context/GraphContext'
import { FiSearch, FiChevronDown } from 'react-icons/fi'

const modes = [
  { value: 'learn', label: 'Learn', icon: '📚' },
  { value: 'interview', label: 'Interview Preparation', icon: '💼' },
  { value: 'project', label: 'Project Building', icon: '🛠' },
  { value: 'research', label: 'Research', icon: '🔬' },
  { value: 'quick', label: 'Quick Overview', icon: '⚡' },
]

export default function SearchBar() {
  const [value, setValue] = useState('')
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const { generateGraph, loading, error, setError, mode, setMode } = useContext(GraphContext)
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

  const handleSubmit = () => {
    if (!value.trim()) return
    setError(null)
    generateGraph(value.trim(), mode)
  }

  return (
      <div className="animate-fadeIn space-y-2">
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

      <div className="relative">
        <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" />
        <input
          className="w-full pl-11 pr-32 py-3 rounded-xl bg-deep-800 border border-surface-600/30 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/20 transition-all duration-200"
          placeholder="Search any topic..."
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSubmit()}
        />
        <div className="absolute right-2 top-1/2 -translate-y-1/2 flex gap-2">
          <button
            onClick={handleSubmit}
            disabled={loading || !value.trim()}
            className="px-4 py-1.5 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
          >
            {loading ? '...' : 'Explore'}
          </button>
        </div>
      </div>
      {error && (
        <div className="mt-2 text-sm text-accent-red bg-accent-red/10 border border-accent-red/20 rounded-lg px-4 py-2">
          {error}
        </div>
      )}
    </div>
  )
}
