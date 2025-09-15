"""
Base AI Agent class and interface definitions.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Enumeration of agent capabilities."""
    PHYSICS_SIMULATION = "physics_simulation"
    PHYSICS_DEBUGGING = "physics_debugging"
    VISUALIZATION_3D = "visualization_3d"
    VISUALIZATION_PLOTS = "visualization_plots"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    GPU_OPTIMIZATION = "gpu_optimization"
    CODE_DEBUGGING = "code_debugging"
    ERROR_ANALYSIS = "error_analysis"
    PARAMETER_TUNING = "parameter_tuning"
    EQUATION_ASSISTANCE = "equation_assistance"


@dataclass
class AgentResponse:
    """Response from an AI agent."""
    agent_id: str
    agent_type: str
    response: str
    confidence_score: float
    capabilities_used: List[AgentCapability] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    suggestions: List[str] = field(default_factory=list)
    code_snippets: List[str] = field(default_factory=list)
    response_time: float = 0.0
    tokens_used: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class AgentContext:
    """Context shared between agents."""
    session_id: UUID
    notebook_id: Optional[UUID] = None
    cell_id: Optional[UUID] = None
    current_code: Optional[str] = None
    execution_state: Dict[str, Any] = field(default_factory=dict)
    physics_parameters: Dict[str, Any] = field(default_factory=dict)
    gpu_resources: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[Dict[str, Any]] = field(default_factory=list)
    active_agents: Set[str] = field(default_factory=set)
    shared_variables: Dict[str, Any] = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents.
    
    Defines the interface and common functionality for specialized AI agents
    that provide assistance for different aspects of simulation development.
    """
    
    def __init__(self, agent_id: Optional[str] = None):
        self.agent_id = agent_id or str(uuid4())
        self.agent_type = self.__class__.__name__.lower().replace('agent', '')
        self.capabilities: Set[AgentCapability] = set()
        self.is_active = False
        self.context: Optional[AgentContext] = None
        self.performance_metrics = {
            'total_queries': 0,
            'average_response_time': 0.0,
            'average_confidence': 0.0,
            'success_rate': 0.0
        }
        
    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name of the agent."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of the agent's purpose and capabilities."""
        pass
        
    @abstractmethod
    async def process_query(
        self, 
        query: str, 
        context: AgentContext
    ) -> AgentResponse:
        """
        Process a query and return a response.
        
        Args:
            query: The user's query or request
            context: Current context including notebook state, code, etc.
            
        Returns:
            AgentResponse with the agent's response and metadata
        """
        pass
        
    @abstractmethod
    def can_handle_query(self, query: str, context: AgentContext) -> float:
        """
        Determine if this agent can handle the given query.
        
        Args:
            query: The user's query
            context: Current context
            
        Returns:
            Confidence score (0.0 to 1.0) indicating ability to handle query
        """
        pass
        
    async def initialize(self, context: AgentContext) -> None:
        """
        Initialize the agent with context.
        
        Args:
            context: The agent context for this session
        """
        self.context = context
        self.is_active = True
        logger.info(f"Agent {self.agent_id} ({self.agent_type}) initialized")
        
    async def shutdown(self) -> None:
        """Shutdown the agent and cleanup resources."""
        self.is_active = False
        self.context = None
        logger.info(f"Agent {self.agent_id} ({self.agent_type}) shutdown")
        
    def update_context(self, context: AgentContext) -> None:
        """Update the agent's context."""
        self.context = context
        
    def get_capabilities(self) -> Set[AgentCapability]:
        """Get the agent's capabilities."""
        return self.capabilities.copy()
        
    def has_capability(self, capability: AgentCapability) -> bool:
        """Check if agent has a specific capability."""
        return capability in self.capabilities
        
    def update_performance_metrics(self, response: AgentResponse) -> None:
        """Update performance metrics based on response."""
        self.performance_metrics['total_queries'] += 1
        
        # Update average response time
        total_queries = self.performance_metrics['total_queries']
        current_avg_time = self.performance_metrics['average_response_time']
        new_avg_time = ((current_avg_time * (total_queries - 1)) + response.response_time) / total_queries
        self.performance_metrics['average_response_time'] = new_avg_time
        
        # Update average confidence
        current_avg_conf = self.performance_metrics['average_confidence']
        new_avg_conf = ((current_avg_conf * (total_queries - 1)) + response.confidence_score) / total_queries
        self.performance_metrics['average_confidence'] = new_avg_conf
        
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics."""
        return {
            'agent_id': self.agent_id,
            'agent_type': self.agent_type,
            'name': self.name,
            'is_active': self.is_active,
            'capabilities': [cap.value for cap in self.capabilities],
            'performance_metrics': self.performance_metrics.copy(),
            'has_context': self.context is not None
        }


class AgentRegistry:
    """Registry for managing available agents."""
    
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_types: Dict[str, type] = {}
        
    def register_agent_type(self, agent_type: str, agent_class: type) -> None:
        """Register an agent type."""
        self._agent_types[agent_type] = agent_class
        logger.info(f"Registered agent type: {agent_type}")
        
    def create_agent(self, agent_type: str, agent_id: Optional[str] = None) -> BaseAgent:
        """Create an agent instance."""
        if agent_type not in self._agent_types:
            raise ValueError(f"Unknown agent type: {agent_type}")
            
        agent_class = self._agent_types[agent_type]
        agent = agent_class(agent_id=agent_id)
        self._agents[agent.agent_id] = agent
        
        logger.info(f"Created agent {agent.agent_id} of type {agent_type}")
        return agent
        
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)
        
    def remove_agent(self, agent_id: str) -> bool:
        """Remove an agent from registry."""
        if agent_id in self._agents:
            agent = self._agents.pop(agent_id)
            asyncio.create_task(agent.shutdown())
            logger.info(f"Removed agent {agent_id}")
            return True
        return False
        
    def get_agents_by_capability(self, capability: AgentCapability) -> List[BaseAgent]:
        """Get all agents with a specific capability."""
        return [
            agent for agent in self._agents.values()
            if agent.has_capability(capability)
        ]
        
    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self._agents.values())
        
    def get_agent_types(self) -> List[str]:
        """Get all registered agent types."""
        return list(self._agent_types.keys())


# Global agent registry instance
agent_registry = AgentRegistry()