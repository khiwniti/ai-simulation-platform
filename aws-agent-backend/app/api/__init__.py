from fastapi import APIRouter
from app.api import agents, projects, demo

router = APIRouter()

# Include all API routers
router.include_router(agents.router, prefix="/agents", tags=["agents"])
router.include_router(projects.router, prefix="/projects", tags=["projects"])
router.include_router(demo.router, prefix="/demo", tags=["demo"])
