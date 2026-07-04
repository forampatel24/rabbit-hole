import React, { useState, useContext } from 'react'
import { GraphContext } from '../context/GraphContext'

export default function SearchBar() {
  const [value, setValue] = useState('')
  const { generateGraph, loading, error, setError } = useContext(GraphContext)

  const handleSubmit = () => {
    if (!value.trim()) return
    setError(null)
    generateGraph(value.trim())
  }

  return (
    <div>
      <div className="p-4 flex gap-2">
        <input
          className="flex-1 p-2 rounded bg-[#0B1220] text-[#F8FAFC] border border-[#23303F] placeholder-[#475569]"
          placeholder="Enter topic e.g. Transformers"
          value={value}
          onChange={e => setValue(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSubmit()}
        />
        <button
          className="px-4 py-2 rounded bg-[#3B82F6] text-black font-medium hover:bg-[#2563EB] transition-colors disabled:opacity-50"
          onClick={handleSubmit}
          disabled={loading || !value.trim()}
        >
          {loading ? 'Generating...' : 'Generate Map'}
        </button>
      </div>
      {loading && (
        <div className="px-4 pb-2 text-[#94A3B8] text-sm">Generating Knowledge Universe...</div>
      )}
      {error && (
        <div className="px-4 pb-2 text-[#EF4444] text-sm">{error}</div>
      )}
    </div>
  )
}
