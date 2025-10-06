import asyncio
from typing import Dict, Any, List, Optional, Set
from enum import Enum
import uuid
from datetime import datetime
import structlog

from app.services.bedrock_service import BedrockService
from app.services.nova_act_service import NovaActService
from app.agents.physics_agent import PhysicsAgent
from app.agents.design_agent import DesignAgent
from app.agents.optimization_agent import OptimizationAgent
from app.agents.materials_agent import MaterialsAgent
from app.agents.project_manager_agent import ProjectManagerAgent

logger = structlog.get_logger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class AgentOrchestrator:
    """
    AWS Bedrock AgentCore-powered orchestrator for autonomous AI engineering team
    """
    
    def __init__(self, bedrock_service: BedrockService):
        self.bedrock_service = bedrock_service
        self.nova_service = NovaActService()
        
        # Initialize specialized agents
        self.agents = {
            "physics": PhysicsAgent(bedrock_service, self.nova_service),
            "design": DesignAgent(bedrock_service, self.nova_service),
            "optimization": OptimizationAgent(bedrock_service, self.nova_service),
            "materials": MaterialsAgent(bedrock_service, self.nova_service),
            "project_manager": ProjectManagerAgent(bedrock_service, self.nova_service)
        }
        
        # Task management
        self.active_tasks = {}
        self.task_dependencies = {}
        self.agent_workload = {agent_id: 0 for agent_id in self.agents.keys()}
        
    async def execute_engineering_project(
        self,
        project_description: str,
        requirements: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute a complete engineering project using autonomous AI team
        """
        project_id = str(uuid.uuid4())
        logger.info("Starting autonomous engineering project", project_id=project_id)
        
        try:
            # 1. Project Analysis & Planning (Project Manager Agent)
            planning_result = await self._plan_project(
                project_id, project_description, requirements, constraints
            )
            
            if not planning_result["success"]:
                return planning_result
            
            # 2. Task Decomposition & Assignment
            task_plan = planning_result["task_plan"]
            execution_results = await self._execute_task_plan(project_id, task_plan)
            
            # 3. Results Integration & Final Report
            final_report = await self._generate_final_report(
                project_id, project_description, execution_results
            )
            
            return {
                "success": True,
                "project_id": project_id,
                "project_description": project_description,
                "planning": planning_result,
                "execution": execution_results,
                "final_report": final_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Project execution failed", project_id=project_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "project_id": project_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _plan_project(
        self,
        project_id: str,
        description: str,
        requirements: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use Project Manager Agent to create comprehensive project plan
        """
        try:
            project_manager = self.agents["project_manager"]
            
            planning_context = {
                "project_id": project_id,
                "description": description,
                "requirements": requirements or {},
                "constraints": constraints or {},
                "available_agents": list(self.agents.keys()),
                "agent_capabilities": {
                    agent_id: agent.get_capabilities() 
                    for agent_id, agent in self.agents.items()
                }
            }
            
            plan = await project_manager.create_project_plan(planning_context)
            
            return {
                "success": True,
                "task_plan": plan,
                "planning_agent": "project_manager",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Project planning failed", project_id=project_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_task_plan(
        self, 
        project_id: str, 
        task_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the project task plan using specialized agents
        """
        tasks = task_plan.get("tasks", [])
        execution_results = []
        
        try:
            # Create dependency graph
            dependency_graph = self._build_dependency_graph(tasks)
            
            # Execute tasks in dependency order
            while dependency_graph:
                # Find tasks with no dependencies (ready to execute)
                ready_tasks = [
                    task for task in dependency_graph 
                    if not dependency_graph[task["id"]]["dependencies"]
                ]
                
                if not ready_tasks:
                    # Check for circular dependencies
                    logger.error("Circular dependency detected in task plan", project_id=project_id)
                    break
                
                # Execute ready tasks concurrently
                task_results = await asyncio.gather(*[
                    self._execute_single_task(project_id, task)
                    for task in ready_tasks
                ])
                
                execution_results.extend(task_results)
                
                # Remove completed tasks from dependency graph
                completed_task_ids = {
                    result["task_id"] for result in task_results 
                    if result["success"]
                }
                
                # Update dependency graph
                dependency_graph = {
                    task_id: {
                        "task": task_data["task"],
                        "dependencies": [
                            dep for dep in task_data["dependencies"]
                            if dep not in completed_task_ids
                        ]
                    }
                    for task_id, task_data in dependency_graph.items()
                    if task_id not in completed_task_ids
                }
            
            return {
                "success": True,
                "project_id": project_id,
                "executed_tasks": len(execution_results),
                "task_results": execution_results,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Task plan execution failed", project_id=project_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "project_id": project_id,
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_single_task(
        self, 
        project_id: str, 
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a single task using the appropriate specialized agent
        """
        task_id = task["id"]
        agent_type = task["agent_type"]
        
        try:
            logger.info("Executing task", project_id=project_id, task_id=task_id, agent=agent_type)
            
            if agent_type not in self.agents:
                raise ValueError(f"Unknown agent type: {agent_type}")
            
            agent = self.agents[agent_type]
            
            # Track agent workload
            self.agent_workload[agent_type] += 1
            
            try:
                # Execute task with appropriate agent
                result = await agent.execute_task(task)
                
                return {
                    "success": True,
                    "task_id": task_id,
                    "agent_type": agent_type,
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }
                
            finally:
                self.agent_workload[agent_type] -= 1
                
        except Exception as e:
            logger.error("Task execution failed", 
                        project_id=project_id, task_id=task_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "task_id": task_id,
                "agent_type": agent_type,
                "timestamp": datetime.now().isoformat()
            }
    
    def _build_dependency_graph(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Build task dependency graph for execution ordering
        """
        dependency_graph = {}
        
        for task in tasks:
            task_id = task["id"]
            dependencies = task.get("dependencies", [])
            
            dependency_graph[task_id] = {
                "task": task,
                "dependencies": dependencies.copy()
            }
        
        return dependency_graph
    
    async def _generate_final_report(
        self,
        project_id: str,
        project_description: str,
        execution_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive final engineering report
        """
        try:
            # Use Project Manager Agent to compile final report
            project_manager = self.agents["project_manager"]
            
            report_context = {
                "project_id": project_id,
                "project_description": project_description,
                "execution_results": execution_results,
                "agent_contributions": {
                    agent_type: [
                        result for result in execution_results["task_results"]
                        if result.get("agent_type") == agent_type
                    ]
                    for agent_type in self.agents.keys()
                }
            }
            
            final_report = await project_manager.generate_final_report(report_context)
            
            return {
                "success": True,
                "report": final_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Final report generation failed", project_id=project_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """
        Get current status of all agents
        """
        return {
            "agents": {
                agent_id: {
                    "status": "active",
                    "current_workload": self.agent_workload[agent_id],
                    "capabilities": agent.get_capabilities()
                }
                for agent_id, agent in self.agents.items()
            },
            "active_tasks": len(self.active_tasks),
            "timestamp": datetime.now().isoformat()
        }
    
    async def interrupt_project(self, project_id: str, reason: str = "User request") -> Dict[str, Any]:
        """
        Interrupt and cancel an active project
        """
        try:
            # Cancel all tasks for this project
            cancelled_tasks = []
            for task_id, task_info in list(self.active_tasks.items()):
                if task_info.get("project_id") == project_id:
                    self.active_tasks[task_id]["status"] = TaskStatus.CANCELLED
                    cancelled_tasks.append(task_id)
            
            logger.info("Project interrupted", 
                       project_id=project_id, 
                       reason=reason, 
                       cancelled_tasks=len(cancelled_tasks))
            
            return {
                "success": True,
                "project_id": project_id,
                "reason": reason,
                "cancelled_tasks": cancelled_tasks,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error("Project interruption failed", project_id=project_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def create_autonomous_bridge_design(
        self,
        span_length: float,
        load_requirements: Dict[str, Any],
        material_constraints: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Demonstration scenario: Autonomous bridge design
        """
        project_description = f"""
        Design a pedestrian bridge with the following specifications:
        - Span length: {span_length} meters
        - Load requirements: {load_requirements}
        - Material constraints: {material_constraints or 'Standard engineering materials'}
        
        The design should include:
        1. Structural analysis and calculations
        2. Material selection and optimization
        3. 3D visualization and CAD model
        4. Safety factor verification
        5. Cost optimization
        6. Comprehensive engineering documentation
        """
        
        requirements = {
            "span_length": span_length,
            "load_requirements": load_requirements,
            "material_constraints": material_constraints,
            "safety_factor_minimum": 2.0,
            "design_standards": ["AISC", "AASHTO"],
            "deliverables": [
                "structural_calculations",
                "cad_model", 
                "material_specifications",
                "cost_analysis",
                "engineering_drawings"
            ]
        }
        
        return await self.execute_engineering_project(
            project_description,
            requirements=requirements,
            constraints={"budget": "optimize", "timeline": "standard"}
        )