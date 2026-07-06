import React, { useContext, useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { GraphContext } from '../context/GraphContext'
import api from '../services/api'
import { FiHexagon, FiClock, FiBarChart2, FiBook, FiExternalLink, FiTrash2, FiUser, FiMail, FiCalendar } from 'react-icons/fi'

export default function ProfilePage() {
  const { user, logout } = useContext(AuthContext)
  const { loadSavedGraph, deleteGraph } = useContext(GraphContext)
  const navigate = useNavigate()
  const [graphs, setGraphs] = useState([])
  const [loadingGraphs, setLoadingGraphs] = useState(true)

  useEffect(() => {
    api.get('/graphs/list')
      .then(res => setGraphs(res.data))
      .catch(err => console.error(err))
      .finally(() => setLoadingGraphs(false))
  }, [])

  const handleOpenGraph = async (graph) => {
    await loadSavedGraph(graph.id)
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-deep-900 text-text-primary">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-4">
          <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors">
            <span>&larr;</span> Back to Home
          </Link>
        </div>
        <div className="glass-card rounded-2xl p-6 mb-8">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
              <FiUser className="text-white text-xl" />
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-bold">{user?.username || 'Profile'}</h1>
              <div className="flex items-center gap-4 mt-1 text-sm text-text-muted">
                <span className="flex items-center gap-1.5">
                  <FiMail size={14} />
                  {user?.email}
                </span>
                <span className="flex items-center gap-1.5">
                  <FiCalendar size={14} />
                  Joined {user?.created_at ? new Date(user.created_at).toLocaleDateString() : ''}
                </span>
              </div>
            </div>
            <button
              onClick={logout}
              className="px-4 py-2 rounded-lg bg-deep-700 border border-surface-600/30 text-text-secondary text-sm hover:bg-deep-600 transition-colors"
            >
              Sign Out
            </button>
          </div>
        </div>

        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FiBook className="text-accent-blue" />
          Saved Graphs
        </h2>

        {loadingGraphs ? (
          <div className="text-text-muted text-sm">Loading saved graphs...</div>
        ) : graphs.length === 0 ? (
          <div className="glass-card rounded-2xl p-8 text-center">
            <FiBarChart2 className="text-text-muted text-3xl mx-auto mb-3" />
            <p className="text-text-muted text-sm">No saved graphs yet</p>
            <Link to="/" className="inline-block mt-3 px-4 py-2 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-sm font-medium hover:opacity-90 transition-opacity">
              Explore a Topic
            </Link>
          </div>
        ) : (
          <div className="space-y-3">
            {graphs.map(g => {
              const pct = g.total_count > 0 ? Math.round((g.completed_count / g.total_count) * 100) : 0
              return (
                <div key={g.id} className="glass-card rounded-2xl p-5 flex items-center gap-4">
                  <div className="w-10 h-10 rounded-lg bg-accent-blue/10 flex items-center justify-center shrink-0">
                    <FiBook className="text-accent-blue" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold text-text-primary truncate">{g.topic}</h3>
                    <div className="flex items-center gap-3 mt-1 text-xs text-text-muted">
                      <span className="flex items-center gap-1">
                        <FiClock size={12} />
                        Saved {new Date(g.created_at).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1">
                        <FiBarChart2 size={12} />
                        {g.completed_count} / {g.total_count} concepts
                      </span>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="text-right">
                      <div className="text-sm font-medium text-accent-green">{pct}%</div>
                      <div className="w-20 h-1.5 bg-deep-700 rounded-full mt-1 overflow-hidden">
                        <div className="h-full bg-gradient-to-r from-accent-blue to-accent-green rounded-full transition-all" style={{ width: `${pct}%` }} />
                      </div>
                    </div>
                    <button
                      onClick={() => handleOpenGraph(g)}
                      className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-xs font-medium hover:opacity-90 transition-opacity flex items-center gap-1"
                    >
                      <FiExternalLink size={12} />
                      Open
                    </button>
                    <button
                      onClick={async () => {
                        if (confirm('Delete this saved graph?')) {
                          await deleteGraph(g.id)
                          setGraphs(prev => prev.filter(x => x.id !== g.id))
                        }
                      }}
                      className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors flex items-center gap-1"
                    >
                      <FiTrash2 size={12} />
                      Delete
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
