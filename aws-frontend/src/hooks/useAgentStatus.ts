'use client'

import { useState, useEffect } from 'react'

interface Agent {
  status: 'ready' | 'working' | 'error'
  workload: number
}

export function useAgentStatus() {
  const [agents, setAgents] = useState<Record<string, Agent> | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAgentStatus = async () => {
      try {
        const response = await fetch('/api/agents/status')
        if (response.ok) {
          const data = await response.json()
          if (data.success) {
            setAgents(data.agents)
          } else {
            setError('Failed to fetch agent status')
          }
        } else {
          setError(`HTTP ${response.status}: ${response.statusText}`)
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        // Fallback mock data for demo
        setAgents({
          physics_agent: { status: 'ready', workload: 0 },
          design_agent: { status: 'ready', workload: 0 },
          optimization_agent: { status: 'ready', workload: 0 },
          materials_agent: { status: 'ready', workload: 0 },
          project_manager_agent: { status: 'ready', workload: 0 }
        })
      } finally {
        setLoading(false)
      }
    }

    fetchAgentStatus()
    
    // Refresh every 5 seconds
    const interval = setInterval(fetchAgentStatus, 5000)
    return () => clearInterval(interval)
  }, [])

  return { agents, loading, error }
}