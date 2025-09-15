"""
Unit tests for Pydantic schemas.
"""

import pytest
from uuid import uuid4
from pydantic import ValidationError
from app.schemas import (
    WorkbookCreate, WorkbookUpdate, WorkbookResponse,
    NotebookCreate, NotebookUpdate, NotebookResponse,
    CellCreate, CellUpdate, CellResponse,
    SimulationContextCreate, SimulationContextUpdate,
    AgentInteractionCreate
)
from app.models.notebook import CellType


class TestWorkbookSchemas:
    """Test cases for workbook schemas."""
    
    def test_workbook_create_valid(self):
        """Test valid workbook creation."""
        data = {
            "title": "Test Workbook",
            "description": "A test workbook"
        }
        schema = WorkbookCreate(**data)
        assert schema.title == "Test Workbook"
        assert schema.description == "A test workbook"
    
    def test_workbook_create_minimal(self):
        """Test workbook creation with minimal data."""
        data = {"title": "Minimal Workbook"}
        schema = WorkbookCreate(**data)
        assert schema.title == "Minimal Workbook"
        assert schema.description is None
    
    def test_workbook_create_invalid_title(self):
        """Test workbook creation with invalid title."""
        with pytest.raises(ValidationError):
            WorkbookCreate(title="")  # Empty title should fail
        
        with pytest.raises(ValidationError):
            WorkbookCreate(title="x" * 256)  # Too long title should fail
    
    def test_workbook_update(self):
        """Test workbook update schema."""
        data = {"title": "Updated Title"}
        schema = WorkbookUpdate(**data)
        assert schema.title == "Updated Title"
        assert schema.description is None
    
    def test_workbook_response(self):
        """Test workbook response schema."""
        data = {
            "id": uuid4(),
            "title": "Test Workbook",
            "description": "A test workbook",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00"
        }
        schema = WorkbookResponse(**data)
        assert schema.title == "Test Workbook"
        assert schema.id == data["id"]


class TestNotebookSchemas:
    """Test cases for notebook schemas."""
    
    def test_notebook_create_valid(self):
        """Test valid notebook creation."""
        workbook_id = uuid4()
        data = {
            "title": "Test Notebook",
            "description": "A test notebook",
            "workbook_id": workbook_id,
            "metadata": {"physics_engine": "physx"}
        }
        schema = NotebookCreate(**data)
        assert schema.title == "Test Notebook"
        assert schema.workbook_id == workbook_id
        assert schema.metadata["physics_engine"] == "physx"
    
    def test_notebook_create_minimal(self):
        """Test notebook creation with minimal data."""
        workbook_id = uuid4()
        data = {
            "title": "Minimal Notebook",
            "workbook_id": workbook_id
        }
        schema = NotebookCreate(**data)
        assert schema.title == "Minimal Notebook"
        assert schema.workbook_id == workbook_id
        assert schema.metadata == {}
    
    def test_notebook_update(self):
        """Test notebook update schema."""
        data = {
            "title": "Updated Notebook",
            "metadata": {"version": "2.0"}
        }
        schema = NotebookUpdate(**data)
        assert schema.title == "Updated Notebook"
        assert schema.metadata["version"] == "2.0"


class TestCellSchemas:
    """Test cases for cell schemas."""
    
    def test_cell_create_valid(self):
        """Test valid cell creation."""
        notebook_id = uuid4()
        data = {
            "notebook_id": notebook_id,
            "cell_type": CellType.CODE,
            "content": "print('Hello World')",
            "position": 0,
            "metadata": {"language": "python"}
        }
        schema = CellCreate(**data)
        assert schema.notebook_id == notebook_id
        assert schema.cell_type == CellType.CODE
        assert schema.content == "print('Hello World')"
        assert schema.position == 0
    
    def test_cell_create_different_types(self):
        """Test cell creation with different types."""
        notebook_id = uuid4()
        
        # Test each cell type
        for cell_type in CellType:
            data = {
                "notebook_id": notebook_id,
                "cell_type": cell_type,
                "content": f"Content for {cell_type.value}",
                "position": 0
            }
            schema = CellCreate(**data)
            assert schema.cell_type == cell_type
    
    def test_cell_update(self):
        """Test cell update schema."""
        data = {
            "content": "Updated content",
            "position": 1,
            "metadata": {"updated": True}
        }
        schema = CellUpdate(**data)
        assert schema.content == "Updated content"
        assert schema.position == 1
        assert schema.metadata["updated"] is True


class TestSimulationContextSchemas:
    """Test cases for simulation context schemas."""
    
    def test_simulation_context_create(self):
        """Test simulation context creation."""
        notebook_id = uuid4()
        data = {
            "notebook_id": notebook_id,
            "physics_parameters": {"gravity": 9.81, "timestep": 0.01},
            "execution_state": "running",
            "active_agents": ["physics", "visualization"]
        }
        schema = SimulationContextCreate(**data)
        assert schema.notebook_id == notebook_id
        assert schema.physics_parameters["gravity"] == 9.81
        assert "physics" in schema.active_agents
    
    def test_simulation_context_update(self):
        """Test simulation context update."""
        data = {
            "execution_state": "completed",
            "gpu_device_id": 0,
            "gpu_memory_limit": 8.0
        }
        schema = SimulationContextUpdate(**data)
        assert schema.execution_state == "completed"
        assert schema.gpu_device_id == 0
        assert schema.gpu_memory_limit == 8.0


class TestAgentInteractionSchemas:
    """Test cases for agent interaction schemas."""
    
    def test_agent_interaction_create(self):
        """Test agent interaction creation."""
        session_id = uuid4()
        notebook_id = uuid4()
        data = {
            "session_id": session_id,
            "agent_type": "physics",
            "query": "How do I set up a physics simulation?",
            "context": {"simulation_type": "rigid_body"},
            "notebook_id": notebook_id
        }
        schema = AgentInteractionCreate(**data)
        assert schema.session_id == session_id
        assert schema.agent_type == "physics"
        assert schema.query == "How do I set up a physics simulation?"
        assert schema.notebook_id == notebook_id
    
    def test_agent_interaction_create_minimal(self):
        """Test agent interaction creation with minimal data."""
        session_id = uuid4()
        data = {
            "session_id": session_id,
            "agent_type": "physics",
            "query": "Help with physics"
        }
        schema = AgentInteractionCreate(**data)
        assert schema.session_id == session_id
        assert schema.agent_type == "physics"
        assert schema.query == "Help with physics"
        assert schema.context == {}
    
    def test_agent_interaction_invalid_query(self):
        """Test agent interaction with invalid query."""
        session_id = uuid4()
        with pytest.raises(ValidationError):
            AgentInteractionCreate(
                session_id=session_id,
                agent_type="physics",
                query=""  # Empty query should fail
            )


class TestSchemaValidation:
    """Test cases for schema validation edge cases."""
    
    def test_uuid_validation(self):
        """Test UUID field validation."""
        # Valid UUID
        valid_uuid = uuid4()
        data = {
            "title": "Test Notebook",
            "workbook_id": valid_uuid
        }
        schema = NotebookCreate(**data)
        assert schema.workbook_id == valid_uuid
        
        # Invalid UUID should fail
        with pytest.raises(ValidationError):
            NotebookCreate(
                title="Test Notebook",
                workbook_id="invalid-uuid"
            )
    
    def test_json_field_validation(self):
        """Test JSON field validation."""
        # Valid JSON data
        data = {
            "title": "Test Notebook",
            "workbook_id": uuid4(),
            "metadata": {
                "physics_engine": "physx",
                "version": 1.0,
                "settings": {
                    "gravity": 9.81,
                    "enabled": True
                }
            }
        }
        schema = NotebookCreate(**data)
        assert schema.metadata["physics_engine"] == "physx"
        assert schema.metadata["settings"]["gravity"] == 9.81
    
    def test_optional_fields(self):
        """Test optional field handling."""
        # Test with all optional fields None
        data = {
            "title": "Test Notebook",
            "workbook_id": uuid4()
        }
        schema = NotebookCreate(**data)
        assert schema.description is None
        assert schema.metadata == {}
    
    def test_field_constraints(self):
        """Test field constraint validation."""
        # Test string length constraints
        with pytest.raises(ValidationError):
            WorkbookCreate(title="")  # Too short
        
        with pytest.raises(ValidationError):
            WorkbookCreate(title="x" * 300)  # Too long
        
        # Test minimum values
        notebook_id = uuid4()
        with pytest.raises(ValidationError):
            CellCreate(
                notebook_id=notebook_id,
                position=-1  # Negative position should fail
            )