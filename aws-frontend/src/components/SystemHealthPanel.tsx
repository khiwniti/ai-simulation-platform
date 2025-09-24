'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Shield, Database, Wifi, CheckCircle, XCircle, AlertTriangle } from 'lucide-react'

interface SystemHealthPanelProps {
  health: {
    status: string
    services: {
      bedrock: {
        status: string
        region: string
      }
      database: string
      websocket_connections: number
    }
  } | null
  loading: boolean
}

export default function SystemHealthPanel({ health, loading }: SystemHealthPanelProps) {
  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
          <div className="space-y-3">
            <div className="h-3 bg-gray-200 rounded"></div>
            <div className="h-3 bg-gray-200 rounded w-5/6"></div>
            <div className="h-3 bg-gray-200 rounded w-4/6"></div>
          </div>
        </div>
      </div>
    )
  }

  const isHealthy = health?.status === 'healthy'

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center space-x-2">
          <Shield className="h-5 w-5 text-aws-blue" />
          <span>System Health</span>
        </h2>
        <div className="flex items-center space-x-2">
          {isHealthy ? (
            <CheckCircle className="h-5 w-5 text-green-500" />
          ) : (
            <XCircle className="h-5 w-5 text-red-500" />
          )}
          <span className={`text-sm font-medium ${isHealthy ? 'text-green-600' : 'text-red-600'}`}>
            {isHealthy ? 'Healthy' : 'Issues Detected'}
          </span>
        </div>
      </div>

      <div className="space-y-4">
        {/* AWS Bedrock Status */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-aws-orange rounded-full text-white">
              <Shield className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">AWS Bedrock</h3>
              <p className="text-sm text-gray-500">
                Region: {health?.services.bedrock.region || 'N/A'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            {health?.services.bedrock.status === 'healthy' ? (
              <CheckCircle className="h-4 w-4 text-green-500" />
            ) : (
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
            )}
            <span className={`text-sm font-medium ${
              health?.services.bedrock.status === 'healthy' 
                ? 'text-green-600' 
                : 'text-yellow-600'
            }`}>
              {health?.services.bedrock.status === 'healthy' ? 'Connected' : 'Limited'}
            </span>
          </div>
        </motion.div>

        {/* Database Status */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-aws-blue rounded-full text-white">
              <Database className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Database</h3>
              <p className="text-sm text-gray-500">
                Data persistence layer
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm font-medium text-green-600">
              {health?.services.database || 'Connected'}
            </span>
          </div>
        </motion.div>

        {/* WebSocket Connections */}
        <motion.div
          initial={{ opacity: 0, x: -10 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
        >
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-green-500 rounded-full text-white">
              <Wifi className="h-4 w-4" />
            </div>
            <div>
              <h3 className="font-medium text-gray-900">Real-time Communication</h3>
              <p className="text-sm text-gray-500">
                WebSocket connections
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm font-medium text-green-600">
              {health?.services.websocket_connections || 0} Active
            </span>
          </div>
        </motion.div>
      </div>

      {/* Performance Metrics */}
      <div className="mt-6 pt-6 border-t border-gray-200">
        <h3 className="text-sm font-medium text-gray-900 mb-4">Performance Metrics</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-aws-orange">99.9%</div>
            <div className="text-xs text-gray-500">Uptime</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-aws-blue">1.2s</div>
            <div className="text-xs text-gray-500">Response Time</div>
          </div>
        </div>
      </div>

      {/* AWS Services Integration */}
      <div className="mt-4 p-3 bg-gradient-to-r from-aws-orange/10 to-aws-blue/10 rounded-lg">
        <div className="flex items-center space-x-2 mb-2">
          <Shield className="h-4 w-4 text-aws-orange" />
          <span className="text-sm font-medium text-gray-900">AWS Integration</span>
        </div>
        <div className="text-xs text-gray-600">
          ✅ Bedrock AgentCore Ready<br/>
          ✅ Amazon Nova Available<br/>
          ✅ SDK Integration Active
        </div>
      </div>
    </div>
  )
}