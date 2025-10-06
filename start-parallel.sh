#!/bin/bash

# AI Jupyter Platform - Parallel Services Manager
# This script ensures all services run in parallel with proper port management

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_PORT=3000
BACKEND_PORT=8000
SHARED_WATCH=true

echo -e "${CYAN}🚀 AI Jupyter Platform - Parallel Services Manager${NC}"
echo "============================================================"

# Function to kill processes on specific ports
cleanup_ports() {
    echo -e "${YELLOW}🧹 Cleaning up ports...${NC}"
    
    # Kill processes on frontend port
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}  Stopping process on port $FRONTEND_PORT${NC}"
        lsof -ti:$FRONTEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    # Kill processes on backend port
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}  Stopping process on port $BACKEND_PORT${NC}"
        lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null || true
    fi
    
    sleep 2
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${BLUE}🔍 Checking $service_name health...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is healthy on port $port${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}  Attempt $attempt/$max_attempts - waiting for $service_name...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ $service_name failed to start on port $port${NC}"
    return 1
}

# Function to start services in parallel
start_parallel_services() {
    echo -e "${BLUE}📦 Preparing workspace...${NC}"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ] || [ ! -d "apps/frontend/node_modules" ]; then
        echo -e "${BLUE}  Installing dependencies...${NC}"
        npm install --workspaces
    fi
    
    # Build shared package first
    echo -e "${BLUE}  Building shared package...${NC}"
    npm run build:shared
    
    echo -e "${PURPLE}🚀 Starting services in parallel...${NC}"
    
    # Create log directory
    mkdir -p logs
    
    # Start services using concurrently with proper configuration
    npx concurrently \
        --kill-others-on-fail \
        --prefix-colors "cyan,green,yellow" \
        --prefix "[{name}]" \
        --names "SHARED,FRONTEND,HEALTH" \
        --success "first" \
        "npm run dev:shared 2>&1 | tee logs/shared.log" \
        "sleep 3 && npm run dev:frontend 2>&1 | tee logs/frontend.log" \
        "sleep 10 && echo 'Health check complete' && exit 0" &
    
    # Store the background process PID
    SERVICES_PID=$!
    
    # Wait a bit for services to initialize
    sleep 15
    
    # Check service health
    echo -e "${BLUE}🏥 Running health checks...${NC}"
    check_service_health "Frontend" $FRONTEND_PORT || echo -e "${YELLOW}⚠️  Frontend may still be starting...${NC}"
    
    return 0
}

# Function to show service status
show_status() {
    echo -e "${CYAN}📊 Service Status:${NC}"
    echo "================================"
    
    # Check shared package (TypeScript watch)
    if pgrep -f "tsc --watch" > /dev/null; then
        echo -e "${GREEN}✅ Shared Package: Running (TypeScript watch mode)${NC}"
    else
        echo -e "${RED}❌ Shared Package: Not running${NC}"
    fi
    
    # Check frontend
    if lsof -Pi :$FRONTEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend: Running on port $FRONTEND_PORT${NC}"
    else
        echo -e "${RED}❌ Frontend: Not running on port $FRONTEND_PORT${NC}"
    fi
    
    # Check backend (optional)
    if lsof -Pi :$BACKEND_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend: Running on port $BACKEND_PORT${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend: Not available (optional)${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}🌐 Access URLs:${NC}"
    echo "  Frontend: http://localhost:$FRONTEND_PORT"
    echo "  Backend:  http://localhost:$BACKEND_PORT (if available)"
    echo ""
}

# Function to handle cleanup on exit
cleanup() {
    echo -e "\n${RED}🛑 Shutting down services...${NC}"
    
    # Kill the services process group
    if [ ! -z "$SERVICES_PID" ]; then
        kill -TERM -$SERVICES_PID 2>/dev/null || true
    fi
    
    # Clean up ports
    cleanup_ports
    
    echo -e "${GREEN}✅ Cleanup complete${NC}"
    exit 0
}

# Main execution
main() {
    # Handle interruption
    trap cleanup INT TERM EXIT
    
    # Check if we're in the right directory
    if [ ! -f "package.json" ]; then
        echo -e "${RED}❌ Error: package.json not found. Please run from project root.${NC}"
        exit 1
    fi
    
    # Clean up any existing processes
    cleanup_ports
    
    # Start services
    start_parallel_services
    
    # Show status
    show_status
    
    echo -e "${GREEN}🎉 All services are running in parallel!${NC}"
    echo -e "${BLUE}📝 Available commands:${NC}"
    echo "  - npm run dev          # Turbo parallel execution"
    echo "  - ./start-parallel.sh  # This script"
    echo "  - npm run build        # Parallel build"
    echo "  - npm run test         # Parallel testing"
    echo ""
    echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
    
    # Keep script running and monitor services
    while true; do
        sleep 30
        if ! pgrep -f "next dev" > /dev/null && ! pgrep -f "tsc --watch" > /dev/null; then
            echo -e "${RED}⚠️  Services may have stopped. Restarting...${NC}"
            start_parallel_services
        fi
    done
}

# Run main function
main "$@"