#!/bin/bash
echo "Starting AI Jupyter Platform..."
cd apps/frontend
echo "Installing dependencies..."
yarn install
echo "Starting Next.js dev server on port 3001..."
yarn dev -p 3001