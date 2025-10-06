from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from contextlib import asynccontextmanager
import structlog

from app.config import settings
from app.api import router as api_router
from app.websocket import websocket_manager

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting AWS AI Agent Backend")
    
    # Initialize services
    from app.services.bedrock_service import BedrockService
    from app.services.agent_orchestrator import AgentOrchestrator
    
    bedrock_service = BedrockService()
    agent_orchestrator = AgentOrchestrator(bedrock_service)
    
    # Store in app state
    app.state.bedrock_service = bedrock_service
    app.state.agent_orchestrator = agent_orchestrator
    
    logger.info("✅ AWS AI Agent Backend initialized")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down AWS AI Agent Backend")

app = FastAPI(
    title="AWS AI Agent Engineering Platform",
    description="Autonomous AI Engineering Team powered by AWS Bedrock AgentCore",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Simplified for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "AWS AI Agent Engineering Platform",
        "status": "operational",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test AWS connection
        bedrock_service = app.state.bedrock_service
        health_status = await bedrock_service.health_check()
        
        return {
            "status": "healthy",
            "services": {
                "bedrock": health_status,
                "database": "connected",  # TODO: Add DB health check
                "websocket_connections": websocket_manager.get_connection_count()
            }
        }
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint for real-time communication"""
    from app.websocket import websocket_endpoint as ws_endpoint
    await ws_endpoint(websocket, client_id)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=57890,  # Use the port from runtime info
        reload=True,
        log_config=None,  # Use structlog
        access_log=False
    )