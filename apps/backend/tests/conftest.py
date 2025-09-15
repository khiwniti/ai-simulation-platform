"""
Pytest configuration and fixtures.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base, get_db
from app.main import app
from app.models.workbook import Workbook
from app.models.notebook import Notebook, Cell, CellType, CellOutput
from app.models.simulation import SimulationContext
from app.models.agent import AgentInteraction


@pytest.fixture(scope="function")
def db():
    """Create a test database session."""
    # Use in-memory SQLite for testing
    engine = create_engine(
        "sqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    
    # Override the get_db dependency
    def override_get_db():
        try:
            yield session
        finally:
            pass  # Don't close session here, let fixture handle it
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.clear()


@pytest.fixture
def sample_workbook_data():
    """Sample workbook data for testing."""
    return {
        "title": "Test Workbook",
        "description": "A test workbook for physics simulations"
    }


@pytest.fixture
def sample_notebook_data():
    """Sample notebook data for testing."""
    return {
        "title": "Test Notebook",
        "description": "A test notebook for physics simulations",
        "metadata": {"physics_engine": "physx", "version": "1.0"}
    }


@pytest.fixture
def sample_cell_data():
    """Sample cell data for testing."""
    return {
        "cell_type": CellType.CODE,
        "content": "import numpy as np\nprint('Hello Physics!')",
        "position": 0,
        "metadata": {"language": "python"}
    }