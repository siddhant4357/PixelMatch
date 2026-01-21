import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import KeepAlive from './components/KeepAlive'
import Home from './pages/Home'
import Admin from './pages/Admin'
import Guest from './pages/Guest'

const App = () => {
  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <Navbar />
        <KeepAlive />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/admin" element={<Admin />} />
            <Route path="/guest" element={<Guest />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App