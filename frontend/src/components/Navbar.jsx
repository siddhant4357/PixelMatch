import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { Camera, LayoutDashboard, Settings, Menu, X } from 'lucide-react'
import { UserButton, SignedIn } from '@clerk/clerk-react'

const Navbar = () => {
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const isActive = (path) => location.pathname.startsWith(path)

  return (
    <nav className="bg-white/80 backdrop-blur-md border-b border-purple-100/60 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-5">
        <div className="flex items-center justify-between h-16">

          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group" onClick={() => setMenuOpen(false)}>
            <div className="p-2 rounded-xl bg-gradient-to-br from-purple-500 to-pink-500 group-hover:scale-110 transition-transform shadow-md shadow-purple-300/40">
              <Camera className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-extrabold bg-gradient-to-r from-purple-600 to-pink-500 bg-clip-text text-transparent leading-none">
              PixelMatch
            </span>
          </Link>

          {/* Desktop nav — signed-in only */}
          <SignedIn>
            <div className="hidden sm:flex items-center gap-6">
              <Link
                to="/dashboard"
                className={`flex items-center gap-1.5 font-semibold transition-colors ${
                  isActive('/dashboard') ? 'text-purple-600' : 'text-slate-500 hover:text-purple-500'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                <span>Dashboard</span>
              </Link>
              <Link
                to="/settings"
                className={`flex items-center gap-1.5 font-semibold transition-colors ${
                  isActive('/settings') ? 'text-purple-600' : 'text-slate-500 hover:text-purple-500'
                }`}
              >
                <Settings className="w-4 h-4" />
                <span>Settings</span>
              </Link>
              <div className="pl-4 border-l border-slate-200">
                <UserButton afterSignOutUrl="/" />
              </div>
            </div>

            {/* Mobile: avatar + hamburger */}
            <div className="flex sm:hidden items-center gap-3">
              <UserButton afterSignOutUrl="/" />
              <button
                onClick={() => setMenuOpen((v) => !v)}
                className="p-2 rounded-xl text-slate-600 hover:bg-purple-50 transition-colors"
                aria-label="Toggle menu"
              >
                {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
            </div>
          </SignedIn>
        </div>
      </div>

      {/* Mobile drawer */}
      <SignedIn>
        {menuOpen && (
          <div className="sm:hidden border-t border-purple-100/60 bg-white/90 backdrop-blur-md px-5 py-4 flex flex-col gap-3 animate-in slide-in-from-top-2 duration-200">
            <Link
              to="/dashboard"
              onClick={() => setMenuOpen(false)}
              className={`flex items-center gap-2 px-4 py-3 rounded-2xl font-semibold transition-colors ${
                isActive('/dashboard') ? 'bg-purple-50 text-purple-700' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              Dashboard
            </Link>
            <Link
              to="/settings"
              onClick={() => setMenuOpen(false)}
              className={`flex items-center gap-2 px-4 py-3 rounded-2xl font-semibold transition-colors ${
                isActive('/settings') ? 'bg-purple-50 text-purple-700' : 'text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Settings className="w-5 h-5" />
              Settings
            </Link>
          </div>
        )}
      </SignedIn>
    </nav>
  )
}

export default Navbar