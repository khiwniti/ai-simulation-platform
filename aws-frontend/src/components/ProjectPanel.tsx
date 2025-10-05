'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { 
  FolderOpen, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  BarChart3,
  FileText,
  Settings,
  Download
} from 'lucide-react'

interface ProjectPanelProps {
  project: any
  isSimulationRunning: boolean
}

export default function ProjectPanel({ project, isSimulationRunning }: ProjectPanelProps) {
  const hasProject = project && project.success

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
          <FolderOpen className="h-5 w-5 text-aws-blue" />
          <span>Active Project</span>
        </h2>
        {hasProject && (
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm text-green-600">In Progress</span>
          </div>
        )}
      </div>

      {hasProject ? (
        <div className="space-y-6">
          {/* Project Overview */}
          <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-100">
            <h3 className="font-semibold text-gray-900 mb-2">Bridge Design Project</h3>
            <p className="text-sm text-gray-600 mb-3">
              150m cable-stayed bridge with seismic resistance and sustainability features
            </p>
            
            {/* Project ID */}
            <div className="text-xs text-gray-500 font-mono bg-white/50 px-2 py-1 rounded">
              ID: {project.result?.project_id?.slice(0, 8)}...
            </div>
          </div>

          {/* Task Progress */}
          {project.result?.planning?.task_plan?.tasks && (
            <div>
              <h4 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
                <BarChart3 className="h-4 w-4" />
                <span>Task Progress</span>
              </h4>
              
              <div className="space-y-2">
                {project.result.planning.task_plan.tasks.slice(0, 4).map((task: any, index: number) => (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg"
                  >
                    <div className={`w-2 h-2 rounded-full ${
                      isSimulationRunning && index === 0 
                        ? 'bg-blue-500 animate-pulse' 
                        : index < 2 
                        ? 'bg-green-500' 
                        : 'bg-gray-300'
                    }`} />
                    
                    <div className="flex-1">
                      <div className="text-sm font-medium text-gray-900">{task.name}</div>
                      <div className="text-xs text-gray-500">
                        {task.agent_type.replace('_', ' ').replace(/\b\w/g, (l: string) => l.toUpperCase())} • {task.estimated_duration}
                      </div>
                    </div>
                    
                    {index < 2 && (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    )}
                    
                    {isSimulationRunning && index === 0 && (
                      <div className="flex items-center space-x-1">
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" />
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                        <div className="w-1 h-1 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                      </div>
                    )}
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {/* Project Timeline */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-2 mb-2">
              <Clock className="h-4 w-4 text-gray-600" />
              <span className="text-sm font-medium text-gray-900">Timeline</span>
            </div>
            <div className="text-sm text-gray-600">
              Estimated Duration: {project.result?.planning?.task_plan?.estimated_duration || '5-7 days'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              Started: {new Date().toLocaleDateString()}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="flex space-x-2">
            <button className="flex-1 flex items-center justify-center space-x-2 px-3 py-2 bg-aws-blue text-white rounded-lg text-sm hover:bg-blue-600 transition-colors">
              <FileText className="h-4 w-4" />
              <span>View Report</span>
            </button>
            
            <button className="flex items-center justify-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors">
              <Download className="h-4 w-4" />
            </button>
            
            <button className="flex items-center justify-center px-3 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors">
              <Settings className="h-4 w-4" />
            </button>
          </div>

        </div>
      ) : (
        <div className="text-center py-12">
          <FolderOpen className="h-12 w-12 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Active Projects</h3>
          <p className="text-gray-500 mb-4">
            Start a bridge design simulation to see project details here
          </p>
          
          {isSimulationRunning && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-center space-x-2 text-blue-600"
            >
              <div className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
              <span className="text-sm">Initializing project...</span>
            </motion.div>
          )}
        </div>
      )}

      {/* Demo Info */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <div className="flex items-start space-x-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
          <div className="text-sm">
            <div className="font-medium text-yellow-800">Demo Mode</div>
            <div className="text-yellow-700">
              This simulation demonstrates AI agent collaboration for autonomous engineering design.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}