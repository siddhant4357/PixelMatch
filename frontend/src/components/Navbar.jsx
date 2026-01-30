import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Camera, Upload, Search, Sparkles } from 'lucide-react'

const Navbar = () => {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-white/60 backdrop-blur-md border-b border-purple-200/50 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="p-2 rounded-xl bg-gradient-to-br from-purple-400 to-pink-400 group-hover:scale-110 transition-transform shadow-md">
              <Camera className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent">
              PixelMatch
            </span>
          </Link>

          {/* Navigation Links */}
          <div className="flex items-center space-x-2">
            <Link
              to="/"
              className={`px-4 py-2 rounded-xl transition-all font-medium ${isActive('/')
                ? 'bg-gradient-to-r from-purple-400 to-pink-400 text-white shadow-md'
                : 'text-slate-700 hover:bg-purple-100/50 hover:text-purple-600'
                }`}
            >
              Home
            </Link>

            <Link
              to="/admin"
              className={`px-4 py-2 rounded-xl transition-all flex items-center space-x-2 font-medium ${isActive('/admin')
                ? 'bg-gradient-to-r from-purple-400 to-pink-400 text-white shadow-md'
                : 'text-slate-700 hover:bg-purple-100/50 hover:text-purple-600'
                }`}
            >
              <Upload className="w-4 h-4" />
              <span>Admin</span>
            </Link>

            <Link
              to="/guest"
              className={`px-4 py-2 rounded-xl transition-all flex items-center space-x-2 font-medium ${isActive('/guest') || isActive('/guest/ask-ai')
                ? 'bg-gradient-to-r from-purple-400 to-pink-400 text-white shadow-md'
                : 'text-slate-700 hover:bg-purple-100/50 hover:text-purple-600'
                }`}
            >
              <Search className="w-4 h-4" />
              <span>Guest</span>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar