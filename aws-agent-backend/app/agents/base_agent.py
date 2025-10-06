from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import structlog
from datetime import datetime

logger = structlog.get_logger(__name__)

class BaseAgent(ABC):
    """
    Base class for all specialized engineering agents
    """
    
    def __init__(self, bedrock_service, nova_service):
        self.bedrock_service = bedrock_service
        self.nova_service = nova_service
        self.agent_id = self.__class__.__name__.lower().replace('agent', '')
        
    @abstractmethod
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific task assigned to this agent
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Return list of capabilities this agent provides
        """
        pass
    
    async def analyze_problem(self, problem_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze a problem using this agent's domain expertise
        """
        prompt = f"""You are a specialized {self.agent_id} AI agent with expertise in {', '.join(self.get_capabilities())}.

Problem: {problem_description}

Context: {context or 'No additional context provided'}

Provide a detailed analysis from your domain perspective including:
1. Key considerations specific to your expertise area
2. Potential challenges and risks
3. Recommended approach
4. Required resources or data
5. Success criteria

Format your response as a structured analysis."""

        return await self.bedrock_service.invoke_model(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            prompt=prompt,
            max_tokens=1500,
            temperature=0.3
        )
    
    async def generate_solution(self, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a solution based on requirements
        """
        prompt = f"""You are a specialized {self.agent_id} AI agent. Generate a detailed solution for the following requirements:

Requirements: {requirements}

Your expertise areas: {', '.join(self.get_capabilities())}

Provide a comprehensive solution including:
1. Technical specifications
2. Implementation steps
3. Tools and methods required
4. Quality assurance measures
5. Deliverables

Format as a structured solution document."""

        return await self.bedrock_service.invoke_model(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            prompt=prompt,
            max_tokens=2000,
            temperature=0.4
        )
    
    async def collaborate_with_agent(self, other_agent_id: str, task_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Collaborate with another agent on a shared task
        """
        prompt = f"""You are the {self.agent_id} agent collaborating with the {other_agent_id} agent.

Task Context: {task_context}

Your capabilities: {', '.join(self.get_capabilities())}

How can you contribute to this collaborative task? Provide:
1. Your specific contributions
2. Information you need from the other agent
3. Coordination requirements
4. Shared deliverables

Format as a collaboration plan."""

        return await self.bedrock_service.invoke_model(
            model_id="anthropic.claude-3-sonnet-20240229-v1:0",
            prompt=prompt,
            max_tokens=1000,
            temperature=0.3
        )
    
    def log_activity(self, activity: str, details: Dict[str, Any] = None):
        """
        Log agent activity for monitoring and debugging
        """
        logger.info(f"{self.agent_id} agent activity", 
                   activity=activity, 
                   details=details or {},
                   timestamp=datetime.now().isoformat())