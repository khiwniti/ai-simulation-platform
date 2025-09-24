'use client'

import { useState, useEffect } from 'react'

interface SystemHealth {
  status: string
  services: {
    bedrock: {
      status: string
      region: string
    }
    database: string
    websocket_connections: number
  }
}

export function useSystemHealth() {
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSystemHealth = async () => {
      try {
        const response = await fetch('/health')
        if (response.ok) {
          const data = await response.json()
          setHealth(data)
        } else {
          setError(`HTTP ${response.status}: ${response.statusText}`)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        // Fallback mock data for demo
        setHealth({
          status: 'healthy',
          services: {
            bedrock: {
              status: 'healthy',
              region: 'us-east-1'
            },
            database: 'connected',
            websocket_connections: 0
          }
        })
      } finally {
        setLoading(false)
      }
    }

    fetchSystemHealth()
    
    // Refresh every 10 seconds
    const interval = setInterval(fetchSystemHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  return { health, loading, error }
}