"""
Tests for chat WebSocket functionality.
"""

import pytest
import json
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

from app.api.v1.chat_websocket import ChatConnectionManager, chat_manager
from app.services.agents.orchestrator import CoordinationResult
from app.services.agents.base import AgentResponse, AgentCapability


class TestChatConnectionManager:
    """Test cases for ChatConnectionManager."""
    
    @pytest.fixture
    def manager(self):
        """Create a fresh ChatConnectionManager instance."""
        return ChatConnectionManager()
    
    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        ws = Mock(spec=WebSocket)
        ws.accept = AsyncMock()
        ws.send_text = AsyncMock()
        return ws
    
    @pytest.mark.asyncio
    async def test_connect_websocket(self, manager, mock_websocket):
        """Test WebSocket connection."""
        session_id = "test-session"
        connection_id = "test-connection"
        
        await manager.connect(mock_websocket, session_id, connection_id)
        
        mock_websocket.accept.assert_called_once()
        assert connection_id in manager.active_connections
        assert session_id in manager.session_connections
        assert connection_id in manager.session_connections[session_id]
    
    def test_disconnect_websocket(self, manager, mock_websocket):
        """Test WebSocket disconnection."""
        session_id = "test-session"
        connection_id = "test-connection"
        
        # Setup connection
        manager.active_connections[connection_id] = mock_websocket
        manager.session_connections[session_id] = {connection_id}
        
        # Disconnect
        manager.disconnect(connection_id, session_id)
        
        assert connection_id not in manager.active_connections
        assert session_id not in manager.session_connections
    
    @pytest.mark.asyncio
    async def test_send_to_session(self, manager, mock_websocket):
        """Test sending message to session."""
        session_id = "test-session"
        connection_id = "test-connection"
        message = {"type": "test", "content": "hello"}
        
        # Setup connection
        manager.active_connections[connection_id] = mock_websocket
        manager.session_connections[session_id] = {connection_id}
        
        await manager.send_to_session(session_id, message)
        
        expected_json = json.dumps(message, default=str)
        mock_websocket.send_text.assert_called_once_with(expected_json)
    
    @pytest.mark.asyncio
    async def test_handle_user_message_single_agent(self, manager):
        """Test handling user message with single agent."""
        session_id = "test-session"
        payload = {
            "content": "Help me with physics",
            "selectedAgents": ["physics"]
        }
        
        # Mock agent response
        mock_agent = Mock()
        mock_agent.is_active = False
        mock_agent.initialize = AsyncMock()
        mock_agent.process_query = AsyncMock()
        
        mock_response = AgentResponse(
            agent_id="physics-1",
            agent_type="physics",
            response="I can help with physics simulations",
            confidence_score=0.9,
            suggestions=["Use PhysX for rigid bodies"],
            code_snippets=[],
            response_time=0.5,
            capabilities_used=[AgentCapability.PHYSICS_MODELING]
        )
        mock_agent.process_query.return_value = mock_response
        
        with patch('app.api.v1.chat_websocket.agent_registry') as mock_registry:
            mock_registry.create_agent.return_value = mock_agent
            
            with patch.object(manager, 'send_to_session') as mock_send:
                await manager._handle_user_message(session_id, payload)
                
                mock_send.assert_called_once()
                sent_message = mock_send.call_args[0][1]
                assert sent_message['type'] == 'agent_response'
                assert sent_message['payload']['response'] == "I can help with physics simulations"
    
    @pytest.mark.asyncio
    async def test_handle_user_message_multi_agent(self, manager):
        """Test handling user message with multiple agents."""
        session_id = "test-session"
        payload = {
            "content": "Help me with physics and visualization",
            "selectedAgents": ["physics", "visualization"]
        }
        
        with patch.object(manager, '_coordinate_multiple_agents') as mock_coordinate:
            await manager._handle_user_message(session_id, payload)
            
            mock_coordinate.assert_called_once_with(
                session_id, 
                "Help me with physics and visualization", 
                ["physics", "visualization"]
            )
    
    @pytest.mark.asyncio
    async def test_handle_agent_coordination(self, manager):
        """Test handling agent coordination request."""
        session_id = "test-session"
        payload = {
            "query": "Optimize my simulation",
            "capabilities": ["performance_optimization"]
        }
        
        # Mock coordination result
        mock_primary_response = AgentResponse(
            agent_id="optimization-1",
            agent_type="optimization",
            response="Here are optimization suggestions",
            confidence_score=0.85,
            suggestions=["Use GPU acceleration"],
            code_snippets=[],
            response_time=1.2,
            capabilities_used=[AgentCapability.PERFORMANCE_OPTIMIZATION]
        )
        
        mock_result = CoordinationResult(
            primary_response=mock_primary_response,
            supporting_responses=[],
            consensus_score=0.9,
            conflicts=[],
            coordination_time=1.5
        )
        
        with patch.object(manager.orchestrator, 'coordinate_agents') as mock_coordinate:
            mock_coordinate.return_value = mock_result
            
            with patch.object(manager, 'send_to_session') as mock_send:
                await manager._handle_agent_coordination(session_id, payload)
                
                mock_send.assert_called_once()
                sent_message = mock_send.call_args[0][1]
                assert sent_message['type'] == 'agent_coordination'
                assert sent_message['payload']['consensus_score'] == 0.9
    
    @pytest.mark.asyncio
    async def test_handle_context_update(self, manager):
        """Test handling context update."""
        session_id = "test-session"
        payload = {
            "context": {"notebook_id": "nb-123", "current_cell": "cell-456"}
        }
        
        with patch.object(manager.orchestrator, 'broadcast_context_update') as mock_broadcast:
            with patch.object(manager, 'send_to_session') as mock_send:
                await manager._handle_context_update(session_id, payload)
                
                mock_broadcast.assert_called_once()
                mock_send.assert_called_once()
                sent_message = mock_send.call_args[0][1]
                assert sent_message['type'] == 'system_message'
    
    @pytest.mark.asyncio
    async def test_auto_coordinate_agents_physics_query(self, manager):
        """Test auto-coordination for physics-related query."""
        session_id = "test-session"
        query = "Help me set up a physics simulation with gravity"
        
        mock_primary_response = AgentResponse(
            agent_id="physics-1",
            agent_type="physics",
            response="Here's how to set up gravity in PhysX",
            confidence_score=0.9,
            suggestions=["Use scene.setGravity()"],
            code_snippets=[],
            response_time=0.8,
            capabilities_used=[AgentCapability.PHYSICS_MODELING]
        )
        
        mock_result = CoordinationResult(
            primary_response=mock_primary_response,
            supporting_responses=[],
            consensus_score=0.95,
            conflicts=[],
            coordination_time=1.0
        )
        
        with patch.object(manager.orchestrator, 'coordinate_agents') as mock_coordinate:
            mock_coordinate.return_value = mock_result
            
            with patch.object(manager, 'send_to_session') as mock_send:
                await manager._auto_coordinate_agents(session_id, query)
                
                # Verify physics capability was selected
                coord_request = mock_coordinate.call_args[0][0]
                assert AgentCapability.PHYSICS_MODELING in coord_request.required_capabilities
    
    @pytest.mark.asyncio
    async def test_auto_coordinate_agents_visualization_query(self, manager):
        """Test auto-coordination for visualization-related query."""
        session_id = "test-session"
        query = "Create a 3D plot of my simulation results"
        
        mock_primary_response = AgentResponse(
            agent_id="visualization-1",
            agent_type="visualization",
            response="Here's how to create 3D plots",
            confidence_score=0.88,
            suggestions=["Use matplotlib or Three.js"],
            code_snippets=[],
            response_time=0.6,
            capabilities_used=[AgentCapability.DATA_VISUALIZATION]
        )
        
        mock_result = CoordinationResult(
            primary_response=mock_primary_response,
            supporting_responses=[],
            consensus_score=0.92,
            conflicts=[],
            coordination_time=0.8
        )
        
        with patch.object(manager.orchestrator, 'coordinate_agents') as mock_coordinate:
            mock_coordinate.return_value = mock_result
            
            with patch.object(manager, 'send_to_session'):
                await manager._auto_coordinate_agents(session_id, query)
                
                # Verify visualization capability was selected
                coord_request = mock_coordinate.call_args[0][0]
                assert AgentCapability.DATA_VISUALIZATION in coord_request.required_capabilities
    
    @pytest.mark.asyncio
    async def test_error_handling_in_user_message(self, manager):
        """Test error handling in user message processing."""
        session_id = "test-session"
        payload = {
            "content": "Test query",
            "selectedAgents": ["invalid-agent"]
        }
        
        with patch('app.api.v1.chat_websocket.agent_registry') as mock_registry:
            mock_registry.create_agent.side_effect = ValueError("Invalid agent type")
            
            with patch.object(manager, 'send_to_session') as mock_send:
                await manager._handle_user_message(session_id, payload)
                
                mock_send.assert_called_once()
                sent_message = mock_send.call_args[0][1]
                assert sent_message['type'] == 'error'
                assert 'Invalid agent type' in sent_message['payload']['message']


class TestChatWebSocketIntegration:
    """Integration tests for chat WebSocket endpoints."""
    
    @pytest.mark.asyncio
    async def test_websocket_message_flow(self):
        """Test complete WebSocket message flow."""
        # This would require a more complex setup with actual WebSocket testing
        # For now, we'll test the message handling logic
        
        manager = ChatConnectionManager()
        session_id = "integration-test-session"
        
        # Test message handling
        message = {
            "type": "user_message",
            "payload": {
                "content": "Help with physics",
                "selectedAgents": []
            }
        }
        
        with patch.object(manager, '_handle_user_message') as mock_handle:
            await manager.handle_message(session_id, message)
            
            mock_handle.assert_called_once_with(
                session_id, 
                message["payload"]
            )
    
    def test_message_type_routing(self):
        """Test that different message types are routed correctly."""
        manager = ChatConnectionManager()
        
        test_cases = [
            ("user_message", "_handle_user_message"),
            ("agent_coordination", "_handle_agent_coordination"),
            ("context_update", "_handle_context_update")
        ]
        
        for message_type, expected_method in test_cases:
            message = {
                "type": message_type,
                "payload": {"test": "data"}
            }
            
            with patch.object(manager, expected_method) as mock_method:
                asyncio.run(manager.handle_message("test-session", message))
                mock_method.assert_called_once()