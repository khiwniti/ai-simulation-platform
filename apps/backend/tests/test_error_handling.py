"""
Tests for error handling and exception handlers.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.main import app
from app.core.exceptions import ErrorResponse

client = TestClient(app)


class TestErrorHandling:
    """Test error handling and exception handlers."""
    
    def test_404_error_format(self, db: Session):
        """Test 404 error response format."""
        response = client.get("/api/v1/workbooks/00000000-0000-0000-0000-000000000000")
        
        assert response.status_code == 404
        data = response.json()
        
        # Check error response structure
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "not found" in data["error"]["message"].lower()
    
    def test_validation_error_format(self, db: Session):
        """Test validation error response format."""
        # Send invalid data (missing required field)
        response = client.post("/api/v1/workbooks/", json={})
        
        assert response.status_code == 422
        data = response.json()
        
        # Check error response structure
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["error"]
        assert "errors" in data["error"]["details"]
    
    def test_conflict_error_format(self, db: Session):
        """Test conflict error response format."""
        # Create workbook
        workbook_data = {"title": "Conflict Test"}
        client.post("/api/v1/workbooks/", json=workbook_data)
        
        # Try to create another with same title
        response = client.post("/api/v1/workbooks/", json=workbook_data)
        
        assert response.status_code == 409
        data = response.json()
        
        # Check error response structure
        assert "error" in data
        assert "already exists" in data["error"]["message"].lower()
    
    def test_invalid_uuid_format(self, db: Session):
        """Test invalid UUID format handling."""
        response = client.get("/api/v1/workbooks/invalid-uuid")
        
        assert response.status_code == 422
        data = response.json()
        assert "error" in data
    
    def test_error_response_utility(self):
        """Test ErrorResponse utility class."""
        error_response = ErrorResponse.create_error_response(
            error_code="TEST_ERROR",
            message="Test error message",
            details={"field": "value"}
        )
        
        assert error_response["error"]["code"] == "TEST_ERROR"
        assert error_response["error"]["message"] == "Test error message"
        assert error_response["error"]["details"]["field"] == "value"
    
    def test_error_response_without_details(self):
        """Test ErrorResponse without details."""
        error_response = ErrorResponse.create_error_response(
            error_code="SIMPLE_ERROR",
            message="Simple error message"
        )
        
        assert error_response["error"]["code"] == "SIMPLE_ERROR"
        assert error_response["error"]["message"] == "Simple error message"
        assert "details" not in error_response["error"]