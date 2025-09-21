"""
Main API v1 router.
"""

from fastapi import APIRouter
from app.api.v1 import (
    auth,
    stripe,
    monitoring,
    ai_enhanced,
    admin,
    performance,
    workbooks,
    notebooks,
    execution,
    agents,
    inline_assistance,
)

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(stripe.router, prefix="/stripe", tags=["payments"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(ai_enhanced.router, prefix="/ai", tags=["ai-enhanced"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(
    performance.router, prefix="/performance", tags=["performance"]
)
api_router.include_router(workbooks.router, prefix="/workbooks", tags=["workbooks"])
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
api_router.include_router(execution.router, prefix="/execution", tags=["execution"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(
    inline_assistance.router, prefix="/inline-assistance", tags=["inline-assistance"]
)
