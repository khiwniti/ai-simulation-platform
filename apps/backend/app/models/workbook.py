"""
Workbook model for organizing notebooks.
"""

from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Workbook(BaseModel):
    """
    Workbook model for organizing multiple notebooks.
    """
    
    __tablename__ = "workbooks"
    
    title = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Relationships
    notebooks = relationship("Notebook", back_populates="workbook", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Workbook(id={self.id}, title='{self.title}')>"