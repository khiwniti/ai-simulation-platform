#!/bin/bash
# Frontend-only startup script
echo "Starting AI Jupyter Frontend (bypassing backend)..."

# Install frontend dependencies
cd apps/frontend
yarn install

# Start the frontend development server
yarn dev