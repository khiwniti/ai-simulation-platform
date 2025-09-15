"""
Notebook backup and recovery service.
"""

import json
import logging
import os
import gzip
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.notebook import Notebook
from app.crud.notebook import notebook as notebook_crud
from app.core.config import settings

logger = logging.getLogger(__name__)


class NotebookBackupService:
    """Service for notebook backup and recovery."""
    
    def __init__(self):
        # Configure backup storage (would be cloud storage in production)
        self.backup_dir = Path(getattr(settings, 'BACKUP_DIR', './backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
        # Backup retention settings
        self.max_backups_per_notebook = getattr(settings, 'MAX_BACKUPS_PER_NOTEBOOK', 10)
        self.backup_retention_days = getattr(settings, 'BACKUP_RETENTION_DAYS', 30)
        
        # Compression settings
        self.compress_backups = getattr(settings, 'COMPRESS_BACKUPS', True)
        
    def create_backup(
        self, 
        db: Session, 
        notebook: Notebook,
        backup_type: str = "manual",
        reason: str = ""
    ) -> Dict[str, Any]:
        """Create a backup of the notebook."""
        
        try:
            backup_id = str(uuid4())
            timestamp = datetime.utcnow()
            
            # Create backup data
            backup_data = self._create_backup_data(notebook, backup_type, reason)
            
            # Save backup to file
            backup_file_path = self._save_backup_to_file(
                notebook.id, 
                backup_id, 
                backup_data, 
                timestamp
            )
            
            # Store backup metadata in notebook
            backup_info = {
                "backup_id": backup_id,
                "timestamp": timestamp.isoformat(),
                "backup_type": backup_type,
                "reason": reason,
                "file_path": str(backup_file_path),
                "file_size": backup_file_path.stat().st_size,
                "compressed": self.compress_backups,
                "notebook_version": notebook.version,
                "cell_count": len(notebook.cells)
            }
            
            self._store_backup_metadata(db, notebook, backup_info)
            
            # Clean up old backups
            self._cleanup_old_backups(db, notebook)
            
            logger.info(f"Created backup {backup_id} for notebook {notebook.id}")
            
            return backup_info
            
        except Exception as e:
            logger.error(f"Failed to create backup for notebook {notebook.id}: {e}")
            raise
    
    def restore_backup(
        self, 
        db: Session, 
        notebook_id: UUID, 
        backup_id: str
    ) -> Optional[Notebook]:
        """Restore notebook from a backup."""
        
        try:
            notebook = notebook_crud.get_with_cells(db, id=notebook_id)
            if not notebook:
                return None
            
            # Find backup metadata
            backup_info = self._get_backup_metadata(notebook, backup_id)
            if not backup_info:
                logger.error(f"Backup {backup_id} not found for notebook {notebook_id}")
                return None
            
            # Load backup data from file
            backup_data = self._load_backup_from_file(backup_info["file_path"])
            if not backup_data:
                logger.error(f"Failed to load backup data from {backup_info['file_path']}")
                return None
            
            # Create a backup of current state before restoring
            self.create_backup(
                db=db, 
                notebook=notebook, 
                backup_type="auto", 
                reason=f"Before restoring backup {backup_id}"
            )
            
            # Restore notebook from backup
            restored_notebook = self._restore_from_backup_data(db, notebook, backup_data)
            
            logger.info(f"Restored notebook {notebook_id} from backup {backup_id}")
            
            return restored_notebook
            
        except Exception as e:
            logger.error(f"Failed to restore backup {backup_id} for notebook {notebook_id}: {e}")
            db.rollback()
            return None
    
    def list_backups(
        self, 
        db: Session, 
        notebook_id: UUID,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List available backups for a notebook."""
        
        notebook = notebook_crud.get(db, id=notebook_id)
        if not notebook:
            return []
        
        backups = notebook.metadata.get("backups", []) if notebook.metadata else []
        
        # Sort by timestamp descending and limit
        sorted_backups = sorted(
            backups, 
            key=lambda x: x.get("timestamp", ""), 
            reverse=True
        )[:limit]
        
        # Filter out backups with missing files
        valid_backups = []
        for backup in sorted_backups:
            file_path = Path(backup.get("file_path", ""))
            if file_path.exists():
                valid_backups.append(backup)
            else:
                logger.warning(f"Backup file not found: {file_path}")
        
        return valid_backups
    
    def delete_backup(
        self, 
        db: Session, 
        notebook_id: UUID, 
        backup_id: str
    ) -> bool:
        """Delete a specific backup."""
        
        try:
            notebook = notebook_crud.get(db, id=notebook_id)
            if not notebook:
                return False
            
            backups = notebook.metadata.get("backups", []) if notebook.metadata else []
            
            # Find and remove backup
            backup_to_remove = None
            updated_backups = []
            
            for backup in backups:
                if backup.get("backup_id") == backup_id:
                    backup_to_remove = backup
                else:
                    updated_backups.append(backup)
            
            if not backup_to_remove:
                return False
            
            # Delete backup file
            file_path = Path(backup_to_remove.get("file_path", ""))
            if file_path.exists():
                file_path.unlink()
            
            # Update metadata
            notebook.metadata["backups"] = updated_backups
            db.commit()
            
            logger.info(f"Deleted backup {backup_id} for notebook {notebook_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete backup {backup_id}: {e}")
            return False
    
    def auto_backup(
        self, 
        db: Session, 
        notebook: Notebook,
        trigger: str = "auto_save"
    ) -> Optional[Dict[str, Any]]:
        """Create automatic backup based on configurable rules."""
        
        # Check if auto-backup is needed
        if not self._should_auto_backup(notebook, trigger):
            return None
        
        return self.create_backup(
            db=db,
            notebook=notebook,
            backup_type="automatic",
            reason=f"Auto backup triggered by {trigger}"
        )
    
    def _create_backup_data(
        self, 
        notebook: Notebook, 
        backup_type: str, 
        reason: str
    ) -> Dict[str, Any]:
        """Create complete backup data structure."""
        
        return {
            "backup_info": {
                "backup_type": backup_type,
                "reason": reason,
                "created_at": datetime.utcnow().isoformat(),
                "simu_lab_version": "1.0.0"  # Would come from actual version
            },
            "notebook": {
                "id": str(notebook.id),
                "title": notebook.title,
                "description": notebook.description,
                "workbook_id": str(notebook.workbook_id),
                "metadata": notebook.metadata or {},
                "version": notebook.version,
                "created_at": notebook.created_at.isoformat() if notebook.created_at else None,
                "updated_at": notebook.updated_at.isoformat() if notebook.updated_at else None
            },
            "cells": [
                {
                    "id": str(cell.id),
                    "cell_type": cell.cell_type.value,
                    "content": cell.content,
                    "position": cell.position,
                    "execution_count": cell.execution_count,
                    "metadata": cell.metadata or {},
                    "outputs": [
                        {
                            "id": str(output.id),
                            "output_type": output.output_type,
                            "content": output.content,
                            "metadata": output.metadata or {},
                            "output_index": output.output_index
                        }
                        for output in cell.outputs
                    ]
                }
                for cell in sorted(notebook.cells, key=lambda x: x.position)
            ]
        }
    
    def _save_backup_to_file(
        self, 
        notebook_id: UUID, 
        backup_id: str, 
        backup_data: Dict[str, Any], 
        timestamp: datetime
    ) -> Path:
        """Save backup data to file."""
        
        # Create notebook-specific backup directory
        notebook_backup_dir = self.backup_dir / str(notebook_id)
        notebook_backup_dir.mkdir(exist_ok=True)
        
        # Create filename with timestamp
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{backup_id}_{timestamp_str}.json"
        
        if self.compress_backups:
            filename += ".gz"
        
        file_path = notebook_backup_dir / filename
        
        # Save data
        json_data = json.dumps(backup_data, indent=2, default=str).encode('utf-8')
        
        if self.compress_backups:
            with gzip.open(file_path, 'wb') as f:
                f.write(json_data)
        else:
            with open(file_path, 'wb') as f:
                f.write(json_data)
        
        return file_path
    
    def _load_backup_from_file(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load backup data from file."""
        
        try:
            path = Path(file_path)
            if not path.exists():
                return None
            
            if path.suffix == '.gz':
                with gzip.open(path, 'rb') as f:
                    data = f.read()
            else:
                with open(path, 'rb') as f:
                    data = f.read()
            
            return json.loads(data.decode('utf-8'))
            
        except Exception as e:
            logger.error(f"Failed to load backup from {file_path}: {e}")
            return None
    
    def _store_backup_metadata(
        self, 
        db: Session, 
        notebook: Notebook, 
        backup_info: Dict[str, Any]
    ) -> None:
        """Store backup metadata in notebook."""
        
        if not notebook.metadata:
            notebook.metadata = {}
        
        if "backups" not in notebook.metadata:
            notebook.metadata["backups"] = []
        
        notebook.metadata["backups"].append(backup_info)
        
        db.commit()
    
    def _get_backup_metadata(
        self, 
        notebook: Notebook, 
        backup_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get backup metadata by ID."""
        
        backups = notebook.metadata.get("backups", []) if notebook.metadata else []
        
        for backup in backups:
            if backup.get("backup_id") == backup_id:
                return backup
        
        return None
    
    def _restore_from_backup_data(
        self, 
        db: Session, 
        notebook: Notebook, 
        backup_data: Dict[str, Any]
    ) -> Notebook:
        """Restore notebook from backup data."""
        
        notebook_data = backup_data.get("notebook", {})
        cells_data = backup_data.get("cells", [])
        
        # Update notebook properties
        notebook.title = notebook_data.get("title", notebook.title)
        notebook.description = notebook_data.get("description", notebook.description)
        notebook.metadata = notebook_data.get("metadata", {})
        notebook.version = notebook_data.get("version", notebook.version)
        notebook.updated_at = datetime.utcnow()
        
        # Clear existing cells
        for cell in notebook.cells:
            db.delete(cell)
        
        db.flush()
        
        # Recreate cells from backup
        from app.models.notebook import Cell, CellOutput, CellType
        
        for cell_data in cells_data:
            cell = Cell(
                notebook_id=notebook.id,
                cell_type=CellType(cell_data.get("cell_type", "code")),
                content=cell_data.get("content", ""),
                position=cell_data.get("position", 0),
                execution_count=cell_data.get("execution_count", 0),
                metadata=cell_data.get("metadata", {})
            )
            
            db.add(cell)
            db.flush()
            
            # Recreate outputs
            for output_data in cell_data.get("outputs", []):
                output = CellOutput(
                    cell_id=cell.id,
                    output_type=output_data.get("output_type", "stream"),
                    content=output_data.get("content", ""),
                    metadata=output_data.get("metadata", {}),
                    output_index=output_data.get("output_index", 0)
                )
                db.add(output)
        
        db.commit()
        db.refresh(notebook)
        
        return notebook
    
    def _should_auto_backup(self, notebook: Notebook, trigger: str) -> bool:
        """Determine if auto-backup should be performed."""
        
        # Get last backup time
        backups = notebook.metadata.get("backups", []) if notebook.metadata else []
        
        if not backups:
            return True
        
        # Find last auto backup
        auto_backups = [b for b in backups if b.get("backup_type") == "automatic"]
        
        if not auto_backups:
            return True
        
        last_backup = max(auto_backups, key=lambda x: x.get("timestamp", ""))
        last_backup_time = datetime.fromisoformat(last_backup["timestamp"])
        
        # Auto-backup if more than 1 hour since last backup
        if datetime.utcnow() - last_backup_time > timedelta(hours=1):
            return True
        
        return False
    
    def _cleanup_old_backups(self, db: Session, notebook: Notebook) -> None:
        """Clean up old backups based on retention policy."""
        
        backups = notebook.metadata.get("backups", []) if notebook.metadata else []
        
        # Sort by timestamp
        sorted_backups = sorted(backups, key=lambda x: x.get("timestamp", ""), reverse=True)
        
        # Keep only the most recent backups
        backups_to_keep = sorted_backups[:self.max_backups_per_notebook]
        backups_to_remove = sorted_backups[self.max_backups_per_notebook:]
        
        # Also remove backups older than retention period
        cutoff_date = datetime.utcnow() - timedelta(days=self.backup_retention_days)
        
        for backup in backups_to_keep[:]:
            backup_time = datetime.fromisoformat(backup["timestamp"])
            if backup_time < cutoff_date:
                backups_to_keep.remove(backup)
                backups_to_remove.append(backup)
        
        # Delete old backup files
        for backup in backups_to_remove:
            file_path = Path(backup.get("file_path", ""))
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info(f"Deleted old backup file: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete backup file {file_path}: {e}")
        
        # Update metadata
        if backups_to_remove:
            notebook.metadata["backups"] = backups_to_keep
            db.commit()


# Global instance
notebook_backup_service = NotebookBackupService()
