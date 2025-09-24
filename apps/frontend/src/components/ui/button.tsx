"use client"

import React from 'react'
import { motion } from 'framer-motion'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/utils'

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-xl text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 transform-gpu will-change-transform",
  {
    variants: {
      variant: {
        default: "bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95",
        destructive: "bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95",
        outline: "border-2 border-blue-600/30 bg-white/10 backdrop-blur-sm text-blue-600 hover:bg-blue-600/10 hover:border-blue-600/60",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700",
        ghost: "text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800",
        link: "text-blue-600 underline-offset-4 hover:underline",
        glass: "bg-white/20 backdrop-blur-xl border border-white/20 text-white shadow-2xl hover:bg-white/30 hover:shadow-3xl",
        gradient: "bg-gradient-to-r from-pink-500 via-purple-500 to-indigo-500 text-white shadow-lg hover:shadow-xl hover:scale-105 active:scale-95"
      },
      size: {
        default: "h-11 px-6 py-2",
        sm: "h-8 px-3 text-xs",
        lg: "h-14 px-8 text-base",
        xl: "h-16 px-12 text-lg",
        icon: "h-11 w-11"
      }
    },
    defaultVariants: {
      variant: "default",
      size: "default"
    }
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
  loading?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={loading || props.disabled}
        {...props}
      >
        {loading ? (
          <div className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
        ) : null}
        {children}
      </button>
    )
  }
)

Button.displayName = "Button"

export { Button, buttonVariants }