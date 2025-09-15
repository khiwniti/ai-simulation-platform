"""
Tests for agent API endpoints.
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock

from main import app
from app.services.agents.base import AgentCapability


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def session_id():
    """Generate test session ID."""
    return str(uuid4())


@pytest.fixture
def notebook_id():
    """Generate test notebook ID."""
    return str(uuid4())


class TestAgentSessionEndpoints:
    """Test agent session management endpoints."""
    
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_create_agent_session(self, mock_orchestrator, mock_auth, client, auth_headers, session_id, notebook_id):
        """Test creating an agent session."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.create_session = AsyncMock()
        
        # Mock agent context
        from app.services.agents.base import AgentContext
        mock_context = AgentContext(session_id=uuid4())
        mock_orchestrator.create_session.return_value = mock_context
        
        response = client.post(
            f"/api/v1/agents/sessions?session_id={session_id}&notebook_id={notebook_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "active_agents" in data
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_end_agent_session(self, mock_orchestrator, mock_auth, client, auth_headers, session_id):
        """Test ending an agent session."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.end_session = AsyncMock()
        
        response = client.delete(
            f"/api/v1/agents/sessions/{session_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Session ended successfully"
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_get_session_agent_status(self, mock_orchestrator, mock_auth, client, auth_headers, session_id):
        """Test getting agent status for a session."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.get_agent_status = AsyncMock()
        
        mock_status = {
            "agent1": {
                "agent_id": "agent1",
                "agent_type": "physics",
                "name": "Physics Agent",
                "is_active": True,
                "capabilities": ["physics_simulation"],
                "performance_metrics": {"total_queries": 5},
                "has_context": True
            }
        }
        mock_orchestrator.get_agent_status.return_value = mock_status
        
        response = client.get(
            f"/api/v1/agents/sessions/{session_id}/status",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "agent1" in data
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_update_session_context(self, mock_orchestrator, mock_auth, client, auth_headers, session_id):
        """Test updating session context."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.broadcast_context_update = AsyncMock()
        
        context_update = {"new_parameter": "test_value"}
        
        response = client.post(
            f"/api/v1/agents/sessions/{session_id}/context",
            json=context_update,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Context updated successfully"


class TestAgentCoordinationEndpoints:
    """Test agent coordination endpoints."""
    
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_coordinate_agents(self, mock_orchestrator, mock_auth, client, auth_headers, session_id):
        """Test multi-agent coordination."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.coordinate_agents = AsyncMock()
        
        # Mock coordination result
        from app.services.agents.base import AgentResponse
        from app.services.agents.orchestrator import CoordinationResult
        
        primary_response = AgentResponse(
            agent_id="agent1",
            agent_type="physics",
            response="Physics simulation response",
            confidence_score=0.9,
            suggestions=["Use PhysX", "Set gravity to -9.81"],
            code_snippets=["physics_code = 'example'"],
            response_time=0.5
        )
        
        mock_result = CoordinationResult(
            primary_response=primary_response,
            supporting_responses=[],
            consensus_score=0.9,
            conflicts=[],
            coordination_time=1.2
        )
        mock_orchestrator.coordinate_agents.return_value = mock_result
        
        request_data = {
            "query": "How do I set up physics simulation?",
            "session_id": session_id,
            "required_capabilities": ["physics_simulation"],
            "max_agents": 2
        }
        
        response = client.post(
            "/api/v1/agents/coordinate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "primary_response" in data
        assert data["primary_response"]["agent_type"] == "physics"
        assert data["consensus_score"] == 0.9
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.agent_registry')
    def test_query_single_agent(self, mock_registry, mock_auth, client, auth_headers, session_id):
        """Test querying a single agent."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        # Mock agent
        mock_agent = AsyncMock()
        mock_agent.is_active = False
        mock_agent.initialize = AsyncMock()
        mock_agent.process_query = AsyncMock()
        
        from app.services.agents.base import AgentResponse, AgentCapability
        mock_response = AgentResponse(
            agent_id="agent1",
            agent_type="physics",
            response="Physics response",
            confidence_score=0.8,
            capabilities_used=[AgentCapability.PHYSICS_SIMULATION],
            suggestions=["Test suggestion"],
            code_snippets=["test_code"],
            response_time=0.3
        )
        mock_agent.process_query.return_value = mock_response
        mock_registry.create_agent.return_value = mock_agent
        
        request_data = {
            "query": "Physics question",
            "session_id": session_id,
            "context": {}
        }
        
        response = client.post(
            "/api/v1/agents/query?agent_type=physics",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["agent_type"] == "physics"
        assert data["confidence_score"] == 0.8
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.agent_registry')
    def test_query_invalid_agent_type(self, mock_registry, mock_auth, client, auth_headers, session_id):
        """Test querying with invalid agent type."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_registry.create_agent.side_effect = ValueError("Unknown agent type")
        
        request_data = {
            "query": "Test question",
            "session_id": session_id
        }
        
        response = client.post(
            "/api/v1/agents/query?agent_type=invalid",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 400
        assert "Invalid agent type" in response.json()["detail"]


class TestAgentMetadataEndpoints:
    """Test agent metadata endpoints."""
    
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.agent_registry')
    def test_get_available_agent_types(self, mock_registry, mock_auth, client, auth_headers):
        """Test getting available agent types."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_registry.get_agent_types.return_value = ["physics", "visualization", "optimization", "debug"]
        
        response = client.get("/api/v1/agents/types", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "physics" in data
        assert "visualization" in data
        
    @patch('app.api.deps.get_current_user')
    def test_get_available_capabilities(self, mock_auth, client, auth_headers):
        """Test getting available capabilities."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        response = client.get("/api/v1/agents/capabilities", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "physics_simulation" in data
        assert "visualization_3d" in data
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_get_orchestrator_metrics(self, mock_orchestrator, mock_auth, client, auth_headers):
        """Test getting orchestrator metrics."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.get_metrics.return_value = {
            "total_coordinations": 10,
            "successful_coordinations": 9,
            "average_coordination_time": 1.5,
            "conflict_resolution_rate": 0.8
        }
        
        response = client.get("/api/v1/agents/metrics", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_coordinations"] == 10
        assert data["successful_coordinations"] == 9
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_get_coordination_history(self, mock_orchestrator, mock_auth, client, auth_headers):
        """Test getting coordination history."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.get_coordination_history.return_value = [
            {
                "primary_agent": "agent1",
                "supporting_agents": ["agent2"],
                "consensus_score": 0.9,
                "conflicts_count": 0,
                "coordination_time": 1.2,
                "timestamp": "2023-01-01T00:00:00"
            }
        ]
        
        response = client.get("/api/v1/agents/coordination-history?limit=5", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["primary_agent"] == "agent1"


class TestAgentManagementEndpoints:
    """Test agent management endpoints."""
    
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.agent_registry')
    def test_shutdown_agent(self, mock_registry, mock_auth, client, auth_headers):
        """Test shutting down an agent."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_registry.remove_agent.return_value = True
        
        response = client.post(
            "/api/v1/agents/agents/agent123/shutdown",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "shutdown successfully" in data["message"]
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.agent_registry')
    def test_shutdown_nonexistent_agent(self, mock_registry, mock_auth, client, auth_headers):
        """Test shutting down a nonexistent agent."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_registry.remove_agent.return_value = False
        
        response = client.post(
            "/api/v1/agents/agents/nonexistent/shutdown",
            headers=auth_headers
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
        
    @patch('app.api.v1.agents.orchestrator')
    @patch('app.api.v1.agents.agent_registry')
    def test_health_check(self, mock_registry, mock_orchestrator, client):
        """Test health check endpoint."""
        mock_orchestrator.is_running = True
        mock_registry.get_agent_types.return_value = ["physics", "visualization"]
        mock_registry.get_all_agents.return_value = [Mock(), Mock()]
        
        response = client.get("/api/v1/agents/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["orchestrator_running"] is True
        assert len(data["registered_agent_types"]) == 2
        assert data["active_agents"] == 2


class TestErrorHandling:
    """Test error handling in agent API."""
    
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_session_creation_error(self, mock_orchestrator, mock_auth, client, auth_headers, session_id):
        """Test error handling in session creation."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.create_session.side_effect = Exception("Database error")
        
        response = client.post(
            f"/api/v1/agents/sessions?session_id={session_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 500
        assert "Failed to create session" in response.json()["detail"]
        
    @patch('app.api.deps.get_current_user')
    @patch('app.api.v1.agents.orchestrator')
    def test_coordination_error(self, mock_orchestrator, mock_auth, client, auth_headers, session_id):
        """Test error handling in agent coordination."""
        mock_auth.return_value = {"user_id": "test-user"}
        mock_orchestrator.coordinate_agents.side_effect = Exception("Coordination failed")
        
        request_data = {
            "query": "Test query",
            "session_id": session_id,
            "required_capabilities": [],
            "max_agents": 1
        }
        
        response = client.post(
            "/api/v1/agents/coordinate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 500
        assert "Agent coordination failed" in response.json()["detail"]


class TestRequestValidation:
    """Test request validation."""
    
    @patch('app.api.deps.get_current_user')
    def test_invalid_coordination_request(self, mock_auth, client, auth_headers):
        """Test validation of coordination request."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        # Missing required fields
        request_data = {
            "query": "",  # Empty query should fail validation
            "max_agents": 0  # Invalid max_agents
        }
        
        response = client.post(
            "/api/v1/agents/coordinate",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
        
    @patch('app.api.deps.get_current_user')
    def test_invalid_query_request(self, mock_auth, client, auth_headers):
        """Test validation of single agent query request."""
        mock_auth.return_value = {"user_id": "test-user"}
        
        # Missing required fields
        request_data = {
            "query": "",  # Empty query
            # Missing session_id
        }
        
        response = client.post(
            "/api/v1/agents/query?agent_type=physics",
            json=request_data,
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error


class TestAuthentication:
    """Test authentication requirements."""
    
    def test_unauthenticated_requests(self, client, session_id):
        """Test that endpoints require authentication."""
        endpoints = [
            ("POST", f"/api/v1/agents/sessions?session_id={session_id}"),
            ("DELETE", f"/api/v1/agents/sessions/{session_id}"),
            ("GET", f"/api/v1/agents/sessions/{session_id}/status"),
            ("POST", "/api/v1/agents/coordinate"),
            ("POST", "/api/v1/agents/query?agent_type=physics"),
            ("GET", "/api/v1/agents/types"),
            ("GET", "/api/v1/agents/capabilities"),
            ("GET", "/api/v1/agents/metrics"),
        ]
        
        for method, endpoint in endpoints:
            if method == "POST":
                response = client.post(endpoint, json={})
            elif method == "DELETE":
                response = client.delete(endpoint)
            else:
                response = client.get(endpoint)
                
            # Should require authentication
            assert response.status_code in [401, 403]


if __name__ == "__main__":
    pytest.main([__file__])