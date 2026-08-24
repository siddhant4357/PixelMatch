import React, { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet, useNavigate } from 'react-router-dom'
import { ClerkProvider, SignedIn, SignedOut, useAuth } from '@clerk/clerk-react'
import Navbar from './components/Navbar'
import Welcome from './pages/Welcome'
import AuthPage from './pages/AuthPage'
import Onboarding from './pages/Onboarding'
import Dashboard from './pages/Dashboard'
import RoomPage from './pages/RoomPage'
import Settings from './pages/Settings'
import AskAI from './pages/AskAI'
import { setTokenProvider } from './services/api'

// Import your publishable key
const PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY

if (!PUBLISHABLE_KEY) {
  console.error("Missing Clerk Publishable Key")
}

// Utility to sync Clerk token with our API service
const ApiTokenProvider = () => {
  const { getToken } = useAuth()
  
  useEffect(() => {
    // Provide the async getToken function to our API wrapper
    setTokenProvider(getToken)
  }, [getToken])
  
  return null
}

// Protected layout that requires authentication
const ProtectedLayout = () => {
  return (
    <SignedIn>
      <Navbar />
      <main className="pb-10">
        <Outlet />
      </main>
    </SignedIn>
  )
}

// Layout for guests (Unauthenticated or Public routes)
const PublicLayout = () => {
  return (
    <>
      <Navbar />
      <main>
        <Outlet />
      </main>
    </>
  )
}

const App = () => {
  return (
    <ClerkProvider publishableKey={PUBLISHABLE_KEY} afterSignOutUrl="/">
      <ApiTokenProvider />
      <Router>
        <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0] font-sans text-slate-900 selection:bg-purple-200 relative overflow-hidden">
          <Routes>
            {/* Root Route: Conditionally render Welcome or redirect to Dashboard */}
            <Route path="/" element={
              <>
                <SignedIn>
                  <Navigate to="/dashboard" replace />
                </SignedIn>
                <SignedOut>
                  <Welcome />
                </SignedOut>
              </>
            } />

            {/* Auth Routes */}
            <Route path="/sign-in/*" element={<AuthPage type="sign-in" />} />
            <Route path="/sign-up/*" element={<AuthPage type="sign-up" />} />

            {/* Protected Routes */}
            <Route element={<ProtectedLayout />}>
              <Route path="/onboarding" element={<Onboarding />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/settings" element={<Settings />} />
              <Route path="/room/:roomCode" element={<RoomPage />} />
              <Route path="/room/:roomCode/ask-ai" element={<AskAI />} />
            </Route>
            
            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </Router>
    </ClerkProvider>
  )
}

export default App