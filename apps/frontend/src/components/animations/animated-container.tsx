"use client"

import React from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface AnimatedContainerProps {
  children: React.ReactNode
  className?: string
  variant?: 'fadeIn' | 'slideUp' | 'slideLeft' | 'slideRight' | 'scale' | 'bounce'
  delay?: number
  duration?: number
  stagger?: number
}

const variants = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 }
  },
  slideUp: {
    initial: { opacity: 0, y: 50 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -50 }
  },
  slideLeft: {
    initial: { opacity: 0, x: 50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -50 }
  },
  slideRight: {
    initial: { opacity: 0, x: -50 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: 50 }
  },
  scale: {
    initial: { opacity: 0, scale: 0.8 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.8 }
  },
  bounce: {
    initial: { opacity: 0, scale: 0.3 },
    animate: { 
      opacity: 1, 
      scale: 1
    },
    exit: { opacity: 0, scale: 0.3 }
  }
}

export function AnimatedContainer({ 
  children, 
  className, 
  variant = 'fadeIn', 
  delay = 0, 
  duration = 0.5,
  stagger = 0
}: AnimatedContainerProps) {
  return (
    <motion.div
      className={className}
      variants={variants[variant]}
      initial="initial"
      animate="animate"
      exit="exit"
      transition={{
        duration: variant === 'bounce' ? undefined : duration,
        delay,
        staggerChildren: stagger,
        ease: variant === 'bounce' ? undefined : "easeOut",
        type: variant === 'bounce' ? "spring" : undefined,
        damping: variant === 'bounce' ? 10 : undefined,
        stiffness: variant === 'bounce' ? 400 : undefined
      }}
    >
      {children}
    </motion.div>
  )
}

export function StaggeredList({ 
  children, 
  className,
  staggerDelay = 0.1 
}: { 
  children: React.ReactNode
  className?: string
  staggerDelay?: number 
}) {
  return (
    <motion.div
      className={className}
      initial="initial"
      animate="animate"
      variants={{
        initial: {},
        animate: {
          transition: {
            staggerChildren: staggerDelay
          }
        }
      }}
    >
      {React.Children.map(children, (child, index) => (
        <motion.div
          key={index}
          variants={{
            initial: { opacity: 0, y: 20 },
            animate: { opacity: 1, y: 0 }
          }}
          transition={{ duration: 0.5, ease: "easeOut" }}
        >
          {child}
        </motion.div>
      ))}
    </motion.div>
  )
}

export function FadeInWhenVisible({ 
  children, 
  className,
  threshold = 0.1 
}: { 
  children: React.ReactNode
  className?: string
  threshold?: number
}) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: 50 }}
      whileInView={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, ease: "easeOut" }}
      viewport={{ once: true, amount: threshold }}
    >
      {children}
    </motion.div>
  )
}

export function FloatingElement({ 
  children, 
  className,
  amplitude = 10,
  duration = 3 
}: { 
  children: React.ReactNode
  className?: string
  amplitude?: number
  duration?: number
}) {
  return (
    <motion.div
      className={className}
      animate={{
        y: [-amplitude, amplitude, -amplitude],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      {children}
    </motion.div>
  )
}

export function PulsingElement({ 
  children, 
  className,
  scale = 1.05,
  duration = 2 
}: { 
  children: React.ReactNode
  className?: string
  scale?: number
  duration?: number
}) {
  return (
    <motion.div
      className={className}
      animate={{
        scale: [1, scale, 1],
      }}
      transition={{
        duration,
        repeat: Infinity,
        ease: "easeInOut"
      }}
    >
      {children}
    </motion.div>
  )
}