"""
Workbook Pydantic schemas.
"""

from typing import Optional, List
from uuid import UUID
from pydantic import Field
from app.schemas.base import BaseSchema, TimestampSchema, UUIDSchema


class WorkbookBase(BaseSchema):
    """Base workbook schema."""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class WorkbookCreate(WorkbookBase):
    """Schema for creating a workbook."""
    pass


class WorkbookUpdate(BaseSchema):
    """Schema for updating a workbook."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class WorkbookResponse(WorkbookBase, UUIDSchema, TimestampSchema):
    """Schema for workbook responses."""
    
    # Optional notebook count for summary views
    notebook_count: Optional[int] = None