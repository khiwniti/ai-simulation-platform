"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { cn, glassmorphism } from '../../lib/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  glass?: keyof typeof glassmorphism
  hover?: boolean
  gradient?: boolean
}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, glass, hover = true, gradient = false, children, ...props }, ref) => {
    const baseClasses = "rounded-2xl p-6 transition-all duration-300"
    const glassClasses = glass ? glassmorphism[glass] : ""
    const gradientClasses = gradient ? "bg-gradient-to-br from-white/5 to-white/20" : "bg-white dark:bg-gray-900"
    
    return (
      <div
        ref={ref}
        className={cn(
          baseClasses,
          glass ? glassClasses : gradientClasses,
          glass ? "" : "border border-gray-200 dark:border-gray-800 shadow-lg",
          hover ? "hover:shadow-xl hover:-translate-y-1 transform" : "",
          className
        )}
        {...props}
      >
        {children}
      </div>
    )
  }
)

Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex flex-col space-y-1.5 pb-6", className)}
      {...props}
    />
  )
)

CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => (
    <h3
      ref={ref}
      className={cn("font-semibold leading-none tracking-tight text-xl", className)}
      {...props}
    />
  )
)

CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => (
    <p
      ref={ref}
      className={cn("text-sm text-gray-600 dark:text-gray-400", className)}
      {...props}
    />
  )
)

CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div ref={ref} className={cn("", className)} {...props} />
  )
)

CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => (
    <div
      ref={ref}
      className={cn("flex items-center pt-6", className)}
      {...props}
    />
  )
)

CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }