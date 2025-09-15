"""
Agent interaction Pydantic schemas.
"""

from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import Field
from app.schemas.base import BaseSchema, TimestampSchema, UUIDSchema


class AgentInteractionBase(BaseSchema):
    """Base agent interaction schema."""
    
    agent_type: str
    query: str = Field(..., min_length=1)
    context: Dict[str, Any] = {}


class AgentInteractionCreate(AgentInteractionBase):
    """Schema for creating an agent interaction."""
    
    session_id: UUID
    notebook_id: Optional[UUID] = None
    cell_id: Optional[UUID] = None


class AgentInteractionResponse(AgentInteractionBase, UUIDSchema, TimestampSchema):
    """Schema for agent interaction responses."""
    
    session_id: UUID
    response: str
    confidence_score: float
    notebook_id: Optional[UUID] = None
    cell_id: Optional[UUID] = None
    response_time: Optional[float] = None
    tokens_used: int = 0