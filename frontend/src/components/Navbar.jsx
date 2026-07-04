import React from 'react'
import { FiHexagon } from 'react-icons/fi'

export default function Navbar() {
  return (
    <nav className="w-full border-b border-surface-700/30 bg-deep-900/80 backdrop-blur-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center gap-3">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
            <FiHexagon className="text-white text-sm" />
          </div>
          <span className="text-lg font-semibold tracking-tight text-text-primary">RabbitHole</span>
        </div>
        <div className="ml-auto flex items-center gap-2">
          <span className="text-xs text-text-muted bg-deep-700/50 px-2.5 py-1 rounded-full border border-surface-700/20">
            Explore
          </span>
        </div>
      </div>
    </nav>
  )
}
