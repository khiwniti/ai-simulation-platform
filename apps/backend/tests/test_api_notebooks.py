"""
Integration tests for notebook API endpoints.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app

client = TestClient(app)


class TestNotebookAPI:
    """Test notebook API endpoints."""
    
    def test_create_notebook(self, db: Session):
        """Test creating a new notebook."""
        # First create a workbook
        workbook_data = {
            "title": "Test Workbook for Notebooks",
            "description": "Workbook for notebook tests"
        }
        workbook_response = client.post("/api/v1/workbooks/", json=workbook_data)
        workbook = workbook_response.json()
        
        # Create notebook
        notebook_data = {
            "title": "Test Notebook",
            "description": "A test notebook for simulations",
            "workbook_id": workbook["id"],
            "metadata": {"simulation_type": "physics"}
        }
        
        response = client.post("/api/v1/notebooks/", json=notebook_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == notebook_data["title"]
        assert data["description"] == notebook_data["description"]
        assert data["workbook_id"] == workbook["id"]
        assert data["metadata"] == notebook_data["metadata"]
        assert data["version"] == 1
        assert "id" in data
    
    def test_create_notebook_invalid_workbook(self, db: Session):
        """Test creating notebook with invalid workbook ID."""
        fake_workbook_id = str(uuid4())
        notebook_data = {
            "title": "Test Notebook",
            "workbook_id": fake_workbook_id
        }
        
        response = client.post("/api/v1/notebooks/", json=notebook_data)
        
        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data["error"]["message"]
    
    def test_create_notebook_duplicate_title_in_workbook(self, db: Session):
        """Test creating notebook with duplicate title in same workbook."""
        # Create workbook
        workbook_data = {"title": "Test Workbook"}
        workbook_response = client.post("/api/v1/workbooks/", json=workbook_data)
        workbook = workbook_response.json()
        
        notebook_data = {
            "title": "Duplicate Notebook",
            "workbook_id": workbook["id"]
        }
        
        # Create first notebook
        response1 = client.post("/api/v1/notebooks/", json=notebook_data)
        assert response1.status_code == 201
        
        # Try to create second notebook with same title in same workbook
        response2 = client.post("/api/v1/notebooks/", json=notebook_data)
        
        assert response2.status_code == 409
        error_data = response2.json()
        assert "already exists" in error_data["error"]["message"]
    
    def test_get_notebooks(self, db: Session):
        """Test retrieving notebooks list."""
        # Create workbook and notebooks
        workbook_data = {"title": "Test Workbook"}
        workbook_response = client.post("/api/v1/workbooks/", json=workbook_data)
        workbook = workbook_response.json()
        
        for i in range(3):
            notebook_data = {
                "title": f"Test Notebook {i}",
                "workbook_id": workbook["id"]
            }
            client.post("/api/v1/notebooks/", json=notebook_data)
        
        response = client.get("/api/v1/notebooks/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    def test_get_notebooks_by_workbook(self, db: Session):
        """Test retrieving notebooks filtered by workbook."""
        # Create two workbooks
        workbook1_data = {"title": "Workbook 1"}
        workbook1_response = client.post("/api/v1/workbooks/", json=workbook1_data)
        workbook1 = workbook1_response.json()
        
        workbook2_data = {"title": "Workbook 2"}
        workbook2_response = client.post("/api/v1/workbooks/", json=workbook2_data)
        workbook2 = workbook2_response.json()
        
        # Create notebooks in each workbook
        for i in range(2):
            notebook_data = {
                "title": f"Notebook W1-{i}",
                "workbook_id": workbook1["id"]
            }
            client.post("/api/v1/notebooks/", json=notebook_data)
        
        notebook_data = {
            "title": "Notebook W2-1",
            "workbook_id": workbook2["id"]
        }
        client.post("/api/v1/notebooks/", json=notebook_data)
        
        # Get notebooks for workbook 1
        response = client.get(f"/api/v1/notebooks/?workbook_id={workbook1['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        for notebook in data:
            assert notebook["workbook_id"] == workbook1["id"]
    
    def test_get_notebook_by_id(self, db: Session):
        """Test retrieving notebook by ID."""
        # Create workbook and notebook
        workbook_data = {"title": "Test Workbook"}
        workbook_response = client.post("/api/v1/workbooks/", json=workbook_data)
        workbook = workbook_response.json()
        
        notebook_data = {
            "title": "Single Notebook",
            "workbook_id": workbook["id"]
        }
        create_response = client.post("/api/v1/notebooks/", json=notebook_data)
        created_notebook = create_response.json()
        
        # Get notebook by ID
        response = client.get(f"/api/v1/notebooks/{created_notebook['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_notebook["id"]
        assert data["title"] == notebook_data["title"]
    
    def test_get_notebook_not_found(self, db: Session):
        """Test retrieving non-existent notebook."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/notebooks/{fake_id}")
        
        assert response.status_code == 404
    
    def test_update_notebook(self, db: Session):
        """Test updating notebook."""
        # Create workbook and notebook
        workbook_data = {"title": "Test Workbook"}
        workbook_response = client.post("/api/v1/workbooks/", json=workbook_data)
        workbook = workbook_response.json()
        
        notebook_data = {
            "title": "Original Notebook",
            "workbook_id": workbook["id"]
        }
        create_response = client.post("/api/v1/notebooks/", json=notebook_data)
        created_notebook = create_response.json()
        
        # Update notebook
        update_data = {
            "title": "Updated Notebook",
            "description": "Updated description",
            "metadata": {"updated": True}
        }
        response = client.put(
            f"/api/v1/notebooks/{created_notebook['id']}", 
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["metadata"] == update_data["metadata"]
    
    def test_delete_notebook(self, db: Session):
        """Test deleting notebook."""
        # Create workbook and notebook
        workbook_data = {"title": "Test Workbook"}
        workbook_response = client.post("/api/v1/workbooks/", json=workbook_data)
        workbook = workbook_response.json()
        
        notebook_data = {
            "title": "To Be Deleted",
            "workbook_id": workbook["id"]
        }
        create_response = client.post("/api/v1/notebooks/", json=notebook_data)
        created_notebook = create_response.json()
        
        # Delete notebook
        response = client.delete(f"/api/v1/notebooks/{created_notebook['id']}")
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/v1/notebooks/{created_notebook['id']}")
        assert get_response.status_code == 404
    
    def test_notebook_validation_errors(self, db: Session):
        """Test notebook validation errors."""
        # Create workbook first
        workbook_data = {"title": "Test Workbook"}
        workbook_response = client.post("/api/v1/workbooks/", json=workbook_data)
        workbook = workbook_response.json()
        
        # Test missing title
        response = client.post("/api/v1/notebooks/", json={
            "workbook_id": workbook["id"]
        })
        assert response.status_code == 422
        
        # Test empty title
        response = client.post("/api/v1/notebooks/", json={
            "title": "",
            "workbook_id": workbook["id"]
        })
        assert response.status_code == 422
        
        # Test missing workbook_id
        response = client.post("/api/v1/notebooks/", json={
            "title": "Test Notebook"
        })
        assert response.status_code == 422