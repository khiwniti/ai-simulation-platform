# 🚀 AI Simulation Platform - Quick Start Guide

## 💨 Fastest Way to Start

```bash
# 1️⃣ One-command setup and start
npm start

# 2️⃣ If you need full setup first
npm run setup

# 3️⃣ Open your browser
# http://localhost:50787/notebook/demo
```

## 📋 Main Commands

| Command | Description | What it does |
|---------|-------------|--------------|
| `npm start` | **Start everything** | Launches backend + frontend |
| `npm run setup` | **Complete setup** | Install deps + check Python |
| `npm run demo` | **Run demo** | Start platform + open demo |
| `npm stop` | **Stop services** | Kill all running processes |

## 🎯 Development Commands

### 🔧 Development Mode
```bash
npm run dev           # Development mode (both services)
npm run dev:backend   # Backend only
npm run dev:frontend  # Frontend only
```

### 🧪 Testing
```bash
npm test              # Run all tests
npm run test:ai       # Test AI assistant
npm run test:cfd      # Test CFD simulation  
npm run test:python   # Test Python execution
npm run health        # Check service health
```

### 🐍 Python Environment
```bash
npm run python:install   # Install Python packages
npm run python:check     # Verify Python setup
npm run python:test      # Test Python environment
```

## 📊 What Gets Started

When you run `npm start`, this happens:

```
🔧 BACKEND (Port 4100)
├── Node.js/Express server
├── Python code executor
├── AI chat endpoints
├── 3D visualization engine
└── Health monitoring

🖥️ FRONTEND (Port 50787)  
├── Next.js React app
├── Jupyter-like notebook interface
├── AI chat assistant
├── 3D plot rendering
└── Interactive UI
```

## 🎮 Interactive Demo

### 1. Start the Platform
```bash
npm start
```

### 2. Open Demo Notebook
Navigate to: http://localhost:50787/notebook/demo

### 3. Test AI Assistant
- Click the AI Assistant button (💬)
- Ask: "Help me simulate external flow around a sphere"
- Insert the generated code
- Run and see 3D CFD simulation!

### 4. Try Different Simulations
- "Create a heat transfer analysis"
- "Show me structural beam analysis"
- "Generate a 3D visualization"

## 🛠️ Maintenance Commands

```bash
npm restart           # Restart all services
npm run clean         # Clean everything
npm run logs          # View service logs
npm run health        # Check if services are running
```

## 📈 Monitoring & Debugging

### Check Service Health
```bash
npm run health        # Quick health check
npm run logs          # View real-time logs
npm run logs:backend  # Backend logs only
npm run logs:frontend # Frontend logs only
```

### URLs to Check
- **Frontend**: http://localhost:50787
- **Backend API**: http://localhost:4100
- **Health Check**: http://localhost:4100/health
- **Demo Notebook**: http://localhost:50787/notebook/demo

## 🔧 Advanced Usage

### Custom Port Configuration
The ports are defined in `package.json`:
```json
"config": {
  "ports": {
    "frontend": 50787,
    "backend": 4100
  }
}
```

### Environment Setup
```bash
# Complete environment setup
npm run setup

# Individual components
npm run install:all     # Install all dependencies
npm run install:python  # Install Python packages
npm run python:check    # Verify Python environment
```

### Production Build
```bash
npm run build           # Build frontend for production
npm run build:all       # Build everything
```

## 🐛 Troubleshooting

### Common Issues

**Port Already in Use**
```bash
npm run clean    # Kill existing processes
npm restart      # Restart fresh
```

**Python Packages Missing**
```bash
npm run python:install  # Reinstall Python packages
npm run python:check    # Verify installation
```

**Services Won't Start**
```bash
npm run health   # Check what's running
npm run logs     # See error messages
npm run clean    # Clean and restart
```

### Verification Commands
```bash
# Test individual components
npm run test:ai       # AI assistant working?
npm run test:python   # Python execution working?
npm run test:cfd      # CFD simulation working?
npm run health        # All services healthy?
```

## 📦 Package.json Scripts Explained

Our `package.json` is organized with emojis for easy navigation:

- 🚀 **Main Commands**: Essential daily commands
- 🎯 **Beta Release**: Beta-specific functionality  
- 🔧 **Development**: Dev-only commands
- 📦 **Installation**: Dependency management
- 🐍 **Python Setup**: Python environment
- 🧪 **Testing**: All testing commands
- 🔍 **Health & Monitoring**: Service monitoring
- 🛠️ **Maintenance**: Cleanup and restart
- 📊 **Demo & Examples**: Demo functionality

## 🎊 Success Indicators

When everything is working correctly, you should see:

✅ **Backend Health**: http://localhost:4100/health returns OK  
✅ **Frontend Loading**: http://localhost:50787 shows the app  
✅ **Python Execution**: Can run Python code in notebook  
✅ **AI Assistant**: Chat responds with code suggestions  
✅ **3D Visualization**: Plots render correctly  
✅ **CFD Simulation**: External flow simulation works  

## 💡 Quick Help

```bash
npm run help    # Show command summary
./start-platform.sh  # Interactive startup script
```

---

**🎯 One Command to Rule Them All:**
```bash
npm start
```

*Then open http://localhost:50787/notebook/demo and start simulating!* 🧬⚡🔬