'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { 
  Atom, 
  Palette, 
  Wrench, 
  Layers, 
  ClipboardList,
  Cpu,
  CheckCircle,
  Loader,
  AlertCircle
} from 'lucide-react'

interface Agent {
  status: 'ready' | 'working' | 'error'
  workload: number
}

interface AgentStatusPanelProps {
  agents: Record<string, Agent> | null
  loading: boolean
  isSimulationRunning: boolean
}

const agentConfig = {
  physics_agent: {
    name: 'Physics Agent',
    icon: Atom,
    color: 'bg-blue-500',
    description: 'Structural analysis & calculations'
  },
  design_agent: {
    name: 'Design Agent',
    icon: Palette,
    color: 'bg-green-500',
    description: 'CAD modeling & drawings'
  },
  optimization_agent: {
    name: 'Optimization Agent',
    icon: Wrench,
    color: 'bg-red-500',
    description: 'Performance optimization'
  },
  materials_agent: {
    name: 'Materials Agent',
    icon: Layers,
    color: 'bg-yellow-500',
    description: 'Material selection & analysis'
  },
  project_manager_agent: {
    name: 'Project Manager',
    icon: ClipboardList,
    color: 'bg-purple-500',
    description: 'Task coordination & planning'
  }
}

export default function AgentStatusPanel({ agents, loading, isSimulationRunning }: AgentStatusPanelProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="flex items-center justify-center h-64">
          <Loader className="h-8 w-8 animate-spin text-aws-orange" />
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
          <Cpu className="h-5 w-5 text-aws-orange" />
          <span>AI Agent Status</span>
        </h2>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isSimulationRunning ? 'bg-blue-500 animate-pulse' : 'bg-green-500'}`} />
          <span className="text-sm text-gray-600">
            {isSimulationRunning ? 'Agents Active' : 'All Ready'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {Object.entries(agentConfig).map(([agentId, config], index) => {
          const agent = agents?.[agentId]
          const isActive = isSimulationRunning && Math.random() > 0.3 // Simulate some agents being active

          return (
            <motion.div
              key={agentId}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`agent-card ${isActive ? 'agent-active' : ''}`}
            >
              <div className="flex items-center space-x-4">
                <div className={`p-3 rounded-full ${config.color} text-white`}>
                  <config.icon className="h-5 w-5" />
                </div>
                
                <div className="flex-1">
                  <h3 className="font-medium text-gray-900">{config.name}</h3>
                  <p className="text-sm text-gray-500">{config.description}</p>
                </div>

                <div className="flex items-center space-x-3">
                  {/* Status Indicator */}
                  <div className="flex items-center space-x-2">
                    {isActive ? (
                      <>
                        <Loader className="h-4 w-4 text-blue-500 animate-spin" />
                        <span className="status-indicator status-working">Working</span>
                      </>
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 text-green-500" />
                        <span className="status-indicator status-ready">Ready</span>
                      </>
                    )}
                  </div>

                  {/* Workload Indicator */}
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <motion.div
                      className={`h-2 rounded-full ${config.color}`}
                      initial={{ width: 0 }}
                      animate={{ 
                        width: isActive ? `${Math.random() * 80 + 20}%` : `${agent?.workload || 0}%` 
                      }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>
              </div>

              {/* Progress Details for Active Agents */}
              {isActive && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="mt-4 p-3 bg-gray-50 rounded-lg"
                >
                  <div className="text-sm text-gray-600">
                    {getAgentActivity(agentId)}
                  </div>
                </motion.div>
              )}
            </motion.div>
          )
        })}
      </div>

      {/* Summary */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">
            System Status
          </span>
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-green-600">
              All agents operational
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}

function getAgentActivity(agentId: string): string {
  const activities = {
    physics_agent: [
      "Calculating structural loads...",
      "Running stress analysis...",
      "Performing seismic simulation...",
      "Validating safety factors..."
    ],
    design_agent: [
      "Creating 3D bridge model...",
      "Generating technical drawings...",
      "Optimizing geometry...",
      "Updating design specifications..."
    ],
    optimization_agent: [
      "Analyzing cost efficiency...",
      "Optimizing material usage...",
      "Running topology optimization...",
      "Evaluating performance metrics..."
    ],
    materials_agent: [
      "Selecting steel grades...",
      "Analyzing concrete properties...",
      "Evaluating weather resistance...",
      "Calculating material costs..."
    ],
    project_manager_agent: [
      "Coordinating agent tasks...",
      "Monitoring progress...",
      "Generating project reports...",
      "Planning next phases..."
    ]
  }

  const agentActivities = activities[agentId as keyof typeof activities] || ["Processing..."]
  return agentActivities[Math.floor(Math.random() * agentActivities.length)]
}