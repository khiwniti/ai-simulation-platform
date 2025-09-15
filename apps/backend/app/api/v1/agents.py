"""
Agent API endpoints for AI agent orchestration.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.agents.orchestrator import (
    AgentOrchestrator, CoordinationRequest, CoordinationResult,
    AgentMessage, MessageType, MessagePriority
)
from app.services.agents.base import AgentContext, AgentCapability, agent_registry
from app.schemas.agent import AgentInteractionCreate, AgentInteractionResponse
from app.api.deps import get_current_user

router = APIRouter()

# Global orchestrator instance
orchestrator = AgentOrchestrator()


class AgentQueryRequest(BaseModel):
    """Request for agent query processing."""
    query: str = Field(..., min_length=1, description="User query or request")
    session_id: UUID = Field(..., description="Session identifier")
    notebook_id: Optional[UUID] = Field(None, description="Current notebook ID")
    cell_id: Optional[UUID] = Field(None, description="Current cell ID")
    current_code: Optional[str] = Field(None, description="Current code context")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class AgentCoordinationRequest(BaseModel):
    """Request for multi-agent coordination."""
    query: str = Field(..., min_length=1)
    session_id: UUID
    required_capabilities: List[str] = Field(default_factory=list)
    preferred_agents: List[str] = Field(default_factory=list)
    max_agents: int = Field(3, ge=1, le=10)
    timeout_seconds: int = Field(30, ge=5, le=300)
    notebook_id: Optional[UUID] = None
    cell_id: Optional[UUID] = None
    current_code: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class AgentStatusResponse(BaseModel):
    """Response for agent status."""
    agent_id: str
    agent_type: str
    name: str
    is_active: bool
    capabilities: List[str]
    performance_metrics: Dict[str, Any]
    has_context: bool


class SessionResponse(BaseModel):
    """Response for session operations."""
    session_id: UUID
    active_agents: List[str]
    context: Dict[str, Any]


@router.on_event("startup")
async def startup_orchestrator():
    """Start the agent orchestrator on API startup."""
    await orchestrator.start()
    
    # Register agent types
    from app.services.agents.physics_agent import PhysicsAgent
    from app.services.agents.visualization_agent import VisualizationAgent
    from app.services.agents.optimization_agent import OptimizationAgent
    from app.services.agents.debug_agent import DebugAgent
    
    agent_registry.register_agent_type("physics", PhysicsAgent)
    agent_registry.register_agent_type("visualization", VisualizationAgent)
    agent_registry.register_agent_type("optimization", OptimizationAgent)
    agent_registry.register_agent_type("debug", DebugAgent)


@router.on_event("shutdown")
async def shutdown_orchestrator():
    """Stop the agent orchestrator on API shutdown."""
    await orchestrator.stop()


@router.post("/sessions", response_model=SessionResponse)
async def create_agent_session(
    session_id: UUID,
    notebook_id: Optional[UUID] = None,
    context: Dict[str, Any] = None,
    current_user: dict = Depends(get_current_user)
):
    """Create a new agent session."""
    try:
        agent_context = await orchestrator.create_session(
            session_id=session_id,
            notebook_id=notebook_id,
            **(context or {})
        )
        
        return SessionResponse(
            session_id=session_id,
            active_agents=list(agent_context.active_agents),
            context={
                "notebook_id": str(agent_context.notebook_id) if agent_context.notebook_id else None,
                "cell_id": str(agent_context.cell_id) if agent_context.cell_id else None
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.delete("/sessions/{session_id}")
async def end_agent_session(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """End an agent session."""
    try:
        await orchestrator.end_session(session_id)
        return {"message": "Session ended successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end session: {str(e)}")


@router.post("/coordinate", response_model=Dict[str, Any])
async def coordinate_agents(
    request: AgentCoordinationRequest,
    current_user: dict = Depends(get_current_user)
):
    """Coordinate multiple agents to handle a complex query."""
    try:
        # Convert capability strings to enums
        capabilities = set()
        for cap_str in request.required_capabilities:
            try:
                capability = AgentCapability(cap_str)
                capabilities.add(capability)
            except ValueError:
                # Skip invalid capabilities
                continue
        
        # Create agent context
        context = AgentContext(
            session_id=request.session_id,
            notebook_id=request.notebook_id,
            cell_id=request.cell_id,
            current_code=request.current_code,
            **request.context
        )
        
        # Create coordination request
        coord_request = CoordinationRequest(
            query=request.query,
            context=context,
            required_capabilities=capabilities,
            preferred_agents=request.preferred_agents,
            max_agents=request.max_agents,
            timeout_seconds=request.timeout_seconds
        )
        
        # Coordinate agents
        result = await orchestrator.coordinate_agents(coord_request)
        
        # Format response
        return {
            "primary_response": {
                "agent_id": result.primary_response.agent_id,
                "agent_type": result.primary_response.agent_type,
                "response": result.primary_response.response,
                "confidence_score": result.primary_response.confidence_score,
                "suggestions": result.primary_response.suggestions,
                "code_snippets": result.primary_response.code_snippets,
                "response_time": result.primary_response.response_time
            },
            "supporting_responses": [
                {
                    "agent_id": resp.agent_id,
                    "agent_type": resp.agent_type,
                    "response": resp.response,
                    "confidence_score": resp.confidence_score,
                    "suggestions": resp.suggestions,
                    "code_snippets": resp.code_snippets
                }
                for resp in result.supporting_responses
            ],
            "consensus_score": result.consensus_score,
            "conflicts": result.conflicts,
            "coordination_time": result.coordination_time
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent coordination failed: {str(e)}")


@router.post("/query", response_model=Dict[str, Any])
async def query_single_agent(
    request: AgentQueryRequest,
    agent_type: str,
    current_user: dict = Depends(get_current_user)
):
    """Query a single specialized agent."""
    try:
        # Create or get agent
        agent = agent_registry.create_agent(agent_type)
        
        # Create context
        context = AgentContext(
            session_id=request.session_id,
            notebook_id=request.notebook_id,
            cell_id=request.cell_id,
            current_code=request.current_code,
            **request.context
        )
        
        # Initialize agent if needed
        if not agent.is_active:
            await agent.initialize(context)
        
        # Process query
        response = await agent.process_query(request.query, context)
        
        return {
            "agent_id": response.agent_id,
            "agent_type": response.agent_type,
            "response": response.response,
            "confidence_score": response.confidence_score,
            "capabilities_used": [cap.value for cap in response.capabilities_used],
            "suggestions": response.suggestions,
            "code_snippets": response.code_snippets,
            "response_time": response.response_time,
            "timestamp": response.timestamp.isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid agent type: {agent_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")


@router.get("/sessions/{session_id}/status", response_model=Dict[str, AgentStatusResponse])
async def get_session_agent_status(
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Get status of all agents in a session."""
    try:
        status = await orchestrator.get_agent_status(session_id)
        
        return {
            agent_id: AgentStatusResponse(**agent_status)
            for agent_id, agent_status in status.items()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get agent status: {str(e)}")


@router.post("/sessions/{session_id}/context")
async def update_session_context(
    session_id: UUID,
    context_update: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Update context for all agents in a session."""
    try:
        await orchestrator.broadcast_context_update(session_id, context_update)
        return {"message": "Context updated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update context: {str(e)}")


@router.get("/types", response_model=List[str])
async def get_available_agent_types(
    current_user: dict = Depends(get_current_user)
):
    """Get list of available agent types."""
    return agent_registry.get_agent_types()


@router.get("/capabilities", response_model=List[str])
async def get_available_capabilities(
    current_user: dict = Depends(get_current_user)
):
    """Get list of available agent capabilities."""
    return [cap.value for cap in AgentCapability]


@router.get("/metrics", response_model=Dict[str, Any])
async def get_orchestrator_metrics(
    current_user: dict = Depends(get_current_user)
):
    """Get orchestrator performance metrics."""
    return orchestrator.get_metrics()


@router.get("/coordination-history", response_model=List[Dict[str, Any]])
async def get_coordination_history(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get recent coordination history."""
    return orchestrator.get_coordination_history(limit)


@router.post("/agents/{agent_id}/shutdown")
async def shutdown_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Shutdown a specific agent."""
    try:
        success = agent_registry.remove_agent(agent_id)
        if success:
            return {"message": f"Agent {agent_id} shutdown successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to shutdown agent: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint for agent system."""
    return {
        "status": "healthy",
        "orchestrator_running": orchestrator.is_running,
        "registered_agent_types": agent_registry.get_agent_types(),
        "active_agents": len(agent_registry.get_all_agents())
    }