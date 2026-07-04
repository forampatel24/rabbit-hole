import React, { useContext } from 'react'
import { GraphProvider, GraphContext } from './context/GraphContext'
import Navbar from './components/Navbar'
import SearchBar from './components/SearchBar'
import TopicOverview from './components/TopicOverview'
import GraphView from './components/GraphView'
import NodePanel from './components/NodePanel'
import KnowledgeGapPanel from './components/KnowledgeGapPanel'
import './index.css'

function AppContent() {
  const { selectedNodeId } = useContext(GraphContext)

  return (
    <div className="min-h-screen bg-[#0F172A] text-[#F8FAFC] flex flex-col">
      <Navbar />
      <div className="flex-1 flex flex-col max-w-7xl w-full mx-auto px-4">
        <SearchBar />
        <TopicOverview />

        <div className="flex-1 flex gap-4 mt-4" style={{ minHeight: '600px' }}>
          <div className="flex-1">
            <GraphView />
          </div>

          {selectedNodeId && (
            <div className="w-96 shrink-0">
              <NodePanel />
            </div>
          )}
        </div>

        <div className="mt-4 mb-6">
          <KnowledgeGapPanel />
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <GraphProvider>
      <AppContent />
    </GraphProvider>
  )
}

export default App
