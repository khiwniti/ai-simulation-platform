"""
Integration tests for the complete chat system.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.v1.chat_websocket import router as chat_router
from app.api.v1.agents import router as agents_router
from app.services.agents.orchestrator import AgentOrchestrator
from app.services.agents.base import AgentResponse, AgentCapability


@pytest.fixture
def app():
    """Create FastAPI app with chat routes."""
    app = FastAPI()
    app.include_router(chat_router)
    app.include_router(agents_router, prefix="/agents")
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


class TestChatSystemIntegration:
    """Integration tests for the complete chat system."""
    
    @pytest.mark.asyncio
    async def test_agent_session_lifecycle(self, client):
        """Test complete agent session lifecycle."""
        session_id = "test-session-123"
        
        # Create session
        with patch('app.api.v1.agents.orchestrator') as mock_orchestrator:
            mock_context = Mock()
            mock_context.active_agents = set()
            mock_orchestrator.create_session.return_value = mock_context
            
            response = client.post(
                f"/agents/sessions?session_id={session_id}",
                json={"notebook_id": "nb-123"}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["session_id"] == session_id
    
    def test_get_available_agents(self, client):
        """Test getting available agents."""
        with patch('app.api.v1.agents.agent_registry') as mock_registry:
            mock_registry.get_agent_types.return_value = ["physics", "visualization"]
            
            response = client.get("/agents/types")
            
            assert response.status_code == 200
            agent_types = response.json()
            assert "physics" in agent_types
            assert "visualization" in agent_types
    
    @pytest.mark.asyncio
    async def test_single_agent_query(self, client):
        """Test querying a single agent."""
        with patch('app.api.v1.agents.agent_registry') as mock_registry:
            # Mock agent
            mock_agent = Mock()
            mock_agent.is_active = False
            mock_agent.initialize = AsyncMock()
            mock_agent.process_query = AsyncMock()
            
            mock_response = AgentResponse(
                agent_id="physics-1",
                agent_type="physics",
                response="Physics simulation help",
                confidence_score=0.9,
                suggestions=["Use PhysX"],
                code_snippets=[],
                response_time=0.5,
                capabilities_used=[AgentCapability.PHYSICS_MODELING]
            )
            mock_agent.process_query.return_value = mock_response
            mock_registry.create_agent.return_value = mock_agent
            
            response = client.post(
                "/agents/query?agent_type=physics",
                json={
                    "query": "Help with physics simulation",
                    "session_id": "test-session"
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["response"] == "Physics simulation help"
            assert data["confidence_score"] == 0.9
    
    @pytest.mark.asyncio
    async def test_multi_agent_coordination(self, client):
        """Test multi-agent coordination."""
        with patch('app.api.v1.agents.orchestrator') as mock_orchestrator:
            # Mock coordination result
            mock_primary = AgentResponse(
                agent_id="physics-1",
                agent_type="physics",
                response="Primary physics response",
                confidence_score=0.9,
                suggestions=["Physics suggestion"],
                code_snippets=[],
                response_time=0.8,
                capabilities_used=[AgentCapability.PHYSICS_MODELING]
            )
            
            mock_supporting = AgentResponse(
                agent_id="visualization-1",
                agent_type="visualization",
                response="Supporting visualization response",
                confidence_score=0.8,
                suggestions=["Viz suggestion"],
                code_snippets=[],
                response_time=0.6,
                capabilities_used=[AgentCapability.DATA_VISUALIZATION]
            )
            
            from app.services.agents.orchestrator import CoordinationResult
            mock_result = CoordinationResult(
                primary_response=mock_primary,
                supporting_responses=[mock_supporting],
                consensus_score=0.85,
                conflicts=[],
                coordination_time=1.5
            )
            
            mock_orchestrator.coordinate_agents.return_value = mock_result
            
            response = client.post(
                "/agents/coordinate",
                json={
                    "query": "Help with physics and visualization",
                    "session_id": "test-session",
                    "required_capabilities": ["physics_modeling", "data_visualization"],
                    "max_agents": 2
                }
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["primary_response"]["response"] == "Primary physics response"
            assert len(data["supporting_responses"]) == 1
            assert data["consensus_score"] == 0.85
    
    def test_session_context_update(self, client):
        """Test updating session context."""
        session_id = "test-session"
        
        with patch('app.api.v1.agents.orchestrator') as mock_orchestrator:
            mock_orchestrator.broadcast_context_update = AsyncMock()
            
            response = client.post(
                f"/agents/sessions/{session_id}/context",
                json={"notebook_id": "new-notebook", "current_cell": "cell-123"}
            )
            
            assert response.status_code == 200
            assert response.json()["message"] == "Context updated successfully"
    
    def test_get_session_status(self, client):
        """Test getting session agent status."""
        session_id = "test-session"
        
        with patch('app.api.v1.agents.orchestrator') as mock_orchestrator:
            mock_status = {
                "physics-1": {
                    "agent_id": "physics-1",
                    "agent_type": "physics",
                    "name": "Physics Agent",
                    "is_active": True,
                    "capabilities": ["physics_modeling"],
                    "performance_metrics": {"avg_response_time": 0.5},
                    "has_context": True
                }
            }
            mock_orchestrator.get_agent_status.return_value = mock_status
            
            response = client.get(f"/agents/sessions/{session_id}/status")
            
            assert response.status_code == 200
            data = response.json()
            assert "physics-1" in data
            assert data["physics-1"]["is_active"] is True
    
    def test_get_orchestrator_metrics(self, client):
        """Test getting orchestrator metrics."""
        with patch('app.api.v1.agents.orchestrator') as mock_orchestrator:
            mock_metrics = {
                "total_coordinations": 10,
                "successful_coordinations": 9,
                "average_coordination_time": 1.2,
                "conflict_resolution_rate": 0.8
            }
            mock_orchestrator.get_metrics.return_value = mock_metrics
            
            response = client.get("/agents/metrics")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_coordinations"] == 10
            assert data["successful_coordinations"] == 9
    
    def test_get_coordination_history(self, client):
        """Test getting coordination history."""
        with patch('app.api.v1.agents.orchestrator') as mock_orchestrator:
            mock_history = [
                {
                    "primary_agent": "physics-1",
                    "supporting_agents": ["visualization-1"],
                    "consensus_score": 0.9,
                    "conflicts_count": 0,
                    "coordination_time": 1.5,
                    "timestamp": "2023-01-01T10:00:00"
                }
            ]
            mock_orchestrator.get_coordination_history.return_value = mock_history
            
            response = client.get("/agents/coordination-history?limit=5")
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["primary_agent"] == "physics-1"
    
    def test_health_check(self, client):
        """Test agent system health check."""
        with patch('app.api.v1.agents.orchestrator') as mock_orchestrator:
            mock_orchestrator.is_running = True
            
            with patch('app.api.v1.agents.agent_registry') as mock_registry:
                mock_registry.get_agent_types.return_value = ["physics", "visualization"]
                mock_registry.get_all_agents.return_value = [Mock(), Mock()]
                
                response = client.get("/agents/health")
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "healthy"
                assert data["orchestrator_running"] is True
                assert len(data["registered_agent_types"]) == 2
                assert data["active_agents"] == 2


class TestChatWebSocketFlow:
    """Test WebSocket message flow scenarios."""
    
    @pytest.mark.asyncio
    async def test_complete_conversation_flow(self):
        """Test a complete conversation flow."""
        from app.api.v1.chat_websocket import ChatConnectionManager
        
        manager = ChatConnectionManager()
        session_id = "conversation-test"
        
        # Simulate user asking for help
        user_message = {
            "type": "user_message",
            "payload": {
                "content": "I need help optimizing my physics simulation",
                "selectedAgents": []
            }
        }
        
        # Mock auto-coordination
        with patch.object(manager, '_auto_coordinate_agents') as mock_auto:
            await manager.handle_message(session_id, user_message)
            
            mock_auto.assert_called_once_with(
                session_id, 
                "I need help optimizing my physics simulation"
            )
    
    @pytest.mark.asyncio
    async def test_code_insertion_flow(self):
        """Test code insertion message flow."""
        from app.api.v1.chat_websocket import ChatConnectionManager
        
        manager = ChatConnectionManager()
        session_id = "code-insertion-test"
        
        # Simulate code insertion request
        code_message = {
            "type": "code_insertion",
            "payload": {
                "snippet": {
                    "id": "snippet-1",
                    "language": "python",
                    "code": "import physx\nscene = physx.create_scene()",
                    "description": "Basic PhysX setup",
                    "insertable": True
                }
            }
        }
        
        with patch.object(manager, 'send_to_session') as mock_send:
            await manager.handle_message(session_id, code_message)
            
            # Should handle unknown message type gracefully
            # In a real implementation, this would trigger code insertion
    
    @pytest.mark.asyncio
    async def test_error_recovery_flow(self):
        """Test error recovery in conversation flow."""
        from app.api.v1.chat_websocket import ChatConnectionManager
        
        manager = ChatConnectionManager()
        session_id = "error-recovery-test"
        
        # Simulate message that causes error
        error_message = {
            "type": "user_message",
            "payload": {
                "content": "Test query",
                "selectedAgents": ["nonexistent-agent"]
            }
        }
        
        with patch('app.api.v1.chat_websocket.agent_registry') as mock_registry:
            mock_registry.create_agent.side_effect = ValueError("Agent not found")
            
            with patch.object(manager, 'send_to_session') as mock_send:
                await manager.handle_message(session_id, error_message)
                
                # Should send error message to client
                mock_send.assert_called()
                error_response = mock_send.call_args[0][1]
                assert error_response['type'] == 'error'
    
    @pytest.mark.asyncio
    async def test_concurrent_sessions(self):
        """Test handling multiple concurrent sessions."""
        from app.api.v1.chat_websocket import ChatConnectionManager
        
        manager = ChatConnectionManager()
        
        # Create multiple sessions
        sessions = ["session-1", "session-2", "session-3"]
        
        for session_id in sessions:
            mock_ws = Mock()
            mock_ws.accept = AsyncMock()
            await manager.connect(mock_ws, session_id, f"conn-{session_id}")
        
        # Verify all sessions are tracked
        assert len(manager.session_connections) == 3
        for session_id in sessions:
            assert session_id in manager.session_connections
        
        # Test broadcasting to specific session
        test_message = {"type": "test", "content": "hello"}
        
        with patch.object(manager.active_connections["conn-session-1"], 'send_text') as mock_send:
            await manager.send_to_session("session-1", test_message)
            mock_send.assert_called_once()
        
        # Other sessions should not receive the message
        for session_id in ["session-2", "session-3"]:
            conn_id = f"conn-{session_id}"
            if conn_id in manager.active_connections:
                manager.active_connections[conn_id].send_text.assert_not_called()