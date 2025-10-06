"use client"

import React, { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import Link from 'next/link'
import { Button } from '../ui/button'
import { Card } from '../ui/card'
import { AnimatedContainer, StaggeredList, FloatingElement } from '../animations/animated-container'
import { BackgroundEffects } from '../animations/background-effects'
import { 
  Zap, 
  Brain, 
  Cpu, 
  BarChart3, 
  Globe, 
  Shield,
  ArrowRight,
  Play,
  Sparkles,
  Rocket
} from 'lucide-react'

export function HeroSection() {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 })

  useEffect(() => {
    const updateMousePosition = (ev: MouseEvent) => {
      setMousePosition({ x: ev.clientX, y: ev.clientY })
    }
    window.addEventListener('mousemove', updateMousePosition)
    return () => window.removeEventListener('mousemove', updateMousePosition)
  }, [])

  const features = [
    {
      icon: Brain,
      title: "AI-Powered",
      description: "Advanced machine learning for predictive simulation"
    },
    {
      icon: Zap,
      title: "Lightning Fast",
      description: "GPU-accelerated physics with real-time results"
    },
    {
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "Deep insights with comprehensive data visualization"
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "Military-grade encryption and compliance"
    }
  ]

  const stats = [
    { value: "10k+", label: "Simulations/Hour" },
    { value: "99.9%", label: "Accuracy" },
    { value: "100ms", label: "Response Time" },
    { value: "150+", label: "Countries" }
  ]

  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden pt-20">
      {/* Background Effects */}
      <BackgroundEffects variant="gradient" />
      
      {/* Interactive Mouse Follower */}
      <motion.div
        className="fixed w-96 h-96 rounded-full bg-gradient-to-r from-blue-400/20 to-purple-600/20 blur-3xl pointer-events-none z-0"
        animate={{
          x: mousePosition.x - 192,
          y: mousePosition.y - 192,
        }}
        transition={{
          type: "spring",
          damping: 50,
          stiffness: 200,
        }}
      />

      <div className="container mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        <div className="text-center">
          {/* Main Heading */}
          <AnimatedContainer variant="slideUp" delay={0.2}>
            <motion.div
              className="inline-flex items-center px-4 py-2 rounded-full bg-gradient-to-r from-blue-500/10 to-purple-500/10 border border-blue-500/20 mb-8"
              whileHover={{ scale: 1.05 }}
            >
              <Sparkles className="w-4 h-4 text-blue-500 mr-2" />
              <span className="text-sm font-medium text-blue-600 dark:text-blue-400">
                Your Engineering Universe
              </span>
            </motion.div>
          </AnimatedContainer>

          <AnimatedContainer variant="slideUp" delay={0.4}>
            <h1 className="text-4xl sm:text-6xl lg:text-7xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-gray-900 via-blue-600 to-purple-600 bg-clip-text text-transparent">
                EnsimuSpace
              </span>
              <br />
              <span className="bg-gradient-to-r from-purple-600 via-pink-600 to-orange-500 bg-clip-text text-transparent">
                AI Simulation Platform
              </span>
            </h1>
          </AnimatedContainer>

          <AnimatedContainer variant="slideUp" delay={0.6}>
            <p className="text-xl sm:text-2xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto leading-relaxed">
              Transform your engineering workflow with{' '}
              <span className="text-blue-600 font-semibold">GPU-accelerated physics</span>,{' '}
              <span className="text-purple-600 font-semibold">AI-assisted modeling</span>, and{' '}
              <span className="text-pink-600 font-semibold">real-time collaboration</span>.
              Build, simulate, and optimize faster than ever before.
            </p>
          </AnimatedContainer>

          {/* CTA Buttons */}
          <AnimatedContainer variant="scale" delay={0.8}>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16">
              <Link href="/auth/login">
                <Button 
                  variant="gradient" 
                  size="xl" 
                  className="group"
                >
                  <Rocket className="w-5 h-5 mr-2 group-hover:rotate-12 transition-transform duration-300" />
                  Enter EnsimuSpace
                  <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
                </Button>
              </Link>
              
              <Button 
                variant="outline" 
                size="xl"
                className="group"
              >
                <Play className="w-5 h-5 mr-2 group-hover:scale-110 transition-transform duration-300" />
                Watch Demo
              </Button>
            </div>
          </AnimatedContainer>

          {/* Features Grid */}
          <StaggeredList className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-16" staggerDelay={0.1}>
            {features.map((feature, index) => (
              <FloatingElement key={index} amplitude={5} duration={3 + index * 0.5}>
                <Card glass="light" className="text-center group cursor-pointer">
                  <motion.div
                    className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform duration-300"
                  >
                    <feature.icon className="w-6 h-6 text-white" />
                  </motion.div>
                  <h3 className="text-lg font-semibold mb-2 text-gray-900 dark:text-white">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-gray-600 dark:text-gray-300">
                    {feature.description}
                  </p>
                </Card>
              </FloatingElement>
            ))}
          </StaggeredList>

          {/* Stats */}
          <AnimatedContainer variant="fadeIn" delay={1.2}>
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <motion.div
                  key={index}
                  className="text-center"
                  initial={{ opacity: 0, scale: 0.5 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: 1.4 + index * 0.1, duration: 0.5 }}
                >
                  <motion.div
                    className="text-3xl lg:text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2"
                    whileHover={{ scale: 1.1 }}
                  >
                    {stat.value}
                  </motion.div>
                  <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                    {stat.label}
                  </div>
                </motion.div>
              ))}
            </div>
          </AnimatedContainer>
        </div>
      </div>

      {/* Scroll Indicator */}
      <motion.div
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 2, duration: 0.8 }}
      >
        <motion.div
          className="w-6 h-10 border-2 border-gray-400 dark:border-gray-600 rounded-full flex justify-center"
          animate={{ y: [0, 8, 0] }}
          transition={{ duration: 1.5, repeat: Infinity }}
        >
          <motion.div
            className="w-1 h-3 bg-gradient-to-b from-blue-500 to-purple-600 rounded-full mt-2"
            animate={{ scaleY: [1, 0.5, 1] }}
            transition={{ duration: 1.5, repeat: Infinity }}
          />
        </motion.div>
      </motion.div>
    </section>
  )
}