import React, { memo } from 'react'
import { Handle, Position } from 'reactflow'
import {
  FiBook, FiCpu, FiZap, FiGrid, FiTool,
  FiLayers, FiHash, FiBox
} from 'react-icons/fi'

const nodeTypeConfig = {
  prerequisite: {
    icon: FiBook,
    color: '#3B82F6',
    label: 'Prerequisite',
  },
  core_concept: {
    icon: FiCpu,
    color: '#10B981',
    label: 'Core',
  },
  advanced_concept: {
    icon: FiZap,
    color: '#8B5CF6',
    label: 'Advanced',
  },
  application: {
    icon: FiGrid,
    color: '#F59E0B',
    label: 'Application',
  },
  framework: {
    icon: FiLayers,
    color: '#EF4444',
    label: 'Framework',
  },
  tool: {
    icon: FiTool,
    color: '#06B6D4',
    label: 'Tool',
  },
  mathematical_foundation: {
    icon: FiHash,
    color: '#EC4899',
    label: 'Math',
  },
  related_concept: {
    icon: FiBox,
    color: '#64748B',
    label: 'Related',
  },
}

const difficultyBadges = {
  Beginner: 'bg-accent-green/20 text-accent-green',
  Intermediate: 'bg-accent-yellow/20 text-accent-yellow',
  Advanced: 'bg-accent-red/20 text-accent-red',
}

function CustomNode({ data, selected }) {
  const config = nodeTypeConfig[data.nodeType] || nodeTypeConfig.related_concept
  const Icon = config.icon
  const badgeColor = difficultyBadges[data.difficulty] || difficultyBadges.Intermediate

  return (
    <div
      className={`relative transition-all duration-200 ${
        selected ? 'scale-105' : 'hover:scale-102'
      }`}
      style={{ filter: selected ? 'drop-shadow(0 0 12px rgba(139, 92, 246, 0.4))' : 'none' }}
    >
      <Handle type="target" position={Position.Top} className="!bg-surface-500 !w-2 !h-2 !border-2 !border-deep-900" />

      <div
        className={`rounded-xl border-2 transition-all duration-200 min-w-[140px] ${
          selected
            ? 'border-accent-purple shadow-lg shadow-accent-purple/20'
            : 'border-transparent hover:border-surface-600/40'
        }`}
        style={{
          background: 'linear-gradient(135deg, rgba(15, 26, 48, 0.95), rgba(11, 18, 37, 0.95))',
        }}
      >
        <div className="flex items-center gap-2 px-3 pt-2.5 pb-1.5">
          <div
            className="w-6 h-6 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: `${config.color}20` }}
          >
            <Icon style={{ color: config.color, fontSize: '12px' }} />
          </div>
          <span className="text-sm font-semibold text-text-primary leading-tight">{data.label}</span>
        </div>

        <div className="flex items-center gap-1.5 px-3 pb-2.5">
          <span
            className="text-[10px] px-1.5 py-0.5 rounded font-medium"
            style={{ backgroundColor: `${config.color}15`, color: config.color }}
          >
            {config.label}
          </span>
          {data.difficulty && (
            <span className={`text-[10px] px-1.5 py-0.5 rounded font-medium ${badgeColor}`}>
              {data.difficulty}
            </span>
          )}
        </div>
      </div>

      <Handle type="source" position={Position.Bottom} className="!bg-surface-500 !w-2 !h-2 !border-2 !border-deep-900" />
    </div>
  )
}

export default memo(CustomNode)
