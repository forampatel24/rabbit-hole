import React, { useContext } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { GraphProvider, GraphContext } from './context/GraphContext'
import { AuthProvider, AuthContext } from './context/AuthContext'
import Navbar from './components/Navbar'
import SearchBar from './components/SearchBar'
import EmptyState from './components/EmptyState'
import TopicOverview from './components/TopicOverview'
import GraphView from './components/GraphView'
import NodePanel from './components/NodePanel'
import KnowledgeGapPanel from './components/KnowledgeGapPanel'
import NotesSection from './components/NotesSection'
import NodeChecklist from './components/NodeChecklist'
import LoadingOverlay from './components/LoadingOverlay'
import LoginPage from './pages/LoginPage'
import SignUpPage from './pages/SignUpPage'
import ProfilePage from './pages/ProfilePage'
import './index.css'

function ProtectedRoute({ children }) {
  const { user, loading } = useContext(AuthContext)
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return children
}

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
        <div className="mt-4 relative z-[9999]">
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

        <div className="mb-8 grid grid-cols-1 lg:grid-cols-2 gap-4">
          <div className="space-y-4">
            <KnowledgeGapPanel />
            <NotesSection />
          </div>
          <div className="space-y-4">
            <NodeChecklist />
          </div>
        </div>
      </div>
    </div>
  )
}

function MainApp() {
  return (
    <AuthProvider>
      <GraphProvider>
        <Routes>
          <Route path="/" element={<AppContent />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/signup" element={<SignUpPage />} />
          <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
        </Routes>
      </GraphProvider>
    </AuthProvider>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <MainApp />
    </BrowserRouter>
  )
}
