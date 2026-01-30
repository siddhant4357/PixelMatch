import React, { useEffect } from 'react'
import { CheckCircle2, X } from 'lucide-react'

const SuccessModal = ({
    isOpen,
    onClose,
    title = 'Success!',
    message = 'Operation completed successfully',
    autoClose = true,
    autoCloseDelay = 5000
}) => {
    useEffect(() => {
        if (isOpen && autoClose) {
            const timer = setTimeout(() => {
                onClose()
            }, autoCloseDelay)
            return () => clearTimeout(timer)
        }
    }, [isOpen, autoClose, autoCloseDelay, onClose])

    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/20 backdrop-blur-sm animate-fadeIn">
            <div className="bg-white/90 backdrop-blur-md border-2 border-green-300 rounded-2xl shadow-2xl max-w-md w-full animate-scaleIn">
                {/* Header with close button */}
                <div className="flex items-start justify-between p-6 pb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-green-400 to-emerald-500 flex items-center justify-center animate-bounce">
                            <CheckCircle2 className="w-7 h-7 text-white" />
                        </div>
                        <h2 className="text-2xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
                            {title}
                        </h2>
                    </div>
                    <button
                        onClick={onClose}
                        className="text-slate-400 hover:text-slate-600 transition-colors p-1 hover:bg-slate-100 rounded-lg"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>

                {/* Message */}
                <div className="px-6 pb-6">
                    <p className="text-slate-700 text-lg leading-relaxed">
                        {message}
                    </p>
                </div>

                {/* Progress bar for auto-close */}
                {autoClose && (
                    <div className="h-1 bg-green-100 rounded-b-2xl overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-green-400 to-emerald-500 animate-shrink"
                            style={{ animationDuration: `${autoCloseDelay}ms` }}
                        />
                    </div>
                )}
            </div>

            <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }

        @keyframes scaleIn {
          from {
            transform: scale(0.9);
            opacity: 0;
          }
          to {
            transform: scale(1);
            opacity: 1;
          }
        }

        @keyframes shrink {
          from {
            width: 100%;
          }
          to {
            width: 0%;
          }
        }

        .animate-fadeIn {
          animation: fadeIn 0.2s ease-out;
        }

        .animate-scaleIn {
          animation: scaleIn 0.3s ease-out;
        }

        .animate-shrink {
          animation: shrink linear;
        }
      `}</style>
        </div>
    )
}

export default SuccessModal
