"""
Notebook and Cell models for the AI Jupyter Notebook platform.
"""

import enum
from sqlalchemy import Column, String, Text, Integer, ForeignKey, JSON, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class CellType(enum.Enum):
    """Enumeration of cell types."""
    CODE = "code"
    MARKDOWN = "markdown"
    PHYSICS = "physics"
    VISUALIZATION = "visualization"


class Notebook(BaseModel):
    """
    Notebook model representing a simulation notebook.
    """
    
    __tablename__ = "notebooks"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    workbook_id = Column(UUID(as_uuid=True), ForeignKey("workbooks.id"), nullable=False)
    metadata = Column(JSON, default=dict)
    version = Column(Integer, default=1, nullable=False)
    
    # Relationships
    workbook = relationship("Workbook", back_populates="notebooks")
    cells = relationship("Cell", back_populates="notebook", cascade="all, delete-orphan", order_by="Cell.position")
    simulation_contexts = relationship("SimulationContext", back_populates="notebook", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Notebook(id={self.id}, title='{self.title}', version={self.version})>"


class Cell(BaseModel):
    """
    Cell model representing individual cells within a notebook.
    """
    
    __tablename__ = "cells"
    
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id"), nullable=False)
    cell_type = Column(Enum(CellType), nullable=False, default=CellType.CODE)
    content = Column(Text, default="")
    execution_count = Column(Integer, default=0)
    position = Column(Integer, nullable=False)
    metadata = Column(JSON, default=dict)
    
    # Relationships
    notebook = relationship("Notebook", back_populates="cells")
    outputs = relationship("CellOutput", back_populates="cell", cascade="all, delete-orphan", order_by="CellOutput.output_index")
    
    def __repr__(self) -> str:
        return f"<Cell(id={self.id}, type={self.cell_type.value}, position={self.position})>"


class CellOutput(BaseModel):
    """
    Cell output model for storing execution results.
    """
    
    __tablename__ = "cell_outputs"
    
    cell_id = Column(UUID(as_uuid=True), ForeignKey("cells.id"), nullable=False)
    output_type = Column(String(50), nullable=False)  # text, html, image, json, etc.
    content = Column(Text)
    metadata = Column(JSON, default=dict)
    output_index = Column(Integer, nullable=False, default=0)
    
    # Relationships
    cell = relationship("Cell", back_populates="outputs")
    
    def __repr__(self) -> str:
        return f"<CellOutput(id={self.id}, type={self.output_type}, index={self.output_index})>"