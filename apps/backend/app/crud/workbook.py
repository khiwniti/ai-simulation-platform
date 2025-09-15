"""
CRUD operations for workbooks.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.crud.base import CRUDBase
from app.models.workbook import Workbook
from app.models.notebook import Notebook
from app.schemas.workbook import WorkbookCreate, WorkbookUpdate


class CRUDWorkbook(CRUDBase[Workbook, WorkbookCreate, WorkbookUpdate]):
    """CRUD operations for workbooks."""
    
    def get_with_notebook_count(self, db: Session, id: UUID) -> Optional[Workbook]:
        """Get workbook with notebook count."""
        workbook = db.query(Workbook).filter(Workbook.id == id).first()
        if workbook:
            # Add notebook count as a dynamic attribute
            notebook_count = db.query(func.count(Notebook.id)).filter(
                Notebook.workbook_id == id
            ).scalar()
            workbook.notebook_count = notebook_count
        return workbook
    
    def get_multi_with_notebook_count(
        self, 
        db: Session, 
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Workbook]:
        """Get multiple workbooks with notebook counts."""
        workbooks = db.query(Workbook).offset(skip).limit(limit).all()
        
        # Add notebook counts
        for workbook in workbooks:
            notebook_count = db.query(func.count(Notebook.id)).filter(
                Notebook.workbook_id == workbook.id
            ).scalar()
            workbook.notebook_count = notebook_count
            
        return workbooks
    
    def get_by_title(self, db: Session, title: str) -> Optional[Workbook]:
        """Get workbook by title."""
        return db.query(Workbook).filter(Workbook.title == title).first()


workbook = CRUDWorkbook(Workbook)