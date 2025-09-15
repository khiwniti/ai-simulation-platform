"""
Tests for notebook persistence and file operations.
"""

import pytest
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from uuid import UUID, uuid4
from sqlalchemy.orm import Session

from app.models.notebook import Notebook, Cell, CellType, CellOutput
from app.models.workbook import Workbook
from app.schemas.notebook import NotebookCreate, NotebookAutoSave, NotebookImport
from app.services.notebook_persistence import notebook_persistence_service
from app.services.notebook_io import notebook_io_service
from app.services.notebook_versioning import notebook_versioning_service
from app.services.notebook_backup import notebook_backup_service
from app.crud.notebook import notebook as notebook_crud
from app.crud.workbook import workbook as workbook_crud


class TestNotebookPersistence:
    """Test notebook persistence and auto-save functionality."""
    
    def test_should_auto_save(self):
        """Test auto-save timing logic."""
        service = notebook_persistence_service
        notebook_id = uuid4()
        
        # Should auto-save when no previous save
        assert service.should_auto_save(notebook_id) is True
        
        # Simulate auto-save
        service.last_auto_save[notebook_id] = datetime.utcnow()
        assert service.should_auto_save(notebook_id) is False
        
        # Should auto-save after interval
        service.last_auto_save[notebook_id] = datetime.utcnow() - timedelta(seconds=60)
        assert service.should_auto_save(notebook_id) is True
    
    def test_auto_save_notebook(self, db: Session):
        """Test auto-save functionality."""
        # Create test workbook and notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook_create = NotebookCreate(
            title="Test Notebook",
            workbook_id=workbook.id,
            metadata={"test": "value"}
        )
        notebook = notebook_crud.create(db, obj_in=notebook_create)
        
        # Create auto-save data
        auto_save_data = NotebookAutoSave(
            metadata={"updated": "auto-save"},
            last_modified=datetime.utcnow().isoformat()
        )
        
        # Perform auto-save
        saved_notebook = notebook_persistence_service.auto_save(
            db=db,
            notebook_id=notebook.id,
            auto_save_data=auto_save_data
        )
        
        assert saved_notebook.id == notebook.id
        assert saved_notebook.metadata["updated"] == "auto-save"
        assert saved_notebook.version == notebook.version  # Version should not increment
    
    def test_force_save_notebook(self, db: Session):
        """Test force save functionality."""
        # Create test workbook and notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook_create = NotebookCreate(
            title="Test Notebook",
            workbook_id=workbook.id
        )
        notebook = notebook_crud.create(db, obj_in=notebook_create)
        original_version = notebook.version
        
        # Perform force save
        saved_notebook = notebook_persistence_service.force_save(db, notebook.id)
        
        assert saved_notebook.version == original_version + 1  # Version should increment
    
    def test_get_auto_save_status(self):
        """Test auto-save status retrieval."""
        service = notebook_persistence_service
        notebook_id = uuid4()
        
        # Get status when no auto-save performed
        status = service.get_auto_save_status(notebook_id)
        assert status["last_auto_save"] is None
        assert status["should_auto_save"] is True
        
        # Simulate auto-save
        service.last_auto_save[notebook_id] = datetime.utcnow()
        status = service.get_auto_save_status(notebook_id)
        assert status["last_auto_save"] is not None
        assert status["should_auto_save"] is False


class TestNotebookIO:
    """Test notebook import/export functionality."""
    
    def test_export_to_jupyter(self, db: Session):
        """Test exporting notebook to Jupyter format."""
        # Create test notebook with cells
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="Test Notebook",
            description="Test Description",
            workbook_id=workbook.id,
            metadata={"custom": "data"}
        )
        db.add(notebook)
        db.flush()
        
        # Add cells
        code_cell = Cell(
            notebook_id=notebook.id,
            cell_type=CellType.CODE,
            content="print('Hello, World!')",
            position=0,
            execution_count=1
        )
        markdown_cell = Cell(
            notebook_id=notebook.id,
            cell_type=CellType.MARKDOWN,
            content="# Test Markdown",
            position=1
        )
        db.add_all([code_cell, markdown_cell])
        db.flush()
        
        # Add cell output
        output = CellOutput(
            cell_id=code_cell.id,
            output_type="stream",
            content="Hello, World!",
            output_index=0
        )
        db.add(output)
        db.commit()
        
        # Refresh to load relationships
        db.refresh(notebook)
        
        # Export to Jupyter
        jupyter_data = notebook_io_service.export_notebook(notebook, "jupyter")
        
        assert jupyter_data["nbformat"] == 4
        assert jupyter_data["nbformat_minor"] == 4
        assert len(jupyter_data["cells"]) == 2
        assert jupyter_data["metadata"]["simu_lab"]["title"] == "Test Notebook"
        
        # Check code cell
        code_cell_data = jupyter_data["cells"][0]
        assert code_cell_data["cell_type"] == "code"
        assert code_cell_data["source"] == ["print('Hello, World!')"]
        assert code_cell_data["execution_count"] == 1
        assert len(code_cell_data["outputs"]) == 1
        
        # Check markdown cell
        markdown_cell_data = jupyter_data["cells"][1]
        assert markdown_cell_data["cell_type"] == "markdown"
        assert markdown_cell_data["source"] == ["# Test Markdown"]
    
    def test_import_from_jupyter(self, db: Session):
        """Test importing notebook from Jupyter format."""
        # Create test workbook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.commit()
        
        # Create Jupyter notebook data
        jupyter_data = {
            "cells": [
                {
                    "cell_type": "code",
                    "source": ["import numpy as np", "print(np.version.version)"],
                    "execution_count": 1,
                    "outputs": [
                        {
                            "output_type": "stream",
                            "text": ["1.21.0"]
                        }
                    ],
                    "metadata": {}
                },
                {
                    "cell_type": "markdown",
                    "source": ["## Data Analysis"],
                    "metadata": {}
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                },
                "simu_lab": {
                    "description": "Imported notebook"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
        
        # Import notebook
        import_data = NotebookImport(
            title="Imported Notebook",
            content=jupyter_data,
            format="jupyter"
        )
        
        imported_notebook = notebook_io_service.import_notebook(
            db=db,
            import_data=import_data,
            workbook_id=workbook.id
        )
        
        assert imported_notebook.title == "Imported Notebook"
        assert len(imported_notebook.cells) == 2
        
        # Check imported cells
        code_cell = next(cell for cell in imported_notebook.cells if cell.cell_type == CellType.CODE)
        assert "import numpy as np" in code_cell.content
        assert len(code_cell.outputs) == 1
        
        markdown_cell = next(cell for cell in imported_notebook.cells if cell.cell_type == CellType.MARKDOWN)
        assert "## Data Analysis" in markdown_cell.content
    
    def test_export_to_json(self, db: Session):
        """Test exporting notebook to JSON format."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="JSON Test",
            workbook_id=workbook.id
        )
        db.add(notebook)
        db.commit()
        db.refresh(notebook)
        
        # Export to JSON
        json_data = notebook_io_service.export_notebook(notebook, "json")
        
        assert json_data["title"] == "JSON Test"
        assert json_data["id"] == str(notebook.id)
        assert json_data["workbook_id"] == str(workbook.id)
        assert "cells" in json_data
    
    def test_import_from_json(self, db: Session):
        """Test importing notebook from JSON format."""
        # Create test workbook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.commit()
        
        # Create JSON notebook data
        json_data = {
            "title": "JSON Import Test",
            "description": "Imported from JSON",
            "metadata": {"format": "json"},
            "cells": [
                {
                    "cell_type": "code",
                    "content": "x = 42",
                    "position": 0,
                    "execution_count": 0,
                    "metadata": {},
                    "outputs": []
                }
            ]
        }
        
        # Import notebook
        import_data = NotebookImport(
            title="JSON Import Test",
            content=json_data,
            format="json"
        )
        
        imported_notebook = notebook_io_service.import_notebook(
            db=db,
            import_data=import_data,
            workbook_id=workbook.id
        )
        
        assert imported_notebook.title == "JSON Import Test"
        assert imported_notebook.description == "Imported from JSON"
        assert len(imported_notebook.cells) == 1
        assert imported_notebook.cells[0].content == "x = 42"
    
    def test_unsupported_format(self, db: Session):
        """Test handling of unsupported formats."""
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(title="Test", workbook_id=workbook.id)
        db.add(notebook)
        db.commit()
        
        # Test unsupported export format
        with pytest.raises(ValueError, match="Unsupported export format"):
            notebook_io_service.export_notebook(notebook, "unsupported")
        
        # Test unsupported import format
        import_data = NotebookImport(
            title="Test",
            content={},
            format="unsupported"
        )
        
        with pytest.raises(ValueError, match="Unsupported import format"):
            notebook_io_service.import_notebook(db, import_data, workbook.id)


class TestNotebookVersioning:
    """Test notebook version control functionality."""
    
    def test_create_version(self, db: Session):
        """Test creating a version checkpoint."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="Version Test",
            workbook_id=workbook.id,
            metadata={}
        )
        db.add(notebook)
        db.commit()
        db.refresh(notebook)
        
        original_version = notebook.version
        
        # Create version
        version_info = notebook_versioning_service.create_version(
            db=db,
            notebook=notebook,
            message="Test version",
            author="test_user"
        )
        
        assert version_info["version_number"] == original_version + 1
        assert version_info["message"] == "Test version"
        assert version_info["author"] == "test_user"
        assert "version_id" in version_info
        
        # Verify notebook version was incremented
        db.refresh(notebook)
        assert notebook.version == original_version + 1
        assert "versions" in notebook.metadata
        assert len(notebook.metadata["versions"]) == 1
    
    def test_get_version_history(self, db: Session):
        """Test retrieving version history."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="History Test",
            workbook_id=workbook.id,
            metadata={}
        )
        db.add(notebook)
        db.commit()
        
        # Create multiple versions
        version1 = notebook_versioning_service.create_version(
            db=db, notebook=notebook, message="First version"
        )
        version2 = notebook_versioning_service.create_version(
            db=db, notebook=notebook, message="Second version"
        )
        
        # Get version history
        history = notebook_versioning_service.get_version_history(
            db=db, notebook_id=notebook.id
        )
        
        assert len(history) == 2
        # Should be sorted by version number descending
        assert history[0]["version_number"] > history[1]["version_number"]
        assert history[0]["message"] == "Second version"
        assert history[1]["message"] == "First version"
    
    def test_get_version_details(self, db: Session):
        """Test retrieving specific version details."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="Details Test",
            workbook_id=workbook.id,
            metadata={}
        )
        db.add(notebook)
        db.commit()
        
        # Create version
        version_info = notebook_versioning_service.create_version(
            db=db, notebook=notebook, message="Test version"
        )
        
        # Get version details
        details = notebook_versioning_service.get_version_details(
            db=db,
            notebook_id=notebook.id,
            version_id=version_info["version_id"]
        )
        
        assert details is not None
        assert details["version_id"] == version_info["version_id"]
        assert details["message"] == "Test version"
        assert "snapshot" in details
    
    def test_compare_versions(self, db: Session):
        """Test comparing two versions."""
        # Create test notebook with cells
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="Compare Test",
            workbook_id=workbook.id,
            metadata={}
        )
        db.add(notebook)
        db.flush()
        
        # Add initial cell
        cell = Cell(
            notebook_id=notebook.id,
            cell_type=CellType.CODE,
            content="print('version 1')",
            position=0
        )
        db.add(cell)
        db.commit()
        db.refresh(notebook)
        
        # Create first version
        version1 = notebook_versioning_service.create_version(
            db=db, notebook=notebook, message="Version 1"
        )
        
        # Modify cell
        cell.content = "print('version 2')"
        db.commit()
        
        # Create second version
        version2 = notebook_versioning_service.create_version(
            db=db, notebook=notebook, message="Version 2"
        )
        
        # Compare versions
        comparison = notebook_versioning_service.compare_versions(
            db=db,
            notebook_id=notebook.id,
            version1_id=version1["version_id"],
            version2_id=version2["version_id"]
        )
        
        assert "differences" in comparison
        assert len(comparison["differences"]["cell_changes"]) == 1
        assert comparison["differences"]["cell_changes"][0]["change_type"] == "modified"
        assert "content" in comparison["differences"]["cell_changes"][0]["changes"]


class TestNotebookBackup:
    """Test notebook backup and recovery functionality."""
    
    def test_create_backup(self, db: Session):
        """Test creating a backup."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="Backup Test",
            workbook_id=workbook.id,
            metadata={}
        )
        db.add(notebook)
        db.commit()
        db.refresh(notebook)
        
        # Create backup
        backup_info = notebook_backup_service.create_backup(
            db=db,
            notebook=notebook,
            backup_type="manual",
            reason="test backup"
        )
        
        assert "backup_id" in backup_info
        assert backup_info["backup_type"] == "manual"
        assert backup_info["reason"] == "test backup"
        assert backup_info["notebook_version"] == notebook.version
        
        # Verify backup metadata was stored
        db.refresh(notebook)
        assert "backups" in notebook.metadata
        assert len(notebook.metadata["backups"]) == 1
    
    def test_list_backups(self, db: Session):
        """Test listing backups."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="List Test",
            workbook_id=workbook.id,
            metadata={}
        )
        db.add(notebook)
        db.commit()
        
        # Create multiple backups
        backup1 = notebook_backup_service.create_backup(
            db=db, notebook=notebook, backup_type="manual", reason="backup 1"
        )
        backup2 = notebook_backup_service.create_backup(
            db=db, notebook=notebook, backup_type="auto", reason="backup 2"
        )
        
        # List backups
        backups = notebook_backup_service.list_backups(db, notebook.id)
        
        assert len(backups) == 2
        # Should be sorted by timestamp descending
        assert backups[0]["timestamp"] >= backups[1]["timestamp"]
    
    def test_should_auto_backup(self, db: Session):
        """Test auto-backup decision logic."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="Auto Backup Test",
            workbook_id=workbook.id,
            metadata={}
        )
        db.add(notebook)
        db.commit()
        
        # Should auto-backup when no backups exist
        assert notebook_backup_service._should_auto_backup(notebook, "test") is True
        
        # Create a recent auto backup
        notebook_backup_service.create_backup(
            db=db,
            notebook=notebook,
            backup_type="automatic",
            reason="recent backup"
        )
        
        db.refresh(notebook)
        
        # Should not auto-backup when recent backup exists
        assert notebook_backup_service._should_auto_backup(notebook, "test") is False
    
    def test_backup_file_operations(self, db: Session):
        """Test backup file creation and loading."""
        # Create test notebook
        workbook = Workbook(title="Test Workbook", description="Test")
        db.add(workbook)
        db.flush()
        
        notebook = Notebook(
            title="File Test",
            workbook_id=workbook.id,
            metadata={"test": "data"}
        )
        db.add(notebook)
        db.flush()
        
        # Add a cell
        cell = Cell(
            notebook_id=notebook.id,
            cell_type=CellType.CODE,
            content="test_content",
            position=0
        )
        db.add(cell)
        db.commit()
        db.refresh(notebook)
        
        # Create backup
        backup_info = notebook_backup_service.create_backup(
            db=db,
            notebook=notebook,
            backup_type="manual",
            reason="test file operations"
        )
        
        # Verify file was created
        file_path = Path(backup_info["file_path"])
        assert file_path.exists()
        assert backup_info["file_size"] > 0
        
        # Load backup data
        backup_data = notebook_backup_service._load_backup_from_file(str(file_path))
        assert backup_data is not None
        assert backup_data["notebook"]["title"] == "File Test"
        assert len(backup_data["cells"]) == 1
        assert backup_data["cells"][0]["content"] == "test_content"
        
        # Clean up
        file_path.unlink()


# Fixtures for testing
@pytest.fixture
def sample_jupyter_notebook():
    """Sample Jupyter notebook data for testing."""
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "source": ["# Test Notebook", "", "This is a test notebook."],
                "metadata": {}
            },
            {
                "cell_type": "code",
                "source": ["import pandas as pd", "df = pd.DataFrame({'a': [1, 2, 3]})"],
                "execution_count": 1,
                "outputs": [
                    {
                        "output_type": "execute_result",
                        "data": {"text/plain": ["   a", "0  1", "1  2", "2  3"]},
                        "execution_count": 1,
                        "metadata": {}
                    }
                ],
                "metadata": {}
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8.5"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


@pytest.fixture
def temp_backup_dir():
    """Temporary directory for backup testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)
