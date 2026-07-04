import React, { useContext, useState } from 'react'
import { GraphContext } from '../context/GraphContext'
import { FiSearch, FiCheck, FiX, FiArrowDown } from 'react-icons/fi'

export default function KnowledgeGapPanel() {
  const { analyzeKnowledgeGap, gapResult, loading } = useContext(GraphContext)
  const [knownText, setKnownText] = useState('')
  const [target, setTarget] = useState('')

  const handleAnalyze = () => {
    if (!target.trim()) return
    const known = knownText.split(',').map(s => s.trim()).filter(Boolean)
    analyzeKnowledgeGap(known, target.trim())
  }

  return (
    <div className="glass-card rounded-2xl p-5 animate-fadeIn">
      <div className="flex items-center gap-2 mb-4">
        <FiSearch className="text-accent-purple text-sm" />
        <h4 className="text-sm font-semibold text-text-primary">Knowledge Gap Analysis</h4>
      </div>

      <div className="space-y-2.5">
        <input
          placeholder="Known concepts (comma separated)"
          value={knownText}
          onChange={e => setKnownText(e.target.value)}
          className="w-full px-3.5 py-2.5 rounded-xl bg-deep-800 border border-surface-600/30 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/20 transition-all"
        />
        <input
          placeholder="Target topic"
          value={target}
          onChange={e => setTarget(e.target.value)}
          className="w-full px-3.5 py-2.5 rounded-xl bg-deep-800 border border-surface-600/30 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/20 transition-all"
        />
        <button
          onClick={handleAnalyze}
          disabled={loading || !target.trim()}
          className="w-full px-4 py-2.5 rounded-xl bg-gradient-to-r from-accent-purple to-accent-pink text-white text-sm font-medium hover:opacity-90 transition-opacity disabled:opacity-40"
        >
          {loading ? 'Analyzing...' : 'Analyze Gap'}
        </button>
      </div>

      {gapResult && (
        <div className="mt-5 space-y-4">
          {gapResult.known?.length > 0 && (
            <div>
              <h5 className="text-xs font-semibold uppercase tracking-wider text-accent-green mb-2 flex items-center gap-1.5">
                <FiCheck /> Known
              </h5>
              <div className="space-y-1">
                {gapResult.known.map((k, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-accent-green bg-accent-green/5 rounded-lg px-3 py-1.5">
                    <FiCheck className="shrink-0 text-xs" />
                    {k}
                  </div>
                ))}
              </div>
            </div>
          )}

          {gapResult.missing?.length > 0 && (
            <div>
              <h5 className="text-xs font-semibold uppercase tracking-wider text-accent-red mb-2 flex items-center gap-1.5">
                <FiX /> Missing
              </h5>
              <div className="space-y-1">
                {gapResult.missing.map((m, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm text-accent-red bg-accent-red/5 rounded-lg px-3 py-1.5">
                    <FiX className="shrink-0 text-xs" />
                    {m}
                  </div>
                ))}
              </div>
            </div>
          )}

          {gapResult.learning_path?.length > 0 && (
            <div>
              <h5 className="text-xs font-semibold uppercase tracking-wider text-accent-yellow mb-2">Learning Path</h5>
              <div className="flex flex-col items-start gap-0.5">
                {gapResult.learning_path.map((step, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="w-5 h-5 rounded-full bg-accent-yellow/15 text-accent-yellow text-xs font-medium flex items-center justify-center shrink-0">
                      {i + 1}
                    </span>
                    <span className="text-text-primary">{step}</span>
                    {i < gapResult.learning_path.length - 1 && (
                      <FiArrowDown className="text-text-muted text-xs ml-1" />
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
