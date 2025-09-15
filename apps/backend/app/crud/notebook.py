"""
CRUD operations for notebooks.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.models.notebook import Notebook, Cell
from app.schemas.notebook import NotebookCreate, NotebookUpdate


class CRUDNotebook(CRUDBase[Notebook, NotebookCreate, NotebookUpdate]):
    """CRUD operations for notebooks."""
    
    def get_with_cells(self, db: Session, id: UUID) -> Optional[Notebook]:
        """Get notebook with all cells loaded."""
        return db.query(Notebook).options(
            joinedload(Notebook.cells).joinedload(Cell.outputs)
        ).filter(Notebook.id == id).first()
    
    def get_by_workbook(
        self, 
        db: Session, 
        workbook_id: UUID,
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Notebook]:
        """Get notebooks by workbook ID."""
        return db.query(Notebook).filter(
            Notebook.workbook_id == workbook_id
        ).offset(skip).limit(limit).all()
    
    def get_by_title_and_workbook(
        self, 
        db: Session, 
        title: str, 
        workbook_id: UUID
    ) -> Optional[Notebook]:
        """Get notebook by title within a workbook."""
        return db.query(Notebook).filter(
            Notebook.title == title,
            Notebook.workbook_id == workbook_id
        ).first()
    
    def increment_version(self, db: Session, notebook_id: UUID) -> Optional[Notebook]:
        """Increment notebook version."""
        notebook = self.get(db, notebook_id)
        if notebook:
            notebook.version += 1
            db.commit()
            db.refresh(notebook)
        return notebook


notebook = CRUDNotebook(Notebook)