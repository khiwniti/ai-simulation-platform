#!/bin/bash

# 🚀 EnsimuSpace Full Platform Launcher
# Complete AI Simulation Platform with EnsimuLab, EnsimuNotebook, and Multi-Agent System

echo "🌟 ========================================"
echo "🚀  EnsimuSpace Full Platform Launcher"
echo "🔧  Complete AI Simulation Environment"
echo "========================================="

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed. Please install Node.js 18+ first."
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed. Please install npm first."
        exit 1
    fi
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed. Please install Python 3.8+ first."
        exit 1
    fi
    
    print_success "All dependencies are available"
}

# Install frontend dependencies
install_frontend() {
    print_status "Installing frontend dependencies..."
    cd apps/frontend
    
    if [ ! -d "node_modules" ]; then
        npm install
        if [ $? -eq 0 ]; then
            print_success "Frontend dependencies installed"
        else
            print_error "Failed to install frontend dependencies"
            exit 1
        fi
    else
        print_success "Frontend dependencies already installed"
    fi
    
    cd ../..
}

# Install backend dependencies
install_backend() {
    print_status "Installing backend dependencies..."
    cd apps/backend
    
    if [ ! -d "node_modules" ]; then
        npm install
        if [ $? -eq 0 ]; then
            print_success "Backend dependencies installed"
        else
            print_error "Failed to install backend dependencies"
            exit 1
        fi
    else
        print_success "Backend dependencies already installed"
    fi
    
    cd ../..
}

# Setup Python environment for AI services
setup_python_env() {
    print_status "Setting up Python environment for AI services..."
    
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Python virtual environment created"
    fi
    
    source venv/bin/activate
    pip install -q --upgrade pip
    
    # Install AI and simulation dependencies
    pip install -q fastapi uvicorn numpy matplotlib plotly scipy pandas scikit-learn
    
    print_success "Python AI environment ready"
}

# Start the full platform
start_platform() {
    print_status "Starting EnsimuSpace Full Platform..."
    
    # Start backend in background
    print_status "Starting backend server..."
    cd apps/backend
    npm run dev &
    BACKEND_PID=$!
    cd ../..
    
    # Give backend time to start
    sleep 3
    
    # Start frontend in background
    print_status "Starting frontend server..."
    cd apps/frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
    
    # Give frontend time to start
    sleep 5
    
    print_success "EnsimuSpace Platform is now running!"
    echo ""
    echo "🌟 ========================================"
    echo "🚀  EnsimuSpace Platform Access URLs"
    echo "========================================="
    echo "🏠 Main Platform:     http://localhost:3000"
    echo "🧪 EnsimuLab:         http://localhost:3000/lab"
    echo "📝 EnsimuNotebook:    http://localhost:3000/notebook"
    echo "🔬 Simulations:       http://localhost:3000/simulations"
    echo "🔌 Backend API:       http://localhost:3001"
    echo "📚 API Docs:          http://localhost:3001/docs"
    echo "========================================="
    echo ""
    echo "🎯 Features Available:"
    echo "✅ EnsimuLab - Project management and collaboration"
    echo "✅ EnsimuNotebook - AI-enhanced Jupyter-like notebooks"
    echo "✅ Multi-Agent AI System - Physics, visualization, optimization"
    echo "✅ 3D Visualization Engine - Matplotlib, Plotly, PyVista"
    echo "✅ Real-time Chat Assistant - CFD simulation templates"
    echo "✅ Code Execution - Python with health monitoring"
    echo "✅ Data Persistence - Workbook and notebook management"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Function to cleanup on exit
    cleanup() {
        print_warning "Shutting down EnsimuSpace Platform..."
        kill $BACKEND_PID 2>/dev/null
        kill $FRONTEND_PID 2>/dev/null
        print_success "Platform stopped successfully"
        exit 0
    }
    
    # Set trap to cleanup on Ctrl+C
    trap cleanup SIGINT
    
    # Wait for user to stop the platform
    while true; do
        sleep 1
    done
}

# Main execution flow
main() {
    print_status "Initializing EnsimuSpace Full Platform..."
    
    check_dependencies
    install_frontend
    install_backend
    setup_python_env
    start_platform
}

# Run the main function
main "$@"