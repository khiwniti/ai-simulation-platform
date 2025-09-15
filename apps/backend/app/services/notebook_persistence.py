"""
Notebook persistence and auto-save service.
"""

import logging
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.notebook import Notebook, Cell
from app.crud.notebook import notebook as notebook_crud
from app.crud.cell import cell as cell_crud
from app.schemas.notebook import NotebookAutoSave

logger = logging.getLogger(__name__)


class NotebookPersistenceService:
    """Service for handling notebook persistence and auto-save functionality."""
    
    def __init__(self):
        self.auto_save_interval = timedelta(seconds=30)  # Auto-save every 30 seconds
        self.last_auto_save: Dict[UUID, datetime] = {}
        
    def should_auto_save(self, notebook_id: UUID) -> bool:
        """Check if notebook should be auto-saved based on last save time."""
        last_save = self.last_auto_save.get(notebook_id)
        if not last_save:
            return True
            
        return datetime.utcnow() - last_save > self.auto_save_interval
        
    def auto_save(
        self, 
        db: Session, 
        notebook_id: UUID, 
        auto_save_data: NotebookAutoSave
    ) -> Notebook:
        """
        Auto-save notebook changes without incrementing version.
        This is for temporary saves while user is working.
        """
        try:
            notebook = notebook_crud.get_with_cells(db, id=notebook_id)
            if not notebook:
                raise ValueError(f"Notebook {notebook_id} not found")
                
            # Update metadata if provided
            if auto_save_data.metadata:
                notebook.metadata.update(auto_save_data.metadata)
                
            # Update cells if provided
            if auto_save_data.cells:
                for cell_data in auto_save_data.cells:
                    if hasattr(cell_data, 'id') and cell_data.id:
                        # Update existing cell
                        existing_cell = next(
                            (cell for cell in notebook.cells if str(cell.id) == str(cell_data.id)), 
                            None
                        )
                        if existing_cell:
                            existing_cell.content = cell_data.content
                            existing_cell.cell_type = cell_data.cell_type
                            existing_cell.metadata = cell_data.metadata
                    else:
                        # Create new cell
                        new_cell = Cell(
                            notebook_id=notebook_id,
                            cell_type=cell_data.cell_type,
                            content=cell_data.content,
                            position=cell_data.position,
                            metadata=cell_data.metadata
                        )
                        db.add(new_cell)
                        
            # Update last modified time
            notebook.updated_at = datetime.utcnow()
            
            # Don't increment version for auto-save
            db.commit()
            db.refresh(notebook)
            
            # Track auto-save time
            self.last_auto_save[notebook_id] = datetime.utcnow()
            
            logger.info(f"Auto-saved notebook {notebook_id}")
            return notebook
            
        except Exception as e:
            logger.error(f"Auto-save failed for notebook {notebook_id}: {e}")
            db.rollback()
            raise
            
    def force_save(self, db: Session, notebook_id: UUID) -> Notebook:
        """
        Force save notebook and increment version.
        This is for explicit saves by user action.
        """
        try:
            notebook = notebook_crud.get(db, id=notebook_id)
            if not notebook:
                raise ValueError(f"Notebook {notebook_id} not found")
                
            # Increment version for manual save
            notebook.version += 1
            notebook.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(notebook)
            
            # Clear auto-save tracking since we've done a manual save
            self.last_auto_save[notebook_id] = datetime.utcnow()
            
            logger.info(f"Force saved notebook {notebook_id}, version {notebook.version}")
            return notebook
            
        except Exception as e:
            logger.error(f"Force save failed for notebook {notebook_id}: {e}")
            db.rollback()
            raise
            
    def get_auto_save_status(self, notebook_id: UUID) -> Dict[str, Any]:
        """Get auto-save status for a notebook."""
        last_save = self.last_auto_save.get(notebook_id)
        
        return {
            'last_auto_save': last_save.isoformat() if last_save else None,
            'should_auto_save': self.should_auto_save(notebook_id),
            'auto_save_interval_seconds': self.auto_save_interval.total_seconds()
        }
        
    def cleanup_auto_save_tracking(self, notebook_id: UUID) -> None:
        """Clean up auto-save tracking for a notebook (e.g., when deleted)."""
        if notebook_id in self.last_auto_save:
            del self.last_auto_save[notebook_id]


# Global instance
notebook_persistence_service = NotebookPersistenceService()
