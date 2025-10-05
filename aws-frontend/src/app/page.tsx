'use client'

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Cpu, 
  Zap, 
  BarChart3, 
  Settings, 
  PlayCircle, 
  PauseCircle,
  CheckCircle,
  AlertCircle,
  Users,
  Brain,
  Rocket
} from 'lucide-react'

import AgentStatusPanel from '@/components/AgentStatusPanel'
import SimulationCanvas from '@/components/SimulationCanvas'
import ProjectPanel from '@/components/ProjectPanel'
import SystemHealthPanel from '@/components/SystemHealthPanel'
import { useAgentStatus } from '@/hooks/useAgentStatus'
import { useSystemHealth } from '@/hooks/useSystemHealth'

export default function HomePage() {
  const [activeProject, setActiveProject] = useState(null)
  const [isSimulationRunning, setIsSimulationRunning] = useState(false)
  const { agents, loading: agentsLoading } = useAgentStatus()
  const { health, loading: healthLoading } = useSystemHealth()

  const handleStartSimulation = async () => {
    setIsSimulationRunning(true)
    // Trigger bridge design demo
    try {
      const response = await fetch('/api/demo/bridge-design', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          span_length: 150,
          load_requirements: {
            live_load: 8000,
            dead_load: 3000,
            vehicle_load: 25000,
            seismic_load: 5000
          },
          material_constraints: {
            budget: 750000,
            sustainability: "high",
            local_materials: true
          },
          environmental_conditions: {
            wind_speed: 120,
            seismic_zone: 4,
            temperature_range: [-20, 40],
            corrosive_environment: false
          }
        })
      })
      
      const result = await response.json()
      setActiveProject(result)
      setTimeout(() => setIsSimulationRunning(false), 8000)
    } catch (error) {
      console.error('Simulation error:', error)
      setIsSimulationRunning(false)
    }
  }

  return (
    <div className="min-h-screen">
      {/* Header */}
      <motion.header 
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-white shadow-sm border-b border-gray-200"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Brain className="h-8 w-8 text-aws-orange" />
                <div>
                  <h1 className="text-xl font-bold text-gray-900">
                    AWS AI Agent Platform
                  </h1>
                  <p className="text-sm text-gray-500">
                    Autonomous Engineering Team
                  </p>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${health?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-sm text-gray-600">
                  {health?.status === 'healthy' ? 'System Healthy' : 'System Issues'}
                </span>
              </div>
              
              <button
                onClick={handleStartSimulation}
                disabled={isSimulationRunning}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-white font-medium transition-all ${
                  isSimulationRunning 
                    ? 'bg-gray-400 cursor-not-allowed' 
                    : 'bg-aws-orange hover:bg-orange-600 hover:shadow-lg'
                }`}
              >
                {isSimulationRunning ? (
                  <>
                    <PauseCircle className="h-4 w-4" />
                    <span>Simulation Running...</span>
                  </>
                ) : (
                  <>
                    <PlayCircle className="h-4 w-4" />
                    <span>Start Bridge Demo</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </motion.header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* System Health Panel */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-12 lg:col-span-4"
          >
            <SystemHealthPanel health={health} loading={healthLoading} />
          </motion.div>

          {/* Agent Status Panel */}
          <motion.div 
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-12 lg:col-span-8"
          >
            <AgentStatusPanel 
              agents={agents} 
              loading={agentsLoading}
              isSimulationRunning={isSimulationRunning}
            />
          </motion.div>

          {/* 3D Simulation Canvas */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="col-span-12 lg:col-span-8"
          >
            <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
                  <Cpu className="h-5 w-5 text-aws-blue" />
                  <span>3D Engineering Simulation</span>
                </h2>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isSimulationRunning ? 'bg-blue-500 animate-pulse' : 'bg-gray-300'}`} />
                  <span className="text-sm text-gray-600">
                    {isSimulationRunning ? 'Active' : 'Idle'}
                  </span>
                </div>
              </div>
              
              <div className="h-96 bg-gray-50 rounded-lg relative overflow-hidden">
                <SimulationCanvas isRunning={isSimulationRunning} />
              </div>
            </div>
          </motion.div>

          {/* Project Management Panel */}
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="col-span-12 lg:col-span-4"
          >
            <ProjectPanel 
              project={activeProject} 
              isSimulationRunning={isSimulationRunning}
            />
          </motion.div>

          {/* Statistics Cards */}
          <div className="col-span-12">
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Active Projects</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {activeProject ? '1' : '0'}
                    </p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-aws-blue" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">AI Agents Ready</p>
                    <p className="text-2xl font-bold text-gray-900">
                      {agents ? Object.keys(agents).length : '0'}
                    </p>
                  </div>
                  <Users className="h-8 w-8 text-aws-orange" />
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">System Performance</p>
                    <p className="text-2xl font-bold text-green-600">
                      {health?.status === 'healthy' ? '100%' : '0%'}
                    </p>
                  </div>
                  <Rocket className="h-8 w-8 text-green-500" />
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Demo Instructions */}
      <motion.div 
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="fixed bottom-4 right-4 bg-aws-dark text-white p-4 rounded-lg shadow-lg max-w-sm"
      >
        <h3 className="font-semibold mb-2 flex items-center space-x-2">
          <Zap className="h-4 w-4 text-aws-orange" />
          <span>Demo Instructions</span>
        </h3>
        <p className="text-sm text-gray-300">
          Click "Start Bridge Demo" to see the AI agents collaborate on an autonomous bridge design simulation.
        </p>
        <div className="mt-2 flex items-center space-x-2">
          <CheckCircle className="h-3 w-3 text-green-400" />
          <span className="text-xs text-gray-400">
            AWS Bedrock & Nova Ready
          </span>
        </div>
      </motion.div>
    </div>
  )
}