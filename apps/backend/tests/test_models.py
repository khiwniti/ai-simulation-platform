"""
Unit tests for database models.
"""

import pytest
from uuid import uuid4
from app.models import (
    Workbook, Notebook, Cell, CellOutput, CellType,
    SimulationContext, GPUResourceConfig, ExecutionState,
    AgentInteraction, AgentType
)


class TestWorkbookModel:
    """Test cases for Workbook model."""
    
    def test_create_workbook(self, test_db, sample_workbook_data):
        """Test creating a workbook."""
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        assert workbook.id is not None
        assert workbook.title == sample_workbook_data["title"]
        assert workbook.description == sample_workbook_data["description"]
        assert workbook.created_at is not None
        assert workbook.updated_at is not None
    
    def test_workbook_repr(self, test_db, sample_workbook_data):
        """Test workbook string representation."""
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        repr_str = repr(workbook)
        assert "Workbook" in repr_str
        assert str(workbook.id) in repr_str
        assert workbook.title in repr_str


class TestNotebookModel:
    """Test cases for Notebook model."""
    
    def test_create_notebook(self, test_db, sample_workbook_data, sample_notebook_data):
        """Test creating a notebook."""
        # Create workbook first
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        # Create notebook
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        assert notebook.id is not None
        assert notebook.title == sample_notebook_data["title"]
        assert notebook.workbook_id == workbook.id
        assert notebook.version == 1
        assert notebook.metadata == sample_notebook_data["metadata"]
    
    def test_notebook_workbook_relationship(self, test_db, sample_workbook_data, sample_notebook_data):
        """Test notebook-workbook relationship."""
        # Create workbook
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        # Create notebook
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        # Test relationship
        assert notebook.workbook == workbook
        assert notebook in workbook.notebooks


class TestCellModel:
    """Test cases for Cell model."""
    
    def test_create_cell(self, test_db, sample_workbook_data, sample_notebook_data, sample_cell_data):
        """Test creating a cell."""
        # Create workbook and notebook
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        # Create cell
        cell_data = {**sample_cell_data, "notebook_id": notebook.id}
        cell = Cell(**cell_data)
        test_db.add(cell)
        test_db.commit()
        
        assert cell.id is not None
        assert cell.cell_type == CellType.CODE
        assert cell.content == sample_cell_data["content"]
        assert cell.position == 0
        assert cell.execution_count == 0
    
    def test_cell_types(self, test_db, sample_workbook_data, sample_notebook_data):
        """Test different cell types."""
        # Setup
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        # Test each cell type
        cell_types = [CellType.CODE, CellType.MARKDOWN, CellType.PHYSICS, CellType.VISUALIZATION]
        
        for i, cell_type in enumerate(cell_types):
            cell = Cell(
                notebook_id=notebook.id,
                cell_type=cell_type,
                content=f"Content for {cell_type.value}",
                position=i
            )
            test_db.add(cell)
        
        test_db.commit()
        
        # Verify all cells were created
        cells = test_db.query(Cell).filter(Cell.notebook_id == notebook.id).all()
        assert len(cells) == 4
        
        for cell in cells:
            assert cell.cell_type in cell_types


class TestCellOutputModel:
    """Test cases for CellOutput model."""
    
    def test_create_cell_output(self, test_db, sample_workbook_data, sample_notebook_data, sample_cell_data):
        """Test creating cell output."""
        # Setup
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        cell_data = {**sample_cell_data, "notebook_id": notebook.id}
        cell = Cell(**cell_data)
        test_db.add(cell)
        test_db.commit()
        
        # Create cell output
        output = CellOutput(
            cell_id=cell.id,
            output_type="text",
            content="Hello Physics!",
            output_index=0,
            metadata={"execution_time": 0.1}
        )
        test_db.add(output)
        test_db.commit()
        
        assert output.id is not None
        assert output.cell_id == cell.id
        assert output.output_type == "text"
        assert output.content == "Hello Physics!"
        assert output.output_index == 0


class TestSimulationContextModel:
    """Test cases for SimulationContext model."""
    
    def test_create_simulation_context(self, test_db, sample_workbook_data, sample_notebook_data):
        """Test creating simulation context."""
        # Setup
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        # Create simulation context
        sim_context = SimulationContext(
            notebook_id=notebook.id,
            physics_parameters={"gravity": 9.81, "timestep": 0.01},
            execution_state=ExecutionState.IDLE.value,
            active_agents=["physics", "visualization"],
            gpu_device_id=0,
            gpu_memory_limit=8.0
        )
        test_db.add(sim_context)
        test_db.commit()
        
        assert sim_context.id is not None
        assert sim_context.notebook_id == notebook.id
        assert sim_context.physics_parameters["gravity"] == 9.81
        assert sim_context.execution_state == ExecutionState.IDLE.value
        assert "physics" in sim_context.active_agents


class TestGPUResourceConfigModel:
    """Test cases for GPUResourceConfig model."""
    
    def test_create_gpu_config(self, test_db):
        """Test creating GPU resource configuration."""
        gpu_config = GPUResourceConfig(
            device_name="NVIDIA RTX 4090",
            device_id=0,
            total_memory=24.0,
            compute_capability="8.9",
            driver_version="535.98",
            cuda_version="12.2",
            physx_compatible="true"
        )
        test_db.add(gpu_config)
        test_db.commit()
        
        assert gpu_config.id is not None
        assert gpu_config.device_name == "NVIDIA RTX 4090"
        assert gpu_config.total_memory == 24.0
        assert gpu_config.compute_capability == "8.9"
        assert gpu_config.physx_compatible == "true"


class TestAgentInteractionModel:
    """Test cases for AgentInteraction model."""
    
    def test_create_agent_interaction(self, test_db, sample_workbook_data, sample_notebook_data):
        """Test creating agent interaction."""
        # Setup
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        # Create agent interaction
        session_id = uuid4()
        interaction = AgentInteraction(
            session_id=session_id,
            agent_type=AgentType.PHYSICS.value,
            query="How do I set up a physics simulation?",
            response="You can start by defining the physics parameters...",
            context={"simulation_type": "rigid_body"},
            confidence_score=0.95,
            notebook_id=notebook.id,
            response_time=0.5,
            tokens_used=150
        )
        test_db.add(interaction)
        test_db.commit()
        
        assert interaction.id is not None
        assert interaction.session_id == session_id
        assert interaction.agent_type == AgentType.PHYSICS.value
        assert interaction.confidence_score == 0.95
        assert interaction.notebook_id == notebook.id


class TestModelValidation:
    """Test cases for model validation."""
    
    def test_required_fields(self, test_db):
        """Test that required fields are enforced."""
        # Test workbook without title should fail
        with pytest.raises(Exception):
            workbook = Workbook(description="No title")
            test_db.add(workbook)
            test_db.commit()
    
    def test_foreign_key_constraints(self, test_db):
        """Test foreign key constraints."""
        # Test notebook with invalid workbook_id should fail
        with pytest.raises(Exception):
            notebook = Notebook(
                title="Test",
                workbook_id=uuid4()  # Non-existent workbook
            )
            test_db.add(notebook)
            test_db.commit()
    
    def test_cascade_delete(self, test_db, sample_workbook_data, sample_notebook_data):
        """Test cascade delete behavior."""
        # Create workbook with notebook
        workbook = Workbook(**sample_workbook_data)
        test_db.add(workbook)
        test_db.commit()
        
        notebook_data = {**sample_notebook_data, "workbook_id": workbook.id}
        notebook = Notebook(**notebook_data)
        test_db.add(notebook)
        test_db.commit()
        
        notebook_id = notebook.id
        
        # Delete workbook should cascade to notebook
        test_db.delete(workbook)
        test_db.commit()
        
        # Notebook should be deleted
        deleted_notebook = test_db.query(Notebook).filter(Notebook.id == notebook_id).first()
        assert deleted_notebook is None