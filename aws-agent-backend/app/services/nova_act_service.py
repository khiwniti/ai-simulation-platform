import boto3
import json
import asyncio
from typing import Dict, Any, List, Optional, Callable
import structlog
from datetime import datetime
from enum import Enum
import os

from app.config import settings

logger = structlog.get_logger(__name__)

class ActionType(Enum):
    """Types of actions Nova can execute"""
    FILE_OPERATION = "file_operation"
    API_CALL = "api_call"
    CALCULATION = "calculation"
    SIMULATION = "simulation"
    DATABASE_QUERY = "database_query"
    CODE_EXECUTION = "code_execution"
    VISUALIZATION = "visualization"

class NovaActService:
    """
    Amazon Nova Act SDK integration for autonomous action execution
    """
    
    def __init__(self):
        self.session = boto3.Session()
        self.bedrock_client = self.session.client(
            'bedrock-runtime',
            region_name=settings.AWS_REGION
        )
        
        # Action handlers registry
        self.action_handlers: Dict[ActionType, Callable] = {
            ActionType.FILE_OPERATION: self._handle_file_operation,
            ActionType.API_CALL: self._handle_api_call,
            ActionType.CALCULATION: self._handle_calculation,
            ActionType.SIMULATION: self._handle_simulation,
            ActionType.DATABASE_QUERY: self._handle_database_query,
            ActionType.CODE_EXECUTION: self._handle_code_execution,
            ActionType.VISUALIZATION: self._handle_visualization,
        }
        
    async def execute_action_plan(
        self,
        plan_description: str,
        context: Optional[Dict[str, Any]] = None,
        max_actions: int = 10
    ) -> Dict[str, Any]:
        """
        Execute a multi-step action plan using Nova
        """
        try:
            # Generate action plan using Nova
            action_plan = await self._generate_action_plan(plan_description, context)
            
            if not action_plan["success"]:
                return action_plan
            
            # Execute each action in the plan
            execution_results = []
            for i, action in enumerate(action_plan["actions"][:max_actions]):
                logger.info(f"Executing action {i+1}/{len(action_plan['actions'])}", action=action)
                
                result = await self._execute_single_action(action)
                execution_results.append(result)
                
                # If action failed and is critical, stop execution
                if not result["success"] and action.get("critical", False):
                    logger.error("Critical action failed, stopping execution", action=action)
                    break
            
            return {
                "success": True,
                "plan_description": plan_description,
                "action_plan": action_plan,
                "execution_results": execution_results,
                "completed_actions": len(execution_results),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Action plan execution failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _generate_action_plan(
        self,
        plan_description: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a structured action plan using Nova
        """
        prompt = f"""You are Nova, an autonomous action execution AI. Given the following engineering task, create a detailed action plan.

Task: {plan_description}

Context: {json.dumps(context, indent=2) if context else 'No additional context provided'}

Create a JSON action plan with the following structure:
{{
    "actions": [
        {{
            "id": "unique_action_id",
            "type": "file_operation|api_call|calculation|simulation|database_query|code_execution|visualization",
            "description": "What this action does",
            "parameters": {{}},
            "critical": true/false,
            "dependencies": ["action_ids_that_must_complete_first"],
            "expected_duration": "estimated_seconds"
        }}
    ],
    "total_estimated_time": "seconds",
    "complexity": "low|medium|high",
    "risk_level": "low|medium|high"
}}

Available action types:
- file_operation: Read, write, or manipulate files
- api_call: Make external API calls
- calculation: Perform mathematical calculations
- simulation: Run physics or engineering simulations
- database_query: Query or update database
- code_execution: Execute Python code
- visualization: Create charts, graphs, or 3D visualizations

Provide only the JSON response, no additional text."""

        try:
            response = await self._invoke_nova(prompt, max_tokens=2000)
            
            if not response["success"]:
                return response
            
            # Parse the action plan JSON
            action_plan_json = json.loads(response["text"])
            
            return {
                "success": True,
                "actions": action_plan_json["actions"],
                "metadata": {
                    "total_estimated_time": action_plan_json.get("total_estimated_time"),
                    "complexity": action_plan_json.get("complexity"),
                    "risk_level": action_plan_json.get("risk_level")
                },
                "timestamp": datetime.now().isoformat()
            }
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse action plan JSON", error=str(e))
            return {
                "success": False,
                "error": f"Invalid JSON response: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error("Action plan generation failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_single_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single action from the plan
        """
        action_type = ActionType(action["type"])
        handler = self.action_handlers.get(action_type)
        
        if not handler:
            return {
                "success": False,
                "error": f"No handler for action type: {action_type}",
                "action_id": action["id"],
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            result = await handler(action)
            return {
                "success": True,
                "action_id": action["id"],
                "type": action["type"],
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error("Action execution failed", action_id=action["id"], error=str(e))
            return {
                "success": False,
                "error": str(e),
                "action_id": action["id"],
                "type": action["type"],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _invoke_nova(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.1
    ) -> Dict[str, Any]:
        """
        Invoke Nova model through Bedrock
        """
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=settings.NOVA_MODEL_ID or settings.BEDROCK_MODEL_ID,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(body)
            )
            
            response_body = json.loads(response['body'].read())
            text = response_body['content'][0]['text']
            
            return {
                "success": True,
                "text": text,
                "usage": response_body.get('usage', {}),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Nova invocation failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    # Action Handlers
    
    async def _handle_file_operation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations (read, write, create, delete)"""
        params = action.get("parameters", {})
        operation = params.get("operation")  # read, write, create, delete
        file_path = params.get("file_path")
        content = params.get("content", "")
        
        try:
            if operation == "read":
                with open(file_path, 'r') as f:
                    content = f.read()
                return {"operation": "read", "file_path": file_path, "content": content}
            
            elif operation == "write":
                with open(file_path, 'w') as f:
                    f.write(content)
                return {"operation": "write", "file_path": file_path, "bytes_written": len(content)}
            
            elif operation == "create":
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(content)
                return {"operation": "create", "file_path": file_path, "created": True}
            
            elif operation == "delete":
                os.remove(file_path)
                return {"operation": "delete", "file_path": file_path, "deleted": True}
            
            else:
                raise ValueError(f"Unknown file operation: {operation}")
                
        except Exception as e:
            raise Exception(f"File operation failed: {str(e)}")
    
    async def _handle_api_call(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle external API calls"""
        import aiohttp
        
        params = action.get("parameters", {})
        url = params.get("url")
        method = params.get("method", "GET").upper()
        headers = params.get("headers", {})
        data = params.get("data")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if data else None
                ) as response:
                    result = await response.text()
                    return {
                        "url": url,
                        "method": method,
                        "status_code": response.status,
                        "response": result
                    }
        except Exception as e:
            raise Exception(f"API call failed: {str(e)}")
    
    async def _handle_calculation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle mathematical calculations"""
        params = action.get("parameters", {})
        expression = params.get("expression")
        variables = params.get("variables", {})
        
        try:
            # Use numpy and scipy for calculations
            import numpy as np
            import scipy as sp
            from scipy import optimize, integrate
            import sympy
            
            # Create safe evaluation environment
            safe_dict = {
                "__builtins__": {},
                "np": np,
                "scipy": sp,
                "optimize": optimize,
                "integrate": integrate,
                "sympy": sympy,
                "sin": np.sin,
                "cos": np.cos,
                "tan": np.tan,
                "exp": np.exp,
                "log": np.log,
                "sqrt": np.sqrt,
                "pi": np.pi,
                "e": np.e,
                **variables
            }
            
            result = eval(expression, safe_dict)
            
            return {
                "expression": expression,
                "result": float(result) if isinstance(result, (int, float, np.number)) else str(result),
                "variables": variables
            }
        except Exception as e:
            raise Exception(f"Calculation failed: {str(e)}")
    
    async def _handle_simulation(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle physics simulations"""
        params = action.get("parameters", {})
        simulation_type = params.get("type")  # "structural", "thermal", "fluid", etc.
        
        # This would integrate with the existing physics engine
        # For now, return a mock result
        return {
            "simulation_type": simulation_type,
            "status": "completed",
            "results": {
                "max_stress": 125.5,
                "safety_factor": 2.1,
                "displacement": 0.003
            }
        }
    
    async def _handle_database_query(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle database operations"""
        params = action.get("parameters", {})
        query_type = params.get("type")  # "select", "insert", "update", "delete"
        
        # This would integrate with the database
        # For now, return a mock result
        return {
            "query_type": query_type,
            "rows_affected": 1,
            "status": "success"
        }
    
    async def _handle_code_execution(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Python code execution"""
        params = action.get("parameters", {})
        code = params.get("code")
        
        try:
            # Create safe execution environment
            safe_globals = {
                "__builtins__": {
                    "print": print,
                    "len": len,
                    "range": range,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                },
                "numpy": __import__("numpy"),
                "math": __import__("math"),
            }
            
            # Capture output
            from io import StringIO
            import sys
            
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                exec(code, safe_globals)
                output = captured_output.getvalue()
            finally:
                sys.stdout = old_stdout
            
            return {
                "code": code,
                "output": output,
                "status": "executed"
            }
        except Exception as e:
            raise Exception(f"Code execution failed: {str(e)}")
    
    async def _handle_visualization(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Handle visualization creation"""
        params = action.get("parameters", {})
        viz_type = params.get("type")  # "plot", "3d", "chart"
        data = params.get("data", [])
        
        # This would integrate with plotting libraries
        # For now, return a mock result
        return {
            "visualization_type": viz_type,
            "data_points": len(data),
            "file_path": "/tmp/visualization.png",
            "status": "created"
        }