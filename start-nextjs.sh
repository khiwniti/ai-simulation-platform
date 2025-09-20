#!/bin/bash

# AI Jupyter Platform - Direct Next.js Start
echo "🚀 AI Jupyter Platform - Starting Next.js App"
echo "=============================================="

# Clean up any package manager conflicts
find . -name "package-lock.json" -delete 2>/dev/null || true
find . -name "yarn.lock" -delete 2>/dev/null || true

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

echo "🔥 Starting Next.js development server..."
echo "   Available at: http://localhost:3000"
echo ""

# Start Next.js directly
exec npx next dev