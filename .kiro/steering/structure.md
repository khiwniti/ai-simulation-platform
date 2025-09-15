# Project Structure

## Monorepo Organization

```
ai-jupyter-notebook/
├── apps/                    # Application packages
│   ├── frontend/           # Next.js React application
│   └── backend/            # FastAPI Python backend
├── packages/               # Shared packages
│   └── shared/            # Shared TypeScript types
├── .github/workflows/      # CI/CD configuration
└── docker-compose.yml     # Development environment
```

## Frontend Structure (`apps/frontend/`)

```
src/
├── app/                    # Next.js App Router pages
├── components/             # React components
│   ├── chat/              # Real-time chat components
│   ├── inline-assistance/ # AI assistance widgets
│   ├── layout/            # Layout components (Sidebar, MainContent)
│   ├── notebook/          # Notebook editor and cells
│   ├── visualization/     # 3D visualization components
│   └── workbook/          # Workbook management
├── hooks/                 # Custom React hooks
├── services/              # API and WebSocket services
├── stores/                # Zustand state management
├── styles/                # CSS and styling
└── __tests__/             # Component and service tests
```

## Backend Structure (`apps/backend/`)

```
app/
├── api/v1/                # API route handlers
├── core/                  # Core configuration and utilities
├── crud/                  # Database CRUD operations
├── middleware/            # Custom middleware (auth, etc.)
├── models/                # SQLAlchemy database models
├── schemas/               # Pydantic request/response schemas
└── services/              # Business logic services
    ├── agents/           # AI agent implementations
    └── execution_service.py
migrations/                # Alembic database migrations
tests/                     # Backend tests
docker/                    # Docker configurations
```

## Shared Package (`packages/shared/`)

```
src/
├── types.ts              # Core domain types (Notebook, Cell, Workbook)
└── chat-types.ts         # Chat and messaging types
```

## Key Architectural Patterns

### Frontend Patterns
- **Component Organization**: Feature-based folders with co-located tests
- **State Management**: Zustand stores for each domain (workbook, chat, etc.)
- **Service Layer**: Separate services for API calls and WebSocket connections
- **Custom Hooks**: Reusable logic extraction (e.g., `useInlineAssistance`)

### Backend Patterns
- **Layered Architecture**: API → Services → CRUD → Models
- **Dependency Injection**: Services injected into route handlers
- **Error Handling**: Centralized exception handlers
- **Agent System**: Orchestrator pattern for multi-agent coordination

### Database Schema
- **Workbooks**: Top-level containers
- **Notebooks**: Collections of cells within workbooks
- **Cells**: Individual executable units with type-specific behavior
- **Agents**: AI assistant configurations and contexts

## File Naming Conventions

### Frontend
- Components: PascalCase (e.g., `ChatInterface.tsx`)
- Services: camelCase (e.g., `chatApiService.ts`)
- Stores: camelCase with "Store" suffix (e.g., `workbookStore.ts`)
- Tests: Same as source with `.test.` suffix

### Backend
- Models: snake_case files, PascalCase classes (e.g., `notebook.py` → `Notebook`)
- Services: snake_case (e.g., `execution_service.py`)
- API routes: snake_case (e.g., `chat_websocket.py`)
- Tests: `test_` prefix (e.g., `test_notebook.py`)

## Import Conventions
- Shared types: Import from `@ai-jupyter/shared`
- Relative imports: Use relative paths within same package
- Absolute imports: Use from package root for cross-feature imports