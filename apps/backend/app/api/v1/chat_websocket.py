"""
WebSocket handler for real-time chat communication with AI agents.
"""

import json
import logging
from typing import Dict, Set
from uuid import UUID
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.routing import APIRouter

from app.services.agents.orchestrator import AgentOrchestrator, CoordinationRequest
from app.services.agents.base import AgentContext, AgentCapability, agent_registry

logger = logging.getLogger(__name__)

router = APIRouter()

# Global connection manager
class ChatConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.session_connections: Dict[str, Set[str]] = {}
        self.orchestrator = AgentOrchestrator()

    async def connect(self, websocket: WebSocket, session_id: str, connection_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections[connection_id] = websocket
        
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)
        
        logger.info(f"Chat WebSocket connected: {connection_id} for session {session_id}")

    def disconnect(self, connection_id: str, session_id: str):
        """Remove a WebSocket connection."""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        logger.info(f"Chat WebSocket disconnected: {connection_id}")

    async def send_to_session(self, session_id: str, message: dict):
        """Send a message to all connections in a session."""
        if session_id not in self.session_connections:
            return
        
        message_json = json.dumps(message, default=str)
        disconnected = []
        
        for connection_id in self.session_connections[session_id]:
            if connection_id in self.active_connections:
                try:
                    await self.active_connections[connection_id].send_text(message_json)
                except Exception as e:
                    logger.error(f"Failed to send message to {connection_id}: {e}")
                    disconnected.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected:
            self.disconnect(connection_id, session_id)

    async def handle_message(self, session_id: str, message: dict):
        """Handle incoming message from client."""
        try:
            message_type = message.get('type')
            payload = message.get('payload', {})
            
            if message_type == 'user_message':
                await self._handle_user_message(session_id, payload)
            elif message_type == 'agent_coordination':
                await self._handle_agent_coordination(session_id, payload)
            elif message_type == 'context_update':
                await self._handle_context_update(session_id, payload)
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
            await self.send_to_session(session_id, {
                'type': 'error',
                'payload': {'message': f'Error processing message: {str(e)}'},
                'timestamp': datetime.utcnow().isoformat()
            })

    async def _handle_user_message(self, session_id: str, payload: dict):
        """Handle user message and route to appropriate agents."""
        query = payload.get('content', '')
        selected_agents = payload.get('selectedAgents', [])
        
        if not query.strip():
            return
        
        try:
            if len(selected_agents) == 1:
                # Single agent query
                agent_type = selected_agents[0]
                agent = agent_registry.create_agent(agent_type)
                
                context = AgentContext(session_id=UUID(session_id))
                if not agent.is_active:
                    await agent.initialize(context)
                
                response = await agent.process_query(query, context)
                
                await self.send_to_session(session_id, {
                    'type': 'agent_response',
                    'payload': {
                        'agent_id': response.agent_id,
                        'agent_type': response.agent_type,
                        'response': response.response,
                        'confidence_score': response.confidence_score,
                        'suggestions': response.suggestions,
                        'code_snippets': response.code_snippets,
                        'response_time': response.response_time,
                        'capabilities_used': [cap.value for cap in response.capabilities_used]
                    },
                    'timestamp': datetime.utcnow().isoformat()
                })
                
            elif len(selected_agents) > 1:
                # Multi-agent coordination
                await self._coordinate_multiple_agents(session_id, query, selected_agents)
            else:
                # Auto-select appropriate agents
                await self._auto_coordinate_agents(session_id, query)
                
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            await self.send_to_session(session_id, {
                'type': 'error',
                'payload': {'message': f'Error processing query: {str(e)}'},
                'timestamp': datetime.utcnow().isoformat()
            })

    async def _handle_agent_coordination(self, session_id: str, payload: dict):
        """Handle explicit agent coordination request."""
        query = payload.get('query', '')
        capabilities = payload.get('capabilities', [])
        
        try:
            # Convert capability strings to enums
            capability_enums = set()
            for cap_str in capabilities:
                try:
                    capability = AgentCapability(cap_str)
                    capability_enums.add(capability)
                except ValueError:
                    continue
            
            context = AgentContext(session_id=UUID(session_id))
            
            coord_request = CoordinationRequest(
                query=query,
                context=context,
                required_capabilities=capability_enums,
                max_agents=3,
                timeout_seconds=30
            )
            
            result = await self.orchestrator.coordinate_agents(coord_request)
            
            await self.send_to_session(session_id, {
                'type': 'agent_coordination',
                'payload': {
                    'primary_response': {
                        'agent_id': result.primary_response.agent_id,
                        'agent_type': result.primary_response.agent_type,
                        'response': result.primary_response.response,
                        'confidence_score': result.primary_response.confidence_score,
                        'suggestions': result.primary_response.suggestions,
                        'code_snippets': result.primary_response.code_snippets,
                        'response_time': result.primary_response.response_time
                    },
                    'supporting_responses': [
                        {
                            'agent_id': resp.agent_id,
                            'agent_type': resp.agent_type,
                            'response': resp.response,
                            'confidence_score': resp.confidence_score,
                            'suggestions': resp.suggestions,
                            'code_snippets': resp.code_snippets
                        }
                        for resp in result.supporting_responses
                    ],
                    'consensus_score': result.consensus_score,
                    'conflicts': result.conflicts,
                    'coordination_time': result.coordination_time
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in agent coordination: {e}")
            await self.send_to_session(session_id, {
                'type': 'error',
                'payload': {'message': f'Coordination failed: {str(e)}'},
                'timestamp': datetime.utcnow().isoformat()
            })

    async def _coordinate_multiple_agents(self, session_id: str, query: str, selected_agents: list):
        """Coordinate multiple selected agents."""
        try:
            context = AgentContext(session_id=UUID(session_id))
            
            coord_request = CoordinationRequest(
                query=query,
                context=context,
                required_capabilities=set(),  # Will be inferred from agents
                preferred_agents=selected_agents,
                max_agents=len(selected_agents),
                timeout_seconds=30
            )
            
            result = await self.orchestrator.coordinate_agents(coord_request)
            
            await self.send_to_session(session_id, {
                'type': 'agent_coordination',
                'payload': {
                    'primary_response': {
                        'agent_id': result.primary_response.agent_id,
                        'agent_type': result.primary_response.agent_type,
                        'response': result.primary_response.response,
                        'confidence_score': result.primary_response.confidence_score,
                        'suggestions': result.primary_response.suggestions,
                        'code_snippets': result.primary_response.code_snippets,
                        'response_time': result.primary_response.response_time
                    },
                    'supporting_responses': [
                        {
                            'agent_id': resp.agent_id,
                            'agent_type': resp.agent_type,
                            'response': resp.response,
                            'confidence_score': resp.confidence_score,
                            'suggestions': resp.suggestions,
                            'code_snippets': resp.code_snippets
                        }
                        for resp in result.supporting_responses
                    ],
                    'consensus_score': result.consensus_score,
                    'conflicts': result.conflicts,
                    'coordination_time': result.coordination_time
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error coordinating multiple agents: {e}")
            await self.send_to_session(session_id, {
                'type': 'error',
                'payload': {'message': f'Multi-agent coordination failed: {str(e)}'},
                'timestamp': datetime.utcnow().isoformat()
            })

    async def _auto_coordinate_agents(self, session_id: str, query: str):
        """Automatically select and coordinate appropriate agents."""
        try:
            # Simple keyword-based agent selection
            query_lower = query.lower()
            selected_capabilities = set()
            
            if any(word in query_lower for word in ['physics', 'simulation', 'physx', 'force', 'gravity']):
                selected_capabilities.add(AgentCapability.PHYSICS_MODELING)
            
            if any(word in query_lower for word in ['visualization', '3d', 'render', 'plot', 'chart']):
                selected_capabilities.add(AgentCapability.DATA_VISUALIZATION)
            
            if any(word in query_lower for word in ['optimize', 'performance', 'gpu', 'memory', 'speed']):
                selected_capabilities.add(AgentCapability.PERFORMANCE_OPTIMIZATION)
            
            if any(word in query_lower for word in ['debug', 'error', 'fix', 'problem', 'issue']):
                selected_capabilities.add(AgentCapability.ERROR_ANALYSIS)
            
            # Default to physics if no specific capabilities detected
            if not selected_capabilities:
                selected_capabilities.add(AgentCapability.PHYSICS_MODELING)
            
            context = AgentContext(session_id=UUID(session_id))
            
            coord_request = CoordinationRequest(
                query=query,
                context=context,
                required_capabilities=selected_capabilities,
                max_agents=min(len(selected_capabilities), 3),
                timeout_seconds=30
            )
            
            result = await self.orchestrator.coordinate_agents(coord_request)
            
            await self.send_to_session(session_id, {
                'type': 'agent_coordination',
                'payload': {
                    'primary_response': {
                        'agent_id': result.primary_response.agent_id,
                        'agent_type': result.primary_response.agent_type,
                        'response': result.primary_response.response,
                        'confidence_score': result.primary_response.confidence_score,
                        'suggestions': result.primary_response.suggestions,
                        'code_snippets': result.primary_response.code_snippets,
                        'response_time': result.primary_response.response_time
                    },
                    'supporting_responses': [
                        {
                            'agent_id': resp.agent_id,
                            'agent_type': resp.agent_type,
                            'response': resp.response,
                            'confidence_score': resp.confidence_score,
                            'suggestions': resp.suggestions,
                            'code_snippets': resp.code_snippets
                        }
                        for resp in result.supporting_responses
                    ],
                    'consensus_score': result.consensus_score,
                    'conflicts': result.conflicts,
                    'coordination_time': result.coordination_time
                },
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error in auto coordination: {e}")
            await self.send_to_session(session_id, {
                'type': 'error',
                'payload': {'message': f'Auto coordination failed: {str(e)}'},
                'timestamp': datetime.utcnow().isoformat()
            })

    async def _handle_context_update(self, session_id: str, payload: dict):
        """Handle context update from client."""
        context_data = payload.get('context', {})
        
        try:
            await self.orchestrator.broadcast_context_update(UUID(session_id), context_data)
            
            await self.send_to_session(session_id, {
                'type': 'system_message',
                'payload': {'message': 'Context updated successfully'},
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error updating context: {e}")
            await self.send_to_session(session_id, {
                'type': 'error',
                'payload': {'message': f'Context update failed: {str(e)}'},
                'timestamp': datetime.utcnow().isoformat()
            })


# Global connection manager instance
chat_manager = ChatConnectionManager()


@router.websocket("/ws/chat/{session_id}")
async def chat_websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for chat communication."""
    connection_id = f"{session_id}_{datetime.utcnow().timestamp()}"
    
    await chat_manager.connect(websocket, session_id, connection_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            await chat_manager.handle_message(session_id, message)
            
    except WebSocketDisconnect:
        chat_manager.disconnect(connection_id, session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        chat_manager.disconnect(connection_id, session_id)