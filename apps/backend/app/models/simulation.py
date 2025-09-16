"""
Simulation context and GPU resource models.
"""

import enum
from sqlalchemy import Column, String, JSON, ForeignKey, Float, Integer
from sqlalchemy.orm import relationship
from app.models.base import BaseModel, UUID


class ExecutionState(enum.Enum):
    """Enumeration of execution states."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"
    CANCELLED = "cancelled"


class SimulationContext(BaseModel):
    """
    Simulation context model for managing physics simulation state.
    """
    
    __tablename__ = "simulation_contexts"
    
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id"), nullable=False)
    physics_parameters = Column(JSON, default=dict)
    execution_state = Column(String(20), default=ExecutionState.IDLE.value)
    active_agents = Column(JSON, default=list)  # Store as JSON array instead of PostgreSQL ARRAY
    
    # GPU Resource Configuration
    gpu_device_id = Column(Integer)
    gpu_memory_limit = Column(Float)  # in GB
    gpu_compute_capability = Column(String(10))
    
    # Performance metrics
    last_execution_time = Column(Float)  # in seconds
    memory_usage = Column(Float)  # in MB
    
    # Relationships
    notebook = relationship("Notebook", back_populates="simulation_contexts")
    
    def __repr__(self) -> str:
        return f"<SimulationContext(id={self.id}, state={self.execution_state})>"


class GPUResourceConfig(BaseModel):
    """
    GPU resource configuration model for managing GPU allocation.
    """
    
    __tablename__ = "gpu_resource_configs"
    
    device_name = Column(String(255), nullable=False)
    device_id = Column(Integer, nullable=False)
    total_memory = Column(Float, nullable=False)  # in GB
    compute_capability = Column(String(10), nullable=False)
    is_available = Column(String(10), default="true")
    current_usage = Column(Float, default=0.0)  # percentage
    
    # Configuration metadata
    driver_version = Column(String(50))
    cuda_version = Column(String(50))
    physx_compatible = Column(String(10), default="true")
    
    def __repr__(self) -> str:
        return f"<GPUResourceConfig(device_id={self.device_id}, name='{self.device_name}')>"