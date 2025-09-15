"""
Tests for execution API endpoints
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from datetime import datetime

from main import app
from app.services.execution_service import ExecutionStatus, ExecutionOutput


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_execution_request():
    """Sample execution request data"""
    return {
        "code": "print('Hello, World!')",
        "cell_id": "cell-123",
        "notebook_id": "notebook-456",
        "execution_count": 1,
        "timeout": 30
    }


class TestExecutionAPI:
    """Test cases for execution API endpoints"""
    
    def test_execute_code_success(self, client, sample_execution_request):
        """Test successful code execution request"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.redis_client = True  # Simulate initialized service
            mock_service.execute_code = AsyncMock(return_value="test-execution-id")
            
            response = client.post("/api/v1/execution/execute", json=sample_execution_request)
            
            assert response.status_code == 200
            data = response.json()
            assert data["execution_id"] == "test-execution-id"
            assert data["status"] == "queued"
            
    def test_execute_code_service_not_initialized(self, client, sample_execution_request):
        """Test execution when service is not initialized"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.redis_client = None
            mock_service.initialize = AsyncMock()
            mock_service.execute_code = AsyncMock(return_value="test-execution-id")
            
            response = client.post("/api/v1/execution/execute", json=sample_execution_request)
            
            assert response.status_code == 200
            mock_service.initialize.assert_called_once()
            
    def test_execute_code_invalid_request(self, client):
        """Test execution with invalid request data"""
        invalid_request = {
            "code": "",  # Empty code
            "cell_id": "",
            "notebook_id": "",
            "execution_count": -1  # Invalid count
        }
        
        response = client.post("/api/v1/execution/execute", json=invalid_request)
        
        # Should return validation error
        assert response.status_code == 422
        
    def test_execute_code_service_error(self, client, sample_execution_request):
        """Test execution when service raises error"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.redis_client = True
            mock_service.execute_code = AsyncMock(side_effect=Exception("Service error"))
            
            response = client.post("/api/v1/execution/execute", json=sample_execution_request)
            
            assert response.status_code == 500
            assert "Failed to start execution" in response.json()["detail"]
            
    def test_get_execution_status_success(self, client):
        """Test successful status retrieval"""
        execution_id = "test-execution-id"
        mock_status = ExecutionStatus(
            execution_id=execution_id,
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.get_execution_status = AsyncMock(return_value=mock_status)
            
            response = client.get(f"/api/v1/execution/status/{execution_id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["execution_id"] == execution_id
            assert data["status"] == "completed"
            
    def test_get_execution_status_not_found(self, client):
        """Test status retrieval for non-existent execution"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.get_execution_status = AsyncMock(return_value=None)
            
            response = client.get("/api/v1/execution/status/non-existent")
            
            assert response.status_code == 404
            assert "Execution not found" in response.json()["detail"]
            
    def test_get_execution_status_service_error(self, client):
        """Test status retrieval when service raises error"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.get_execution_status = AsyncMock(side_effect=Exception("Service error"))
            
            response = client.get("/api/v1/execution/status/test-id")
            
            assert response.status_code == 500
            assert "Failed to get status" in response.json()["detail"]
            
    def test_cancel_execution_success(self, client):
        """Test successful execution cancellation"""
        execution_id = "test-execution-id"
        
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.cancel_execution = AsyncMock(return_value=True)
            
            response = client.delete(f"/api/v1/execution/cancel/{execution_id}")
            
            assert response.status_code == 200
            assert "cancelled successfully" in response.json()["message"]
            
    def test_cancel_execution_not_found(self, client):
        """Test cancellation of non-existent execution"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.cancel_execution = AsyncMock(return_value=False)
            
            response = client.delete("/api/v1/execution/cancel/non-existent")
            
            assert response.status_code == 404
            assert "not found" in response.json()["detail"]
            
    def test_get_queue_status_success(self, client):
        """Test successful queue status retrieval"""
        mock_status = {
            "queue_length": 3,
            "running_executions": 2,
            "max_concurrent": 5,
            "available_slots": 3
        }
        
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.get_queue_status = AsyncMock(return_value=mock_status)
            
            response = client.get("/api/v1/execution/queue/status")
            
            assert response.status_code == 200
            data = response.json()
            assert data["queue_length"] == 3
            assert data["running_executions"] == 2
            assert data["available_slots"] == 3
            
    def test_initialize_service_success(self, client):
        """Test successful service initialization"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.initialize = AsyncMock()
            
            response = client.post("/api/v1/execution/initialize")
            
            assert response.status_code == 200
            assert "initialized successfully" in response.json()["message"]
            mock_service.initialize.assert_called_once()
            
    def test_initialize_service_error(self, client):
        """Test service initialization error"""
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.initialize = AsyncMock(side_effect=Exception("Init error"))
            
            response = client.post("/api/v1/execution/initialize")
            
            assert response.status_code == 500
            assert "Failed to initialize" in response.json()["detail"]


class TestExecutionStreaming:
    """Test cases for execution output streaming"""
    
    def test_stream_execution_output_success(self, client):
        """Test successful output streaming"""
        execution_id = "test-execution-id"
        
        # Mock outputs
        mock_outputs = [
            ExecutionOutput(
                output_type="stdout",
                content={"text": "Hello, World!"},
                timestamp=datetime.utcnow()
            ),
            ExecutionOutput(
                output_type="execute_result",
                content={"data": {"text/plain": "42"}},
                execution_count=1,
                timestamp=datetime.utcnow()
            )
        ]
        
        async def mock_stream():
            for output in mock_outputs:
                yield output
                
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.stream_execution_output = AsyncMock(return_value=mock_stream())
            
            response = client.get(f"/api/v1/execution/stream/{execution_id}")
            
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            
            # Check streaming headers
            assert "no-cache" in response.headers.get("cache-control", "")
            assert "keep-alive" in response.headers.get("connection", "")
            
    def test_stream_execution_output_error(self, client):
        """Test streaming when service raises error"""
        execution_id = "test-execution-id"
        
        async def mock_stream_error():
            raise Exception("Stream error")
            yield  # This won't be reached but makes it a generator
            
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.stream_execution_output = AsyncMock(return_value=mock_stream_error())
            
            response = client.get(f"/api/v1/execution/stream/{execution_id}")
            
            assert response.status_code == 200  # Streaming starts successfully
            # Error would be in the stream content


class TestExecutionRequestValidation:
    """Test request validation for execution endpoints"""
    
    def test_execution_request_missing_fields(self, client):
        """Test execution request with missing required fields"""
        incomplete_request = {
            "code": "print('test')"
            # Missing cell_id, notebook_id, execution_count
        }
        
        response = client.post("/api/v1/execution/execute", json=incomplete_request)
        
        assert response.status_code == 422
        error_detail = response.json()["detail"]
        assert any("cell_id" in str(error) for error in error_detail)
        assert any("notebook_id" in str(error) for error in error_detail)
        
    def test_execution_request_invalid_types(self, client):
        """Test execution request with invalid field types"""
        invalid_request = {
            "code": 123,  # Should be string
            "cell_id": "cell-123",
            "notebook_id": "notebook-456",
            "execution_count": "invalid",  # Should be int
            "timeout": "invalid"  # Should be int
        }
        
        response = client.post("/api/v1/execution/execute", json=invalid_request)
        
        assert response.status_code == 422
        
    def test_execution_request_valid_defaults(self, client):
        """Test execution request uses valid defaults"""
        minimal_request = {
            "code": "print('test')",
            "cell_id": "cell-123",
            "notebook_id": "notebook-456",
            "execution_count": 1
        }
        
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.redis_client = True
            mock_service.execute_code = AsyncMock(return_value="test-id")
            
            response = client.post("/api/v1/execution/execute", json=minimal_request)
            
            assert response.status_code == 200
            
            # Verify defaults were applied
            call_args = mock_service.execute_code.call_args[0][0]
            assert call_args.timeout == 30  # Default timeout
            assert call_args.memory_limit == "512m"  # Default memory
            assert call_args.cpu_limit == 1.0  # Default CPU


class TestExecutionSecurity:
    """Test security aspects of execution API"""
    
    def test_execution_request_code_length_limit(self, client):
        """Test handling of very long code requests"""
        # Create a very long code string
        long_code = "print('x')\n" * 10000
        
        request = {
            "code": long_code,
            "cell_id": "cell-123",
            "notebook_id": "notebook-456",
            "execution_count": 1
        }
        
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.redis_client = True
            mock_service.execute_code = AsyncMock(return_value="test-id")
            
            response = client.post("/api/v1/execution/execute", json=request)
            
            # Should still accept (length limits would be in service layer)
            assert response.status_code == 200
            
    def test_execution_request_resource_limits(self, client):
        """Test resource limit validation"""
        request = {
            "code": "print('test')",
            "cell_id": "cell-123",
            "notebook_id": "notebook-456",
            "execution_count": 1,
            "timeout": 300,  # 5 minutes
            "memory_limit": "1g",
            "cpu_limit": 2.0
        }
        
        with patch('app.api.v1.execution.execution_service') as mock_service:
            mock_service.redis_client = True
            mock_service.execute_code = AsyncMock(return_value="test-id")
            
            response = client.post("/api/v1/execution/execute", json=request)
            
            assert response.status_code == 200
            
            # Verify limits were passed through
            call_args = mock_service.execute_code.call_args[0][0]
            assert call_args.timeout == 300
            assert call_args.memory_limit == "1g"
            assert call_args.cpu_limit == 2.0