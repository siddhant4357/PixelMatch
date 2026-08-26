import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus, Users, Loader2, ArrowRight, Camera } from 'lucide-react'
import { getMyRooms, createRoom, joinRoom, getProfile } from '../services/api'

const Dashboard = () => {
  const navigate = useNavigate()
  const [rooms, setRooms] = useState([])
  const [loading, setLoading] = useState(true)
  
  // Modals
  const [showCreate, setShowCreate] = useState(false)
  const [showJoin, setShowJoin] = useState(false)
  
  // Forms
  const [eventName, setEventName] = useState('')
  const [roomCode, setRoomCode] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    const init = async () => {
      try {
        // Check if user has uploaded a selfie
        const profileData = await getProfile()
        if (!profileData.has_embedding) {
          navigate('/onboarding')
          return
        }
        
        // Fetch rooms
        const data = await getMyRooms()
        setRooms(data)
      } catch (err) {
        console.error(err)
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [navigate])

  const handleCreateRoom = async (e) => {
    e.preventDefault()
    if (!eventName.trim()) return
    
    setIsSubmitting(true)
    setError('')
    try {
      const room = await createRoom(eventName, null) // Password removed for simplicity
      navigate(`/room/${room.room_code}`)
    } catch (err) {
      setError(err.message)
      setIsSubmitting(false)
    }
  }

  const handleJoinRoom = async (e) => {
    e.preventDefault()
    if (!roomCode.trim()) return
    
    setIsSubmitting(true)
    setError('')
    try {
      const room = await joinRoom(roomCode)
      navigate(`/room/${room.room_code}`)
    } catch (err) {
      setError(err.message)
      setIsSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-[80vh] flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-indigo-500" />
      </div>
    )
  }

  return (
    <div className="container mx-auto px-6 py-12 max-w-6xl relative z-10">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-12 gap-4">
        <div>
          <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">Your Events</h1>
          <p className="text-slate-600 mt-2">Manage and access all your event photos in one place.</p>
        </div>
        <div className="flex w-full sm:w-auto gap-3">
          <button 
            onClick={() => setShowJoin(true)}
            className="flex-1 sm:flex-none px-5 py-3 bg-white/80 backdrop-blur-md border border-purple-200 text-purple-700 rounded-2xl hover:bg-white font-bold transition-all flex items-center justify-center gap-2 shadow-sm hover:shadow-md"
          >
            <Users className="w-4 h-4" />
            Join
          </button>
          <button 
            onClick={() => setShowCreate(true)}
            className="flex-1 sm:flex-none px-5 py-3 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl hover:opacity-90 font-bold transition-opacity flex items-center justify-center gap-2 shadow-lg shadow-purple-500/30"
          >
            <Plus className="w-4 h-4" />
            Create Event
          </button>
        </div>
      </div>

      {rooms.length === 0 ? (
        <div className="text-center py-24 bg-white/60 backdrop-blur-xl rounded-[2rem] shadow-xl shadow-purple-900/5 border border-white">
          <div className="bg-gradient-to-br from-purple-100 to-pink-100 w-24 h-24 rounded-full flex items-center justify-center mx-auto mb-6 shadow-inner">
            <Camera className="w-10 h-10 text-purple-500" />
          </div>
          <h3 className="text-2xl font-bold text-slate-900 mb-2">No events yet</h3>
          <p className="text-slate-600 mb-8 max-w-sm mx-auto text-lg">Create a new event or join an existing one to get started.</p>
          <button 
            onClick={() => setShowCreate(true)}
            className="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all shadow-xl shadow-purple-500/30"
          >
            Create Your First Event
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
          {rooms.map((room) => (
            <div 
              key={room.room_code}
              onClick={() => navigate(`/room/${room.room_code}`)}
              className="bg-white/80 backdrop-blur-md rounded-3xl shadow-sm hover:shadow-xl hover:shadow-purple-500/10 transition-all duration-300 border border-white overflow-hidden cursor-pointer group hover:-translate-y-1"
            >
              <div className="h-32 bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center text-5xl shadow-inner">
                📸
              </div>
              <div className="p-6 relative">
                <div className="absolute -top-6 right-6 bg-white/90 backdrop-blur-sm p-2 px-4 rounded-xl shadow-md border border-purple-100 text-xs font-bold text-purple-700 uppercase tracking-wider">
                  {room.role}
                </div>
                <h3 className="text-xl font-bold text-slate-900 mb-1 group-hover:text-purple-600 transition-colors">
                  {room.event_name}
                </h3>
                <p className="text-sm text-slate-500 mb-4 font-mono font-medium">{room.room_code}</p>
                <div className="flex items-center justify-between text-sm font-semibold text-slate-600 border-t border-purple-100 pt-4">
                  <span>{room.photo_count || 0} Photos</span>
                  <ArrowRight className="w-5 h-5 text-purple-300 group-hover:text-pink-500 transition-colors" />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showCreate && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white/90 backdrop-blur-xl rounded-[2rem] border border-white w-full max-w-md p-8 shadow-2xl animate-in zoom-in-95 duration-200">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Create New Event</h2>
            {error && <div className="p-3 bg-red-50 text-red-600 rounded-xl text-sm mb-6 font-medium">{error}</div>}
            <form onSubmit={handleCreateRoom}>
              <div className="mb-6">
                <label className="block text-sm font-bold text-slate-700 mb-2">Event Name</label>
                <input 
                  type="text" 
                  value={eventName}
                  onChange={(e) => setEventName(e.target.value)}
                  placeholder="e.g., Summer Wedding 2024"
                  className="w-full px-5 py-3 bg-white border border-slate-200 rounded-2xl focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 outline-none font-medium transition-all"
                  autoFocus
                />
              </div>
              <div className="flex space-x-4 mt-8">
                <button 
                  type="button" 
                  onClick={() => setShowCreate(false)}
                  className="flex-1 px-4 py-3 bg-slate-100 text-slate-700 rounded-2xl font-bold hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={!eventName.trim() || isSubmitting}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all shadow-lg shadow-purple-500/30 disabled:opacity-50 flex justify-center items-center"
                >
                  {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Create'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Join Modal */}
      {showJoin && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4 animate-in fade-in duration-200">
          <div className="bg-white/90 backdrop-blur-xl rounded-[2rem] border border-white w-full max-w-md p-8 shadow-2xl animate-in zoom-in-95 duration-200">
            <h2 className="text-2xl font-bold text-slate-900 mb-6">Join an Event</h2>
            {error && <div className="p-3 bg-red-50 text-red-600 rounded-xl text-sm mb-6 font-medium">{error}</div>}
            <form onSubmit={handleJoinRoom}>
              <div className="mb-6">
                <label className="block text-sm font-bold text-slate-700 mb-2">Room Code</label>
                <input 
                  type="text" 
                  value={roomCode}
                  onChange={(e) => setRoomCode(e.target.value.toUpperCase())}
                  placeholder="e.g., A7X92B"
                  className="w-full px-5 py-3 bg-white border border-slate-200 rounded-2xl focus:ring-4 focus:ring-purple-500/20 focus:border-purple-500 outline-none font-mono uppercase font-bold text-center tracking-widest text-lg transition-all"
                  autoFocus
                />
              </div>
              <div className="flex space-x-4 mt-8">
                <button 
                  type="button" 
                  onClick={() => setShowJoin(false)}
                  className="flex-1 px-4 py-3 bg-slate-100 text-slate-700 rounded-2xl font-bold hover:bg-slate-200 transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  disabled={!roomCode.trim() || isSubmitting}
                  className="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-500 text-white rounded-2xl font-bold hover:opacity-90 transition-all shadow-lg shadow-purple-500/30 disabled:opacity-50 flex justify-center items-center"
                >
                  {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Join'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
