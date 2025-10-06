#!/bin/bash

# 🚀 AI Simulation Platform - Quick Start Script
# This script demonstrates how to use the new package.json commands

echo "🚀 AI Simulation Platform - Quick Start"
echo "======================================="

# Colors for better output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}📋 Available Commands:${NC}"
echo ""
echo -e "${GREEN}🚀 Main Commands:${NC}"
echo "  npm start          - Start the entire platform"
echo "  npm run setup      - Complete setup with checks"
echo "  npm run demo       - Run demo and open browser"
echo "  npm stop           - Stop all services"
echo ""
echo -e "${GREEN}🔧 Development:${NC}"
echo "  npm run dev        - Development mode"
echo "  npm test           - Run all tests"
echo "  npm run health     - Check service health"
echo ""
echo -e "${GREEN}🐍 Python Setup:${NC}"
echo "  npm run python:install  - Install Python packages"
echo "  npm run python:check    - Check Python environment"
echo ""
echo -e "${GREEN}🧪 Testing:${NC}"
echo "  npm run test:ai    - Test AI assistant"
echo "  npm run test:cfd   - Test CFD simulation"
echo "  npm run test:python - Test Python execution"
echo ""
echo -e "${GREEN}🛠️ Maintenance:${NC}"
echo "  npm run clean      - Clean all files"
echo "  npm restart        - Restart services"
echo "  npm run logs       - View logs"
echo ""

echo -e "${YELLOW}💡 Quick Start Instructions:${NC}"
echo "1. Run: npm run setup"
echo "2. Run: npm start"
echo "3. Open: http://localhost:50787/notebook/demo"
echo "4. Click the AI Assistant button and ask for help!"
echo ""

echo -e "${BLUE}🎯 Ready to start? Choose an option:${NC}"
echo "1) Complete setup and start"
echo "2) Just start (if already set up)"
echo "3) Show help"
echo "4) Exit"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        echo "🔧 Running complete setup..."
        npm run setup && npm start
        ;;
    2)
        echo "🚀 Starting platform..."
        npm start
        ;;
    3)
        npm run help
        ;;
    4)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac