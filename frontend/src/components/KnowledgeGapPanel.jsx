import React, { useContext, useState } from 'react'
import { GraphContext } from '../context/GraphContext'

export default function KnowledgeGapPanel() {
  const { analyzeKnowledgeGap, gapResult } = useContext(GraphContext)
  const [knownText, setKnownText] = useState('')
  const [target, setTarget] = useState('')

  const handleAnalyze = () => {
    if (!target.trim()) return
    const known = knownText.split(',').map(s => s.trim()).filter(Boolean)
    analyzeKnowledgeGap(known, target.trim())
  }

  return (
    <div className="p-4 bg-[#071027] text-[#F8FAFC] rounded mt-4">
      <h4 className="font-semibold text-sm uppercase tracking-wide text-[#94A3B8]">Knowledge Gap Analysis</h4>

      <div className="mt-3 space-y-2">
        <input
          placeholder="Known concepts (comma separated)"
          value={knownText}
          onChange={e => setKnownText(e.target.value)}
          className="w-full p-2 bg-[#0B1220] border border-[#23303F] rounded text-[#F8FAFC] text-sm placeholder-[#475569]"
        />
        <input
          placeholder="Target topic"
          value={target}
          onChange={e => setTarget(e.target.value)}
          className="w-full p-2 bg-[#0B1220] border border-[#23303F] rounded text-[#F8FAFC] text-sm placeholder-[#475569]"
        />
        <button
          onClick={handleAnalyze}
          className="w-full px-3 py-2 bg-[#8B5CF6] text-black font-medium rounded text-sm hover:bg-[#7C3AED] transition-colors"
        >
          Analyze Gap
        </button>
      </div>

      {gapResult && (
        <div className="mt-4 space-y-3 text-sm">
          <div>
            <h5 className="text-[#94A3B8] text-xs uppercase tracking-wide mb-1">Goal: {gapResult.learning_path?.slice(-1)[0] || target}</h5>
          </div>

          {gapResult.known?.length > 0 && (
            <div>
              <h5 className="text-[#10B981] text-xs uppercase tracking-wide mb-1">Known</h5>
              <ul className="space-y-1">
                {gapResult.known.map((k, i) => (
                  <li key={i} className="text-[#10B981]">✓ {k}</li>
                ))}
              </ul>
            </div>
          )}

          {gapResult.missing?.length > 0 && (
            <div>
              <h5 className="text-[#EF4444] text-xs uppercase tracking-wide mb-1">Missing</h5>
              <ul className="space-y-1">
                {gapResult.missing.map((m, i) => (
                  <li key={i} className="text-[#EF4444]">✗ {m}</li>
                ))}
              </ul>
            </div>
          )}

          {gapResult.learning_path?.length > 0 && (
            <div>
              <h5 className="text-[#F59E0B] text-xs uppercase tracking-wide mb-1">Learning Path</h5>
              <div className="flex flex-col items-start gap-1">
                {gapResult.learning_path.map((step, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="text-[#F59E0B]">{i + 1}.</span>
                    <span className="text-[#F8FAFC]">{step}</span>
                    {i < gapResult.learning_path.length - 1 && (
                      <span className="text-[#475569]">↓</span>
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
