#!/bin/bash

# Beta Deployment Script for EnsimuNotebook
# Simplified AI-Enhanced Engineering Simulation Platform

echo "🚀 EnsimuNotebook Beta - Starting..."
echo "============================================"
echo "AI-Enhanced Engineering Simulation Platform"
echo "Inspired by luminarycloud.com architecture"
echo "============================================"

# Set up environment
export NODE_ENV=development
export NEXT_PUBLIC_APP_NAME="EnsimuNotebook Beta"
export NEXT_PUBLIC_APP_DESCRIPTION="AI-Enhanced Engineering Simulation"

# Clean up previous installations
echo "🧹 Cleaning previous installations..."
rm -f package-lock.json yarn.lock
rm -rf node_modules
find . -name "package-lock.json" -delete
find . -name "yarn.lock" -delete
find . -name "node_modules" -type d -exec rm -rf {} + 2>/dev/null || true

# Navigate to frontend
cd apps/frontend

echo "📦 Installing frontend dependencies..."
npm install --no-package-lock --legacy-peer-deps

# Check if installation succeeded
if [ $? -ne 0 ]; then
    echo "❌ Frontend installation failed. Trying alternative approach..."
    rm -rf node_modules
    npm install --force --no-package-lock
fi

echo "🔧 Building optimized version..."
npm run build

echo "🌟 Starting EnsimuNotebook Beta..."
echo ""
echo "🎯 Features enabled:"
echo "  ✓ AI-Enhanced Jupyter Notebooks"
echo "  ✓ Engineering Simulation Focus"
echo "  ✓ Physics Visualization"
echo "  ✓ Real-time Code Assistance"
echo "  ✓ Interactive 3D Simulations"
echo ""
echo "🌐 Access your beta at:"
echo "  → http://localhost:4000"
echo "  → http://localhost:50787 (if available)"
echo ""
echo "📝 To create a new notebook, go to:"
echo "  → http://localhost:4000/notebook/demo"
echo ""

# Start the server
exec npm run dev