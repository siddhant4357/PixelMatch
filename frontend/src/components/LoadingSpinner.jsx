import React, { useState, useEffect } from 'react'
import { Sparkles } from 'lucide-react'

const LoadingSpinner = ({
    message = 'Processing...',
    tips = [],
    fullScreen = true,
    size = 'large'
}) => {
    const [currentTip, setCurrentTip] = useState(0)

    // Default tips if none provided
    const defaultTips = [
        "💡 Our AI can recognize faces even in group shots!",
        "✨ The more photos you upload, the better the search results!",
        "🎯 Try searching by location, date, or even emotions!",
        "🚀 Face recognition happens in real-time!",
        "💜 Your photos are processed securely and privately!"
    ]

    const displayTips = tips.length > 0 ? tips : defaultTips

    // Rotate tips every 3 seconds
    useEffect(() => {
        if (displayTips.length > 1) {
            const interval = setInterval(() => {
                setCurrentTip((prev) => (prev + 1) % displayTips.length)
            }, 3000)
            return () => clearInterval(interval)
        }
    }, [displayTips.length])

    const spinnerSize = size === 'large' ? 'w-24 h-24' : size === 'medium' ? 'w-16 h-16' : 'w-12 h-12'
    const containerClass = fullScreen
        ? 'fixed inset-0 z-50 flex items-center justify-center bg-gradient-to-br from-[#FFF5E6]/95 via-[#FFE8D6]/95 to-[#FFF0E0]/95 backdrop-blur-xl'
        : 'flex items-center justify-center p-8'

    return (
        <div className={containerClass}>
            <div className="text-center">
                {/* Animated Gradient Orbs */}
                <div className="relative inline-block mb-8">
                    {/* Main pulsing circle */}
                    <div className={`${spinnerSize} relative`}>
                        {/* Outer glow */}
                        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-purple-400 to-pink-400 opacity-20 animate-ping"></div>

                        {/* Middle rotating ring */}
                        <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-purple-400 border-r-pink-400 animate-spin"></div>

                        {/* Inner pulsing orb */}
                        <div className="absolute inset-2 rounded-full bg-gradient-to-br from-purple-400 to-pink-400 opacity-60 animate-pulse"></div>

                        {/* Center icon */}
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Sparkles className="w-8 h-8 text-white animate-pulse" />
                        </div>
                    </div>

                    {/* Orbiting dots */}
                    <div className="absolute inset-0 animate-spin" style={{ animationDuration: '3s' }}>
                        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-gradient-to-r from-purple-500 to-pink-500"></div>
                    </div>
                    <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDirection: 'reverse' }}>
                        <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-2 h-2 rounded-full bg-gradient-to-r from-pink-500 to-purple-500"></div>
                    </div>
                </div>

                {/* Message */}
                <div className="mb-4">
                    <h3 className="text-2xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent mb-2">
                        {message}
                    </h3>
                </div>

                {/* Rotating Tips */}
                {displayTips.length > 0 && (
                    <div className="max-w-md mx-auto">
                        <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-xl p-4 shadow-lg transition-all duration-500">
                            <p className="text-slate-700 text-sm leading-relaxed">
                                {displayTips[currentTip]}
                            </p>
                        </div>
                    </div>
                )}

                {/* Loading dots animation */}
                <div className="flex justify-center gap-2 mt-6">
                    <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 rounded-full bg-pink-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" style={{ animationDelay: '300ms' }}></div>
                </div>
            </div>
        </div>
    )
}

export default LoadingSpinner
