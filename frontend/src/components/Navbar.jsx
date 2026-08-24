import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Camera, LayoutDashboard, Settings, Sparkles } from 'lucide-react'
import { UserButton, SignedIn } from '@clerk/clerk-react'

const Navbar = () => {
  const location = useLocation()
  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-indigo-100 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2 group">
            <div className="p-2 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-500 group-hover:scale-110 transition-transform shadow-md">
              <Camera className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent leading-none">
              PixelMatch
            </span>
          </Link>

          {/* Navigation Links - Only visible when signed in */}
          <SignedIn>
            <div className="flex items-center space-x-6">
              <Link
                to="/dashboard"
                className={`flex items-center space-x-2 font-medium transition-all ${
                  isActive('/dashboard')
                    ? 'text-indigo-600'
                    : 'text-slate-500 hover:text-indigo-500'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>
              <Link
                to="/settings"
                className={`flex items-center space-x-2 font-medium transition-all ${
                  isActive('/settings')
                    ? 'text-indigo-600'
                    : 'text-slate-500 hover:text-indigo-500'
                }`}
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </Link>

              <div className="pl-4 border-l border-slate-200 flex items-center">
                <UserButton afterSignOutUrl="/" />
              </div>
            </div>
          </SignedIn>
        </div>
      </div>
    </nav>
  )
}

export default Navbar