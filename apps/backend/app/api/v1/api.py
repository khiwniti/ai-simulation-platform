"""
Main API v1 router.
"""

from fastapi import APIRouter
from app.api.v1 import workbooks, notebooks, execution, agents, inline_assistance, chat_websocket

api_router = APIRouter()

# Include routers
api_router.include_router(workbooks.router, prefix="/workbooks", tags=["workbooks"])
api_router.include_router(notebooks.router, prefix="/notebooks", tags=["notebooks"])
api_router.include_router(execution.router, prefix="/execution", tags=["execution"])
api_router.include_router(agents.router, prefix="/agents", tags=["agents"])
api_router.include_router(inline_assistance.router, prefix="/inline-assistance", tags=["inline-assistance"])