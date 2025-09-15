"""
Integration tests for workbook API endpoints.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.models.workbook import Workbook

client = TestClient(app)


class TestWorkbookAPI:
    """Test workbook API endpoints."""
    
    def test_create_workbook(self, db: Session):
        """Test creating a new workbook."""
        workbook_data = {
            "title": "Test Workbook",
            "description": "A test workbook for simulation projects"
        }
        
        response = client.post("/api/v1/workbooks/", json=workbook_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == workbook_data["title"]
        assert data["description"] == workbook_data["description"]
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_workbook_duplicate_title(self, db: Session):
        """Test creating workbook with duplicate title fails."""
        workbook_data = {
            "title": "Duplicate Title",
            "description": "First workbook"
        }
        
        # Create first workbook
        response1 = client.post("/api/v1/workbooks/", json=workbook_data)
        assert response1.status_code == 201
        
        # Try to create second workbook with same title
        workbook_data["description"] = "Second workbook"
        response2 = client.post("/api/v1/workbooks/", json=workbook_data)
        
        assert response2.status_code == 409
        error_data = response2.json()
        assert "already exists" in error_data["error"]["message"]
    
    def test_get_workbooks(self, db: Session):
        """Test retrieving workbooks list."""
        # Create test workbooks
        for i in range(3):
            workbook_data = {
                "title": f"Test Workbook {i}",
                "description": f"Description {i}"
            }
            client.post("/api/v1/workbooks/", json=workbook_data)
        
        response = client.get("/api/v1/workbooks/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 3
    
    def test_get_workbook_by_id(self, db: Session):
        """Test retrieving workbook by ID."""
        # Create workbook
        workbook_data = {
            "title": "Single Workbook",
            "description": "Test description"
        }
        create_response = client.post("/api/v1/workbooks/", json=workbook_data)
        created_workbook = create_response.json()
        
        # Get workbook by ID
        response = client.get(f"/api/v1/workbooks/{created_workbook['id']}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_workbook["id"]
        assert data["title"] == workbook_data["title"]
    
    def test_get_workbook_not_found(self, db: Session):
        """Test retrieving non-existent workbook."""
        fake_id = str(uuid4())
        response = client.get(f"/api/v1/workbooks/{fake_id}")
        
        assert response.status_code == 404
        error_data = response.json()
        assert "not found" in error_data["error"]["message"]
    
    def test_update_workbook(self, db: Session):
        """Test updating workbook."""
        # Create workbook
        workbook_data = {
            "title": "Original Title",
            "description": "Original description"
        }
        create_response = client.post("/api/v1/workbooks/", json=workbook_data)
        created_workbook = create_response.json()
        
        # Update workbook
        update_data = {
            "title": "Updated Title",
            "description": "Updated description"
        }
        response = client.put(
            f"/api/v1/workbooks/{created_workbook['id']}", 
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
    
    def test_update_workbook_not_found(self, db: Session):
        """Test updating non-existent workbook."""
        fake_id = str(uuid4())
        update_data = {"title": "New Title"}
        
        response = client.put(f"/api/v1/workbooks/{fake_id}", json=update_data)
        
        assert response.status_code == 404
    
    def test_delete_workbook(self, db: Session):
        """Test deleting workbook."""
        # Create workbook
        workbook_data = {
            "title": "To Be Deleted",
            "description": "This will be deleted"
        }
        create_response = client.post("/api/v1/workbooks/", json=workbook_data)
        created_workbook = create_response.json()
        
        # Delete workbook
        response = client.delete(f"/api/v1/workbooks/{created_workbook['id']}")
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/api/v1/workbooks/{created_workbook['id']}")
        assert get_response.status_code == 404
    
    def test_delete_workbook_not_found(self, db: Session):
        """Test deleting non-existent workbook."""
        fake_id = str(uuid4())
        response = client.delete(f"/api/v1/workbooks/{fake_id}")
        
        assert response.status_code == 404
    
    def test_workbook_validation_errors(self, db: Session):
        """Test workbook validation errors."""
        # Test missing title
        response = client.post("/api/v1/workbooks/", json={"description": "No title"})
        assert response.status_code == 422
        
        # Test empty title
        response = client.post("/api/v1/workbooks/", json={"title": ""})
        assert response.status_code == 422
        
        # Test title too long
        long_title = "x" * 300
        response = client.post("/api/v1/workbooks/", json={"title": long_title})
        assert response.status_code == 422