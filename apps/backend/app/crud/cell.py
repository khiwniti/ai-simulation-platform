"""
CRUD operations for cells.
"""

from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from app.crud.base import CRUDBase
from app.models.notebook import Cell, CellOutput
from app.schemas.notebook import CellCreate, CellUpdate


class CRUDCell(CRUDBase[Cell, CellCreate, CellUpdate]):
    """CRUD operations for cells."""
    
    def get_with_outputs(self, db: Session, id: UUID) -> Optional[Cell]:
        """Get cell with all outputs loaded."""
        return db.query(Cell).options(
            joinedload(Cell.outputs)
        ).filter(Cell.id == id).first()
    
    def get_by_notebook(
        self, 
        db: Session, 
        notebook_id: UUID,
        *, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Cell]:
        """Get cells by notebook ID."""
        return db.query(Cell).filter(
            Cell.notebook_id == notebook_id
        ).order_by(Cell.position).offset(skip).limit(limit).all()
    
    def get_by_position(
        self, 
        db: Session, 
        notebook_id: UUID,
        position: int
    ) -> Optional[Cell]:
        """Get cell by position within a notebook."""
        return db.query(Cell).filter(
            Cell.notebook_id == notebook_id,
            Cell.position == position
        ).first()
    
    def reorder_cells(
        self, 
        db: Session, 
        notebook_id: UUID,
        cell_id: UUID,
        new_position: int
    ) -> bool:
        """Reorder cells when one is moved."""
        try:
            cell = self.get(db, cell_id)
            if not cell or cell.notebook_id != notebook_id:
                return False
                
            old_position = cell.position
            
            if old_position == new_position:
                return True
                
            # Get all cells in notebook
            cells = self.get_by_notebook(db, notebook_id)
            
            # Update positions
            if old_position < new_position:
                # Moving down - shift cells up
                for c in cells:
                    if old_position < c.position <= new_position and c.id != cell_id:
                        c.position -= 1
            else:
                # Moving up - shift cells down
                for c in cells:
                    if new_position <= c.position < old_position and c.id != cell_id:
                        c.position += 1
            
            # Update the moved cell
            cell.position = new_position
            
            db.commit()
            return True
            
        except Exception:
            db.rollback()
            return False
    
    def increment_execution_count(self, db: Session, cell_id: UUID) -> Optional[Cell]:
        """Increment cell execution count."""
        cell = self.get(db, cell_id)
        if cell:
            cell.execution_count += 1
            db.commit()
            db.refresh(cell)
        return cell


cell = CRUDCell(Cell)
