#!/bin/bash

# AI Jupyter Platform - Frontend Direct Start
echo "🚀 Starting AI Jupyter Platform (Frontend Direct Mode)"
echo "===================================================="

# Remove any conflicting lock files
rm -f package-lock.json yarn.lock
rm -f apps/frontend/package-lock.json apps/frontend/yarn.lock

# Check if frontend directory exists
if [ ! -d "apps/frontend" ]; then
    echo "❌ Frontend directory not found!"
    exit 1
fi

echo "📁 Found frontend directory"
echo "📦 Installing frontend dependencies..."

# Install dependencies directly in frontend
cd apps/frontend
npm install

echo "🔥 Starting Next.js development server..."
exec npm run dev