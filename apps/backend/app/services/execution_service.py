"""
Python Code Execution Service

Provides secure Python code execution with containerized environments,
streaming output support, resource management, and NVIDIA PhysX AI integration.
"""

import asyncio
import json
import uuid
import tempfile
import shutil
import base64
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from pathlib import Path
from datetime import datetime, timedelta
import docker
from docker.models.containers import Container
import redis.asyncio as redis
from pydantic import BaseModel
import logging

from .physics_service import physics_service, PhysicsContext

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
    # Physics-specific parameters
    enable_physics: bool = False
    physics_requirements: Optional[Dict[str, Any]] = None


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
    Secure Python code execution service with containerized environments and physics support
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.docker_client = docker.from_env()
        self.redis_client = None
        self.redis_url = redis_url
        self.execution_queue = "execution_queue"
        self.max_concurrent_executions = 5
        self.running_executions: Dict[str, Container] = {}
        self.physics_contexts: Dict[str, PhysicsContext] = {}
        
    async def initialize(self):
        """Initialize the execution service"""
        self.redis_client = redis.from_url(self.redis_url)
        await self._ensure_execution_images()
        
        # Initialize physics service
        await physics_service.initialize()
        
    async def _ensure_execution_images(self):
        """Ensure both regular and physics execution Docker images exist"""
        # Regular execution image
        try:
            self.docker_client.images.get("python-executor:latest")
        except docker.errors.ImageNotFound:
            logger.info("Building Python execution image...")
            await self._build_execution_image()
            
        # Physics execution image
        try:
            self.docker_client.images.get("python-physics-executor:latest")
        except docker.errors.ImageNotFound:
            logger.info("Building Physics execution image...")
            await self._build_physics_execution_image()
            
    async def _build_execution_image(self):
        """Build the secure Python execution Docker image"""
        dockerfile_content = """
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    g++ \\
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for scientific computing
RUN pip install --no-cache-dir \\
    numpy==1.24.3 \\
    matplotlib==3.7.1 \\
    pandas==2.0.3 \\
    scipy==1.11.1 \\
    sympy==1.12 \\
    plotly==5.15.0 \\
    seaborn==0.12.2 \\
    pillow==10.0.0 \\
    ipython==8.14.0

# Create non-root user for security
RUN useradd -m -u 1000 executor
USER executor
WORKDIR /home/executor

# Set up execution environment
ENV PYTHONPATH=/home/executor
ENV MPLBACKEND=Agg

CMD ["python", "-u", "/home/executor/execute.py"]
"""
        
        # Create temporary directory for build context
        with tempfile.TemporaryDirectory() as temp_dir:
            dockerfile_path = Path(temp_dir) / "Dockerfile"
            dockerfile_path.write_text(dockerfile_content)
            
            # Build image
            self.docker_client.images.build(
                path=temp_dir,
                tag="python-executor:latest",
                rm=True
            )
            
    async def _build_physics_execution_image(self):
        """Build the physics-enabled Python execution Docker image"""
        # Read the physics dockerfile and execution script
        docker_dir = Path(__file__).parent.parent.parent / "docker"
        dockerfile_path = docker_dir / "physics_executor.dockerfile"
        execute_script_path = docker_dir / "physics_execute.py"
        
        if not dockerfile_path.exists() or not execute_script_path.exists():
            logger.error("Physics Docker files not found, using fallback")
            return
            
        # Create temporary directory for build context
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copy dockerfile
            shutil.copy2(dockerfile_path, temp_path / "Dockerfile")
            
            # Copy execution script
            shutil.copy2(execute_script_path, temp_path / "physics_execute.py")
            
            # Build image
            try:
                self.docker_client.images.build(
                    path=temp_dir,
                    tag="python-physics-executor:latest",
                    rm=True
                )
                logger.info("Physics execution image built successfully")
            except Exception as e:
                logger.error(f"Failed to build physics execution image: {e}")
                # Continue without physics support
            
    async def execute_code(self, request: ExecutionRequest) -> str:
        """
        Execute Python code and return execution ID for tracking
        """
        execution_id = str(uuid.uuid4())
        
        # Create physics context if physics is enabled
        if request.enable_physics and request.physics_requirements:
            try:
                physics_context = await physics_service.create_physics_context(
                    execution_id, 
                    request.physics_requirements
                )
                self.physics_contexts[execution_id] = physics_context
                logger.info(f"Created physics context for execution {execution_id}")
            except Exception as e:
                logger.warning(f"Failed to create physics context: {e}")
                # Continue without physics support
        
        # Store execution request
        await self.redis_client.hset(
            f"execution:{execution_id}",
            mapping={
                "request": request.model_dump_json(),
                "status": "queued",
                "created_at": datetime.utcnow().isoformat(),
                "has_physics": str(execution_id in self.physics_contexts)
            }
        )
        
        # Add to execution queue
        await self.redis_client.lpush(self.execution_queue, execution_id)
        
        # Start background execution if capacity available
        asyncio.create_task(self._process_execution_queue())
        
        return execution_id
        
    async def _process_execution_queue(self):
        """Process the execution queue with physics support"""
        if len(self.running_executions) >= self.max_concurrent_executions:
            return
            
        # Get next execution from queue
        execution_id = await self.redis_client.rpop(self.execution_queue)
        if not execution_id:
            return
            
        execution_id = execution_id.decode('utf-8')
        
        try:
            # Get execution request
            data = await self.redis_client.hgetall(f"execution:{execution_id}")
            if not data:
                logger.error(f"Execution data not found for {execution_id}")
                return
                
            request = ExecutionRequest.model_validate_json(data["request"])
            
            # Update status to running
            await self.redis_client.hset(
                f"execution:{execution_id}",
                mapping={
                    "status": "running",
                    "started_at": datetime.utcnow().isoformat()
                }
            )
            
            # Execute with or without physics
            if execution_id in self.physics_contexts:
                await self._execute_with_physics(execution_id, request)
            else:
                await self._execute_regular(execution_id, request)
                
        except Exception as e:
            logger.error(f"Error processing execution {execution_id}: {e}")
            await self._mark_execution_failed(execution_id, str(e))
            
    async def _execute_with_physics(self, execution_id: str, request: ExecutionRequest):
        """Execute code with physics support"""
        physics_context = self.physics_contexts[execution_id]
        
        try:
            # Get physics Docker configuration
            docker_config = physics_service.get_physics_docker_config(physics_context)
            
            # Create and run container
            container = self.docker_client.containers.run(
                image=docker_config["image"],
                command=["python", "-u", "/home/executor/execute.py"],
                environment=docker_config["environment"],
                mem_limit=docker_config["mem_limit"],
                detach=True,
                stdin_open=True,
                stdout=True,
                stderr=True,
                remove=False,
                **({
                    "device_requests": docker_config["device_requests"]
                } if "device_requests" in docker_config else {})
            )
            
            self.running_executions[execution_id] = container
            
            # Send code to container
            container_socket = container.attach_socket(params={'stdin': 1, 'stream': 1})
            container_socket._sock.send(request.code.encode('utf-8'))
            container_socket._sock.shutdown(1)  # Close stdin
            
            # Stream output
            await self._stream_container_output(execution_id, container)
            
        except Exception as e:
            logger.error(f"Physics execution failed for {execution_id}: {e}")
            await self._mark_execution_failed(execution_id, str(e))
        finally:
            # Clean up physics context
            if execution_id in self.physics_contexts:
                await physics_service.release_physics_context(execution_id)
                del self.physics_contexts[execution_id]
                
    async def _execute_regular(self, execution_id: str, request: ExecutionRequest):
        """Execute code without physics support"""
        try:
            # Create execution script
            execution_script = self._create_execution_script(request.code)
            
            # Create and run container
            container = self.docker_client.containers.run(
                image="python-executor:latest",
                command=["python", "-u", "-c", execution_script],
                mem_limit=request.memory_limit,
                cpu_period=100000,
                cpu_quota=int(request.cpu_limit * 100000),
                detach=True,
                stdout=True,
                stderr=True,
                remove=False
            )
            
            self.running_executions[execution_id] = container
            
            # Stream output
            await self._stream_container_output(execution_id, container)
            
        except Exception as e:
            logger.error(f"Regular execution failed for {execution_id}: {e}")
            await self._mark_execution_failed(execution_id, str(e))
            
    async def _stream_container_output(self, execution_id: str, container: Container):
        """Stream container output to Redis"""
        try:
            # Wait for container to finish with timeout
            result = container.wait(timeout=30)
            
            # Get logs
            logs = container.logs(stdout=True, stderr=True).decode('utf-8')
            
            # Parse and store outputs
            for line in logs.strip().split('\n'):
                if line.strip():
                    try:
                        output_data = json.loads(line)
                        output = ExecutionOutput(**output_data)
                        await self.redis_client.lpush(
                            f"execution:{execution_id}:outputs",
                            output.model_dump_json()
                        )
                    except json.JSONDecodeError:
                        # Handle non-JSON output
                        output = ExecutionOutput(
                            output_type="stdout",
                            content={"text": line},
                            timestamp=datetime.utcnow()
                        )
                        await self.redis_client.lpush(
                            f"execution:{execution_id}:outputs",
                            output.model_dump_json()
                        )
            
            # Mark as completed
            await self.redis_client.hset(
                f"execution:{execution_id}",
                mapping={
                    "status": "completed",
                    "completed_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error streaming output for {execution_id}: {e}")
            await self._mark_execution_failed(execution_id, str(e))
        finally:
            # Clean up container
            try:
                container.remove()
            except:
                pass
            if execution_id in self.running_executions:
                del self.running_executions[execution_id]
                
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
            container = self.running_executions[execution_id]
            try:
                container.stop(timeout=5)
                container.remove()
                del self.running_executions[execution_id]
                
                # Clean up physics context if exists
                if execution_id in self.physics_contexts:
                    await physics_service.release_physics_context(execution_id)
                    del self.physics_contexts[execution_id]
                
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
        physics_contexts_count = len(self.physics_contexts)
        
        # Get physics service status
        physics_status = await physics_service.get_service_status()
        
        return {
            "queue_length": queue_length,
            "running_executions": running_count,
            "max_concurrent": self.max_concurrent_executions,
            "available_slots": self.max_concurrent_executions - running_count,
            "physics_contexts": physics_contexts_count,
            "physics_service": physics_status
        }

    def _create_execution_script(self, user_code: str) -> str:
        """Create the execution script with output capture"""
        return f"""
import sys
import json
import traceback
import io
import base64
from contextlib import redirect_stdout, redirect_stderr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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
            
        # Capture any matplotlib figures
        figures = []
        for i in plt.get_fignums():
            fig = plt.figure(i)
            img_buffer = io.BytesIO()
            fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            figures.append(img_data)
            plt.close(fig)
            
        # Output results
        stdout_content = stdout_buffer.getvalue()
        if stdout_content:
            print(json.dumps({{
                "output_type": "stdout",
                "content": {{"text": stdout_content}},
                "timestamp": "{{}}".format(__import__('datetime').datetime.utcnow().isoformat())
            }}))
            
        # Output figures
        for i, fig_data in enumerate(figures):
            print(json.dumps({{
                "output_type": "display_data",
                "content": {{
                    "data": {{
                        "image/png": fig_data
                    }},
                    "metadata": {{}}
                }},
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


# Global execution service instance (lazy initialization to avoid Docker connection on import)
execution_service = None

def get_execution_service():
    """Get or create the global execution service instance"""
    global execution_service
    if execution_service is None:
        execution_service = ExecutionService()
    return execution_service