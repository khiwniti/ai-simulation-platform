# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Architecture

This is a **dual-platform engineering simulation system** with two distinct architectures:

### Primary Platform: AI-Jupyter Simulation Platform
**Location**: `apps/` directory (monorepo structure)
- **Frontend**: Next.js React app on port 4000 (`apps/frontend/`)
- **Backend**: Node.js Express API on port 4100 (`apps/backend/`)
- **Shared**: Common types and utilities (`packages/shared/`)

### AWS AI Agent Platform
**Location**: `aws-agent-backend/` and `aws-frontend/` directories
- **Backend**: Python FastAPI on port 57890 (`aws-agent-backend/`)
- **Frontend**: Next.js React app on port 3000 (`aws-frontend/`)

## Development Commands

### Project Setup
```bash
# Install all dependencies (monorepo + individual apps)
npm run setup

# Install specific workspaces
npm run install:frontend
npm run install:backend
npm run install:shared
```

### Development Servers
```bash
# Start all services
npm run dev

# Start individual services
npm run dev:frontend    # Next.js on port 4000
npm run dev:backend     # Express API on port 4100

# AWS Platform (separate)
cd aws-agent-backend && python main.py     # FastAPI on port 57890
cd aws-frontend && npm run dev              # Next.js on port 3000
```

### Testing
```bash
# Run all tests
npm run test

# Individual test suites
npm run test:frontend
npm run test:backend
npm run test:shared

# Backend tests (Node.js)
cd apps/backend && npm test

# AWS Backend tests (Python)
cd aws-agent-backend && pytest
```

### Build & Deployment
```bash
# Build all packages
npm run build

# Build individual packages
npm run build:frontend
npm run build:shared

# Docker (AWS platform)
npm run docker:up
npm run docker:build
```

### Database Operations (Node.js Backend)
```bash
# Database migration
npm run migrate

# Seed test data
npm run seed

# Clear database
npm run clear-data
```

## Key Technologies

### Frontend Stack
- **Framework**: Next.js 14 with TypeScript
- **UI**: TailwindCSS, Radix UI, Headless UI
- **3D Graphics**: Three.js, React Three Fiber, Cannon.js (physics)
- **State**: Zustand for state management
- **Real-time**: Socket.IO client
- **Editor**: Monaco Editor (VS Code-style)

### Backend Stack (Node.js)
- **Framework**: Express.js with Socket.IO
- **Database**: PostgreSQL with direct SQL queries
- **Auth**: JWT with bcryptjs
- **Validation**: Joi schemas
- **Logging**: Winston
- **Security**: Helmet, CORS, rate limiting

### Backend Stack (Python/AWS)
- **Framework**: FastAPI with structured logging
- **AWS Services**: Bedrock AgentCore, Nova Act
- **Physics**: NumPy, SciPy, SymPy, PyVista
- **Real-time**: WebSocket support
- **AI**: Multi-agent orchestration system

## Core Features Architecture

### 1. Multi-Agent AI System (AWS Platform)
- **Agent Types**: Physics, Design, Optimization, Materials, Project Manager
- **Orchestration**: Central coordinator with Bedrock AgentCore
- **Location**: `aws-agent-backend/app/agents/`

### 2. Jupyter-Style Notebooks
- **Cell Types**: Code, Markdown, Physics, Visualization
- **Auto-save**: Automatic persistence with version control
- **Real-time**: Collaborative editing via WebSocket
- **Location**: `apps/frontend/src/components/notebook/`

### 3. Physics Simulation Engine
- **3D Rendering**: Three.js with React Three Fiber
- **Physics**: Cannon.js for real-time physics simulation
- **Interactive**: Drag-and-drop object library
- **Location**: `apps/frontend/src/components/visualization/`

### 4. Real-time Collaboration
- **WebSocket**: Socket.IO for live updates
- **Rooms**: Project-based collaboration spaces
- **Sync**: Real-time cursor tracking and conflict resolution
- **Location**: `apps/backend/src/server.js` (Socket.IO handlers)

### 5. AI Code Assistance
- **Providers**: OpenAI GPT-4, Anthropic Claude support
- **Context**: AST parsing for intelligent suggestions
- **Inline**: Monaco Editor integration
- **Location**: `apps/frontend/src/services/` and `apps/backend/src/routes/ai.js`

## Important File Locations

### Configuration
- **Environment**: `.env.example` files in each app directory
- **TypeScript**: `tsconfig.json` in workspace packages
- **Tailwind**: `tailwind.config.js` in frontend apps
- **ESLint**: `.eslintrc.json` in individual packages

### Database (Node.js)
- **Connection**: `apps/backend/src/database/connection.js`
- **Migrations**: `apps/backend/src/database/migrate.js`
- **Schema**: SQL schema files in database directory

### API Routes (Node.js)
- **Auth**: `apps/backend/src/routes/auth.js`
- **Notebooks**: `apps/backend/src/routes/notebooks.js`
- **AI**: `apps/backend/src/routes/ai.js`
- **Simulations**: `apps/backend/src/routes/simulations.js`

### API Routes (Python/AWS)
- **Demo**: `aws-agent-backend/app/api/demo.py`
- **Agents**: `aws-agent-backend/app/api/agents.py`
- **Projects**: `aws-agent-backend/app/api/projects.py`

### Frontend Components
- **Notebooks**: `apps/frontend/src/components/notebook/`
- **Visualization**: `apps/frontend/src/components/visualization/`
- **Chat**: `apps/frontend/src/components/chat/`
- **UI**: `apps/frontend/src/components/ui/`

### Shared Types
- **Types**: `packages/shared/src/types.ts`
- **Schemas**: `packages/shared/src/schemas.ts`
- **Chat**: `packages/shared/src/chat-types.ts`

## Development Workflow

### Working with the Monorepo
1. **Root level**: Use npm workspaces commands for cross-package operations
2. **Package level**: Navigate to specific package for package-specific commands
3. **Shared types**: Update `packages/shared` when adding new interfaces
4. **Testing**: Run tests at both root and package levels

### Adding New Features
1. **Types first**: Define interfaces in `packages/shared/src/types.ts`
2. **Backend routes**: Add API endpoints in `apps/backend/src/routes/`
3. **Frontend components**: Create components in appropriate subdirectory
4. **Real-time**: Add Socket.IO events if collaboration needed

### Working with Physics Simulations
1. **Physics objects**: Define in `apps/frontend/src/components/visualization/`
2. **Three.js setup**: Use React Three Fiber patterns
3. **Cannon.js physics**: Integrate physics engine with rendering
4. **Performance**: Use React.memo and useMemo for optimization

### AI Integration
1. **Provider abstraction**: Support multiple AI providers
2. **Context analysis**: Parse code with AST for intelligent suggestions
3. **Domain detection**: Identify physics, visualization, ML contexts
4. **Agent orchestration**: Use multi-agent patterns for complex queries

## Testing Strategy

### Frontend Testing
- **Unit tests**: Jest with React Testing Library
- **Component tests**: Focus on user interactions
- **Physics tests**: Mock Three.js and Cannon.js for simulation testing
- **Location**: `apps/frontend/src/components/**/*.test.tsx`

### Backend Testing
- **API tests**: Use Supertest for HTTP endpoint testing
- **WebSocket tests**: Test real-time functionality
- **Database tests**: Mock database connections
- **Location**: `apps/backend/test/` (if exists) or inline `*.test.js`

### Integration Testing
- **E2E**: Playwright for full application workflows
- **Multi-platform**: Test both Node.js and Python backends
- **Real-time**: Test collaborative features across multiple clients

## Environment Setup

### Required Environment Variables

#### Node.js Backend (`apps/backend/.env`)
```bash
PORT=4100
NODE_ENV=development
DATABASE_URL=postgresql://user:pass@localhost:5432/aispace
JWT_SECRET=your-secret-key
CORS_ORIGINS=http://localhost:3000,http://localhost:4000
```

#### React Frontend (`apps/frontend/.env.local`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:4100
NEXT_PUBLIC_WS_URL=ws://localhost:4100
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

#### Python/AWS Backend (`aws-agent-backend/.env`)
```bash
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
```

## Port Configuration

- **Frontend (Primary)**: 4000 (AI-Jupyter platform)
- **Backend (Primary)**: 4100 (Node.js Express)
- **Frontend (AWS)**: 3000 (AWS AI Agent platform)
- **Backend (AWS)**: 57890 (Python FastAPI)

## Performance Considerations

### Frontend Optimization
- **Code splitting**: Use Next.js dynamic imports for large components
- **Three.js optimization**: Implement object pooling for physics simulations
- **Monaco Editor**: Lazy load editor to reduce initial bundle size
- **WebSocket**: Implement connection pooling and reconnection logic

### Backend Optimization
- **Database**: Use connection pooling and prepared statements
- **Caching**: Implement Redis caching for frequent operations
- **Rate limiting**: Configure appropriate limits for AI API calls
- **WebSocket**: Implement room-based message broadcasting

### AI Integration Efficiency
- **Provider fallback**: Implement graceful degradation between AI providers
- **Context optimization**: Limit context size to improve response times
- **Caching**: Cache AI responses for repeated queries
- **Batch processing**: Group similar AI requests when possible