"""
Tests for the Python code execution service
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.services.execution_service import (
    ExecutionService,
    ExecutionRequest,
    ExecutionStatus,
    ExecutionOutput
)


@pytest.fixture
async def execution_service():
    """Create execution service for testing"""
    service = ExecutionService(redis_url="redis://localhost:6379")
    
    # Mock Redis client for testing
    service.redis_client = AsyncMock()
    service.docker_client = Mock()
    
    return service


@pytest.fixture
def sample_execution_request():
    """Sample execution request for testing"""
    return ExecutionRequest(
        code="print('Hello, World!')",
        cell_id="cell-123",
        notebook_id="notebook-456",
        execution_count=1,
        timeout=30
    )


class TestExecutionService:
    """Test cases for ExecutionService"""
    
    @pytest.mark.asyncio
    async def test_execute_code_queues_execution(self, execution_service, sample_execution_request):
        """Test that code execution is properly queued"""
        # Mock Redis operations
        execution_service.redis_client.hset = AsyncMock()
        execution_service.redis_client.lpush = AsyncMock()
        
        execution_id = await execution_service.execute_code(sample_execution_request)
        
        # Verify execution ID is returned
        assert execution_id is not None
        assert len(execution_id) > 0
        
        # Verify Redis operations were called
        execution_service.redis_client.hset.assert_called_once()
        execution_service.redis_client.lpush.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_get_execution_status_returns_status(self, execution_service):
        """Test getting execution status"""
        execution_id = "test-execution-id"
        
        # Mock Redis response
        execution_service.redis_client.hgetall = AsyncMock(return_value={
            "status": "completed",
            "started_at": "2024-01-01T00:00:00",
            "completed_at": "2024-01-01T00:01:00"
        })
        execution_service.redis_client.lrange = AsyncMock(return_value=[])
        
        status = await execution_service.get_execution_status(execution_id)
        
        assert status is not None
        assert status.execution_id == execution_id
        assert status.status == "completed"
        
    @pytest.mark.asyncio
    async def test_get_execution_status_not_found(self, execution_service):
        """Test getting status for non-existent execution"""
        execution_service.redis_client.hgetall = AsyncMock(return_value={})
        
        status = await execution_service.get_execution_status("non-existent")
        
        assert status is None
        
    @pytest.mark.asyncio
    async def test_cancel_execution_success(self, execution_service):
        """Test successful execution cancellation"""
        execution_id = "test-execution-id"
        
        # Mock running container
        mock_container = Mock()
        mock_container.stop = Mock()
        mock_container.remove = Mock()
        execution_service.running_executions[execution_id] = mock_container
        
        # Mock Redis operations
        execution_service.redis_client.hset = AsyncMock()
        
        result = await execution_service.cancel_execution(execution_id)
        
        assert result is True
        mock_container.stop.assert_called_once()
        mock_container.remove.assert_called_once()
        assert execution_id not in execution_service.running_executions
        
    @pytest.mark.asyncio
    async def test_cancel_execution_not_running(self, execution_service):
        """Test cancelling non-running execution"""
        result = await execution_service.cancel_execution("non-existent")
        assert result is False
        
    def test_create_execution_script_basic_code(self, execution_service):
        """Test creation of execution script with basic code"""
        user_code = "print('Hello, World!')"
        script = execution_service._create_execution_script(user_code)
        
        assert user_code in script
        assert "import sys" in script
        assert "import json" in script
        assert "capture_output()" in script
        
    def test_create_execution_script_matplotlib_code(self, execution_service):
        """Test execution script handles matplotlib"""
        user_code = "import matplotlib.pyplot as plt\nplt.plot([1,2,3])"
        script = execution_service._create_execution_script(user_code)
        
        assert "matplotlib" in script
        assert "plt.get_fignums()" in script
        assert "base64" in script
        
    @pytest.mark.asyncio
    async def test_mark_execution_failed(self, execution_service):
        """Test marking execution as failed"""
        execution_id = "test-execution-id"
        error_message = "Test error"
        
        execution_service.redis_client.hset = AsyncMock()
        execution_service.redis_client.lpush = AsyncMock()
        
        await execution_service._mark_execution_failed(execution_id, error_message)
        
        # Verify Redis operations
        execution_service.redis_client.hset.assert_called_once()
        execution_service.redis_client.lpush.assert_called_once()
        
        # Check the error output was created
        call_args = execution_service.redis_client.lpush.call_args
        assert f"execution:{execution_id}:outputs" in call_args[0]
        
    @pytest.mark.asyncio
    async def test_mark_execution_timeout(self, execution_service):
        """Test marking execution as timed out"""
        execution_id = "test-execution-id"
        
        execution_service.redis_client.hset = AsyncMock()
        execution_service.redis_client.lpush = AsyncMock()
        
        await execution_service._mark_execution_timeout(execution_id)
        
        # Verify timeout status was set
        call_args = execution_service.redis_client.hset.call_args
        assert "timeout" in str(call_args)
        
    @pytest.mark.asyncio
    async def test_get_queue_status(self, execution_service):
        """Test getting queue status"""
        execution_service.redis_client.llen = AsyncMock(return_value=5)
        execution_service.running_executions = {"exec1": Mock(), "exec2": Mock()}
        
        status = await execution_service.get_queue_status()
        
        assert status["queue_length"] == 5
        assert status["running_executions"] == 2
        assert status["max_concurrent"] == 5
        assert status["available_slots"] == 3


class TestExecutionModels:
    """Test cases for execution data models"""
    
    def test_execution_request_validation(self):
        """Test ExecutionRequest model validation"""
        request = ExecutionRequest(
            code="print('test')",
            cell_id="cell-123",
            notebook_id="notebook-456",
            execution_count=1
        )
        
        assert request.code == "print('test')"
        assert request.timeout == 30  # default value
        assert request.memory_limit == "512m"  # default value
        
    def test_execution_output_creation(self):
        """Test ExecutionOutput model creation"""
        output = ExecutionOutput(
            output_type="stdout",
            content={"text": "Hello, World!"},
            timestamp=datetime.utcnow()
        )
        
        assert output.output_type == "stdout"
        assert output.content["text"] == "Hello, World!"
        assert output.execution_count is None
        
    def test_execution_status_creation(self):
        """Test ExecutionStatus model creation"""
        status = ExecutionStatus(
            execution_id="test-id",
            status="running",
            started_at=datetime.utcnow()
        )
        
        assert status.execution_id == "test-id"
        assert status.status == "running"
        assert status.completed_at is None
        assert len(status.outputs) == 0


class TestExecutionScenarios:
    """Test various code execution scenarios"""
    
    def test_simple_print_script(self, execution_service):
        """Test script generation for simple print statement"""
        code = "print('Hello, World!')"
        script = execution_service._create_execution_script(code)
        
        # Verify the script contains necessary components
        assert "print('Hello, World!')" in script
        assert "stdout" in script
        assert "json.dumps" in script
        
    def test_error_handling_script(self, execution_service):
        """Test script generation includes error handling"""
        code = "raise ValueError('Test error')"
        script = execution_service._create_execution_script(code)
        
        assert "except Exception as e:" in script
        assert "error_type" in script or "ename" in script
        assert "traceback" in script
        
    def test_matplotlib_output_script(self, execution_service):
        """Test script handles matplotlib output"""
        code = """
import matplotlib.pyplot as plt
plt.figure()
plt.plot([1, 2, 3, 4])
plt.title('Test Plot')
"""
        script = execution_service._create_execution_script(code)
        
        assert "matplotlib" in script
        assert "plt.get_fignums()" in script
        assert "savefig" in script
        assert "base64" in script
        
    def test_multiple_output_types_script(self, execution_service):
        """Test script handles multiple output types"""
        code = """
print("Text output")
import matplotlib.pyplot as plt
plt.plot([1, 2, 3])
import sys
print("Error output", file=sys.stderr)
"""
        script = execution_service._create_execution_script(code)
        
        # Should handle stdout, stderr, and display_data
        assert "stdout" in script
        assert "stderr" in script
        assert "display_data" in script


@pytest.mark.integration
class TestExecutionIntegration:
    """Integration tests for execution service"""
    
    @pytest.mark.asyncio
    async def test_full_execution_workflow(self, execution_service, sample_execution_request):
        """Test complete execution workflow"""
        # This would require actual Redis and Docker setup
        # For now, we'll mock the key components
        
        with patch.object(execution_service, '_process_execution_queue') as mock_process:
            mock_process.return_value = None
            
            execution_id = await execution_service.execute_code(sample_execution_request)
            
            assert execution_id is not None
            # In a real integration test, we would verify the execution completes
            
    @pytest.mark.asyncio
    async def test_concurrent_executions(self, execution_service):
        """Test handling multiple concurrent executions"""
        requests = [
            ExecutionRequest(
                code=f"print('Execution {i}')",
                cell_id=f"cell-{i}",
                notebook_id="notebook-test",
                execution_count=i
            )
            for i in range(3)
        ]
        
        # Mock the queue processing
        with patch.object(execution_service, '_process_execution_queue'):
            execution_ids = []
            for request in requests:
                execution_id = await execution_service.execute_code(request)
                execution_ids.append(execution_id)
                
            assert len(execution_ids) == 3
            assert len(set(execution_ids)) == 3  # All unique