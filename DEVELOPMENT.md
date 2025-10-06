# Development Workflow

This document explains how to set up and run the AI Jupyter Notebook platform for development.

## Prerequisites

- Node.js 18+ and npm 9+
- Python 3.8+ with pip
- Docker and Docker Compose (optional, for containerized development)

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Run the automated development setup script
./dev-start.sh
```

### Option 2: Manual Setup

1. **Install all dependencies:**
   ```bash
   npm run setup
   ```

2. **Build shared packages:**
   ```bash
   npm run build:shared
   ```

3. **Start development servers:**
   ```bash
   npm run dev
   ```

## Available Scripts

### Installation Scripts
- `npm run setup` - Install all dependencies (npm + Python)
- `npm run install:all` - Install npm dependencies for all workspaces
- `npm run install:backend` - Install Python dependencies for backend
- `npm run install:frontend` - Install frontend dependencies only
- `npm run install:shared` - Install shared package dependencies only

### Development Scripts
- `npm run dev` - Start all development servers in parallel (uses Turbo)
- `npm run dev:frontend` - Start only the frontend development server
- `npm run dev:backend` - Start only the backend development server
- `npm run dev:shared` - Start shared package in watch mode

### Production Scripts
- `npm run build` - Build all packages for production
- `npm run build:all` - Build frontend and shared packages
- `npm run start:all` - Start production servers in parallel
- `npm run start:frontend` - Start frontend production server
- `npm run start:backend` - Start backend production server

### Testing Scripts
- `npm run test` - Run all tests (uses Turbo)
- `npm run test:all` - Run all tests in parallel
- `npm run test:frontend` - Run frontend tests only
- `npm run test:backend` - Run backend tests only
- `npm run test:shared` - Run shared package tests only

### Utility Scripts
- `npm run lint` - Lint all packages
- `npm run type-check` - Type check all TypeScript packages
- `npm run clean` - Clean all build artifacts
- `npm run clean:all` - Clean build artifacts and node_modules

### Docker Scripts
- `npm run docker:up` - Start services with Docker Compose
- `npm run docker:down` - Stop Docker Compose services
- `npm run docker:build` - Build Docker images
- `npm run docker:logs` - View Docker Compose logs

## Development URLs

When running in development mode:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Backend API Docs**: http://localhost:8000/docs

## Architecture

This is a monorepo managed with:
- **Turborepo**: For task orchestration and caching
- **npm workspaces**: For dependency management
- **concurrently**: For running multiple services in parallel

### Workspace Structure
```
/
├── apps/
│   ├── frontend/     # Next.js frontend application
│   └── backend/      # FastAPI backend application
├── packages/
│   └── shared/       # Shared TypeScript types and utilities
├── package.json      # Root package.json with workspace configuration
└── turbo.json        # Turborepo configuration
```

## Troubleshooting

### Common Issues

1. **Port conflicts**: Make sure ports 3000 (frontend) and 8000 (backend) are available
2. **Python dependencies**: Ensure you have Python 3.8+ and pip installed
3. **Node version**: Ensure you're using Node.js 18 or higher

### Clean Installation
If you encounter dependency issues:
```bash
npm run clean:all
npm run setup
```

### Individual Service Debugging
To debug issues with specific services, run them individually:
```bash
# Frontend only
npm run dev:frontend

# Backend only
npm run dev:backend

# Shared package only
npm run dev:shared
```