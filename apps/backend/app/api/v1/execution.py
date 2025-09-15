"""
Execution API endpoints for Python code execution
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import json
import asyncio

from app.services.execution_service import (
    get_execution_service,
    ExecutionRequest,
    ExecutionStatus,
    ExecutionOutput
)

router = APIRouter()


@router.post("/execute", response_model=Dict[str, str])
async def execute_code(request: ExecutionRequest, background_tasks: BackgroundTasks):
    """
    Execute Python code in a secure container
    
    Returns execution ID for tracking progress
    """
    try:
        # Get execution service instance
        execution_service = get_execution_service()
        
        # Ensure execution service is initialized
        if not execution_service.redis_client:
            await execution_service.initialize()
            
        execution_id = await execution_service.execute_code(request)
        
        return {
            "execution_id": execution_id,
            "status": "queued"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start execution: {str(e)}")


@router.get("/status/{execution_id}", response_model=ExecutionStatus)
async def get_execution_status(execution_id: str):
    """
    Get the current status of a code execution
    """
    try:
        execution_service = get_execution_service()
        status = await execution_service.get_execution_status(execution_id)
        if not status:
            raise HTTPException(status_code=404, detail="Execution not found")
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")


@router.get("/stream/{execution_id}")
async def stream_execution_output(execution_id: str):
    """
    Stream execution output in real-time using Server-Sent Events
    """
    async def generate_stream():
        try:
            async for output in execution_service.stream_execution_output(execution_id):
                # Format as Server-Sent Events
                data = output.model_dump_json()
                yield f"data: {data}\n\n"
                
        except Exception as e:
            error_data = {
                "output_type": "error",
                "content": {
                    "ename": "StreamError",
                    "evalue": str(e),
                    "traceback": [str(e)]
                },
                "timestamp": "2024-01-01T00:00:00"
            }
            yield f"data: {json.dumps(error_data)}\n\n"
        finally:
            yield "event: close\ndata: {}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.delete("/cancel/{execution_id}")
async def cancel_execution(execution_id: str):
    """
    Cancel a running execution
    """
    try:
        success = await execution_service.cancel_execution(execution_id)
        if not success:
            raise HTTPException(status_code=404, detail="Execution not found or already completed")
            
        return {"message": "Execution cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel execution: {str(e)}")


@router.get("/queue/status")
async def get_queue_status():
    """
    Get current execution queue status
    """
    try:
        status = await execution_service.get_queue_status()
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get queue status: {str(e)}")


@router.post("/initialize")
async def initialize_execution_service():
    """
    Initialize the execution service (build Docker image if needed)
    """
    try:
        await execution_service.initialize()
        return {"message": "Execution service initialized successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initialize: {str(e)}")