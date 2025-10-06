#!/bin/bash

# AI Jupyter Platform - Ultimate Fix
echo "🚀 AI Jupyter Platform - Frontend Ready!"
echo "======================================"

# Ensure we're in the right directory
if [ ! -d "apps/frontend" ]; then
    echo "❌ Frontend directory not found!"
    exit 1
fi

# Clean up any package manager conflicts
echo "🧹 Cleaning up package manager conflicts..."
find . -name "package-lock.json" -delete 2>/dev/null || true
find . -name "yarn.lock" -delete 2>/dev/null || true

# Navigate to frontend and start
echo "📁 Navigating to frontend directory..."
cd apps/frontend

echo "📦 Ensuring dependencies are installed..."
npm install --silent

echo "🔥 Starting Next.js development server..."
echo "   Frontend will be available at: http://localhost:3000"
echo "   Press Ctrl+C to stop the server"
echo ""

# Start the development server
exec npm run dev