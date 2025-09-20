#!/bin/bash

# Simple startup script that bypasses workspace issues entirely
echo "🚀 AI Jupyter Platform - Frontend Only Mode"
echo "==========================================="

# Clean up any conflicting files
rm -f package-lock.json yarn.lock
find . -name "package-lock.json" -delete
find . -name "yarn.lock" -delete

# Start frontend directly without workspace resolution
cd apps/frontend
echo "📦 Installing dependencies..."
npm install --no-package-lock

echo "🔥 Starting development server..."
exec npm run dev