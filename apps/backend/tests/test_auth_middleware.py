"""
Tests for authentication middleware.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.auth import AuthMiddleware

client = TestClient(app)


class TestAuthMiddleware:
    """Test authentication middleware."""
    
    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "user123", "username": "testuser"}
        token = AuthMiddleware.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_valid_token(self):
        """Test verifying valid JWT token."""
        data = {"sub": "user123", "username": "testuser"}
        token = AuthMiddleware.create_access_token(data)
        
        payload = AuthMiddleware.verify_token(token)
        
        assert payload["sub"] == "user123"
        assert payload["username"] == "testuser"
    
    def test_verify_invalid_token(self):
        """Test verifying invalid JWT token."""
        invalid_token = "invalid.jwt.token"
        
        with pytest.raises(Exception):  # Should raise HTTPException
            AuthMiddleware.verify_token(invalid_token)
    
    def test_verify_malformed_token(self):
        """Test verifying malformed JWT token."""
        malformed_token = "not-a-jwt-token"
        
        with pytest.raises(Exception):  # Should raise HTTPException
            AuthMiddleware.verify_token(malformed_token)
    
    def test_api_without_auth_works(self):
        """Test that public endpoints work without authentication."""
        response = client.get("/")
        assert response.status_code == 200
        
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_token_roundtrip(self):
        """Test complete token creation and verification cycle."""
        original_data = {
            "sub": "user456", 
            "username": "anotheruser",
            "role": "engineer"
        }
        
        # Create token
        token = AuthMiddleware.create_access_token(original_data)
        
        # Verify token
        decoded_data = AuthMiddleware.verify_token(token)
        
        # Check that essential data is preserved
        assert decoded_data["sub"] == original_data["sub"]
        assert decoded_data["username"] == original_data["username"]
        assert decoded_data["role"] == original_data["role"]