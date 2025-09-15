"""
Notebook and Cell Pydantic schemas.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import Field
from app.models.notebook import CellType
from app.schemas.base import BaseSchema, TimestampSchema, UUIDSchema


class CellOutputResponse(UUIDSchema, TimestampSchema):
    """Schema for cell output responses."""
    
    cell_id: UUID
    output_type: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = {}
    output_index: int


class CellBase(BaseSchema):
    """Base cell schema."""
    
    cell_type: CellType = CellType.CODE
    content: str = ""
    position: int
    metadata: Dict[str, Any] = {}


class CellCreate(CellBase):
    """Schema for creating a cell."""
    
    notebook_id: UUID


class CellUpdate(BaseSchema):
    """Schema for updating a cell."""
    
    cell_type: Optional[CellType] = None
    content: Optional[str] = None
    position: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CellResponse(CellBase, UUIDSchema, TimestampSchema):
    """Schema for cell responses."""
    
    notebook_id: UUID
    execution_count: int
    outputs: List[CellOutputResponse] = []


class NotebookBase(BaseSchema):
    """Base notebook schema."""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}


class NotebookCreate(NotebookBase):
    """Schema for creating a notebook."""
    
    workbook_id: UUID


class NotebookUpdate(BaseSchema):
    """Schema for updating a notebook."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class NotebookResponse(NotebookBase, UUIDSchema, TimestampSchema):
    """Schema for notebook responses."""
    
    workbook_id: UUID
    version: int
    cells: List[CellResponse] = []


class NotebookAutoSave(BaseSchema):
    """Schema for auto-save data."""
    
    cells: Optional[List[CellCreate]] = None
    metadata: Optional[Dict[str, Any]] = None
    last_modified: Optional[str] = None


class NotebookExport(BaseSchema):
    """Schema for notebook export."""
    
    format: str = "jupyter"
    include_outputs: bool = True
    include_metadata: bool = True


class NotebookImport(BaseSchema):
    """Schema for notebook import."""
    
    title: str
    content: Dict[str, Any]  # Raw notebook content (e.g., .ipynb JSON)
    format: str = "jupyter"
    preserve_ids: bool = False