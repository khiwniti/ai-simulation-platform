"""
Inline AI Assistance API endpoints.
"""

from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from app.services.agents.orchestrator import AgentOrchestrator
from app.services.agents.base import AgentContext, AgentCapability, agent_registry
from app.services.inline_assistance_service import InlineAssistanceService
from app.api.deps import get_current_user

router = APIRouter()

# Service instance
inline_service = InlineAssistanceService()


class InlineAssistanceRequest(BaseModel):
    """Request for inline AI assistance."""
    session_id: UUID = Field(..., description="Session identifier")
    notebook_id: UUID = Field(..., description="Notebook ID")
    cell_id: UUID = Field(..., description="Cell ID")
    code_content: str = Field(..., description="Current code content")
    cursor_position: int = Field(..., ge=0, description="Cursor position in code")
    line_number: int = Field(..., ge=1, description="Current line number")
    column_number: int = Field(..., ge=0, description="Current column number")
    trigger_type: str = Field(..., description="Trigger type: 'completion', 'hover', 'manual'")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")


class InlineSuggestion(BaseModel):
    """Inline suggestion from AI agent."""
    id: str
    agent_id: str
    agent_type: str
    suggestion_type: str  # 'completion', 'fix', 'optimization', 'explanation'
    text: str
    insert_text: Optional[str] = None
    replace_range: Optional[Dict[str, int]] = None  # start_pos, end_pos
    confidence_score: float
    priority: int = 1  # 1=high, 2=medium, 3=low
    explanation: Optional[str] = None
    documentation: Optional[str] = None


class InlineAssistanceResponse(BaseModel):
    """Response for inline assistance request."""
    suggestions: List[InlineSuggestion]
    context_analysis: Dict[str, Any]
    processing_time: float
    agents_used: List[str]


@router.post("/suggestions", response_model=InlineAssistanceResponse)
async def get_inline_suggestions(
    request: InlineAssistanceRequest,
    current_user: dict = Depends(get_current_user)
):
    """Get inline AI suggestions based on cursor position and code context."""
    try:
        # Analyze code context
        context_analysis = await inline_service.analyze_code_context(
            code_content=request.code_content,
            cursor_position=request.cursor_position,
            line_number=request.line_number,
            column_number=request.column_number
        )
        
        # Get suggestions from appropriate agents
        suggestions = await inline_service.get_suggestions(
            session_id=request.session_id,
            notebook_id=request.notebook_id,
            cell_id=request.cell_id,
            code_content=request.code_content,
            cursor_position=request.cursor_position,
            context_analysis=context_analysis,
            trigger_type=request.trigger_type,
            additional_context=request.context
        )
        
        return InlineAssistanceResponse(
            suggestions=suggestions,
            context_analysis=context_analysis,
            processing_time=context_analysis.get('processing_time', 0.0),
            agents_used=list(set(s.agent_id for s in suggestions))
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inline assistance failed: {str(e)}")


@router.post("/apply-suggestion")
async def apply_suggestion(
    suggestion_id: str,
    session_id: UUID,
    current_user: dict = Depends(get_current_user)
):
    """Apply an inline suggestion and provide feedback to the agent."""
    try:
        result = await inline_service.apply_suggestion(suggestion_id, session_id)
        return {
            "success": True,
            "applied_text": result.get("applied_text"),
            "message": "Suggestion applied successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply suggestion: {str(e)}")


@router.post("/reject-suggestion")
async def reject_suggestion(
    suggestion_id: str,
    session_id: UUID,
    reason: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Reject an inline suggestion and provide feedback to the agent."""
    try:
        await inline_service.reject_suggestion(suggestion_id, session_id, reason)
        return {
            "success": True,
            "message": "Suggestion rejected successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to reject suggestion: {str(e)}")


@router.get("/context-analysis")
async def analyze_code_context(
    code_content: str,
    cursor_position: int,
    line_number: int,
    column_number: int,
    current_user: dict = Depends(get_current_user)
):
    """Analyze code context for debugging purposes."""
    try:
        analysis = await inline_service.analyze_code_context(
            code_content=code_content,
            cursor_position=cursor_position,
            line_number=line_number,
            column_number=column_number
        )
        
        return analysis
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Context analysis failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check for inline assistance service."""
    return {
        "status": "healthy",
        "service_active": inline_service.is_active(),
        "supported_triggers": ["completion", "hover", "manual"]
    }