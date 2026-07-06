import React, { useContext } from 'react'
import { Link } from 'react-router-dom'
import { FiHexagon, FiUser, FiLogIn, FiLogOut, FiBook } from 'react-icons/fi'
import { AuthContext } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useContext(AuthContext)

  return (
    <nav className="w-full border-b border-surface-700/30 bg-deep-900/80 backdrop-blur-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 h-14 flex items-center gap-3">
        <Link to="/" className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-accent-blue to-accent-purple flex items-center justify-center">
            <FiHexagon className="text-white text-sm" />
          </div>
          <span className="text-lg font-semibold tracking-tight text-text-primary">RabbitHole</span>
        </Link>
        <div className="ml-auto flex items-center gap-2">
          {user ? (
            <>
              <Link
                to="/profile"
                className="flex items-center gap-1.5 text-xs text-text-muted bg-deep-700/50 px-2.5 py-1 rounded-full border border-surface-700/20 hover:text-text-primary transition-colors"
              >
                <FiUser size={12} />
                {user.username}
              </Link>
              <button
                onClick={logout}
                className="flex items-center gap-1.5 text-xs text-text-muted hover:text-accent-red transition-colors px-2 py-1"
              >
                <FiLogOut size={12} />
                Sign Out
              </button>
            </>
          ) : (
            <>
              <Link
                to="/login"
                className="flex items-center gap-1.5 text-xs text-text-muted bg-deep-700/50 px-2.5 py-1 rounded-full border border-surface-700/20 hover:text-text-primary transition-colors"
              >
                <FiLogIn size={12} />
                Sign In
              </Link>
              <Link
                to="/signup"
                className="flex items-center gap-1.5 text-xs text-white bg-gradient-to-r from-accent-blue to-accent-purple px-3 py-1 rounded-full font-medium hover:opacity-90 transition-opacity"
              >
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </nav>
  )
}
