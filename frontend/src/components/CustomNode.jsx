import React, { memo } from 'react'
import { Handle, Position } from 'reactflow'
import {
  FiBook, FiCpu, FiZap, FiGrid, FiTool,
  FiLayers, FiHash, FiBox, FiCheckCircle,
  FiFile, FiAward, FiCompass, FiTarget,
  FiFlag, FiCloud, FiCode, FiServer,
  FiUsers, FiStar, FiAlertTriangle, FiTrendingUp,
  FiDatabase, FiChevronRight
} from 'react-icons/fi'

const nodeTypeConfig = {
  // Shared
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
  application_area: {
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
  related_field: {
    icon: FiBox,
    color: '#64748B',
    label: 'Related',
  },
  concept: {
    icon: FiBook,
    color: '#64748B',
    label: 'Concept',
  },

  // Research mode
  foundation: {
    icon: FiLayers,
    color: '#3B82F6',
    label: 'Foundation',
  },
  seminal_paper: {
    icon: FiFile,
    color: '#8B5CF6',
    label: 'Seminal Paper',
  },
  state_of_art: {
    icon: FiAward,
    color: '#F59E0B',
    label: 'SOTA',
  },
  recent_advance: {
    icon: FiZap,
    color: '#EC4899',
    label: 'Recent Advance',
  },
  research_direction: {
    icon: FiCompass,
    color: '#06B6D4',
    label: 'Research Direction',
  },
  open_problem: {
    icon: FiAlertTriangle,
    color: '#EF4444',
    label: 'Open Problem',
  },
  challenge: {
    icon: FiAlertTriangle,
    color: '#EF4444',
    label: 'Challenge',
  },
  methodology: {
    icon: FiLayers,
    color: '#10B981',
    label: 'Methodology',
  },
  benchmark: {
    icon: FiTrendingUp,
    color: '#F59E0B',
    label: 'Benchmark',
  },
  dataset: {
    icon: FiDatabase,
    color: '#3B82F6',
    label: 'Dataset',
  },
  research_group: {
    icon: FiUsers,
    color: '#64748B',
    label: 'Research Group',
  },
  emerging_trend: {
    icon: FiTrendingUp,
    color: '#EC4899',
    label: 'Emerging Trend',
  },

  // Interview mode
  must_know: {
    icon: FiStar,
    color: '#EF4444',
    label: 'Must Know',
  },
  frequently_asked: {
    icon: FiZap,
    color: '#F59E0B',
    label: 'Frequently Asked',
  },
  coding_pattern: {
    icon: FiCode,
    color: '#10B981',
    label: 'Coding Pattern',
  },
  system_design_fundamental: {
    icon: FiServer,
    color: '#8B5CF6',
    label: 'System Design',
  },
  behavioral: {
    icon: FiUsers,
    color: '#3B82F6',
    label: 'Behavioral',
  },
  optimization_tip: {
    icon: FiTrendingUp,
    color: '#06B6D4',
    label: 'Optimization Tip',
  },
  common_pitfall: {
    icon: FiAlertTriangle,
    color: '#EF4444',
    label: 'Common Pitfall',
  },

  // Project mode
  goal: {
    icon: FiTarget,
    color: '#EF4444',
    label: 'Goal',
  },
  phase: {
    icon: FiLayers,
    color: '#8B5CF6',
    label: 'Phase',
  },
  step: {
    icon: FiChevronRight,
    color: '#10B981',
    label: 'Step',
  },
  technology_option: {
    icon: FiTool,
    color: '#06B6D4',
    label: 'Tech Option',
  },
  tool_alternative: {
    icon: FiTool,
    color: '#F59E0B',
    label: 'Alternative',
  },
  milestone: {
    icon: FiFlag,
    color: '#10B981',
    label: 'Milestone',
  },
  deployment_option: {
    icon: FiCloud,
    color: '#3B82F6',
    label: 'Deployment',
  },
  database: {
    icon: FiDatabase,
    color: '#EC4899',
    label: 'Database',
  },
  api_service: {
    icon: FiServer,
    color: '#F59E0B',
    label: 'API Service',
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
  const completed = data.completed

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
            : completed
              ? 'border-accent-green/50'
              : 'border-transparent hover:border-surface-600/40'
        }`}
        style={{
          background: completed
            ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(11, 18, 37, 0.95))'
            : 'linear-gradient(135deg, rgba(15, 26, 48, 0.95), rgba(11, 18, 37, 0.95))',
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
          {completed && (
            <FiCheckCircle className="text-accent-green shrink-0" size={14} />
          )}
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
