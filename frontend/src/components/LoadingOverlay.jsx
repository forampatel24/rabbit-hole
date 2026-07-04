import React, { useContext, useState, useEffect } from 'react'
import { GraphContext } from '../context/GraphContext'

const messages = [
  'Building your knowledge universe...',
  'Analyzing concepts...',
  'Finding dependencies...',
  'Connecting ideas...',
  'Structuring knowledge...',
  'Almost there...',
]

export default function LoadingOverlay() {
  const { loading } = useContext(GraphContext)
  const [msgIndex, setMsgIndex] = useState(0)

  useEffect(() => {
    if (!loading) {
      setMsgIndex(0)
      return
    }
    const interval = setInterval(() => {
      setMsgIndex(i => Math.min(i + 1, messages.length - 1))
    }, 2000)
    return () => clearInterval(interval)
  }, [loading])

  if (!loading) return null

  return (
    <div className="fixed inset-0 z-40 flex items-center justify-center bg-deep-900/60 backdrop-blur-sm">
      <div className="glass-card rounded-2xl px-8 py-6 flex flex-col items-center gap-4 min-w-[300px]">
        <div className="relative w-12 h-12">
          <div className="absolute inset-0 rounded-full border-2 border-surface-600/30" />
          <div className="absolute inset-0 rounded-full border-2 border-transparent border-t-accent-blue animate-spin" />
          <div className="absolute inset-2 rounded-full bg-gradient-to-br from-accent-blue/20 to-accent-purple/20 animate-pulse" />
        </div>
        <p className="text-text-secondary text-sm animate-fadeIn" key={msgIndex}>
          {messages[msgIndex]}
        </p>
      </div>
    </div>
  )
}
