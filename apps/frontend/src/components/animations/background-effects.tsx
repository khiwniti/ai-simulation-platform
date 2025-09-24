"use client"

import React from 'react'
import { motion } from 'framer-motion'

interface BackgroundEffectsProps {
  variant?: 'particles' | 'grid' | 'gradient' | 'waves'
  className?: string
}

export function BackgroundEffects({ variant = 'gradient', className }: BackgroundEffectsProps) {
  if (variant === 'particles') {
    return <ParticleBackground className={className} />
  }
  
  if (variant === 'grid') {
    return <GridBackground className={className} />
  }
  
  if (variant === 'waves') {
    return <WaveBackground className={className} />
  }
  
  return <GradientBackground className={className} />
}

function ParticleBackground({ className }: { className?: string }) {
  const particles = Array.from({ length: 50 }, (_, i) => i)
  
  return (
    <div className={`fixed inset-0 overflow-hidden pointer-events-none ${className}`}>
      {particles.map((particle) => (
        <motion.div
          key={particle}
          className="absolute w-1 h-1 bg-blue-400/30 rounded-full"
          initial={{
            x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1920,
            y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : Math.random() * 1080,
          }}
          animate={{
            x: typeof window !== 'undefined' ? Math.random() * window.innerWidth : Math.random() * 1920,
            y: typeof window !== 'undefined' ? Math.random() * window.innerHeight : Math.random() * 1080,
          }}
          transition={{
            duration: Math.random() * 10 + 10,
            repeat: Infinity,
            ease: "linear"
          }}
        />
      ))}
    </div>
  )
}

function GridBackground({ className }: { className?: string }) {
  return (
    <div className={`fixed inset-0 pointer-events-none ${className}`}>
      <div className="absolute inset-0 bg-[linear-gradient(rgba(120,120,120,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(120,120,120,0.1)_1px,transparent_1px)] bg-[size:50px_50px]" />
      <motion.div
        className="absolute inset-0 bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-pink-500/10"
        animate={{
          background: [
            "linear-gradient(45deg, rgba(59,130,246,0.1), rgba(147,51,234,0.1), rgba(236,72,153,0.1))",
            "linear-gradient(135deg, rgba(236,72,153,0.1), rgba(59,130,246,0.1), rgba(147,51,234,0.1))",
            "linear-gradient(225deg, rgba(147,51,234,0.1), rgba(236,72,153,0.1), rgba(59,130,246,0.1))",
            "linear-gradient(315deg, rgba(59,130,246,0.1), rgba(147,51,234,0.1), rgba(236,72,153,0.1))"
          ]
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </div>
  )
}

function GradientBackground({ className }: { className?: string }) {
  return (
    <div className={`fixed inset-0 pointer-events-none ${className}`}>
      <motion.div
        className="absolute inset-0 opacity-30"
        animate={{
          background: [
            "radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 40% 40%, rgba(120, 200, 255, 0.3) 0%, transparent 50%)",
            "radial-gradient(circle at 60% 20%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 20% 60%, rgba(255, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 80% 80%, rgba(120, 200, 255, 0.3) 0%, transparent 50%)",
            "radial-gradient(circle at 80% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 40% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%), radial-gradient(circle at 20% 40%, rgba(120, 200, 255, 0.3) 0%, transparent 50%)"
          ]
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </div>
  )
}

function WaveBackground({ className }: { className?: string }) {
  return (
    <div className={`fixed inset-0 pointer-events-none overflow-hidden ${className}`}>
      <motion.div
        className="absolute -inset-10 opacity-20"
        style={{
          background: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%234f46e5' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
        }}
        animate={{
          x: [-60, 0],
          y: [-60, 0],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      <motion.div
        className="absolute -inset-10 opacity-10"
        style={{
          background: `url("data:image/svg+xml,%3Csvg width='100' height='100' viewBox='0 0 100 100' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%23ec4899' fill-opacity='0.1'%3E%3Cpolygon points='50 0 60 40 100 50 60 60 50 100 40 60 0 50 40 40'/%3E%3C/g%3E%3C/svg%3E")`,
        }}
        animate={{
          x: [0, -100],
          y: [0, -100],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "linear"
        }}
      />
    </div>
  )
}