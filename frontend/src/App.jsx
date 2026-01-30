import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import KeepAlive from './components/KeepAlive'
import Home from './pages/Home'
import Admin from './pages/Admin'
import Guest from './pages/Guest'
import AskAI from './pages/AskAI'

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0]">
        <Navbar />
        <KeepAlive />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/guest" element={<Guest />} />
            <Route path="/guest/ask-ai" element={<AskAI />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App