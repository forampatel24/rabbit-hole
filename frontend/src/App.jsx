import React from 'react'
import { GraphProvider } from './context/GraphContext'
import Navbar from './components/Navbar'
import SearchBar from './components/SearchBar'
import TopicOverview from './components/TopicOverview'
import GraphView from './components/GraphView'
import NodePanel from './components/NodePanel'
import KnowledgeGapPanel from './components/KnowledgeGapPanel'
import './index.css'

function App(){
  return (
    <GraphProvider>
      <div className="min-h-screen bg-[#0F172A] text-[#F8FAFC]">
        <Navbar />
        <main className="max-w-6xl mx-auto p-4">
          <SearchBar />
          <div className="mt-4 grid grid-cols-3 gap-4">
            <div className="col-span-2">
              <TopicOverview />
              <GraphView />
            </div>
            <div className="col-span-1">
              <NodePanel />
              <KnowledgeGapPanel />
            </div>
          </div>
        </main>
      </div>
    </GraphProvider>
  )
}

export default App
