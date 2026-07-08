import React, { useContext, useEffect } from 'react'
import { GraphContext } from '../context/GraphContext'
import { AuthContext } from '../context/AuthContext'
import LearningHub from './LearningHub'
import {
  FiX, FiBook, FiBarChart2, FiClock, FiStar,
  FiArrowRight, FiGrid, FiHeart,
  FiChevronRight, FiZap, FiLayers, FiCheckCircle, FiCircle,
  FiHelpCircle, FiTool, FiThumbsUp, FiThumbsDown,
  FiTerminal, FiAlertTriangle
} from 'react-icons/fi'

const difficultyColors = {
  Beginner: 'text-accent-green bg-accent-green/10',
  Intermediate: 'text-accent-yellow bg-accent-yellow/10',
  Advanced: 'text-accent-red bg-accent-red/10',
}

export default function NodePanel() {
  const { selectedNodeId, nodeDetails, closePanel, expandNode, savedGraphId, completions, toggleCompletion, fetchResources, resources, resourceLoading } = useContext(GraphContext)
  const { user } = useContext(AuthContext)

  useEffect(() => {
    if (selectedNodeId && nodeDetails[selectedNodeId]?.name) {
      fetchResources(nodeDetails[selectedNodeId].name)
    }
  }, [selectedNodeId])

  if (!selectedNodeId) return null
  const node = nodeDetails[selectedNodeId]
  if (!node) return null

  const badgeColor = difficultyColors[node.difficulty] || difficultyColors.Intermediate
  const isCompleted = completions?.[selectedNodeId] || false

  return (
    <div className="glass-card rounded-2xl h-full overflow-hidden flex flex-col">
      <div className="p-5 border-b border-surface-700/20">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-bold text-text-primary tracking-tight truncate">{node.name}</h3>
            <div className="flex items-center gap-2 mt-1.5">
              <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeColor}`}>
                {node.difficulty}
              </span>
              <span className="text-xs text-text-muted">
                <FiStar className="inline mr-0.5 text-accent-yellow" />
                {node.importance_score}/10
              </span>
            </div>
          </div>
          <button onClick={closePanel} className="p-1.5 rounded-lg hover:bg-surface-700/30 text-text-muted hover:text-text-primary transition-colors">
            <FiX size={16} />
          </button>
        </div>

        {savedGraphId && user && (
          <button
            onClick={() => toggleCompletion(selectedNodeId)}
            className={`mt-3 w-full px-3 py-2 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-all ${
              isCompleted
                ? 'bg-accent-green/10 text-accent-green border border-accent-green/30'
                : 'bg-deep-700/50 text-text-muted border border-surface-600/20 hover:border-accent-green/30 hover:text-accent-green'
            }`}
          >
            {isCompleted ? (
              <><FiCheckCircle size={14} /> Completed</>
            ) : (
              <><FiCircle size={14} /> Mark as Completed</>
            )}
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        <Section icon={FiBook} title="Overview">
          <p className="text-sm text-text-secondary leading-relaxed">{node.description}</p>
          <div className="flex items-center gap-2 mt-2 text-xs text-text-muted">
            <FiClock className="shrink-0" />
            <span>{node.estimated_learning_time}</span>
          </div>
        </Section>

        {node.prerequisites?.length > 0 && (
          <Section icon={FiArrowRight} title="Prerequisites" accent="text-accent-yellow">
            <ul className="space-y-1.5">
              {node.prerequisites.map((p, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-text-secondary">
                  <FiChevronRight className="text-accent-yellow shrink-0 text-xs" />
                  {p}
                </li>
              ))}
            </ul>
          </Section>
        )}

        {node.unlocks?.length > 0 && (
          <Section icon={FiZap} title="Unlocks" accent="text-accent-green">
            <ul className="space-y-1.5">
              {node.unlocks.map((u, i) => (
                <li key={i} className="flex items-center gap-2 text-sm text-text-secondary">
                  <FiChevronRight className="text-accent-green shrink-0 text-xs" />
                  {u}
                </li>
              ))}
            </ul>
          </Section>
        )}

        {node.applications?.length > 0 && (
          <Section icon={FiGrid} title="Applications" accent="text-accent-blue">
            <div className="flex flex-wrap gap-1.5">
              {node.applications.map((a, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-accent-blue/10 text-accent-blue border border-accent-blue/20">
                  {a}
                </span>
              ))}
            </div>
          </Section>
        )}

        {node.why_it_matters && (
          <Section icon={FiHeart} title="Why It Matters" accent="text-accent-pink">
            <p className="text-sm text-text-secondary leading-relaxed">{node.why_it_matters}</p>
          </Section>
        )}

        {node.resources?.interview_questions?.length > 0 && (
          <Section icon={FiHelpCircle} title="Interview Questions" accent="text-accent-yellow">
            <ul className="space-y-2">
              {node.resources.interview_questions.map((q, i) => (
                <li key={i} className="text-sm text-text-secondary bg-deep-800/50 rounded-lg p-2.5 border border-surface-600/10">
                  <span className="text-accent-yellow font-medium">Q{i + 1}: </span>
                  {q}
                </li>
              ))}
            </ul>
          </Section>
        )}

        {node.resources?.technology_alternatives?.length > 0 && (
          <Section icon={FiTool} title="Technology Alternatives" accent="text-accent-blue">
            <div className="space-y-2">
              {node.resources.technology_alternatives.map((alt, i) => (
                <div key={i} className="text-sm bg-deep-800/50 rounded-lg p-3 border border-surface-600/10">
                  <div className="font-medium text-text-primary mb-1">{alt.name}</div>
                  {alt.pros?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-1">
                      {alt.pros.map((p, j) => (
                        <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-accent-green/10 text-accent-green flex items-center gap-0.5">
                          <FiThumbsUp size={10} />{p}
                        </span>
                      ))}
                    </div>
                  )}
                  {alt.cons?.length > 0 && (
                    <div className="flex flex-wrap gap-1 mb-1">
                      {alt.cons.map((c, j) => (
                        <span key={j} className="text-xs px-1.5 py-0.5 rounded bg-accent-red/10 text-accent-red flex items-center gap-0.5">
                          <FiThumbsDown size={10} />{c}
                        </span>
                      ))}
                    </div>
                  )}
                  {alt.best_for && (
                    <div className="text-xs text-text-muted mt-1">
                      Best for: <span className="text-accent-blue">{alt.best_for}</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Section>
        )}

        {node.resources?.key_papers?.length > 0 && (
          <Section icon={FiBook} title="Key Papers" accent="text-accent-purple">
            <div className="space-y-2">
              {node.resources.key_papers.map((paper, i) => (
                <div key={i} className="text-sm bg-deep-800/50 rounded-lg p-3 border border-surface-600/10">
                  <div className="font-medium text-text-primary">{paper.title}</div>
                  {paper.authors?.length > 0 && (
                    <div className="text-xs text-text-muted mt-0.5">{paper.authors.join(', ')}</div>
                  )}
                  <div className="flex items-center gap-2 mt-1 text-xs text-text-muted">
                    {paper.year && <span>{paper.year}</span>}
                    {paper.venue && <span className="text-accent-blue">{paper.venue}</span>}
                    {paper.impact && <span className="text-accent-yellow">Impact: {paper.impact}</span>}
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )}

        {node.resources?.execution_guide && (
          <Section icon={FiTerminal} title="Execution Guide" accent="text-accent-green">
            <div className="space-y-2">
              {node.resources.execution_guide.languages?.length > 0 && (
                <div>
                  <div className="text-xs text-text-muted mb-1">Languages:</div>
                  <div className="flex flex-wrap gap-1">
                    {node.resources.execution_guide.languages.map((lang, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded bg-accent-blue/10 text-accent-blue border border-accent-blue/20">{lang}</span>
                    ))}
                  </div>
                </div>
              )}
              {node.resources.execution_guide.frameworks?.length > 0 && (
                <div>
                  <div className="text-xs text-text-muted mb-1">Frameworks:</div>
                  <div className="flex flex-wrap gap-1">
                    {node.resources.execution_guide.frameworks.map((fw, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded bg-accent-purple/10 text-accent-purple border border-accent-purple/20">{fw}</span>
                    ))}
                  </div>
                </div>
              )}
              {node.resources.execution_guide.tools?.length > 0 && (
                <div>
                  <div className="text-xs text-text-muted mb-1">Tools:</div>
                  <div className="flex flex-wrap gap-1">
                    {node.resources.execution_guide.tools.map((t, i) => (
                      <span key={i} className="text-xs px-2 py-0.5 rounded bg-accent-yellow/10 text-accent-yellow border border-accent-yellow/20">{t}</span>
                    ))}
                  </div>
                </div>
              )}
              {node.resources.execution_guide.setup_commands && (
                <div>
                  <div className="text-xs text-text-muted mb-1">Setup Commands:</div>
                  <pre className="text-xs bg-deep-900/80 rounded-lg p-2.5 text-accent-green font-mono overflow-x-auto border border-surface-600/10">{node.resources.execution_guide.setup_commands}</pre>
                </div>
              )}
              {node.resources.execution_guide.how_to_execute && (
                <div>
                  <div className="text-xs text-text-muted mb-1">How to Execute:</div>
                  <p className="text-sm text-text-secondary leading-relaxed">{node.resources.execution_guide.how_to_execute}</p>
                </div>
              )}
              {node.resources.execution_guide.code_snippet && (
                <div>
                  <div className="text-xs text-text-muted mb-1">Code Snippet:</div>
                  <pre className="text-xs bg-deep-900/80 rounded-lg p-2.5 text-accent-blue font-mono overflow-x-auto border border-surface-600/10 whitespace-pre-wrap">{node.resources.execution_guide.code_snippet}</pre>
                </div>
              )}
              {node.resources.execution_guide.common_mistakes?.length > 0 && (
                <div>
                  <div className="text-xs text-text-muted mb-1">Common Mistakes:</div>
                  <ul className="space-y-1">
                    {node.resources.execution_guide.common_mistakes.map((m, i) => (
                      <li key={i} className="flex items-start gap-1.5 text-sm text-text-secondary">
                        <FiAlertTriangle className="text-accent-red shrink-0 mt-0.5" size={12} />
                        {m}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {node.resources.execution_guide.verification && (
                <div>
                  <div className="text-xs text-text-muted mb-1">Verification:</div>
                  <p className="text-sm text-accent-green">{node.resources.execution_guide.verification}</p>
                </div>
              )}
            </div>
          </Section>
        )}

        {node.resources?.key_researchers?.length > 0 && (
          <Section icon={FiUsers} title="Key Researchers" accent="text-accent-blue">
            <div className="flex flex-wrap gap-1.5">
              {node.resources.key_researchers.map((r, i) => (
                <span key={i} className="text-xs px-2.5 py-1 rounded-full bg-accent-blue/10 text-accent-blue border border-accent-blue/20">{r}</span>
              ))}
            </div>
          </Section>
        )}

        {resourceLoading[node.name] && (
          <div className="flex items-center gap-2 text-xs text-text-muted py-2">
            <div className="w-3 h-3 border-2 border-accent-blue border-t-transparent rounded-full animate-spin" />
            Loading learning resources...
          </div>
        )}

        {resources[node.name] && !resourceLoading[node.name] && (
          <LearningHub resources={resources[node.name]} />
        )}
      </div>

      <div className="p-4 border-t border-surface-700/20 space-y-2">
        <button
          onClick={() => expandNode(node.id)}
          className="w-full px-4 py-2.5 rounded-xl bg-gradient-to-r from-accent-blue to-accent-purple text-white text-sm font-medium hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
        >
          <FiLayers />
          Expand Concept
        </button>
      </div>
    </div>
  )
}

function Section({ icon: Icon, title, children, accent = 'text-text-muted' }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-2">
        <Icon className={`${accent} text-sm`} />
        <h4 className="text-xs font-semibold uppercase tracking-wider text-text-muted">{title}</h4>
      </div>
      {children}
    </div>
  )
}
