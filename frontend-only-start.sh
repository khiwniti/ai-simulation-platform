#!/bin/bash

# AI Jupyter Platform - Frontend Only Mode
echo "🚀 AI Jupyter Platform - Frontend Direct Start"
echo "=============================================="

# Clean up any package manager conflicts
find . -name "package-lock.json" -delete 2>/dev/null || true

# Check if we can access the frontend directory
if [ -d "apps/frontend" ]; then
    echo "📁 Found frontend directory"
    cd apps/frontend
    
    echo "📦 Installing dependencies..."
    yarn install
    
    echo "🔥 Starting Next.js development server..."
    exec yarn dev
else
    echo "❌ Frontend directory not found!"
    echo "📁 Available directories:"
    ls -la
    exit 1
fi