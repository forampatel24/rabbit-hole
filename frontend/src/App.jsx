import React, { useContext } from 'react'
import { GraphProvider, GraphContext } from './context/GraphContext'
import Navbar from './components/Navbar'
import SearchBar from './components/SearchBar'
import EmptyState from './components/EmptyState'
import TopicOverview from './components/TopicOverview'
import GraphView from './components/GraphView'
import NodePanel from './components/NodePanel'
import KnowledgeGapPanel from './components/KnowledgeGapPanel'
import LoadingOverlay from './components/LoadingOverlay'
import './index.css'

function AppContent() {
  const { overview, selectedNodeId, graph, loading } = useContext(GraphContext)
  const hasGraph = graph?.nodes?.length > 0

  if (!hasGraph && !loading) {
    return (
      <div className="min-h-screen bg-deep-900 flex flex-col">
        <Navbar />
        <EmptyState />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-deep-900 text-text-primary flex flex-col">
      <Navbar />
      <LoadingOverlay />

      <div className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-6">
        <div className="mt-4">
          <SearchBar />
        </div>

        {overview && <TopicOverview />}

        <div className="flex-1 flex gap-5 mt-4 mb-6" style={{ minHeight: '500px' }}>
          <div className="flex-1 relative glass rounded-2xl overflow-hidden">
            <GraphView />
          </div>

          {selectedNodeId && (
            <div className="w-96 shrink-0 animate-slideInRight">
              <NodePanel />
            </div>
          )}
        </div>

        <div className="mb-8">
          <KnowledgeGapPanel />
        </div>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <GraphProvider>
      <AppContent />
    </GraphProvider>
  )
}
