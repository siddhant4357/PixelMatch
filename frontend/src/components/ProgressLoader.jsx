import React from 'react'
import { CheckCircle2, Loader2 } from 'lucide-react'

const ProgressLoader = ({
    progress = 0,
    total = 100,
    current = 0,
    message = 'Processing...',
    status = 'processing',
    showPercentage = true,
    showCount = false
}) => {
    const percentage = total > 0 ? Math.round((progress / total) * 100) : 0
    const isComplete = status === 'complete' || percentage >= 100

    return (
        <div className="bg-white/60 backdrop-blur-md border border-purple-200/50 rounded-2xl p-6 shadow-lg">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                    {message}
                </h3>
                {isComplete ? (
                    <CheckCircle2 className="w-6 h-6 text-green-500" />
                ) : (
                    <Loader2 className="w-6 h-6 text-purple-500 animate-spin" />
                )}
            </div>

            {/* Progress Bar */}
            <div className="relative mb-4">
                {/* Background track */}
                <div className="h-3 bg-purple-100 rounded-full overflow-hidden">
                    {/* Progress fill with gradient */}
                    <div
                        className="h-full bg-gradient-to-r from-purple-400 via-pink-400 to-purple-500 rounded-full transition-all duration-500 ease-out relative overflow-hidden"
                        style={{ width: `${percentage}%` }}
                    >
                        {/* Shimmer effect */}
                        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                    </div>
                </div>

                {/* Percentage badge */}
                {showPercentage && (
                    <div className="absolute -top-1 right-0 transform translate-y-[-100%] mb-2">
                        <div className="bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow-md">
                            {percentage}%
                        </div>
                    </div>
                )}
            </div>

            {/* Count and Status */}
            <div className="flex items-center justify-between text-sm">
                {showCount && total > 0 ? (
                    <span className="text-slate-600 font-medium">
                        Processing {current} of {total} {total === 1 ? 'item' : 'items'}
                    </span>
                ) : (
                    <span className="text-slate-600 font-medium">
                        {status === 'processing' ? 'Processing...' : status === 'complete' ? 'Complete!' : status}
                    </span>
                )}

                {!isComplete && (
                    <div className="flex gap-1">
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse"></div>
                        <div className="w-1.5 h-1.5 rounded-full bg-pink-400 animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                )}
            </div>
        </div>
    )
}

export default ProgressLoader
