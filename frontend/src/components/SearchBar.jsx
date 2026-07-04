import React, { useState, useContext } from 'react'
import { GraphContext } from '../context/GraphContext'
import { FiSearch } from 'react-icons/fi'

export default function SearchBar() {
  const [value, setValue] = useState('')
  const { generateGraph, loading, error, setError } = useContext(GraphContext)

  const handleSubmit = () => {
    if (!value.trim()) return
    setError(null)
    generateGraph(value.trim())
  }

  return (
    <div className="animate-fadeIn">
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
