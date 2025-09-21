"""
Main FastAPI application entry point for AI Jupyter Notebook platform.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
import os

from app.core.config import settings
from app.core.error_handlers import (
    http_exception_handler,
    validation_exception_handler,
    sqlalchemy_exception_handler,
    general_exception_handler,
)
from app.api.v1.api import api_router
from app.services.execution_service_simple import execution_service
from app.middleware.rate_limiting import create_rate_limit_middleware
from app.middleware.security import (
    SecurityHeadersMiddleware,
    RequestValidationMiddleware,
    RequestLoggingMiddleware,
    HealthCheckMiddleware,
)
from app.services.performance import performance_monitor, PerformanceMiddleware

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add security and performance middleware (order matters!)
app.add_middleware(HealthCheckMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(PerformanceMiddleware, monitor=performance_monitor)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestValidationMiddleware)

# Add rate limiting middleware
redis_url = os.getenv("REDIS_URL")
if redis_url:
    app.add_middleware(create_rate_limit_middleware, redis_url=redis_url)
else:
    app.add_middleware(create_rate_limit_middleware)

# Configure CORS (should be last middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=[
        "X-RateLimit-Limit",
        "X-RateLimit-Remaining",
        "X-RateLimit-Window",
        "X-Process-Time",
    ],
)

# Add exception handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await execution_service.initialize()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": f"{settings.PROJECT_NAME} is running"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
