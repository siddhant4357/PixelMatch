import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Upload, Send, Loader2, AlertCircle, Sparkles, MapPin, Calendar, Download } from 'lucide-react'
import { uploadSelfieForAI, queryAI, getPhotoUrl } from '../services/api'
import LoadingSpinner from '../components/LoadingSpinner'

const AskAI = () => {
    const navigate = useNavigate()

    // State
    const [selfieFile, setSelfieFile] = useState(null)
    const [selfiePreview, setSelfiePreview] = useState(null)
    const [sessionId, setSessionId] = useState(null)
    const [uploading, setUploading] = useState(false)
    const [messages, setMessages] = useState([])
    const [inputMessage, setInputMessage] = useState('')
    const [sending, setSending] = useState(false)
    const [error, setError] = useState(null)
    const [results, setResults] = useState([])

    const chatEndRef = useRef(null)
    const inputRef = useRef(null)

    // Auto-scroll to bottom of chat
    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    // Handle selfie selection
    const handleFileSelect = (e) => {
        const file = e.target.files[0]
        if (file) {
            setSelfieFile(file)

            // Create preview
            const reader = new FileReader()
            reader.onload = (e) => setSelfiePreview(e.target.result)
            reader.readAsDataURL(file)
        }
    }

    // Upload selfie and create session
    const handleUploadSelfie = async () => {
        if (!selfieFile) return

        setUploading(true)
        setError(null)

        try {
            const data = await uploadSelfieForAI(selfieFile)
            setSessionId(data.session_id)

            // Add AI welcome message
            setMessages([{
                type: 'ai',
                text: data.message + ' What photos are you looking for?',
                timestamp: new Date().toISOString()
            }])

            // Focus input
            setTimeout(() => inputRef.current?.focus(), 100)

        } catch (err) {
            setError(err.message)
        } finally {
            setUploading(false)
        }
    }

    // Send message to AI
    const handleSendMessage = async () => {
        if (!inputMessage.trim() || !sessionId || sending) return

        const userMessage = inputMessage.trim()
        setInputMessage('')
        setSending(true)
        setError(null)

        // Add user message
        setMessages(prev => [...prev, {
            type: 'user',
            text: userMessage,
            timestamp: new Date().toISOString()
        }])

        try {
            const data = await queryAI(sessionId, userMessage)

            // Add AI response
            setMessages(prev => [...prev, {
                type: 'ai',
                text: data.ai_message,
                timestamp: new Date().toISOString()
            }])

            // Update results
            setResults(data.photos || [])

        } catch (err) {
            setError(err.message)
            setMessages(prev => [...prev, {
                type: 'ai',
                text: `Sorry, I encountered an error: ${err.message}`,
                timestamp: new Date().toISOString(),
                isError: true
            }])
        } finally {
            setSending(false)
        }
    }

    // Handle Enter key
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleSendMessage()
        }
    }

    const aiTips = [
        "💡 Ask me anything about your photos!",
        "✨ I can search by location, date, or even emotions!",
        "🎯 Try: 'Show photos from the beach'",
        "🚀 Processing your request with AI...",
        "💜 Understanding your query..."
    ]

    return (
        <div className="min-h-screen">
            {/* Premium Loading Overlay */}
            {uploading && (
                <LoadingSpinner
                    message="Processing Your Selfie"
                    tips={aiTips}
                    fullScreen={true}
                />
            )}

            <div className="container mx-auto px-6 py-12 max-w-7xl">
                {/* Header */}
                <div className="text-center mb-12">
                    <div className="inline-flex items-center gap-2 mb-4">
                        <Sparkles className="w-8 h-8 text-purple-500" />
                        <h1 className="text-5xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent">Ask AI</h1>
                    </div>
                    <p className="text-xl text-slate-600">Find your photos using natural language</p>
                </div>

                {/* Step 1: Upload Selfie */}
                {!sessionId && (
                    <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl p-8 mb-8 shadow-lg">
                        <h2 className="text-2xl font-bold mb-6 bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">Step 1: Upload Your Selfie</h2>

                        <div className="mb-6">
                            <input
                                type="file"
                                id="selfieInput"
                                accept="image/*"
                                onChange={handleFileSelect}
                                className="hidden"
                            />

                            <label
                                htmlFor="selfieInput"
                                className="block border-2 border-dashed border-purple-200 hover:border-purple-300 bg-purple-50/30 rounded-xl p-12 text-center cursor-pointer transition-all"
                            >
                                <Upload className="w-16 h-16 text-purple-400 mx-auto mb-4" />
                                <div className="text-xl font-semibold text-slate-800 mb-2">
                                    Click to select your selfie
                                </div>
                                <div className="text-slate-600">
                                    Make sure your face is clearly visible
                                </div>
                            </label>
                        </div>

                        {/* Preview */}
                        {selfiePreview && (
                            <div className="mb-6 text-center">
                                <img
                                    src={selfiePreview}
                                    alt="Selfie preview"
                                    className="max-w-xs mx-auto rounded-xl border-2 border-purple-200 shadow-lg"
                                />
                                <div className="text-slate-600 mt-3 font-medium">{selfieFile?.name}</div>
                            </div>
                        )}

                        <button
                            onClick={handleUploadSelfie}
                            disabled={!selfieFile || uploading}
                            className="w-full px-6 py-4 bg-gradient-to-r from-purple-400 to-pink-400 text-white rounded-xl font-semibold hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center space-x-2 shadow-lg"
                        >
                            {uploading ? (
                                <>
                                    <Loader2 className="w-5 h-5 animate-spin" />
                                    <span>Processing...</span>
                                </>
                            ) : (
                                <>
                                    <Sparkles className="w-5 h-5" />
                                    <span>Start AI Search</span>
                                </>
                            )}
                        </button>
                    </div>
                )}

                {/* Step 2: Chat with AI */}
                {sessionId && (
                    <div className="grid lg:grid-cols-2 gap-8">
                        {/* Chat Section */}
                        <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl overflow-hidden flex flex-col shadow-lg" style={{ height: '600px' }}>
                            <div className="p-6 border-b border-purple-200">
                                <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent flex items-center gap-2">
                                    <Sparkles className="w-6 h-6 text-purple-400" />
                                    Chat with AI
                                </h2>
                            </div>

                            {/* Messages */}
                            <div className="flex-1 overflow-y-auto p-6 space-y-4">
                                {messages.map((msg, index) => (
                                    <div
                                        key={index}
                                        className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                                    >
                                        <div
                                            className={`max-w-[80%] rounded-2xl px-4 py-3 ${msg.type === 'user'
                                                ? 'bg-gradient-to-r from-purple-400 to-pink-400 text-white shadow-md'
                                                : msg.isError
                                                    ? 'bg-red-50 border border-red-300 text-red-700'
                                                    : 'bg-white/80 backdrop-blur-sm text-slate-800 border border-purple-100'
                                                }`}
                                        >
                                            <div className="text-sm font-medium mb-1">
                                                {msg.type === 'user' ? 'You' : '🤖 AI'}
                                            </div>
                                            <div>{msg.text}</div>
                                        </div>
                                    </div>
                                ))}

                                {sending && (
                                    <div className="flex justify-start">
                                        <div className="bg-white/80 backdrop-blur-sm border border-purple-100 rounded-2xl px-4 py-3">
                                            <Loader2 className="w-5 h-5 text-purple-400 animate-spin" />
                                        </div>
                                    </div>
                                )}

                                <div ref={chatEndRef} />
                            </div>

                            {/* Input */}
                            <div className="p-4 border-t border-purple-200 bg-white/40 backdrop-blur-sm">
                                <div className="flex gap-2">
                                    <input
                                        ref={inputRef}
                                        type="text"
                                        value={inputMessage}
                                        onChange={(e) => setInputMessage(e.target.value)}
                                        onKeyPress={handleKeyPress}
                                        placeholder="Ask about your photos... (e.g., 'Show photos from Paris')"
                                        className="flex-1 px-4 py-3 bg-white/50 border border-purple-200 rounded-xl text-slate-700 placeholder-slate-500 focus:border-purple-400 focus:outline-none focus:ring-2 focus:ring-purple-400"
                                        disabled={sending}
                                    />
                                    <button
                                        onClick={handleSendMessage}
                                        disabled={!inputMessage.trim() || sending}
                                        className="px-6 py-3 bg-gradient-to-r from-purple-400 to-pink-400 text-white rounded-xl font-semibold hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center gap-2 shadow-md"
                                    >
                                        <Send className="w-5 h-5" />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Results Section */}
                        <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl overflow-hidden shadow-lg" style={{ height: '600px' }}>
                            <div className="p-6 border-b border-purple-200">
                                <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                                    Results ({results.length})
                                </h2>
                            </div>

                            <div className="overflow-y-auto p-6" style={{ height: 'calc(600px - 80px)' }}>
                                {results.length === 0 ? (
                                    <div className="text-center text-slate-500 py-12">
                                        <Sparkles className="w-16 h-16 mx-auto mb-4 opacity-50" />
                                        <p>Ask AI to find your photos!</p>
                                        <p className="text-sm mt-2">Try: "Show photos from the beach"</p>
                                    </div>
                                ) : (
                                    <div className="grid gap-4">
                                        {results.map((result, index) => {
                                            // Extract filename from photo_path
                                            const photoName = result.photo_path
                                                ? result.photo_path.split(/[/\\]/).pop()
                                                : result.photo_name || 'Unknown'

                                            return (
                                                <div
                                                    key={index}
                                                    className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-xl overflow-hidden hover:border-purple-400 transition-all group shadow-lg"
                                                >
                                                    <img
                                                        src={getPhotoUrl(photoName)}
                                                        alt={photoName}
                                                        className="w-full h-48 object-cover"
                                                    />
                                                    <div className="p-4">
                                                        <div className="text-slate-800 font-semibold text-sm mb-2 truncate">
                                                            {photoName}
                                                        </div>
                                                        <div className="flex items-center justify-between mb-3">
                                                            <span className="px-3 py-1 bg-purple-500 text-white rounded-full text-sm font-semibold">
                                                                {Math.round((result.similarity || 0) * 100)}% match
                                                            </span>
                                                            {result.location_name && (
                                                                <span className="text-xs text-slate-400 flex items-center gap-1">
                                                                    <MapPin className="w-3 h-3" />
                                                                    {result.location_name.split(',')[0]}
                                                                </span>
                                                            )}
                                                        </div>
                                                        <a
                                                            href={getPhotoUrl(photoName)}
                                                            download
                                                            className="w-full px-4 py-2 bg-gradient-to-r from-purple-400 to-pink-400 hover:scale-105 text-white rounded-lg text-sm font-semibold transition-all flex items-center justify-center space-x-2 shadow-md"
                                                        >
                                                            <Download className="w-4 h-4" />
                                                            <span>Download</span>
                                                        </a>
                                                    </div>
                                                </div>
                                            )
                                        })}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Error Message */}
                {error && (
                    <div className="mt-8 bg-red-50 border border-red-300 rounded-xl p-5 flex items-start space-x-3 shadow-sm">
                        <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                        <div>
                            <div className="font-semibold text-red-700">Error</div>
                            <div className="text-red-600">{error}</div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default AskAI
