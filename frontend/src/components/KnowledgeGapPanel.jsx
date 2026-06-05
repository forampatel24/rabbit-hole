import React, {useContext, useState} from 'react'
import { GraphContext } from '../context/GraphContext'

export default function KnowledgeGapPanel(){
  const { analyzeKnowledgeGap, gapResult } = useContext(GraphContext)
  const [knownText, setKnownText] = useState('')
  const [target, setTarget] = useState('')
  return (
    <div className="p-4 bg-[#071027] text-[#F8FAFC] rounded mt-4">
      <h4 className="font-semibold">Knowledge Gap</h4>
      <div className="mt-2 flex gap-2">
        <input placeholder="Known concepts comma separated" value={knownText} onChange={e=>setKnownText(e.target.value)} className="flex-1 p-2 bg-[#0B1220] border border-[#23303F] rounded text-[#F8FAFC]" />
        <input placeholder="Target topic" value={target} onChange={e=>setTarget(e.target.value)} className="w-48 p-2 bg-[#0B1220] border border-[#23303F] rounded text-[#F8FAFC]" />
        <button className="px-3 py-2 bg-[#8B5CF6] text-black rounded" onClick={()=>analyzeKnowledgeGap(knownText.split(',').map(s=>s.trim()).filter(Boolean), target)}>Analyze</button>
      </div>
      {gapResult && (
        <div className="mt-3 text-sm text-[#94A3B8]">
          <div><strong>Known:</strong> {gapResult.known.join(', ')}</div>
          <div className="mt-2"><strong>Missing:</strong> {gapResult.missing.join(', ')}</div>
          <div className="mt-2"><strong>Learning Path:</strong> {gapResult.learning_path.join(' ↓ ')}</div>
        </div>
      )}
    </div>
  )
}
