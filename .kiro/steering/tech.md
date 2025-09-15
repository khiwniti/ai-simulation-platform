# Technology Stack

## Build System
- **Monorepo**: Turborepo for managing multiple packages and applications
- **Package Manager**: npm with workspaces
- **Node.js**: 18+ required
- **Python**: 3.11+ required

## Frontend Stack
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript 5.0+
- **State Management**: Zustand
- **Code Editor**: Monaco Editor
- **3D Graphics**: Three.js with cannon-es physics
- **Styling**: Tailwind CSS
- **Testing**: Jest with React Testing Library
- **WebSocket**: Socket.io-client for real-time features

## Backend Stack
- **Framework**: FastAPI with async support
- **Language**: Python 3.11+
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis
- **Migration**: Alembic
- **Testing**: pytest with async support
- **Physics**: NVIDIA PhysX AI integration
- **Container Runtime**: Docker with NVIDIA runtime support

## Shared Packages
- **Types**: Shared TypeScript interfaces and types
- **Validation**: Pydantic schemas for API contracts

## Development Environment
- **Containerization**: Docker Compose for local development
- **GPU Support**: NVIDIA Docker runtime for PhysX AI
- **CI/CD**: GitHub Actions workflow

## Common Commands

### Development
```bash
# Install all dependencies
npm install

# Start all services in development
npm run dev

# Start individual services
npm run dev --workspace=@ai-jupyter/frontend
cd apps/backend && uvicorn main:app --reload
```

### Building
```bash
# Build all packages
npm run build

# Type checking
npm run type-check
```

### Testing
```bash
# Run all tests
npm run test

# Frontend tests only
npm run test --workspace=@ai-jupyter/frontend

# Backend tests only
cd apps/backend && pytest
```

### Docker Development
```bash
# Start full environment
docker-compose up -d

# View logs
docker-compose logs -f backend
```

## Code Quality
- **Linting**: ESLint for TypeScript/JavaScript, flake8 for Python
- **Formatting**: Prettier for frontend, black for backend
- **Type Safety**: Strict TypeScript configuration