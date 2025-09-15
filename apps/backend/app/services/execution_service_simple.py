"""
Simplified Python Code Execution Service for testing
"""

import asyncio
import json
import uuid
import subprocess
import tempfile
import os
from typing import Dict, Any, List, Optional, AsyncGenerator
from pathlib import Path
from datetime import datetime, timedelta
import redis.asyncio as redis
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)


class ExecutionRequest(BaseModel):
    """Request model for code execution"""
    code: str
    cell_id: str
    notebook_id: str
    execution_count: int
    timeout: int = 30
    memory_limit: str = "512m"
    cpu_limit: float = 1.0


class ExecutionOutput(BaseModel):
    """Output model for execution results"""
    output_type: str  # stdout, stderr, display_data, execute_result, error
    content: Dict[str, Any]
    execution_count: Optional[int] = None
    timestamp: datetime


class ExecutionStatus(BaseModel):
    """Status model for execution tracking"""
    execution_id: str
    status: str  # queued, running, completed, failed, timeout
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    outputs: List[ExecutionOutput] = []


class ExecutionService:
    """
    Simplified Python code execution service using subprocess
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_client = None
        self.redis_url = redis_url
        self.execution_queue = "execution_queue"
        self.max_concurrent_executions = 5
        self.running_executions: Dict[str, subprocess.Popen] = {}
        
    async def initialize(self):
        """Initialize the execution service"""
        self.redis_client = redis.from_url(self.redis_url)
        
    async def execute_code(self, request: ExecutionRequest) -> str:
        """
        Execute Python code and return execution ID for tracking
        """
        execution_id = str(uuid.uuid4())
        
        # Store execution request
        await self.redis_client.hset(
            f"execution:{execution_id}",
            mapping={
                "request": request.model_dump_json(),
                "status": "queued",
                "created_at": datetime.utcnow().isoformat()
            }
        )
        
        # Add to execution queue
        await self.redis_client.lpush(self.execution_queue, execution_id)
        
        # Start background execution if capacity available
        asyncio.create_task(self._process_execution_queue())
        
        return execution_id
        
    async def get_execution_status(self, execution_id: str) -> Optional[ExecutionStatus]:
        """Get the current status of an execution"""
        data = await self.redis_client.hgetall(f"execution:{execution_id}")
        if not data:
            return None
            
        status = ExecutionStatus(
            execution_id=execution_id,
            status=data.get("status", "unknown"),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )
        
        # Get outputs
        outputs_data = await self.redis_client.lrange(f"execution:{execution_id}:outputs", 0, -1)
        status.outputs = [ExecutionOutput.model_validate_json(output) for output in outputs_data]
        
        return status
        
    async def stream_execution_output(self, execution_id: str) -> AsyncGenerator[ExecutionOutput, None]:
        """Stream execution outputs in real-time"""
        last_output_count = 0
        
        while True:
            # Check if execution is complete
            status = await self.get_execution_status(execution_id)
            if not status:
                break
                
            # Get new outputs
            outputs_data = await self.redis_client.lrange(
                f"execution:{execution_id}:outputs", 
                last_output_count, 
                -1
            )
            
            for output_json in outputs_data:
                yield ExecutionOutput.model_validate_json(output_json)
                last_output_count += 1
                
            # Break if execution is complete
            if status.status in ["completed", "failed", "timeout"]:
                break
                
            # Wait before checking again
            await asyncio.sleep(0.1)
            
    async def cancel_execution(self, execution_id: str) -> bool:
        """Cancel a running execution"""
        if execution_id in self.running_executions:
            process = self.running_executions[execution_id]
            try:
                process.terminate()
                process.wait(timeout=5)
                del self.running_executions[execution_id]
                
                # Update status
                await self.redis_client.hset(
                    f"execution:{execution_id}",
                    mapping={
                        "status": "cancelled",
                        "completed_at": datetime.utcnow().isoformat()
                    }
                )
                return True
            except Exception as e:
                logger.error(f"Error cancelling execution {execution_id}: {e}")
                return False
        return False
        
    async def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        queue_length = await self.redis_client.llen(self.execution_queue)
        running_count = len(self.running_executions)
        
        return {
            "queue_length": queue_length,
            "running_executions": running_count,
            "max_concurrent": self.max_concurrent_executions,
            "available_slots": self.max_concurrent_executions - running_count
        }

    async def _process_execution_queue(self):
        """Process queued executions"""
        if len(self.running_executions) >= self.max_concurrent_executions:
            return
            
        execution_id = await self.redis_client.rpop(self.execution_queue)
        if not execution_id:
            return
            
        execution_id = execution_id.decode('utf-8')
        
        try:
            await self._execute_with_subprocess(execution_id)
        except Exception as e:
            logger.error(f"Error executing {execution_id}: {e}")
            await self._mark_execution_failed(execution_id, str(e))
            
    async def _execute_with_subprocess(self, execution_id: str):
        """Execute code using subprocess"""
        # Get execution request
        data = await self.redis_client.hgetall(f"execution:{execution_id}")
        request = ExecutionRequest.model_validate_json(data["request"])
        
        # Update status to running
        await self.redis_client.hset(
            f"execution:{execution_id}",
            mapping={
                "status": "running",
                "started_at": datetime.utcnow().isoformat()
            }
        )
        
        # Create execution script
        execution_script = self._create_execution_script(request.code)
        
        # Create temporary file for execution
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(execution_script)
            script_path = f.name
            
        try:
            # Execute the script
            process = subprocess.Popen(
                ['python3', script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.running_executions[execution_id] = process
            
            # Wait for completion with timeout
            try:
                stdout, stderr = process.communicate(timeout=request.timeout)
                
                # Process output
                await self._process_subprocess_output(execution_id, stdout, stderr)
                
                # Mark as completed
                await self.redis_client.hset(
                    f"execution:{execution_id}",
                    mapping={
                        "status": "completed",
                        "completed_at": datetime.utcnow().isoformat()
                    }
                )
                
            except subprocess.TimeoutExpired:
                process.kill()
                await self._mark_execution_timeout(execution_id)
                
        except Exception as e:
            await self._mark_execution_failed(execution_id, str(e))
        finally:
            # Clean up
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
            try:
                os.unlink(script_path)
            except:
                pass
                
    async def _process_subprocess_output(self, execution_id: str, stdout: str, stderr: str):
        """Process subprocess output and store in Redis"""
        # Process stdout line by line
        for line in stdout.strip().split('\n'):
            if line.strip():
                try:
                    output_data = json.loads(line)
                    output = ExecutionOutput(**output_data)
                    
                    # Store output
                    await self.redis_client.lpush(
                        f"execution:{execution_id}:outputs",
                        output.model_dump_json()
                    )
                except json.JSONDecodeError:
                    # Handle non-JSON output as stdout
                    output = ExecutionOutput(
                        output_type="stdout",
                        content={"text": line},
                        timestamp=datetime.utcnow()
                    )
                    await self.redis_client.lpush(
                        f"execution:{execution_id}:outputs",
                        output.model_dump_json()
                    )
                    
        # Process stderr if any
        if stderr.strip():
            output = ExecutionOutput(
                output_type="stderr",
                content={"text": stderr},
                timestamp=datetime.utcnow()
            )
            await self.redis_client.lpush(
                f"execution:{execution_id}:outputs",
                output.model_dump_json()
            )

    def _create_execution_script(self, user_code: str) -> str:
        """Create the execution script with output capture"""
        return f"""
import sys
import json
import traceback
import io
import base64
from contextlib import redirect_stdout, redirect_stderr

def capture_output():
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()
    
    try:
        # Redirect stdout and stderr
        with redirect_stdout(stdout_buffer), redirect_stderr(stderr_buffer):
            # Execute user code
            exec_globals = {{'__name__': '__main__'}}
            exec('''
{user_code}
''', exec_globals)
            
        # Output results
        stdout_content = stdout_buffer.getvalue()
        if stdout_content:
            print(json.dumps({{
                "output_type": "stdout",
                "content": {{"text": stdout_content}},
                "timestamp": "{{}}".format(__import__('datetime').datetime.utcnow().isoformat())
            }}))
            
    except Exception as e:
        # Output error
        error_traceback = traceback.format_exc()
        print(json.dumps({{
            "output_type": "error",
            "content": {{
                "ename": type(e).__name__,
                "evalue": str(e),
                "traceback": error_traceback.split('\\n')
            }},
            "timestamp": "{{}}".format(__import__('datetime').datetime.utcnow().isoformat())
        }}))
        
    # Output stderr if any
    stderr_content = stderr_buffer.getvalue()
    if stderr_content:
        print(json.dumps({{
            "output_type": "stderr",
            "content": {{"text": stderr_content}},
            "timestamp": "{{}}".format(__import__('datetime').datetime.utcnow().isoformat())
        }}))

if __name__ == "__main__":
    capture_output()
"""
        
    async def _mark_execution_failed(self, execution_id: str, error_message: str):
        """Mark execution as failed"""
        await self.redis_client.hset(
            f"execution:{execution_id}",
            mapping={
                "status": "failed",
                "completed_at": datetime.utcnow().isoformat(),
                "error": error_message
            }
        )
        
        # Add error output
        error_output = ExecutionOutput(
            output_type="error",
            content={
                "ename": "ExecutionError",
                "evalue": error_message,
                "traceback": [error_message]
            },
            timestamp=datetime.utcnow()
        )
        await self.redis_client.lpush(
            f"execution:{execution_id}:outputs",
            error_output.model_dump_json()
        )
        
    async def _mark_execution_timeout(self, execution_id: str):
        """Mark execution as timed out"""
        await self.redis_client.hset(
            f"execution:{execution_id}",
            mapping={
                "status": "timeout",
                "completed_at": datetime.utcnow().isoformat()
            }
        )
        
        # Add timeout output
        timeout_output = ExecutionOutput(
            output_type="error",
            content={
                "ename": "TimeoutError",
                "evalue": "Code execution timed out",
                "traceback": ["TimeoutError: Code execution timed out"]
            },
            timestamp=datetime.utcnow()
        )
        await self.redis_client.lpush(
            f"execution:{execution_id}:outputs",
            timeout_output.model_dump_json()
        )


# Global execution service instance
execution_service = ExecutionService()