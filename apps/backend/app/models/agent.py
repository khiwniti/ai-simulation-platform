"""
AI Agent interaction models.
"""

import enum
from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, JSON
from app.models.base import BaseModel, UUID


class AgentType(enum.Enum):
    """Enumeration of AI agent types."""
    PHYSICS = "physics"
    VISUALIZATION = "visualization"
    OPTIMIZATION = "optimization"
    DEBUG = "debug"
    GENERAL = "general"


class AgentInteraction(BaseModel):
    """
    Agent interaction model for storing AI agent conversations and responses.
    """
    
    __tablename__ = "agent_interactions"
    
    session_id = Column(UUID(as_uuid=True), nullable=False)
    agent_type = Column(String(20), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    context = Column(JSON, default=dict)
    confidence_score = Column(Float, default=0.0)
    
    # Optional notebook context
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id"), nullable=True)
    cell_id = Column(UUID(as_uuid=True), ForeignKey("cells.id"), nullable=True)
    
    # Performance metrics
    response_time = Column(Float)  # in seconds
    tokens_used = Column(Integer, default=0)
    
    def __repr__(self) -> str:
        return f"<AgentInteraction(id={self.id}, agent={self.agent_type}, confidence={self.confidence_score})>"