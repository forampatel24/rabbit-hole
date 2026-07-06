import React, { useContext, useState, useEffect, useRef } from 'react'
import { GraphContext } from '../context/GraphContext'
import { FiEdit3, FiSave } from 'react-icons/fi'

export default function NotesSection() {
  const { overview, savedGraphId, notes, saveNotes } = useContext(GraphContext)
  const [localNotes, setLocalNotes] = useState(notes)
  const timerRef = useRef(null)

  useEffect(() => {
    setLocalNotes(notes)
  }, [notes, savedGraphId])

  const handleChange = (e) => {
    setLocalNotes(e.target.value)
    if (savedGraphId) {
      if (timerRef.current) clearTimeout(timerRef.current)
      timerRef.current = setTimeout(() => {
        saveNotes(e.target.value)
      }, 1000)
    }
  }

  if (!overview) return null

  return (
    <div className="glass-card rounded-2xl p-5 animate-fadeIn">
      <div className="flex items-center gap-2 mb-3">
        <FiEdit3 className="text-accent-purple text-sm" />
        <h4 className="text-sm font-semibold text-text-primary">Notes</h4>
        {!savedGraphId && (
          <span className="text-xs text-text-muted ml-auto">Save graph to persist notes</span>
        )}
      </div>
      <textarea
        value={localNotes}
        onChange={handleChange}
        placeholder="Write your notes here..."
        className="w-full h-28 px-3.5 py-2.5 rounded-xl bg-deep-800 border border-surface-600/30 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/20 transition-all resize-none"
      />
    </div>
  )
}
