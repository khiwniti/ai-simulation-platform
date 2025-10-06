#!/bin/bash

# 🚀 AI Simulation Platform - Beta Release v1.0 Deployment Script

echo "🚀 Starting AI Simulation Platform Beta Deployment..."
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    print_error "Please run this script from the root directory of the project"
    exit 1
fi

# Check Node.js version
print_info "Checking Node.js version..."
NODE_VERSION=$(node --version 2>/dev/null)
if [ $? -eq 0 ]; then
    print_status "Node.js found: $NODE_VERSION"
else
    print_error "Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>/dev/null)
if [ $? -eq 0 ]; then
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check if on beta branch
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null)
if [ "$CURRENT_BRANCH" != "beta-release-1.0" ]; then
    print_warning "Not on beta-release-1.0 branch. Current branch: $CURRENT_BRANCH"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Switching to beta-release-1.0 branch..."
        git checkout beta-release-1.0
    fi
fi

# Install dependencies
print_info "Installing Node.js dependencies..."
yarn install
if [ $? -eq 0 ]; then
    print_status "Node.js dependencies installed"
else
    print_error "Failed to install Node.js dependencies"
    exit 1
fi

# Install Python dependencies
print_info "Installing Python dependencies..."
pip3 install numpy matplotlib plotly pyvista vtk scipy scikit-image
if [ $? -eq 0 ]; then
    print_status "Python dependencies installed"
else
    print_warning "Some Python dependencies may have failed. Continuing..."
fi

# Create logs directory
mkdir -p logs

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        return 1
    else
        return 0
    fi
}

# Check ports
print_info "Checking port availability..."
if ! check_port 4100; then
    print_warning "Port 4100 is already in use. Backend may conflict."
fi

if ! check_port 50787; then
    print_warning "Port 50787 is already in use. Frontend may conflict."
fi

# Start backend
print_info "Starting backend server..."
cd apps/backend
nohup node src/server.js > ../../logs/backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../../logs/backend.pid
cd ../..

# Wait for backend to start
print_info "Waiting for backend to initialize..."
sleep 3

# Check if backend is running
if ps -p $BACKEND_PID > /dev/null; then
    print_status "Backend server started (PID: $BACKEND_PID)"
else
    print_error "Backend server failed to start"
    exit 1
fi

# Test backend health
print_info "Testing backend health..."
HEALTH_CHECK=$(curl -s http://localhost:4100/health 2>/dev/null)
if [ $? -eq 0 ]; then
    print_status "Backend health check passed"
else
    print_warning "Backend health check failed, but continuing..."
fi

# Start frontend
print_info "Starting frontend server..."
cd apps/frontend
nohup npm run dev > ../../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../../logs/frontend.pid
cd ../..

# Wait for frontend to start
print_info "Waiting for frontend to initialize..."
sleep 5

# Check if frontend is running
if ps -p $FRONTEND_PID > /dev/null; then
    print_status "Frontend server started (PID: $FRONTEND_PID)"
else
    print_error "Frontend server failed to start"
    exit 1
fi

# Test basic API endpoints
print_info "Testing API endpoints..."

# Test Python execution
print_info "Testing Python execution..."
PYTHON_TEST=$(curl -s -X POST http://localhost:4100/api/notebooks/execute \
  -H "Content-Type: application/json" \
  -d '{"code": "print(\"Hello from Python!\")"}' 2>/dev/null)

if echo "$PYTHON_TEST" | grep -q "success.*true"; then
    print_status "Python execution test passed"
else
    print_warning "Python execution test failed"
fi

# Test AI chat
print_info "Testing AI chat..."
AI_TEST=$(curl -s -X POST http://localhost:4100/api/ai/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "notebookContext": {}, "conversationHistory": []}' 2>/dev/null)

if echo "$AI_TEST" | grep -q "success.*true"; then
    print_status "AI chat test passed"
else
    print_warning "AI chat test failed"
fi

# Create status file
cat > beta-status.json << EOF
{
  "version": "1.0.0-beta",
  "status": "running",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "services": {
    "backend": {
      "pid": $BACKEND_PID,
      "port": 4100,
      "url": "http://localhost:4100"
    },
    "frontend": {
      "pid": $FRONTEND_PID,
      "port": 50787,
      "url": "http://localhost:50787"
    }
  },
  "endpoints": {
    "main": "http://localhost:50787",
    "notebook": "http://localhost:50787/notebook/demo",
    "api": "http://localhost:4100",
    "health": "http://localhost:4100/health"
  }
}
EOF

# Display deployment summary
echo ""
echo "🎉 Beta Deployment Complete!"
echo "=============================="
echo ""
print_status "Frontend: http://localhost:50787"
print_status "Notebook: http://localhost:50787/notebook/demo"
print_status "Backend API: http://localhost:4100"
print_status "Health Check: http://localhost:4100/health"
echo ""
print_info "Process IDs:"
echo "  Backend PID: $BACKEND_PID"
echo "  Frontend PID: $FRONTEND_PID"
echo ""
print_info "Log files:"
echo "  Backend logs: logs/backend.log"
echo "  Frontend logs: logs/frontend.log"
echo ""
print_info "To stop services:"
echo "  kill $BACKEND_PID $FRONTEND_PID"
echo "  or run: ./stop-beta.sh"
echo ""

# Create stop script
cat > stop-beta.sh << 'EOF'
#!/bin/bash
echo "🛑 Stopping AI Simulation Platform Beta..."

if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "✅ Backend stopped (PID: $BACKEND_PID)"
    fi
    rm logs/backend.pid
fi

if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "✅ Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm logs/frontend.pid
fi

# Kill any remaining processes on our ports
lsof -ti:4100 | xargs kill -9 2>/dev/null
lsof -ti:50787 | xargs kill -9 2>/dev/null

echo "🎯 All services stopped"
EOF

chmod +x stop-beta.sh

print_status "Deployment script created: stop-beta.sh"
echo ""
print_info "🚀 Beta v1.0 is now running! Test the external flow simulation:"
echo "   1. Open http://localhost:50787/notebook/demo"
echo "   2. Click the AI Assistant button (💬)"
echo "   3. Ask: 'Help me simulate external flow around a sphere'"
echo "   4. Insert and run the generated code"
echo ""
print_status "Happy simulating! 🧬⚡🔬"