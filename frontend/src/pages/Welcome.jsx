import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { createRoom, joinRoom, setRoomInfo } from '../services/api'
import { Camera, Sparkles, Users, Lock, ArrowRight } from 'lucide-react'

const Welcome = () => {
    const [eventName, setEventName] = useState('')
    const [password, setPassword] = useState('')
    const [confirmPassword, setConfirmPassword] = useState('')
    const [roomId, setRoomId] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showLoading, setShowLoading] = useState(true)
    const navigate = useNavigate()

    // Loading screen effect
    useEffect(() => {
        const timer = setTimeout(() => {
            setShowLoading(false)
        }, 2000)
        return () => clearTimeout(timer)
    }, [])

    const handleCreate = async (e) => {
        e.preventDefault()
        if (!eventName.trim()) return

        if (password !== confirmPassword) {
            setError("Passwords do not match")
            return
        }

        setLoading(true)
        setError('')

        try {
            const room = await createRoom(eventName, password)
            setRoomInfo(room)
            navigate('/', { state: { newRoomCreated: true, roomInfo: room } })
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleJoin = async (e) => {
        e.preventDefault()
        if (!roomId.trim()) return

        setLoading(true)
        setError('')

        try {
            const room = await joinRoom(roomId)
            setRoomInfo(room)
            navigate('/')
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    // Loading Screen - matches Home.jsx aesthetic
    if (showLoading) {
        return (
            <div className="fixed inset-0 bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0] flex items-center justify-center z-50">
                <div className="text-center">
                    <div className="relative mb-8">
                        <div className="inline-flex p-6 rounded-3xl bg-white/60 backdrop-blur-md border border-purple-200/50 shadow-2xl">
                            <Camera className="w-20 h-20 text-purple-600" />
                        </div>
                        <Sparkles className="w-8 h-8 text-pink-500 absolute -top-2 -right-2 animate-pulse" />
                    </div>
                    <h1 className="text-5xl font-bold text-slate-800 mb-3">
                        PixelMatch
                    </h1>
                    <p className="text-lg text-slate-600">
                        AI-Powered Photo Discovery
                    </p>
                </div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-[#FFF5E6] via-[#FFE8D6] to-[#FFF0E0] relative overflow-hidden">
            {/* Dotted Grid Pattern - same as Home.jsx */}
            <div className="fixed inset-0 opacity-30" style={{
                backgroundImage: 'radial-gradient(circle, #D8B4A0 1px, transparent 1px)',
                backgroundSize: '24px 24px'
            }}></div>

            {/* Floating Gradient Orbs - same as Home.jsx */}
            <div className="fixed top-20 right-20 w-96 h-96 bg-gradient-to-br from-purple-300/30 to-pink-300/30 rounded-full blur-3xl"></div>
            <div className="fixed bottom-20 left-20 w-96 h-96 bg-gradient-to-br from-pink-300/30 to-purple-300/30 rounded-full blur-3xl"></div>

            <div className="relative min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
                <div className="max-w-6xl w-full">
                    {/* Header */}
                    <div className="text-center mb-12">
                        <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/60 backdrop-blur-md border border-purple-200/50 shadow-lg mb-8">
                            <Sparkles className="w-4 h-4 text-purple-600" />
                            <span className="text-sm font-semibold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                AI-Powered Photo Discovery
                            </span>
                        </div>

                        <h1 className="text-5xl md:text-6xl font-bold mb-4">
                            <span className="block text-slate-800 mb-2">Welcome to</span>
                            <span className="bg-gradient-to-r from-purple-400 via-pink-400 to-purple-600 bg-clip-text text-transparent">
                                PixelMatch
                            </span>
                        </h1>
                        <p className="text-xl text-slate-600 max-w-2xl mx-auto">
                            Create a new event or join an existing one to get started
                        </p>
                    </div>

                    {/* Error Message */}
                    {error && (
                        <div className="max-w-2xl mx-auto mb-6 bg-red-50 border border-red-200 rounded-2xl p-4">
                            <p className="text-red-700 text-center font-medium">{error}</p>
                        </div>
                    )}

                    {/* Main Cards Container */}
                    <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
                        {/* Create Event Card */}
                        <div className="group bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-3xl p-8 shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-purple-400 to-purple-600 shadow-lg">
                                    <Sparkles className="w-6 h-6 text-white" />
                                </div>
                                <h3 className="text-2xl font-bold text-slate-800">Create Event</h3>
                            </div>

                            <form onSubmit={handleCreate} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">
                                        Event Name
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        className="w-full px-4 py-3 bg-white/80 border border-purple-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                        placeholder="e.g., Sarah's Wedding 2026"
                                        value={eventName}
                                        onChange={(e) => setEventName(e.target.value)}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">
                                        <Lock className="w-4 h-4 inline mr-1" />
                                        Password
                                    </label>
                                    <input
                                        type="password"
                                        required
                                        className="w-full px-4 py-3 bg-white/80 border border-purple-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                        placeholder="Create a secure password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                    />
                                </div>

                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">
                                        Confirm Password
                                    </label>
                                    <input
                                        type="password"
                                        required
                                        className="w-full px-4 py-3 bg-white/80 border border-purple-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all"
                                        placeholder="Re-enter password"
                                        value={confirmPassword}
                                        onChange={(e) => setConfirmPassword(e.target.value)}
                                    />
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full mt-6 px-6 py-4 bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                            Creating...
                                        </>
                                    ) : (
                                        <>
                                            Create Event
                                            <ArrowRight className="w-5 h-5" />
                                        </>
                                    )}
                                </button>
                            </form>
                        </div>

                        {/* Join Event Card */}
                        <div className="group bg-white/60 backdrop-blur-md border border-pink-200/50 rounded-3xl p-8 shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300">
                            <div className="flex items-center gap-3 mb-6">
                                <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-pink-400 to-pink-600 shadow-lg">
                                    <Users className="w-6 h-6 text-white" />
                                </div>
                                <h3 className="text-2xl font-bold text-slate-800">Join Event</h3>
                            </div>

                            <form onSubmit={handleJoin} className="space-y-4">
                                <div>
                                    <label className="block text-sm font-medium text-slate-700 mb-2">
                                        Room ID
                                    </label>
                                    <input
                                        type="text"
                                        required
                                        className="w-full px-4 py-3 bg-white/80 border border-pink-200 rounded-xl text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-pink-500 focus:border-transparent transition-all uppercase tracking-widest text-center text-2xl font-bold"
                                        placeholder="ABC123"
                                        maxLength={6}
                                        value={roomId}
                                        onChange={(e) => setRoomId(e.target.value.toUpperCase())}
                                    />
                                    <p className="text-xs text-slate-500 mt-2 text-center">
                                        Enter the 6-character room code
                                    </p>
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full mt-6 px-6 py-4 bg-gradient-to-r from-pink-600 to-pink-500 text-white font-semibold rounded-xl hover:shadow-lg hover:scale-[1.02] focus:outline-none focus:ring-2 focus:ring-pink-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
                                >
                                    {loading ? (
                                        <>
                                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                                            Joining...
                                        </>
                                    ) : (
                                        <>
                                            Join Event
                                            <ArrowRight className="w-5 h-5" />
                                        </>
                                    )}
                                </button>
                            </form>

                            {/* Features List */}
                            <div className="mt-8 pt-6 border-t border-purple-200/50">
                                <p className="text-sm text-slate-700 mb-3 font-medium">What you can do:</p>
                                <ul className="space-y-2 text-sm text-slate-600">
                                    <li className="flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 bg-pink-500 rounded-full"></div>
                                        Upload your selfie
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 bg-pink-500 rounded-full"></div>
                                        AI finds your photos instantly
                                    </li>
                                    <li className="flex items-center gap-2">
                                        <div className="w-1.5 h-1.5 bg-pink-500 rounded-full"></div>
                                        Download all your memories
                                    </li>
                                </ul>
                            </div>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="text-center mt-12">
                        <p className="text-slate-500 text-sm">
                            Powered by AI • Secure • Private
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Welcome
