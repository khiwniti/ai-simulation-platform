"""
Simulation context Pydantic schemas.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import Field
from app.schemas.base import BaseSchema, TimestampSchema, UUIDSchema


class SimulationContextBase(BaseSchema):
    """Base simulation context schema."""
    
    physics_parameters: Dict[str, Any] = {}
    execution_state: str = "idle"
    active_agents: List[str] = []


class SimulationContextCreate(SimulationContextBase):
    """Schema for creating a simulation context."""
    
    notebook_id: UUID


class SimulationContextUpdate(BaseSchema):
    """Schema for updating a simulation context."""
    
    physics_parameters: Optional[Dict[str, Any]] = None
    execution_state: Optional[str] = None
    active_agents: Optional[List[str]] = None
    gpu_device_id: Optional[int] = None
    gpu_memory_limit: Optional[float] = None


class SimulationContextResponse(SimulationContextBase, UUIDSchema, TimestampSchema):
    """Schema for simulation context responses."""
    
    notebook_id: UUID
    gpu_device_id: Optional[int] = None
    gpu_memory_limit: Optional[float] = None
    gpu_compute_capability: Optional[str] = None
    last_execution_time: Optional[float] = None
    memory_usage: Optional[float] = None