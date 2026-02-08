import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet } from 'react-router-dom'
import Navbar from './components/Navbar'
import KeepAlive from './components/KeepAlive'
import Home from './pages/Home'
import Admin from './pages/Admin'
import Guest from './pages/Guest'
import AskAI from './pages/AskAI'
import Welcome from './pages/Welcome'
import { getRoomId } from './services/api'

const ProtectedLayout = () => {
  const roomId = getRoomId()

  if (!roomId) {
    return <Navigate to="/welcome" replace />
  }

  return (
    <>
      <Navbar />
      <KeepAlive />
      <main>
        <Outlet />
      </main>
    </>
  )
}

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0]">
        <Routes>
          <Route path="/welcome" element={<Welcome />} />

          <Route element={<ProtectedLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/guest" element={<Guest />} />
            <Route path="/guest/ask-ai" element={<AskAI />} />
          </Route>
        </Routes>
      </div>
    </Router>
  )
}

export default App