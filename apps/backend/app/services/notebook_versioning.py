"""
Notebook version control and collaboration service.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.models.notebook import Notebook, Cell
from app.crud.notebook import notebook as notebook_crud

logger = logging.getLogger(__name__)


class NotebookVersioningService:
    """Service for notebook version control and collaboration."""
    
    def __init__(self):
        # In a production environment, this would use a dedicated versioning table
        # For now, we'll store versions in the notebook metadata
        pass
    
    def create_version(
        self, 
        db: Session, 
        notebook: Notebook, 
        message: str = "",
        author: str = "system"
    ) -> Dict[str, Any]:
        """Create a new version checkpoint for the notebook."""
        
        try:
            # Create version snapshot
            version_data = self._create_version_snapshot(notebook)
            
            version_info = {
                "version_id": str(uuid4()),
                "version_number": notebook.version + 1,
                "parent_version": notebook.version,
                "message": message,
                "author": author,
                "timestamp": datetime.utcnow().isoformat(),
                "snapshot": version_data
            }
            
            # Store version in metadata
            if not notebook.metadata:
                notebook.metadata = {}
            
            if "versions" not in notebook.metadata:
                notebook.metadata["versions"] = []
            
            notebook.metadata["versions"].append(version_info)
            
            # Increment version
            notebook.version += 1
            notebook.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(notebook)
            
            logger.info(f"Created version {notebook.version} for notebook {notebook.id}")
            
            return {
                "version_id": version_info["version_id"],
                "version_number": version_info["version_number"],
                "message": message,
                "author": author,
                "timestamp": version_info["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Failed to create version for notebook {notebook.id}: {e}")
            db.rollback()
            raise
    
    def get_version_history(
        self, 
        db: Session, 
        notebook_id: UUID, 
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get version history for a notebook."""
        
        notebook = notebook_crud.get(db, id=notebook_id)
        if not notebook:
            return []
        
        versions = notebook.metadata.get("versions", []) if notebook.metadata else []
        
        # Sort by version number descending and limit
        sorted_versions = sorted(
            versions, 
            key=lambda x: x.get("version_number", 0), 
            reverse=True
        )[:limit]
        
        # Return summary info (without full snapshots)
        return [
            {
                "version_id": version.get("version_id"),
                "version_number": version.get("version_number"),
                "parent_version": version.get("parent_version"),
                "message": version.get("message"),
                "author": version.get("author"),
                "timestamp": version.get("timestamp"),
                "cell_count": len(version.get("snapshot", {}).get("cells", [])),
                "content_size": len(str(version.get("snapshot", {})))
            }
            for version in sorted_versions
        ]
    
    def get_version_details(
        self, 
        db: Session, 
        notebook_id: UUID, 
        version_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific version."""
        
        notebook = notebook_crud.get(db, id=notebook_id)
        if not notebook:
            return None
        
        versions = notebook.metadata.get("versions", []) if notebook.metadata else []
        
        for version in versions:
            if version.get("version_id") == version_id:
                return version
        
        return None
    
    def restore_version(
        self, 
        db: Session, 
        notebook_id: UUID, 
        version_id: str,
        create_backup: bool = True
    ) -> Notebook:
        """Restore notebook to a specific version."""
        
        try:
            notebook = notebook_crud.get_with_cells(db, id=notebook_id)
            if not notebook:
                raise ValueError(f"Notebook {notebook_id} not found")
            
            # Get version data
            version_data = self.get_version_details(db, notebook_id, version_id)
            if not version_data:
                raise ValueError(f"Version {version_id} not found")
            
            # Create backup of current state if requested
            if create_backup:
                self.create_version(
                    db=db, 
                    notebook=notebook, 
                    message=f"Backup before restoring to version {version_data.get('version_number')}",
                    author="system"
                )
            
            # Restore from snapshot
            snapshot = version_data.get("snapshot", {})
            self._restore_from_snapshot(db, notebook, snapshot)
            
            # Update version info
            notebook.version = version_data.get("version_number", notebook.version)
            notebook.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(notebook)
            
            logger.info(f"Restored notebook {notebook_id} to version {version_id}")
            return notebook
            
        except Exception as e:
            logger.error(f"Failed to restore notebook {notebook_id} to version {version_id}: {e}")
            db.rollback()
            raise
    
    def compare_versions(
        self, 
        db: Session, 
        notebook_id: UUID, 
        version1_id: str, 
        version2_id: str
    ) -> Dict[str, Any]:
        """Compare two versions of a notebook."""
        
        version1 = self.get_version_details(db, notebook_id, version1_id)
        version2 = self.get_version_details(db, notebook_id, version2_id)
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
        
        snapshot1 = version1.get("snapshot", {})
        snapshot2 = version2.get("snapshot", {})
        
        # Compare basic info
        comparison = {
            "version1": {
                "id": version1_id,
                "number": version1.get("version_number"),
                "timestamp": version1.get("timestamp"),
                "author": version1.get("author")
            },
            "version2": {
                "id": version2_id,
                "number": version2.get("version_number"),
                "timestamp": version2.get("timestamp"),
                "author": version2.get("author")
            },
            "differences": self._compare_snapshots(snapshot1, snapshot2)
        }
        
        return comparison
    
    def _create_version_snapshot(self, notebook: Notebook) -> Dict[str, Any]:
        """Create a complete snapshot of the notebook state."""
        
        return {
            "title": notebook.title,
            "description": notebook.description,
            "metadata": notebook.metadata or {},
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
    
    def _restore_from_snapshot(
        self, 
        db: Session, 
        notebook: Notebook, 
        snapshot: Dict[str, Any]
    ) -> None:
        """Restore notebook from a snapshot."""
        
        # Update notebook properties
        notebook.title = snapshot.get("title", notebook.title)
        notebook.description = snapshot.get("description", notebook.description)
        notebook.metadata = snapshot.get("metadata", {})
        
        # Clear existing cells
        for cell in notebook.cells:
            db.delete(cell)
        
        db.flush()
        
        # Recreate cells from snapshot
        for cell_data in snapshot.get("cells", []):
            cell = Cell(
                notebook_id=notebook.id,
                cell_type=cell_data.get("cell_type", "code"),
                content=cell_data.get("content", ""),
                position=cell_data.get("position", 0),
                execution_count=cell_data.get("execution_count", 0),
                metadata=cell_data.get("metadata", {})
            )
            
            db.add(cell)
            db.flush()
            
            # Recreate outputs
            from app.models.notebook import CellOutput
            for output_data in cell_data.get("outputs", []):
                output = CellOutput(
                    cell_id=cell.id,
                    output_type=output_data.get("output_type", "stream"),
                    content=output_data.get("content", ""),
                    metadata=output_data.get("metadata", {}),
                    output_index=output_data.get("output_index", 0)
                )
                db.add(output)
    
    def _compare_snapshots(
        self, 
        snapshot1: Dict[str, Any], 
        snapshot2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare two snapshots and return differences."""
        
        differences = {
            "title_changed": snapshot1.get("title") != snapshot2.get("title"),
            "description_changed": snapshot1.get("description") != snapshot2.get("description"),
            "metadata_changed": snapshot1.get("metadata") != snapshot2.get("metadata"),
            "cell_changes": []
        }
        
        cells1 = {cell["id"]: cell for cell in snapshot1.get("cells", [])}
        cells2 = {cell["id"]: cell for cell in snapshot2.get("cells", [])}
        
        # Find added, removed, and modified cells
        all_cell_ids = set(cells1.keys()) | set(cells2.keys())
        
        for cell_id in all_cell_ids:
            if cell_id not in cells1:
                differences["cell_changes"].append({
                    "cell_id": cell_id,
                    "change_type": "added",
                    "position": cells2[cell_id].get("position")
                })
            elif cell_id not in cells2:
                differences["cell_changes"].append({
                    "cell_id": cell_id,
                    "change_type": "removed",
                    "position": cells1[cell_id].get("position")
                })
            else:
                cell1 = cells1[cell_id]
                cell2 = cells2[cell_id]
                
                changes = []
                if cell1.get("content") != cell2.get("content"):
                    changes.append("content")
                if cell1.get("cell_type") != cell2.get("cell_type"):
                    changes.append("type")
                if cell1.get("position") != cell2.get("position"):
                    changes.append("position")
                if cell1.get("metadata") != cell2.get("metadata"):
                    changes.append("metadata")
                
                if changes:
                    differences["cell_changes"].append({
                        "cell_id": cell_id,
                        "change_type": "modified",
                        "changes": changes,
                        "position": cell2.get("position")
                    })
        
        return differences
    
    def create_branch(
        self, 
        db: Session, 
        notebook_id: UUID, 
        branch_name: str,
        from_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new branch from the current or specified version."""
        
        # This would be implemented with a proper branching system
        # For now, we'll create a new notebook as a branch
        
        source_notebook = notebook_crud.get_with_cells(db, id=notebook_id)
        if not source_notebook:
            raise ValueError(f"Notebook {notebook_id} not found")
        
        # In a real implementation, this would be a separate branch table
        # For simplicity, we'll add branch info to metadata
        
        branch_info = {
            "branch_id": str(uuid4()),
            "branch_name": branch_name,
            "parent_notebook_id": str(notebook_id),
            "created_from_version": from_version or str(source_notebook.version),
            "created_at": datetime.utcnow().isoformat(),
            "is_branch": True
        }
        
        if not source_notebook.metadata:
            source_notebook.metadata = {}
        
        if "branches" not in source_notebook.metadata:
            source_notebook.metadata["branches"] = []
        
        source_notebook.metadata["branches"].append(branch_info)
        
        db.commit()
        
        logger.info(f"Created branch '{branch_name}' for notebook {notebook_id}")
        
        return branch_info


# Global instance
notebook_versioning_service = NotebookVersioningService()
