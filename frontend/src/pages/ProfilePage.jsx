import React, { useContext, useState, useEffect, useCallback, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { AuthContext } from '../context/AuthContext'
import { GraphContext } from '../context/GraphContext'
import api from '../services/api'
import {
  FiHexagon, FiClock, FiBarChart2, FiBook, FiExternalLink, FiTrash2,
  FiUser, FiMail, FiCalendar, FiFolder, FiPlus, FiSearch,
  FiEdit2, FiCopy, FiMove, FiChevronLeft, FiX
} from 'react-icons/fi'

function useDebounce(value, delay) {
  const [debounced, setDebounced] = useState(value)
  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delay)
    return () => clearTimeout(timer)
  }, [value, delay])
  return debounced
}

export default function ProfilePage() {
  const { user, logout } = useContext(AuthContext)
  const { loadSavedGraph, deleteGraph } = useContext(GraphContext)
  const navigate = useNavigate()

  const [collections, setCollections] = useState([])
  const [selectedCollection, setSelectedCollection] = useState(null)
  const [collectionGraphs, setCollectionGraphs] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreate, setShowCreate] = useState(false)
  const [newName, setNewName] = useState('')
  const [renameId, setRenameId] = useState(null)
  const [renameName, setRenameName] = useState('')

  const [searchQuery, setSearchQuery] = useState('')
  const debouncedSearch = useDebounce(searchQuery, 300)
  const [searchResults, setSearchResults] = useState([])
  const [searching, setSearching] = useState(false)

  const [moveGraphId, setMoveGraphId] = useState(null)
  const [copyGraphId, setCopyGraphId] = useState(null)

  const loadCollections = useCallback(async () => {
    try {
      const res = await api.get('/collections')
      setCollections(res.data)
    } catch (err) {
      console.error(err)
    }
  }, [])

  useEffect(() => {
    setLoading(true)
    Promise.all([loadCollections()]).finally(() => setLoading(false))
  }, [loadCollections])

  useEffect(() => {
    if (!debouncedSearch.trim()) {
      setSearchResults([])
      setSearching(false)
      return
    }
    setSearching(true)
    api.get(`/collections/search/query?q=${encodeURIComponent(debouncedSearch)}`)
      .then(res => setSearchResults(res.data.results || []))
      .catch(err => console.error(err))
      .finally(() => setSearching(false))
  }, [debouncedSearch])

  const openCollection = async (col) => {
    try {
      const res = await api.get(`/collections/${col.id}`)
      setSelectedCollection(res.data)
      setCollectionGraphs(res.data.graphs || [])
    } catch (err) {
      console.error(err)
    }
  }

  const handleCreate = async () => {
    if (!newName.trim()) return
    try {
      await api.post('/collections', { name: newName.trim() })
      setNewName('')
      setShowCreate(false)
      await loadCollections()
    } catch (err) {
      console.error(err)
    }
  }

  const handleRename = async (id) => {
    if (!renameName.trim()) return
    try {
      await api.put(`/collections/${id}`, { name: renameName.trim() })
      setRenameId(null)
      setRenameName('')
      await loadCollections()
      if (selectedCollection?.id === id) {
        openCollection({ id })
      }
    } catch (err) {
      console.error(err)
    }
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this collection? Graphs will be unlinked but not deleted.')) return
    try {
      await api.delete(`/collections/${id}`)
      if (selectedCollection?.id === id) setSelectedCollection(null)
      await loadCollections()
    } catch (err) {
      console.error(err)
    }
  }

  const handleOpenGraph = async (graph) => {
    await loadSavedGraph(graph.id)
    navigate('/')
  }

  const handleMoveGraph = async (graphId, targetCollectionId) => {
    if (!selectedCollection) return
    try {
      await api.put(`/collections/${selectedCollection.id}/graphs/${graphId}/move`, {
        target_collection_id: targetCollectionId || null
      })
      setMoveGraphId(null)
      openCollection({ id: selectedCollection.id })
      await loadCollections()
    } catch (err) {
      console.error(err)
    }
  }

  const handleCopyGraph = async (graphId, targetCollectionId) => {
    if (!selectedCollection) return
    try {
      await api.put(`/collections/${selectedCollection.id}/graphs/${graphId}/copy`, {
        target_collection_id: targetCollectionId
      })
      setCopyGraphId(null)
      await loadCollections()
    } catch (err) {
      console.error(err)
    }
  }

  const handleRemoveFromCollection = async (graphId) => {
    if (!selectedCollection) return
    try {
      await api.put(`/collections/${selectedCollection.id}/graphs/${graphId}/remove`)
      openCollection({ id: selectedCollection.id })
      await loadCollections()
    } catch (err) {
      console.error(err)
    }
  }

  const handleDeleteGraph = async (graphId) => {
    if (!confirm('Delete this saved graph?')) return
    await deleteGraph(graphId)
    if (selectedCollection) {
      openCollection({ id: selectedCollection.id })
    }
    await loadCollections()
  }

  const otherCollections = collections.filter(c => c.id !== selectedCollection?.id)

  return (
    <div className="min-h-screen bg-deep-900 text-text-primary">
      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="mb-4">
          <Link to="/" className="inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text-primary transition-colors">
            <span>&larr;</span> Back to Home
          </Link>
        </div>

        <div className="glass-card rounded-2xl p-6 mb-6">
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
            <button onClick={logout} className="px-4 py-2 rounded-lg bg-deep-700 border border-surface-600/30 text-text-secondary text-sm hover:bg-deep-600 transition-colors">
              Sign Out
            </button>
          </div>
        </div>

        <div className="mb-6">
          <div className="relative">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" />
            <input
              className="w-full pl-11 pr-4 py-3 rounded-xl bg-deep-800 border border-surface-600/30 text-text-primary placeholder-text-muted text-sm focus:outline-none focus:border-accent-blue/50 focus:ring-1 focus:ring-accent-blue/20 transition-all"
              placeholder="Search saved graphs..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
            />
            {searching && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <div className="w-4 h-4 border-2 border-accent-blue border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
          {searchResults.length > 0 && (
            <div className="mt-2 glass rounded-xl border border-surface-600/20 overflow-hidden">
              {searchResults.map(g => (
                <button
                  key={g.id}
                  onClick={() => handleOpenGraph(g)}
                  className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-deep-700/50 transition-colors border-b border-surface-600/10 last:border-0"
                >
                  <FiBook className="text-accent-blue shrink-0" size={14} />
                  <div className="flex-1 min-w-0">
                    <span className="text-sm font-medium text-text-primary truncate block">{g.topic}</span>
                    {g.collection_name && (
                      <span className="text-xs text-text-muted">{g.collection_name}</span>
                    )}
                  </div>
                  <span className="text-xs text-text-muted shrink-0">
                    {g.completed_count}/{g.total_count}
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {selectedCollection ? (
          <div>
            <div className="flex items-center gap-3 mb-4">
              <button
                onClick={() => setSelectedCollection(null)}
                className="p-1.5 rounded-lg hover:bg-deep-700/50 text-text-muted hover:text-text-primary transition-colors"
              >
                <FiChevronLeft size={18} />
              </button>
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <FiFolder className="text-accent-blue" />
                {selectedCollection.name}
              </h2>
              <span className="text-xs text-text-muted">{collectionGraphs.length} graph{collectionGraphs.length !== 1 ? 's' : ''}</span>
            </div>

            {collectionGraphs.length === 0 ? (
              <div className="glass-card rounded-2xl p-8 text-center">
                <FiBook className="text-text-muted text-3xl mx-auto mb-3" />
                <p className="text-text-muted text-sm">No graphs in this collection</p>
              </div>
            ) : (
              <div className="space-y-3">
                {collectionGraphs.map(g => {
                  const pct = g.total_count > 0 ? Math.round((g.completed_count / g.total_count) * 100) : 0
                  return (
                    <div key={g.id} className="glass-card rounded-2xl p-5 flex items-center gap-4">
                      <div className="w-10 h-10 rounded-lg bg-accent-blue/10 flex items-center justify-center shrink-0">
                        <FiBook className="text-accent-blue" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-text-primary truncate">{g.topic}</h3>
                        <div className="flex items-center gap-3 mt-1 text-xs text-text-muted">
                          <span className="flex items-center gap-1"><FiClock size={12} /> Saved {new Date(g.created_at).toLocaleDateString()}</span>
                          <span className="flex items-center gap-1"><FiBarChart2 size={12} /> {g.completed_count} / {g.total_count} concepts</span>
                        </div>
                      </div>
                      <div className="flex items-center gap-3">
                        <div className="text-right">
                          <div className="text-sm font-medium text-accent-green">{pct}%</div>
                          <div className="w-20 h-1.5 bg-deep-700 rounded-full mt-1 overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-accent-blue to-accent-green rounded-full transition-all" style={{ width: `${pct}%` }} />
                          </div>
                        </div>
                        <button onClick={() => handleOpenGraph(g)} className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-xs font-medium hover:opacity-90 transition-opacity flex items-center gap-1">
                          <FiExternalLink size={12} /> Open
                        </button>

                        {moveGraphId === g.id ? (
                          <div className="relative">
                            <select
                              className="text-xs bg-deep-700 border border-surface-600/30 rounded-lg px-2 py-1.5 text-text-primary focus:outline-none"
                              value=""
                              onChange={e => {
                                if (e.target.value) handleMoveGraph(g.id, parseInt(e.target.value))
                              }}
                              onBlur={() => setMoveGraphId(null)}
                              autoFocus
                            >
                              <option value="">Move to...</option>
                              {otherCollections.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                              <option value="none">No collection</option>
                            </select>
                          </div>
                        ) : (
                          <button onClick={() => setMoveGraphId(g.id)} className="px-2.5 py-1.5 rounded-lg bg-deep-700/50 border border-surface-600/20 text-text-muted text-xs hover:text-accent-yellow hover:border-accent-yellow/30 transition-all flex items-center gap-1">
                            <FiMove size={11} /> Move
                          </button>
                        )}

                        {copyGraphId === g.id ? (
                          <div className="relative">
                            <select
                              className="text-xs bg-deep-700 border border-surface-600/30 rounded-lg px-2 py-1.5 text-text-primary focus:outline-none"
                              value=""
                              onChange={e => {
                                if (e.target.value) handleCopyGraph(g.id, parseInt(e.target.value))
                              }}
                              onBlur={() => setCopyGraphId(null)}
                              autoFocus
                            >
                              <option value="">Copy to...</option>
                              {otherCollections.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                            </select>
                          </div>
                        ) : (
                          <button onClick={() => setCopyGraphId(g.id)} className="px-2.5 py-1.5 rounded-lg bg-deep-700/50 border border-surface-600/20 text-text-muted text-xs hover:text-accent-cyan hover:border-accent-cyan/30 transition-all flex items-center gap-1">
                            <FiCopy size={11} /> Copy
                          </button>
                        )}

                        <button onClick={() => handleRemoveFromCollection(g.id)} className="px-2.5 py-1.5 rounded-lg bg-deep-700/50 border border-surface-600/20 text-text-muted text-xs hover:text-accent-red hover:border-accent-red/30 transition-all flex items-center gap-1">
                          <FiX size={11} /> Remove
                        </button>

                        <button onClick={() => handleDeleteGraph(g.id)} className="px-2.5 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors flex items-center gap-1">
                          <FiTrash2 size={11} /> Delete
                        </button>
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold flex items-center gap-2">
                <FiFolder className="text-accent-blue" />
                Collections
              </h2>
              <button
                onClick={() => setShowCreate(true)}
                className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-xs font-medium hover:opacity-90 transition-opacity flex items-center gap-1.5"
              >
                <FiPlus size={12} /> New Collection
              </button>
            </div>

            {showCreate && (
              <div className="glass-card rounded-2xl p-4 mb-4 flex items-center gap-3">
                <input
                  className="flex-1 px-3 py-2 rounded-lg bg-deep-800 border border-surface-600/30 text-text-primary text-sm focus:outline-none focus:border-accent-blue/50"
                  placeholder="Collection name..."
                  value={newName}
                  onChange={e => setNewName(e.target.value)}
                  onKeyDown={e => e.key === 'Enter' && handleCreate()}
                  autoFocus
                />
                <button onClick={handleCreate} className="px-3 py-2 rounded-lg bg-accent-green/10 text-accent-green text-sm font-medium hover:bg-accent-green/20 transition-colors">Create</button>
                <button onClick={() => setShowCreate(false)} className="px-3 py-2 rounded-lg text-text-muted text-sm hover:text-text-primary transition-colors">Cancel</button>
              </div>
            )}

            {loading ? (
              <div className="text-text-muted text-sm">Loading...</div>
            ) : collections.length === 0 ? (
              <div className="glass-card rounded-2xl p-8 text-center">
                <FiFolder className="text-text-muted text-3xl mx-auto mb-3" />
                <p className="text-text-muted text-sm">No collections yet</p>
                <p className="text-text-muted text-xs mt-1">Save graphs and organize them into collections</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {collections.map(c => (
                  <div key={c.id} className="glass-card rounded-2xl p-5 hover:border-accent-blue/30 transition-all cursor-pointer group"
                    onClick={() => openCollection(c)}
                  >
                    {renameId === c.id ? (
                      <div className="flex items-center gap-2" onClick={e => e.stopPropagation()}>
                        <input
                          className="flex-1 px-2 py-1 rounded-lg bg-deep-800 border border-surface-600/30 text-text-primary text-sm focus:outline-none focus:border-accent-blue/50"
                          value={renameName}
                          onChange={e => setRenameName(e.target.value)}
                          onKeyDown={e => e.key === 'Enter' && handleRename(c.id)}
                          autoFocus
                        />
                        <button onClick={() => handleRename(c.id)} className="text-accent-green text-xs">Save</button>
                        <button onClick={() => setRenameId(null)} className="text-text-muted text-xs">Cancel</button>
                      </div>
                    ) : (
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-text-primary truncate">{c.name}</h3>
                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={e => { e.stopPropagation(); setRenameId(c.id); setRenameName(c.name) }}
                            className="p-1 rounded hover:bg-deep-700/50 text-text-muted hover:text-accent-yellow transition-colors"
                          >
                            <FiEdit2 size={12} />
                          </button>
                          <button
                            onClick={e => { e.stopPropagation(); handleDelete(c.id) }}
                            className="p-1 rounded hover:bg-deep-700/50 text-text-muted hover:text-accent-red transition-colors"
                          >
                            <FiTrash2 size={12} />
                          </button>
                        </div>
                      </div>
                    )}
                    <div className="flex items-center gap-2 text-xs text-text-muted">
                      <FiBook size={12} />
                      <span>{c.graph_count} graph{c.graph_count !== 1 ? 's' : ''}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <h2 className="text-lg font-semibold mt-8 mb-4 flex items-center gap-2">
              <FiBook className="text-accent-blue" />
              Uncategorized Graphs
            </h2>

            <UncategorizedGraphs
              onOpen={handleOpenGraph}
              onDelete={handleDeleteGraph}
              collections={collections}
            />
          </div>
        )}
      </div>
    </div>
  )
}

function UncategorizedGraphs({ onOpen, onDelete, collections }) {
  const [graphs, setGraphs] = useState([])
  const [loading, setLoading] = useState(true)
  const [moveId, setMoveId] = useState(null)

  useEffect(() => {
    api.get('/graphs/list')
      .then(res => setGraphs(res.data.filter(g => !g.collection_id)))
      .catch(err => console.error(err))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-text-muted text-sm">Loading...</div>
  if (graphs.length === 0) return <div className="glass-card rounded-2xl p-8 text-center"><p className="text-text-muted text-sm">No uncategorized graphs</p></div>

  return (
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
                <span className="flex items-center gap-1"><FiClock size={12} /> Saved {new Date(g.created_at).toLocaleDateString()}</span>
                <span className="flex items-center gap-1"><FiBarChart2 size={12} /> {g.completed_count} / {g.total_count} concepts</span>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <div className="text-sm font-medium text-accent-green">{pct}%</div>
                <div className="w-20 h-1.5 bg-deep-700 rounded-full mt-1 overflow-hidden">
                  <div className="h-full bg-gradient-to-r from-accent-blue to-accent-green rounded-full transition-all" style={{ width: `${pct}%` }} />
                </div>
              </div>
              <button onClick={() => onOpen(g)} className="px-3 py-1.5 rounded-lg bg-gradient-to-r from-accent-blue to-accent-purple text-white text-xs font-medium hover:opacity-90 transition-opacity flex items-center gap-1">
                <FiExternalLink size={12} /> Open
              </button>
              {moveId === g.id ? (
                <select
                  className="text-xs bg-deep-700 border border-surface-600/30 rounded-lg px-2 py-1.5 text-text-primary focus:outline-none"
                  value=""
                  onChange={e => {
                    if (e.target.value) {
                      const targetId = parseInt(e.target.value)
                      api.put(`/collections/0/graphs/${g.id}/move`, { target_collection_id: targetId })
                        .then(() => setGraphs(prev => prev.filter(x => x.id !== g.id)))
                        .catch(err => console.error(err))
                    }
                    setMoveId(null)
                  }}
                  onBlur={() => setMoveId(null)}
                  autoFocus
                >
                  <option value="">Move to...</option>
                  {collections.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              ) : (
                <button onClick={() => setMoveId(g.id)} className="px-2.5 py-1.5 rounded-lg bg-deep-700/50 border border-surface-600/20 text-text-muted text-xs hover:text-accent-yellow hover:border-accent-yellow/30 transition-all flex items-center gap-1">
                  <FiMove size={11} /> Move
                </button>
              )}
              <button onClick={() => onDelete(g.id)} className="px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs font-medium hover:bg-red-500/20 transition-colors flex items-center gap-1">
                <FiTrash2 size={12} /> Delete
              </button>
            </div>
          </div>
        )
      })}
    </div>
  )
}
