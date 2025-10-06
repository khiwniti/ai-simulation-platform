#!/bin/bash

# Simple frontend startup script that bypasses workspace issues
echo "🚀 Starting AI Jupyter Frontend..."
echo "=================================="

# Remove any conflicting lock files
rm -f package-lock.json yarn.lock
rm -f apps/frontend/package-lock.json apps/frontend/yarn.lock

# Navigate to frontend and start
cd apps/frontend
echo "📦 Installing dependencies..."
npm install

echo "🔥 Starting development server..."
npm run dev