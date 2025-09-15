"""
Notebook import/export service for various formats.
"""

import json
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.notebook import Notebook, Cell, CellType, CellOutput
from app.crud.notebook import notebook as notebook_crud
from app.crud.cell import cell as cell_crud
from app.schemas.notebook import NotebookImport, NotebookCreate

logger = logging.getLogger(__name__)


class NotebookIOService:
    """Service for importing and exporting notebooks in various formats."""
    
    def export_notebook(
        self, 
        notebook: Notebook, 
        format: str = "jupyter"
    ) -> Dict[str, Any]:
        """Export notebook to specified format."""
        
        if format.lower() == "jupyter":
            return self._export_to_jupyter(notebook)
        elif format.lower() == "json":
            return self._export_to_json(notebook)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def import_notebook(
        self, 
        db: Session, 
        import_data: NotebookImport, 
        workbook_id: UUID
    ) -> Notebook:
        """Import notebook from specified format."""
        
        if import_data.format.lower() == "jupyter":
            return self._import_from_jupyter(db, import_data, workbook_id)
        elif import_data.format.lower() == "json":
            return self._import_from_json(db, import_data, workbook_id)
        else:
            raise ValueError(f"Unsupported import format: {import_data.format}")
    
    def _export_to_jupyter(self, notebook: Notebook) -> Dict[str, Any]:
        """Export notebook to Jupyter .ipynb format."""
        
        # Standard Jupyter notebook structure
        jupyter_notebook = {
            "cells": [],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python",
                    "version": "3.8.0"
                },
                "simu_lab": {
                    "notebook_id": str(notebook.id),
                    "workbook_id": str(notebook.workbook_id),
                    "version": notebook.version,
                    "title": notebook.title,
                    "description": notebook.description,
                    "created_at": notebook.created_at.isoformat() if notebook.created_at else None,
                    "updated_at": notebook.updated_at.isoformat() if notebook.updated_at else None
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Add custom metadata
        if notebook.metadata:
            jupyter_notebook["metadata"]["simu_lab"].update(notebook.metadata)
        
        # Convert cells
        for cell in sorted(notebook.cells, key=lambda x: x.position):
            jupyter_cell = self._convert_cell_to_jupyter(cell)
            jupyter_notebook["cells"].append(jupyter_cell)
        
        return jupyter_notebook
    
    def _convert_cell_to_jupyter(self, cell: Cell) -> Dict[str, Any]:
        """Convert our cell format to Jupyter cell format."""
        
        # Map our cell types to Jupyter types
        cell_type_mapping = {
            CellType.CODE: "code",
            CellType.MARKDOWN: "markdown",
            CellType.PHYSICS: "code",  # Physics cells are treated as code in Jupyter
            CellType.VISUALIZATION: "code"  # Visualization cells are treated as code
        }
        
        jupyter_cell = {
            "cell_type": cell_type_mapping.get(cell.cell_type, "code"),
            "metadata": {
                "simu_lab": {
                    "cell_id": str(cell.id),
                    "original_type": cell.cell_type.value,
                    "position": cell.position,
                    "execution_count": cell.execution_count
                }
            },
            "source": cell.content.split('\n') if cell.content else [""]
        }
        
        # Add custom metadata
        if cell.metadata:
            jupyter_cell["metadata"]["simu_lab"].update(cell.metadata)
        
        # Add execution count and outputs for code cells
        if jupyter_cell["cell_type"] == "code":
            jupyter_cell["execution_count"] = cell.execution_count if cell.execution_count > 0 else None
            jupyter_cell["outputs"] = []
            
            # Convert outputs
            for output in cell.outputs:
                jupyter_output = {
                    "output_type": output.output_type,
                    "data": {"text/plain": output.content} if output.content else {},
                    "metadata": output.metadata or {}
                }
                jupyter_cell["outputs"].append(jupyter_output)
        
        return jupyter_cell
    
    def _import_from_jupyter(
        self, 
        db: Session, 
        import_data: NotebookImport, 
        workbook_id: UUID
    ) -> Notebook:
        """Import notebook from Jupyter .ipynb format."""
        
        try:
            jupyter_data = import_data.content
            
            # Extract metadata
            simu_lab_metadata = jupyter_data.get("metadata", {}).get("simu_lab", {})
            
            # Create notebook
            notebook_create = NotebookCreate(
                title=import_data.title,
                description=simu_lab_metadata.get("description", ""),
                workbook_id=workbook_id,
                metadata=simu_lab_metadata
            )
            
            notebook = notebook_crud.create(db, obj_in=notebook_create)
            
            # Import cells
            cells_data = jupyter_data.get("cells", [])
            for position, cell_data in enumerate(cells_data):
                self._import_jupyter_cell(db, cell_data, notebook.id, position)
            
            db.commit()
            db.refresh(notebook)
            
            logger.info(f"Imported Jupyter notebook: {notebook.title} ({notebook.id})")
            return notebook
            
        except Exception as e:
            logger.error(f"Failed to import Jupyter notebook: {e}")
            db.rollback()
            raise
    
    def _import_jupyter_cell(
        self, 
        db: Session, 
        cell_data: Dict[str, Any], 
        notebook_id: UUID, 
        position: int
    ) -> Cell:
        """Import a single cell from Jupyter format."""
        
        # Map Jupyter cell types to our types
        jupyter_type = cell_data.get("cell_type", "code")
        simu_lab_metadata = cell_data.get("metadata", {}).get("simu_lab", {})
        original_type = simu_lab_metadata.get("original_type")
        
        if original_type:
            # Use original type if available
            cell_type = CellType(original_type)
        else:
            # Map from Jupyter types
            type_mapping = {
                "code": CellType.CODE,
                "markdown": CellType.MARKDOWN,
                "raw": CellType.CODE
            }
            cell_type = type_mapping.get(jupyter_type, CellType.CODE)
        
        # Get cell content
        source = cell_data.get("source", [])
        if isinstance(source, list):
            content = '\n'.join(source)
        else:
            content = str(source)
        
        # Create cell
        cell = Cell(
            notebook_id=notebook_id,
            cell_type=cell_type,
            content=content,
            position=position,
            execution_count=cell_data.get("execution_count", 0) or 0,
            metadata=simu_lab_metadata
        )
        
        db.add(cell)
        db.flush()  # Get the ID
        
        # Import outputs for code cells
        if jupyter_type == "code" and "outputs" in cell_data:
            for output_index, output_data in enumerate(cell_data["outputs"]):
                output = CellOutput(
                    cell_id=cell.id,
                    output_type=output_data.get("output_type", "stream"),
                    content=self._extract_output_content(output_data),
                    metadata=output_data.get("metadata", {}),
                    output_index=output_index
                )
                db.add(output)
        
        return cell
    
    def _extract_output_content(self, output_data: Dict[str, Any]) -> str:
        """Extract readable content from Jupyter output data."""
        
        if "text" in output_data:
            text = output_data["text"]
            return '\n'.join(text) if isinstance(text, list) else str(text)
        
        if "data" in output_data:
            data = output_data["data"]
            if "text/plain" in data:
                text = data["text/plain"]
                return '\n'.join(text) if isinstance(text, list) else str(text)
            elif "text/html" in data:
                return str(data["text/html"])
            else:
                # Return first available text format
                for key, value in data.items():
                    if "text" in key:
                        return '\n'.join(value) if isinstance(value, list) else str(value)
        
        return str(output_data.get("text", ""))
    
    def _export_to_json(self, notebook: Notebook) -> Dict[str, Any]:
        """Export notebook to our custom JSON format."""
        
        return {
            "id": str(notebook.id),
            "title": notebook.title,
            "description": notebook.description,
            "workbook_id": str(notebook.workbook_id),
            "metadata": notebook.metadata,
            "version": notebook.version,
            "created_at": notebook.created_at.isoformat() if notebook.created_at else None,
            "updated_at": notebook.updated_at.isoformat() if notebook.updated_at else None,
            "cells": [
                {
                    "id": str(cell.id),
                    "cell_type": cell.cell_type.value,
                    "content": cell.content,
                    "position": cell.position,
                    "execution_count": cell.execution_count,
                    "metadata": cell.metadata,
                    "outputs": [
                        {
                            "id": str(output.id),
                            "output_type": output.output_type,
                            "content": output.content,
                            "metadata": output.metadata,
                            "output_index": output.output_index
                        }
                        for output in cell.outputs
                    ]
                }
                for cell in sorted(notebook.cells, key=lambda x: x.position)
            ]
        }
    
    def _import_from_json(
        self, 
        db: Session, 
        import_data: NotebookImport, 
        workbook_id: UUID
    ) -> Notebook:
        """Import notebook from our custom JSON format."""
        
        try:
            json_data = import_data.content
            
            # Create notebook
            notebook_create = NotebookCreate(
                title=import_data.title,
                description=json_data.get("description", ""),
                workbook_id=workbook_id,
                metadata=json_data.get("metadata", {})
            )
            
            notebook = notebook_crud.create(db, obj_in=notebook_create)
            
            # Import cells
            cells_data = json_data.get("cells", [])
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
                
                # Import outputs
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
            
            logger.info(f"Imported JSON notebook: {notebook.title} ({notebook.id})")
            return notebook
            
        except Exception as e:
            logger.error(f"Failed to import JSON notebook: {e}")
            db.rollback()
            raise


# Global instance
notebook_io_service = NotebookIOService()
