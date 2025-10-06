from typing import Dict, Any, List
import json
import uuid
from datetime import datetime, timedelta

from app.agents.base_agent import BaseAgent

class ProjectManagerAgent(BaseAgent):
    """
    Specialized agent for project management and coordination
    """
    
    def get_capabilities(self) -> List[str]:
        return [
            "project_planning",
            "task_decomposition", 
            "resource_allocation",
            "timeline_management",
            "risk_assessment",
            "quality_assurance",
            "progress_monitoring",
            "report_generation"
        ]
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute project management tasks
        """
        task_type = task.get("type")
        parameters = task.get("parameters", {})
        
        self.log_activity("project_management_task_started", {"task_type": task_type})
        
        try:
            if task_type == "project_planning":
                result = await self.create_project_plan(parameters)
            elif task_type == "progress_monitoring":
                result = await self._monitor_project_progress(parameters)
            elif task_type == "risk_assessment":
                result = await self._assess_project_risks(parameters)
            elif task_type == "quality_review":
                result = await self._perform_quality_review(parameters)
            elif task_type == "final_report":
                result = await self.generate_final_report(parameters)
            else:
                # Use Nova for general project management tasks
                result = await self._execute_general_pm_task(task)
            
            self.log_activity("project_management_task_completed", {"task_type": task_type, "success": True})
            return result
            
        except Exception as e:
            self.log_activity("project_management_task_failed", {"task_type": task_type, "error": str(e)})
            raise
    
    async def create_project_plan(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive project plan with task decomposition
        """
        project_description = context.get("description", "")
        requirements = context.get("requirements", {})
        constraints = context.get("constraints", {})
        available_agents = context.get("available_agents", [])
        
        # Use Bedrock to analyze project and create plan
        planning_prompt = f"""
        You are an expert AI project manager for engineering projects. Create a detailed project plan.

        Project: {project_description}
        Requirements: {json.dumps(requirements, indent=2)}
        Constraints: {json.dumps(constraints, indent=2)}
        Available AI Agents: {available_agents}

        Create a comprehensive project plan with:
        1. Project breakdown structure
        2. Task assignments to appropriate agents
        3. Dependencies and sequencing
        4. Timeline estimates
        5. Risk assessment
        6. Quality checkpoints
        7. Deliverables mapping

        Format as structured project plan.
        """
        
        planning_result = await self.bedrock_service.invoke_model(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            prompt=planning_prompt,
            max_tokens=2500,
            temperature=0.3
        )
        
        # Generate structured task plan
        project_plan = {
            "project_id": str(uuid.uuid4()),
            "project_name": self._extract_project_name(project_description),
            "start_date": datetime.now().isoformat(),
            "estimated_duration": self._estimate_project_duration(requirements),
            "tasks": await self._decompose_into_tasks(project_description, requirements, available_agents),
            "timeline": await self._create_project_timeline(requirements),
            "resource_allocation": await self._allocate_resources(available_agents, requirements),
            "risk_register": await self._create_risk_register(project_description, requirements),
            "quality_gates": await self._define_quality_gates(requirements),
            "deliverables": await self._define_deliverables(requirements),
            "ai_analysis": planning_result
        }
        
        return project_plan
    
    async def generate_final_report(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive final engineering report
        """
        project_id = context.get("project_id", "")
        project_description = context.get("project_description", "")
        execution_results = context.get("execution_results", {})
        agent_contributions = context.get("agent_contributions", {})
        
        # Use Bedrock to generate comprehensive report
        report_prompt = f"""
        Generate a comprehensive final engineering report for this autonomous AI project:

        Project: {project_description}
        Project ID: {project_id}
        Execution Results: {json.dumps(execution_results, indent=2)[:2000]}
        Agent Contributions: {json.dumps(agent_contributions, indent=2)[:1500]}

        Create a professional engineering report including:
        1. Executive Summary
        2. Project Overview and Objectives
        3. Technical Approach and Methodology
        4. Results and Findings from each AI agent
        5. Design Recommendations
        6. Performance Analysis
        7. Risk Assessment and Mitigation
        8. Conclusions and Future Work
        9. Technical Appendices

        Format as a complete engineering document.
        """
        
        report_result = await self.bedrock_service.invoke_model(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0", 
            prompt=report_prompt,
            max_tokens=3000,
            temperature=0.2
        )
        
        final_report = {
            "report_id": str(uuid.uuid4()),
            "project_id": project_id,
            "generated_date": datetime.now().isoformat(),
            "report_type": "final_engineering_report",
            "executive_summary": await self._generate_executive_summary(execution_results),
            "technical_sections": {
                "physics_analysis": self._extract_agent_results(agent_contributions, "physics"),
                "design_specifications": self._extract_agent_results(agent_contributions, "design"),
                "optimization_results": self._extract_agent_results(agent_contributions, "optimization"),
                "materials_analysis": self._extract_agent_results(agent_contributions, "materials")
            },
            "performance_metrics": await self._calculate_project_metrics(execution_results),
            "recommendations": await self._generate_recommendations(agent_contributions),
            "appendices": await self._generate_appendices(execution_results),
            "ai_generated_report": report_result,
            "document_metadata": {
                "total_pages": 45,
                "word_count": 12500,
                "figures": 15,
                "tables": 8,
                "references": 25
            }
        }
        
        return final_report
    
    # Helper methods
    
    def _extract_project_name(self, description: str) -> str:
        """Extract project name from description"""
        # Simple extraction - in practice would use NLP
        if "bridge" in description.lower():
            return "Autonomous Bridge Design Project"
        elif "building" in description.lower():
            return "Autonomous Building Design Project"
        else:
            return "Autonomous Engineering Design Project"
    
    def _estimate_project_duration(self, requirements: Dict[str, Any]) -> str:
        """Estimate project duration based on requirements complexity"""
        complexity_indicators = len(requirements.get("deliverables", []))
        if complexity_indicators <= 3:
            return "2-3 days"
        elif complexity_indicators <= 6:
            return "5-7 days"
        else:
            return "10-14 days"
    
    async def _decompose_into_tasks(self, description: str, requirements: Dict, agents: List[str]) -> List[Dict[str, Any]]:
        """Decompose project into specific tasks for agents"""
        base_tasks = [
            {
                "id": "task_001",
                "name": "Requirements Analysis",
                "agent_type": "project_manager", 
                "description": "Analyze and validate project requirements",
                "dependencies": [],
                "estimated_duration": "2 hours",
                "priority": "high"
            },
            {
                "id": "task_002",
                "name": "Initial Design Concept",
                "agent_type": "design",
                "description": "Create initial design concept and specifications",
                "dependencies": ["task_001"],
                "estimated_duration": "4 hours",
                "priority": "high"
            },
            {
                "id": "task_003", 
                "name": "Structural Analysis",
                "agent_type": "physics",
                "description": "Perform structural analysis and safety calculations",
                "dependencies": ["task_002"],
                "estimated_duration": "6 hours",
                "priority": "high"
            },
            {
                "id": "task_004",
                "name": "Material Selection",
                "agent_type": "materials",
                "description": "Select optimal materials for the design",
                "dependencies": ["task_003"],
                "estimated_duration": "3 hours", 
                "priority": "medium"
            },
            {
                "id": "task_005",
                "name": "Design Optimization",
                "agent_type": "optimization",
                "description": "Optimize design for performance and cost",
                "dependencies": ["task_003", "task_004"],
                "estimated_duration": "5 hours",
                "priority": "medium"
            },
            {
                "id": "task_006",
                "name": "Final Documentation",
                "agent_type": "project_manager",
                "description": "Generate comprehensive project documentation",
                "dependencies": ["task_005"],
                "estimated_duration": "3 hours",
                "priority": "high"
            }
        ]
        
        return base_tasks
    
    async def _execute_general_pm_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute general project management tasks using Nova"""
        return await self.nova_service.execute_action_plan(
            task.get("description", "General project management task"),
            context=task.get("parameters", {})
        )
    
    # Mock helper methods for demonstration
    async def _create_project_timeline(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        return {"phases": ["planning", "design", "analysis", "optimization", "documentation"], "total_duration": "7 days"}
    
    async def _allocate_resources(self, agents: List[str], requirements: Dict[str, Any]) -> Dict[str, Any]:
        return {"agents_allocated": len(agents), "resource_utilization": "optimal"}
    
    async def _create_risk_register(self, description: str, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"risk": "technical_complexity", "probability": "medium", "impact": "high"}]
    
    async def _define_quality_gates(self, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [{"gate": "design_review", "criteria": "completeness_check"}]
    
    async def _define_deliverables(self, requirements: Dict[str, Any]) -> List[str]:
        return ["technical_drawings", "analysis_report", "material_specs"]
    
    async def _generate_executive_summary(self, results: Dict[str, Any]) -> str:
        return "Executive summary of autonomous engineering project results."
    
    def _extract_agent_results(self, contributions: Dict[str, Any], agent_type: str) -> Dict[str, Any]:
        return contributions.get(agent_type, {})
    
    async def _calculate_project_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        return {"completion_time": "5 hours", "quality_score": 9.2}
    
    async def _generate_recommendations(self, contributions: Dict[str, Any]) -> List[str]:
        return ["Implement design optimization suggestions", "Consider alternative materials"]
    
    async def _generate_appendices(self, results: Dict[str, Any]) -> Dict[str, Any]:
        return {"calculations": "detailed_calculations.pdf", "drawings": "technical_drawings.zip"}