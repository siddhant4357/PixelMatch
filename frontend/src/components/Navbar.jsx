import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Camera, Upload, Search } from 'lucide-react'

const Navbar = () => {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-slate-900/80 backdrop-blur-lg border-b border-slate-700 sticky top-0 z-50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <a href="/" className="flex items-center space-x-2">
            <Camera className="w-8 h-8 text-indigo-500" />
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-500 to-purple-500">
              PixelMatch
            </span>
          </a>

          {/* Navigation Links */}
          <div className="flex items-center space-x-1">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg transition-all ${isActive('/')
                ? 'bg-indigo-600 text-white'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
            >
              Home
            </Link>

            <Link
              to="/admin"
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${isActive('/admin')
                ? 'bg-indigo-600 text-white'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
            >
              <Upload className="w-4 h-4" />
              <span>Admin</span>
            </Link>

            <Link
              to="/guest"
              className={`px-4 py-2 rounded-lg transition-all flex items-center space-x-2 ${isActive('/guest')
                ? 'bg-indigo-600 text-white'
                : 'text-slate-300 hover:bg-slate-800 hover:text-white'
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