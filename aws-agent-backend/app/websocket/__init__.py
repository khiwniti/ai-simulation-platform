from typing import Dict, List
import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
import structlog

logger = structlog.get_logger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_projects: Dict[str, str] = {}  # client_id -> project_id
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """
        Accept a new WebSocket connection
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("WebSocket client connected", client_id=client_id)
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "client_id": client_id,
            "message": "Connected to AWS AI Agent Platform"
        }, client_id)
    
    def disconnect(self, client_id: str):
        """
        Remove a WebSocket connection
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_projects:
            del self.client_projects[client_id]
        logger.info("WebSocket client disconnected", client_id=client_id)
    
    async def send_personal_message(self, message: dict, client_id: str):
        """
        Send a message to a specific client
        """
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error("Failed to send WebSocket message", 
                           client_id=client_id, error=str(e))
                self.disconnect(client_id)
    
    async def send_project_update(self, project_id: str, update: dict):
        """
        Send update to all clients watching a specific project
        """
        message = {
            "type": "project_update",
            "project_id": project_id,
            "update": update
        }
        
        for client_id, client_project_id in self.client_projects.items():
            if client_project_id == project_id:
                await self.send_personal_message(message, client_id)
    
    async def send_agent_status(self, agent_update: dict):
        """
        Send agent status update to all connected clients
        """
        message = {
            "type": "agent_status",
            "update": agent_update
        }
        
        for client_id in self.active_connections.keys():
            await self.send_personal_message(message, client_id)
    
    async def broadcast_system_message(self, message: dict):
        """
        Broadcast a system message to all connected clients
        """
        system_message = {
            "type": "system_message",
            "message": message
        }
        
        for client_id in self.active_connections.keys():
            await self.send_personal_message(system_message, client_id)
    
    def subscribe_to_project(self, client_id: str, project_id: str):
        """
        Subscribe a client to project updates
        """
        self.client_projects[client_id] = project_id
        logger.info("Client subscribed to project", 
                   client_id=client_id, project_id=project_id)
    
    def get_connected_clients(self) -> List[str]:
        """
        Get list of currently connected clients
        """
        return list(self.active_connections.keys())
    
    def get_connection_count(self) -> int:
        """
        Get number of active connections
        """
        return len(self.active_connections)

# Global connection manager instance
websocket_manager = ConnectionManager()

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time communication
    """
    await websocket_manager.connect(websocket, client_id)
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                await handle_websocket_message(message, client_id)
            except json.JSONDecodeError:
                await websocket_manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON message"
                }, client_id)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
    except Exception as e:
        logger.error("WebSocket error", client_id=client_id, error=str(e))
        websocket_manager.disconnect(client_id)

async def handle_websocket_message(message: dict, client_id: str):
    """
    Handle incoming WebSocket messages from clients
    """
    message_type = message.get("type")
    
    if message_type == "subscribe_project":
        project_id = message.get("project_id")
        if project_id:
            websocket_manager.subscribe_to_project(client_id, project_id)
            await websocket_manager.send_personal_message({
                "type": "subscription_confirmed",
                "project_id": project_id
            }, client_id)
    
    elif message_type == "get_status":
        # Send current system status
        await websocket_manager.send_personal_message({
            "type": "system_status",
            "status": {
                "agents_active": 5,
                "projects_running": 0,
                "system_health": "operational"
            }
        }, client_id)
    
    elif message_type == "ping":
        await websocket_manager.send_personal_message({
            "type": "pong",
            "timestamp": message.get("timestamp")
        }, client_id)
    
    else:
        await websocket_manager.send_personal_message({
            "type": "error",
            "message": f"Unknown message type: {message_type}"
        }, client_id)