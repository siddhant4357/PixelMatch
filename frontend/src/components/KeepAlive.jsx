import React, { useEffect } from 'react'

/**
 * KeepAlive Component
 * Pings the backend every 10 minutes to prevent it from sleeping on free tier hosting.
 * This is essential for Render.com free tier which sleeps after 15 minutes of inactivity.
 */
const KeepAlive = () => {
    useEffect(() => {
        const PING_INTERVAL = 10 * 60 * 1000 // 10 minutes in milliseconds
        const BACKEND_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

        const pingBackend = async () => {
            try {
                const response = await fetch(`${BACKEND_URL}/ping`, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                })

                if (response.ok) {
                    console.log('[KeepAlive] Backend ping successful')
                } else {
                    console.warn('[KeepAlive] Backend ping failed:', response.status)
                }
            } catch (error) {
                console.error('[KeepAlive] Backend ping error:', error)
            }
        }

        // Ping immediately on mount
        pingBackend()

        // Set up interval for periodic pings
        const intervalId = setInterval(pingBackend, PING_INTERVAL)

        // Cleanup on unmount
        return () => clearInterval(intervalId)
    }, [])

    // This component doesn't render anything
    return null
}

export default KeepAlive
