"""
AI Agent Orchestrator for managing multiple agents and their interactions.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Set, Any, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import json

from .base import (
    BaseAgent, AgentContext, AgentResponse, AgentCapability, 
    agent_registry
)

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages in the agent communication protocol."""
    QUERY = "query"
    RESPONSE = "response"
    COORDINATION = "coordination"
    CONTEXT_UPDATE = "context_update"
    AGENT_STATUS = "agent_status"
    ERROR = "error"


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass
class AgentMessage:
    """Message in the agent communication protocol."""
    id: str = field(default_factory=lambda: str(uuid4()))
    type: MessageType = MessageType.QUERY
    priority: MessagePriority = MessagePriority.NORMAL
    sender_id: str = ""
    recipient_id: Optional[str] = None  # None for broadcast
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    session_id: Optional[UUID] = None
    requires_response: bool = False
    correlation_id: Optional[str] = None


@dataclass
class CoordinationRequest:
    """Request for agent coordination."""
    query: str
    context: AgentContext
    required_capabilities: Set[AgentCapability]
    preferred_agents: List[str] = field(default_factory=list)
    max_agents: int = 3
    timeout_seconds: int = 30


@dataclass
class CoordinationResult:
    """Result of agent coordination."""
    primary_response: AgentResponse
    supporting_responses: List[AgentResponse] = field(default_factory=list)
    consensus_score: float = 0.0
    conflicts: List[Dict[str, Any]] = field(default_factory=list)
    coordination_time: float = 0.0


class AgentOrchestrator:
    """
    Orchestrates multiple AI agents and manages their interactions.
    
    Handles agent selection, coordination, conflict resolution, and context sharing
    for complex simulation tasks that require multiple specialized agents.
    """
    
    def __init__(self):
        self.active_sessions: Dict[UUID, AgentContext] = {}
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.agent_pools: Dict[str, List[BaseAgent]] = {}
        self.coordination_history: List[CoordinationResult] = []
        self.is_running = False
        self._message_processor_task: Optional[asyncio.Task] = None
        
        # Performance metrics
        self.metrics = {
            'total_coordinations': 0,
            'successful_coordinations': 0,
            'average_coordination_time': 0.0,
            'agent_utilization': {},
            'conflict_resolution_rate': 0.0
        }
        
    async def start(self) -> None:
        """Start the orchestrator and message processing."""
        if self.is_running:
            return
            
        self.is_running = True
        self._message_processor_task = asyncio.create_task(self._process_messages())
        logger.info("Agent Orchestrator started")
        
    async def stop(self) -> None:
        """Stop the orchestrator and cleanup."""
        self.is_running = False
        
        if self._message_processor_task:
            self._message_processor_task.cancel()
            try:
                await self._message_processor_task
            except asyncio.CancelledError:
                pass
                
        # Shutdown all active agents
        for context in self.active_sessions.values():
            for agent_id in context.active_agents:
                agent = agent_registry.get_agent(agent_id)
                if agent:
                    await agent.shutdown()
                    
        self.active_sessions.clear()
        logger.info("Agent Orchestrator stopped")
        
    async def create_session(self, session_id: UUID, **context_kwargs) -> AgentContext:
        """Create a new agent session with context."""
        context = AgentContext(session_id=session_id, **context_kwargs)
        self.active_sessions[session_id] = context
        
        logger.info(f"Created agent session {session_id}")
        return context
        
    async def end_session(self, session_id: UUID) -> None:
        """End an agent session and cleanup resources."""
        if session_id not in self.active_sessions:
            return
            
        context = self.active_sessions[session_id]
        
        # Shutdown session agents
        for agent_id in context.active_agents:
            agent = agent_registry.get_agent(agent_id)
            if agent:
                await agent.shutdown()
                agent_registry.remove_agent(agent_id)
                
        del self.active_sessions[session_id]
        logger.info(f"Ended agent session {session_id}")
        
    async def coordinate_agents(self, request: CoordinationRequest) -> CoordinationResult:
        """
        Coordinate multiple agents to handle a complex query.
        
        Args:
            request: Coordination request with query and requirements
            
        Returns:
            CoordinationResult with responses and coordination metadata
        """
        start_time = datetime.utcnow()
        
        try:
            # Select appropriate agents
            selected_agents = await self._select_agents(request)
            
            if not selected_agents:
                raise ValueError("No suitable agents found for the query")
                
            # Process query with selected agents
            responses = await self._process_with_agents(
                selected_agents, request.query, request.context
            )
            
            # Handle complete or partial failure
            if not responses:
                return await self._handle_coordination_failure(request, responses)
            
            # Analyze responses and resolve conflicts
            result = await self._analyze_responses(responses)
            
            # Apply advanced conflict resolution
            if result.conflicts:
                logger.info(f"Resolving {len(result.conflicts)} conflicts")
                result = await self.resolve_conflicts(result)
            
            # Update metrics
            coordination_time = (datetime.utcnow() - start_time).total_seconds()
            result.coordination_time = coordination_time
            
            self._update_coordination_metrics(result, True)
            self.coordination_history.append(result)
            
            logger.info(
                f"Coordination completed in {coordination_time:.2f}s "
                f"with {len(responses)} agents"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Coordination failed: {e}")
            self._update_coordination_metrics(None, False)
            raise
            
    async def send_message(self, message: AgentMessage) -> None:
        """Send a message through the agent communication protocol."""
        await self.message_queue.put(message)
        
    async def broadcast_context_update(
        self, 
        session_id: UUID, 
        context_update: Dict[str, Any]
    ) -> None:
        """Broadcast context update to all agents in a session."""
        if session_id not in self.active_sessions:
            return
            
        context = self.active_sessions[session_id]
        
        # Update context
        for key, value in context_update.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                context.shared_variables[key] = value
                
        # Broadcast to all active agents
        message = AgentMessage(
            type=MessageType.CONTEXT_UPDATE,
            sender_id="orchestrator",
            content=context_update,
            session_id=session_id
        )
        
        await self.send_message(message)
        
    async def get_agent_status(self, session_id: UUID) -> Dict[str, Any]:
        """Get status of all agents in a session."""
        if session_id not in self.active_sessions:
            return {}
            
        context = self.active_sessions[session_id]
        status = {}
        
        for agent_id in context.active_agents:
            agent = agent_registry.get_agent(agent_id)
            if agent:
                status[agent_id] = agent.get_status()
                
        return status
        
    async def _select_agents(self, request: CoordinationRequest) -> List[BaseAgent]:
        """Select appropriate agents for a coordination request using intelligent team assembly."""
        # Analyze query complexity to determine optimal team composition
        team_composition = await self._analyze_optimal_team_composition(request)
        
        # Get initial candidates
        candidates = []
        
        # Get agents by required capabilities
        for capability in request.required_capabilities:
            capable_agents = agent_registry.get_agents_by_capability(capability)
            candidates.extend(capable_agents)
            
        # Add agents based on team composition recommendations
        for agent_type in team_composition['recommended_types']:
            type_agents = [a for a in agent_registry.get_all_agents() 
                          if a.agent_type == agent_type]
            candidates.extend(type_agents)
            
        # Remove duplicates
        unique_candidates = list({agent.agent_id: agent for agent in candidates}.values())
        
        # Score agents based on multiple factors
        scored_agents = []
        for agent in unique_candidates:
            try:
                # Base compatibility score
                compatibility_score = agent.can_handle_query(request.query, request.context)
                
                # Team synergy bonus
                synergy_score = self._calculate_team_synergy(agent, scored_agents)
                
                # Specialization bonus for complex queries
                specialization_score = self._calculate_specialization_bonus(
                    agent, team_composition['complexity_level']
                )
                
                # Performance history bonus
                performance_score = self._calculate_performance_score(agent)
                
                # Combined score
                total_score = (
                    compatibility_score * 0.4 + 
                    synergy_score * 0.2 + 
                    specialization_score * 0.25 + 
                    performance_score * 0.15
                )
                
                if total_score > 0.1:  # Minimum threshold
                    scored_agents.append((agent, total_score))
                    
            except Exception as e:
                logger.warning(f"Error scoring agent {agent.agent_id}: {e}")
                
        # Smart team selection based on composition strategy
        selected = await self._assemble_optimal_team(
            scored_agents, 
            request, 
            team_composition
        )
        
        # Initialize selected agents
        for agent in selected:
            if not agent.is_active:
                await agent.initialize(request.context)
                request.context.active_agents.add(agent.agent_id)
                
        logger.info(f"Assembled team of {len(selected)} agents for {team_composition['complexity_level']} complexity query")
        return selected
        
    async def _analyze_optimal_team_composition(self, request: CoordinationRequest) -> Dict[str, Any]:
        """Analyze query to determine optimal team composition."""
        query_lower = request.query.lower()
        
        # Complexity indicators
        complexity_indicators = [
            'complex', 'advanced', 'sophisticated', 'multiple', 'integrate',
            'optimize', 'performance', 'scale', 'architecture', 'system'
        ]
        
        # Domain indicators
        physics_indicators = ['physics', 'simulation', 'physx', 'dynamics', 'forces']
        viz_indicators = ['visualization', '3d', 'render', 'graphics', 'plot']
        optimization_indicators = ['optimize', 'performance', 'speed', 'efficiency', 'gpu']
        debug_indicators = ['debug', 'error', 'fix', 'problem', 'issue', 'troubleshoot']
        
        # Calculate complexity level
        complexity_matches = sum(1 for indicator in complexity_indicators 
                               if indicator in query_lower)
        
        if complexity_matches >= 3:
            complexity_level = 'high'
            max_agents = min(request.max_agents, 4)
        elif complexity_matches >= 1:
            complexity_level = 'medium' 
            max_agents = min(request.max_agents, 3)
        else:
            complexity_level = 'low'
            max_agents = min(request.max_agents, 2)
            
        # Determine recommended agent types
        recommended_types = []
        
        physics_score = sum(1 for indicator in physics_indicators if indicator in query_lower)
        viz_score = sum(1 for indicator in viz_indicators if indicator in query_lower)
        opt_score = sum(1 for indicator in optimization_indicators if indicator in query_lower)
        debug_score = sum(1 for indicator in debug_indicators if indicator in query_lower)
        
        # Always include the strongest match
        scores = [
            ('physics', physics_score),
            ('visualization', viz_score),
            ('optimization', opt_score),
            ('debug', debug_score)
        ]
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Add top scoring agent types
        for agent_type, score in scores:
            if score > 0 and len(recommended_types) < max_agents:
                recommended_types.append(agent_type)
                
        # For high complexity, ensure multi-domain coverage
        if complexity_level == 'high' and len(recommended_types) >= 2:
            # Add complementary agents
            if 'physics' in recommended_types and 'optimization' not in recommended_types:
                if len(recommended_types) < max_agents:
                    recommended_types.append('optimization')
            if 'visualization' in recommended_types and 'physics' not in recommended_types:
                if len(recommended_types) < max_agents:
                    recommended_types.append('physics')
                    
        return {
            'complexity_level': complexity_level,
            'max_agents': max_agents,
            'recommended_types': recommended_types,
            'domain_scores': {
                'physics': physics_score,
                'visualization': viz_score,
                'optimization': opt_score,
                'debug': debug_score
            }
        }
        
    def _calculate_team_synergy(self, agent: BaseAgent, current_team: List[Tuple[BaseAgent, float]]) -> float:
        """Calculate synergy score for adding this agent to the current team."""
        if not current_team:
            return 0.5  # Neutral score for first agent
            
        synergy_score = 0.0
        
        # Positive synergy combinations
        synergy_matrix = {
            'physics': {'optimization': 0.3, 'debug': 0.2, 'visualization': 0.25},
            'visualization': {'physics': 0.25, 'optimization': 0.2},
            'optimization': {'physics': 0.3, 'visualization': 0.2, 'debug': 0.15},
            'debug': {'physics': 0.2, 'optimization': 0.15}
        }
        
        current_types = [a.agent_type for a, _ in current_team]
        
        for current_type in current_types:
            if agent.agent_type in synergy_matrix.get(current_type, {}):
                synergy_score += synergy_matrix[current_type][agent.agent_type]
            elif current_type in synergy_matrix.get(agent.agent_type, {}):
                synergy_score += synergy_matrix[agent.agent_type][current_type]
                
        # Penalty for duplicate types
        if agent.agent_type in current_types:
            synergy_score -= 0.4
            
        return min(1.0, max(0.0, synergy_score))
        
    def _calculate_specialization_bonus(self, agent: BaseAgent, complexity_level: str) -> float:
        """Calculate specialization bonus based on query complexity."""
        capability_count = len(agent.get_capabilities())
        
        if complexity_level == 'high':
            # High complexity favors specialists
            if capability_count >= 4:
                return 0.8
            elif capability_count >= 2:
                return 0.6
            else:
                return 0.3
        elif complexity_level == 'medium':
            # Medium complexity favors balanced agents
            if capability_count >= 2 and capability_count <= 4:
                return 0.7
            else:
                return 0.4
        else:
            # Low complexity - any agent is fine
            return 0.5
            
    def _calculate_performance_score(self, agent: BaseAgent) -> float:
        """Calculate performance score based on agent's historical performance."""
        metrics = agent.performance_metrics
        
        if metrics['total_queries'] == 0:
            return 0.5  # Neutral score for new agents
            
        # Factors: confidence, response time, success rate
        confidence_score = min(1.0, metrics.get('average_confidence', 0.5))
        
        # Response time score (lower is better, normalize to 0-1)
        avg_response_time = metrics.get('average_response_time', 5.0)
        time_score = max(0.0, min(1.0, (5.0 - avg_response_time) / 5.0))
        
        success_rate = metrics.get('success_rate', 0.5)
        
        # Weighted combination
        performance_score = (
            confidence_score * 0.4 + 
            time_score * 0.3 + 
            success_rate * 0.3
        )
        
        return performance_score
        
    async def _assemble_optimal_team(
        self, 
        scored_agents: List[Tuple[BaseAgent, float]], 
        request: CoordinationRequest, 
        team_composition: Dict[str, Any]
    ) -> List[BaseAgent]:
        """Assemble the optimal team based on scores and composition strategy."""
        if not scored_agents:
            return []
            
        # Sort by score
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        max_agents = team_composition['max_agents']
        
        selected_agents = []
        used_types = set()
        
        # Strategy 1: Ensure diversity for high complexity
        if team_composition['complexity_level'] == 'high':
            # First pass: select top agent from each recommended type
            for agent_type in team_composition['recommended_types']:
                if len(selected_agents) >= max_agents:
                    break
                    
                for agent, score in scored_agents:
                    if (agent.agent_type == agent_type and 
                        agent.agent_type not in used_types):
                        selected_agents.append(agent)
                        used_types.add(agent.agent_type)
                        break
                        
            # Second pass: fill remaining slots with highest scoring agents
            for agent, score in scored_agents:
                if len(selected_agents) >= max_agents:
                    break
                if agent not in selected_agents:
                    selected_agents.append(agent)
                    
        else:
            # Strategy 2: For medium/low complexity, prioritize top scores
            for agent, score in scored_agents:
                if len(selected_agents) >= max_agents:
                    break
                selected_agents.append(agent)
                
        return selected_agents[:max_agents]
        
    async def _process_with_agents(
        self, 
        agents: List[BaseAgent], 
        query: str, 
        context: AgentContext
    ) -> List[AgentResponse]:
        """Process query with multiple agents concurrently."""
        tasks = []
        
        for agent in agents:
            task = asyncio.create_task(
                self._safe_agent_query(agent, query, context)
            )
            tasks.append(task)
            
        # Wait for all responses with timeout
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=30.0
            )
            
            # Filter out exceptions and None responses
            valid_responses = [
                r for r in responses 
                if isinstance(r, AgentResponse)
            ]
            
            return valid_responses
            
        except asyncio.TimeoutError:
            logger.warning("Agent coordination timed out")
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
            return []
            
    async def _safe_agent_query(
        self, 
        agent: BaseAgent, 
        query: str, 
        context: AgentContext
    ) -> Optional[AgentResponse]:
        """Safely query an agent with comprehensive error handling and fallback."""
        max_retries = 2
        retry_delay = 1.0
        
        for attempt in range(max_retries + 1):
            try:
                # Check agent health before querying
                if not await self._check_agent_health(agent):
                    logger.warning(f"Agent {agent.agent_id} failed health check")
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                    else:
                        return await self._create_fallback_response(agent, query, "health_check_failed")
                
                # Process the query
                response = await asyncio.wait_for(
                    agent.process_query(query, context),
                    timeout=30.0  # 30 second timeout per agent
                )
                
                # Validate response quality
                if not self._validate_response_quality(response):
                    logger.warning(f"Agent {agent.agent_id} returned low-quality response")
                    if attempt < max_retries:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                
                # Update performance metrics
                agent.update_performance_metrics(response)
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"Agent {agent.agent_id} query timed out (attempt {attempt + 1})")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    return await self._create_fallback_response(agent, query, "timeout")
                    
            except Exception as e:
                logger.error(f"Agent {agent.agent_id} query failed (attempt {attempt + 1}): {e}")
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    return await self._create_fallback_response(agent, query, str(e))
                    
        return None
        
    async def _check_agent_health(self, agent: BaseAgent) -> bool:
        """Check if an agent is healthy and responsive."""
        try:
            # Basic health checks
            if not agent.is_active:
                return False
                
            if not agent.context:
                return False
                
            # Check if agent has been failing recently
            metrics = agent.performance_metrics
            if metrics['total_queries'] > 5:
                recent_success_rate = metrics.get('success_rate', 1.0)
                if recent_success_rate < 0.3:  # Less than 30% success rate
                    return False
                    
            return True
            
        except Exception as e:
            logger.error(f"Health check failed for agent {agent.agent_id}: {e}")
            return False
            
    def _validate_response_quality(self, response: AgentResponse) -> bool:
        """Validate the quality of an agent response."""
        try:
            # Basic validation checks
            if not response or not response.response:
                return False
                
            # Check minimum response length
            if len(response.response.strip()) < 10:
                return False
                
            # Check confidence score
            if response.confidence_score < 0.1:
                return False
                
            # Check for error indicators in response
            error_indicators = ['error', 'failed', 'unable', 'cannot', 'sorry']
            response_lower = response.response.lower()
            
            # If response contains multiple error indicators, it's likely low quality
            error_count = sum(1 for indicator in error_indicators 
                            if indicator in response_lower)
            if error_count >= 2:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Response validation failed: {e}")
            return False
            
    async def _create_fallback_response(
        self, 
        agent: BaseAgent, 
        query: str, 
        failure_reason: str
    ) -> AgentResponse:
        """Create a fallback response when an agent fails."""
        fallback_responses = {
            "timeout": "I apologize, but I'm experiencing delays processing your request. Please try rephrasing your question or break it into smaller parts.",
            "health_check_failed": "I'm currently experiencing technical difficulties. Please try your request again in a moment.",
            "low_quality": "I'm having trouble providing a comprehensive answer to your question. Could you provide more specific details?"
        }
        
        # Generic fallback for unknown errors
        fallback_text = fallback_responses.get(
            failure_reason, 
            "I encountered an unexpected issue while processing your request. Please try again or contact support if the problem persists."
        )
        
        # Try to provide basic guidance based on query keywords
        query_lower = query.lower()
        
        if 'physics' in query_lower or 'simulation' in query_lower:
            fallback_text += "\n\nFor physics-related questions, you might try:\n- Check PhysX documentation\n- Verify simulation parameters\n- Ensure proper initialization"
        elif 'visualization' in query_lower or '3d' in query_lower:
            fallback_text += "\n\nFor visualization questions, you might try:\n- Check Three.js documentation\n- Verify WebGL support\n- Check browser compatibility"
        elif 'optimization' in query_lower or 'performance' in query_lower:
            fallback_text += "\n\nFor optimization questions, you might try:\n- Check system resources\n- Profile your application\n- Review GPU utilization"
        elif 'debug' in query_lower or 'error' in query_lower:
            fallback_text += "\n\nFor debugging, you might try:\n- Check console logs\n- Verify input parameters\n- Test with simplified cases"
            
        return AgentResponse(
            agent_id=f"fallback_{agent.agent_id}",
            agent_type=f"fallback_{agent.agent_type}",
            response=fallback_text,
            confidence_score=0.1,  # Low confidence for fallback
            capabilities_used=[],
            suggestions=["Try rephrasing your question", "Break down into smaller questions", "Contact support if issue persists"],
            code_snippets=[],
            response_time=0.1,
            timestamp=datetime.utcnow()
        )
        
    async def _handle_coordination_failure(
        self, 
        request: CoordinationRequest, 
        partial_responses: List[AgentResponse]
    ) -> CoordinationResult:
        """Handle cases where coordination partially or completely fails."""
        
        if partial_responses:
            # We have some responses, create a result with them
            result = await self._analyze_responses(partial_responses)
            
            # Add metadata about the failure
            result.conflicts.append({
                'type': 'coordination_partial_failure',
                'message': f'Only {len(partial_responses)} agents responded successfully',
                'severity': 'medium',
                'resolution_strategy': 'use_available_responses'
            })
            
            return result
        else:
            # Complete failure - create emergency fallback
            emergency_response = AgentResponse(
                agent_id="emergency_fallback",
                agent_type="emergency",
                response=("I apologize, but all specialized agents are currently unavailable. "
                         "This might be due to high system load or temporary technical issues. "
                         "Please try your request again in a few moments. "
                         "If the problem persists, consider breaking your question into smaller, "
                         "more specific parts or contact system support."),
                confidence_score=0.05,
                capabilities_used=[],
                suggestions=[
                    "Try again in a few moments",
                    "Break question into smaller parts", 
                    "Check system status",
                    "Contact support if issue persists"
                ],
                code_snippets=[],
                response_time=0.1,
                timestamp=datetime.utcnow()
            )
            
            return CoordinationResult(
                primary_response=emergency_response,
                supporting_responses=[],
                consensus_score=0.0,
                conflicts=[{
                    'type': 'coordination_complete_failure',
                    'message': 'All agents failed to respond',
                    'severity': 'high',
                    'resolution_strategy': 'emergency_fallback'
                }],
                coordination_time=0.1
            )
            
    async def _process_with_agents(
        self, 
        agents: List[BaseAgent], 
        query: str, 
        context: AgentContext
    ) -> List[AgentResponse]:
        """Process query with multiple agents concurrently with enhanced error handling."""
        if not agents:
            return []
            
        tasks = []
        
        for agent in agents:
            task = asyncio.create_task(
                self._safe_agent_query(agent, query, context)
            )
            tasks.append(task)
            
        # Wait for all responses with timeout
        try:
            responses = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=45.0  # Increased timeout for fallback handling
            )
            
            # Filter out exceptions and None responses
            valid_responses = [
                r for r in responses 
                if isinstance(r, AgentResponse) and r is not None
            ]
            
            # Log any exceptions for debugging
            exceptions = [r for r in responses if isinstance(r, Exception)]
            for exc in exceptions:
                logger.error(f"Agent task exception: {exc}")
            
            return valid_responses
            
        except asyncio.TimeoutError:
            logger.warning("Agent coordination timed out")
            # Cancel remaining tasks
            for task in tasks:
                if not task.done():
                    task.cancel()
                    
            # Try to get partial results
            completed_tasks = [task for task in tasks if task.done()]
            partial_responses = []
            
            for task in completed_tasks:
                try:
                    result = task.result()
                    if isinstance(result, AgentResponse):
                        partial_responses.append(result)
                except Exception as e:
                    logger.error(f"Error getting task result: {e}")
                    
            return partial_responses
            
    async def _analyze_responses(self, responses: List[AgentResponse]) -> CoordinationResult:
        """Analyze agent responses and resolve conflicts."""
        if not responses:
            raise ValueError("No valid responses to analyze")
            
        # Sort by confidence score
        responses.sort(key=lambda r: r.confidence_score, reverse=True)
        
        primary_response = responses[0]
        supporting_responses = responses[1:] if len(responses) > 1 else []
        
        # Detect conflicts
        conflicts = self._detect_conflicts(responses)
        
        # Calculate consensus score
        consensus_score = self._calculate_consensus(responses)
        
        return CoordinationResult(
            primary_response=primary_response,
            supporting_responses=supporting_responses,
            consensus_score=consensus_score,
            conflicts=conflicts
        )
        
    def _detect_conflicts(self, responses: List[AgentResponse]) -> List[Dict[str, Any]]:
        """Detect conflicts between agent responses."""
        conflicts = []
        
        # Advanced conflict detection
        for i, response1 in enumerate(responses):
            for j, response2 in enumerate(responses[i+1:], i+1):
                
                # 1. Check for conflicting suggestions
                if (response1.suggestions and response2.suggestions):
                    conflicting_suggestions = self._find_conflicting_suggestions(
                        response1.suggestions, response2.suggestions
                    )
                    
                    if conflicting_suggestions:
                        conflicts.append({
                            'type': 'suggestion_conflict',
                            'agent1': response1.agent_id,
                            'agent2': response2.agent_id,
                            'agent1_suggestions': response1.suggestions,
                            'agent2_suggestions': response2.suggestions,
                            'conflicting_pairs': conflicting_suggestions,
                            'severity': self._assess_conflict_severity(conflicting_suggestions),
                            'resolution_strategy': self._suggest_resolution_strategy(
                                response1, response2, 'suggestion'
                            )
                        })
                
                # 2. Check for conflicting code approaches
                if (response1.code_snippets and response2.code_snippets):
                    code_conflicts = self._detect_code_conflicts(
                        response1.code_snippets, response2.code_snippets
                    )
                    
                    if code_conflicts:
                        conflicts.append({
                            'type': 'code_conflict',
                            'agent1': response1.agent_id,
                            'agent2': response2.agent_id,
                            'conflicts': code_conflicts,
                            'severity': 'medium',
                            'resolution_strategy': self._suggest_resolution_strategy(
                                response1, response2, 'code'
                            )
                        })
                
                # 3. Check for confidence discrepancies
                confidence_diff = abs(response1.confidence_score - response2.confidence_score)
                if confidence_diff > 0.3:  # Significant confidence difference
                    conflicts.append({
                        'type': 'confidence_conflict',
                        'agent1': response1.agent_id,
                        'agent2': response2.agent_id,
                        'confidence1': response1.confidence_score,
                        'confidence2': response2.confidence_score,
                        'difference': confidence_diff,
                        'severity': 'low' if confidence_diff < 0.5 else 'medium',
                        'resolution_strategy': 'favor_higher_confidence'
                    })
                    
        return conflicts
        
    def _calculate_consensus(self, responses: List[AgentResponse]) -> float:
        """Calculate consensus score among responses."""
        if len(responses) <= 1:
            return 1.0
            
        # Simple consensus based on confidence scores
        avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
        confidence_variance = sum(
            (r.confidence_score - avg_confidence) ** 2 for r in responses
        ) / len(responses)
        
        # Higher consensus when confidence scores are similar and high
        consensus = avg_confidence * (1.0 - min(confidence_variance, 1.0))
        return max(0.0, min(1.0, consensus))
        
    def _find_conflicting_suggestions(self, suggestions1: List[str], suggestions2: List[str]) -> List[Dict[str, str]]:
        """Find conflicting suggestion pairs."""
        conflicts = []
        
        # Define conflicting keywords/patterns
        conflict_patterns = [
            (['increase', 'higher', 'more', 'boost'], ['decrease', 'lower', 'less', 'reduce']),
            (['enable', 'turn on', 'activate'], ['disable', 'turn off', 'deactivate']),
            (['use', 'apply', 'implement'], ['avoid', 'remove', 'skip']),
            (['fast', 'quick', 'speed'], ['slow', 'careful', 'gradual']),
            (['simple', 'basic'], ['complex', 'advanced', 'sophisticated'])
        ]
        
        for s1 in suggestions1:
            for s2 in suggestions2:
                s1_lower = s1.lower()
                s2_lower = s2.lower()
                
                # Check for direct contradictions
                for positive_terms, negative_terms in conflict_patterns:
                    if (any(term in s1_lower for term in positive_terms) and 
                        any(term in s2_lower for term in negative_terms)):
                        conflicts.append({
                            'suggestion1': s1,
                            'suggestion2': s2,
                            'conflict_type': 'contradiction'
                        })
                        break
                    elif (any(term in s1_lower for term in negative_terms) and 
                          any(term in s2_lower for term in positive_terms)):
                        conflicts.append({
                            'suggestion1': s1,
                            'suggestion2': s2,
                            'conflict_type': 'contradiction'
                        })
                        break
        
        return conflicts
        
    def _detect_code_conflicts(self, snippets1: List[str], snippets2: List[str]) -> List[Dict[str, str]]:
        """Detect conflicts between code snippets."""
        conflicts = []
        
        # Define conflicting code patterns
        conflict_indicators = [
            ('True', 'False'),
            ('enable', 'disable'),
            ('++', '--'),
            ('add', 'remove'),
            ('create', 'delete')
        ]
        
        for snippet1 in snippets1:
            for snippet2 in snippets2:
                for positive, negative in conflict_indicators:
                    if positive in snippet1 and negative in snippet2:
                        conflicts.append({
                            'snippet1': snippet1[:100] + '...' if len(snippet1) > 100 else snippet1,
                            'snippet2': snippet2[:100] + '...' if len(snippet2) > 100 else snippet2,
                            'conflict_type': f'{positive}_vs_{negative}'
                        })
                        
        return conflicts
        
    def _assess_conflict_severity(self, conflicting_suggestions: List[Dict[str, str]]) -> str:
        """Assess the severity of conflicts."""
        if not conflicting_suggestions:
            return 'none'
        elif len(conflicting_suggestions) == 1:
            return 'low'
        elif len(conflicting_suggestions) <= 3:
            return 'medium'
        else:
            return 'high'
            
    def _suggest_resolution_strategy(
        self, 
        response1: AgentResponse, 
        response2: AgentResponse, 
        conflict_type: str
    ) -> str:
        """Suggest a strategy for resolving conflicts."""
        if conflict_type == 'suggestion':
            if response1.confidence_score > response2.confidence_score + 0.2:
                return f'favor_agent_{response1.agent_id}'
            elif response2.confidence_score > response1.confidence_score + 0.2:
                return f'favor_agent_{response2.agent_id}'
            else:
                return 'hybrid_approach'
        elif conflict_type == 'code':
            # Favor agent with more specialized capabilities for the task
            agent1_caps = len(response1.capabilities_used)
            agent2_caps = len(response2.capabilities_used)
            
            if agent1_caps > agent2_caps:
                return f'favor_agent_{response1.agent_id}'
            elif agent2_caps > agent1_caps:
                return f'favor_agent_{response2.agent_id}'
            else:
                return 'combine_approaches'
        else:
            return 'manual_review'
            
    async def resolve_conflicts(self, result: CoordinationResult) -> CoordinationResult:
        """Actively resolve conflicts in coordination results."""
        if not result.conflicts:
            return result
            
        resolved_conflicts = []
        
        for conflict in result.conflicts:
            resolution_strategy = conflict.get('resolution_strategy', 'manual_review')
            
            try:
                if resolution_strategy.startswith('favor_agent_'):
                    agent_id = resolution_strategy.split('_')[-1]
                    # Promote the favored agent's response
                    if result.primary_response.agent_id != agent_id:
                        # Find the agent in supporting responses
                        for i, response in enumerate(result.supporting_responses):
                            if response.agent_id == agent_id:
                                # Swap primary and supporting
                                result.supporting_responses[i] = result.primary_response
                                result.primary_response = response
                                break
                                
                elif resolution_strategy == 'hybrid_approach':
                    # Create a hybrid response combining both agents
                    hybrid_response = self._create_hybrid_response(
                        result.primary_response,
                        result.supporting_responses
                    )
                    result.primary_response = hybrid_response
                    
                elif resolution_strategy == 'combine_approaches':
                    # Combine code snippets and suggestions
                    all_snippets = result.primary_response.code_snippets.copy()
                    all_suggestions = result.primary_response.suggestions.copy()
                    
                    for response in result.supporting_responses:
                        all_snippets.extend(response.code_snippets)
                        all_suggestions.extend(response.suggestions)
                        
                    result.primary_response.code_snippets = list(set(all_snippets))
                    result.primary_response.suggestions = list(set(all_suggestions))
                    
                # Mark conflict as resolved
                conflict['resolved'] = True
                conflict['resolution_applied'] = resolution_strategy
                resolved_conflicts.append(conflict)
                
            except Exception as e:
                logger.error(f"Failed to resolve conflict: {e}")
                conflict['resolved'] = False
                conflict['resolution_error'] = str(e)
                resolved_conflicts.append(conflict)
                
        result.conflicts = resolved_conflicts
        
        # Recalculate consensus score after resolution
        all_responses = [result.primary_response] + result.supporting_responses
        result.consensus_score = self._calculate_consensus(all_responses)
        
        return result
        
    def _create_hybrid_response(
        self, 
        primary: AgentResponse, 
        supporting: List[AgentResponse]
    ) -> AgentResponse:
        """Create a hybrid response combining multiple agent responses."""
        all_responses = [primary] + supporting
        
        # Combine suggestions (remove duplicates)
        combined_suggestions = []
        for response in all_responses:
            for suggestion in response.suggestions:
                if suggestion not in combined_suggestions:
                    combined_suggestions.append(suggestion)
                    
        # Combine code snippets (remove duplicates)
        combined_snippets = []
        for response in all_responses:
            for snippet in response.code_snippets:
                if snippet not in combined_snippets:
                    combined_snippets.append(snippet)
                    
        # Create hybrid response text
        hybrid_text = f"Based on analysis from multiple specialized agents:\n\n"
        hybrid_text += f"Primary analysis ({primary.agent_type}): {primary.response}\n\n"
        
        for response in supporting:
            hybrid_text += f"Supporting analysis ({response.agent_type}): {response.response}\n\n"
            
        hybrid_text += "Recommended approach combines insights from all agents."
        
        # Calculate weighted confidence
        total_weight = sum(r.confidence_score for r in all_responses)
        weighted_confidence = total_weight / len(all_responses) if all_responses else 0.0
        
        return AgentResponse(
            agent_id=f"hybrid_{primary.agent_id}",
            agent_type="hybrid",
            response=hybrid_text,
            confidence_score=min(0.95, weighted_confidence),  # Cap at 0.95 for hybrid
            capabilities_used=list(set().union(*[r.capabilities_used for r in all_responses])),
            suggestions=combined_suggestions,
            code_snippets=combined_snippets,
            response_time=max(r.response_time for r in all_responses),
            timestamp=datetime.utcnow()
        )
        
    async def _process_messages(self) -> None:
        """Process messages from the message queue."""
        while self.is_running:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    self.message_queue.get(), 
                    timeout=1.0
                )
                
                await self._handle_message(message)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Message processing error: {e}")
                
    async def _handle_message(self, message: AgentMessage) -> None:
        """Handle a single message."""
        try:
            if message.type == MessageType.CONTEXT_UPDATE:
                await self._handle_context_update(message)
            elif message.type == MessageType.AGENT_STATUS:
                await self._handle_agent_status(message)
            elif message.type == MessageType.ERROR:
                await self._handle_error_message(message)
                
        except Exception as e:
            logger.error(f"Error handling message {message.id}: {e}")
            
    async def _handle_context_update(self, message: AgentMessage) -> None:
        """Handle context update message."""
        if not message.session_id or message.session_id not in self.active_sessions:
            return
            
        context = self.active_sessions[message.session_id]
        
        # Update all active agents with new context
        for agent_id in context.active_agents:
            agent = agent_registry.get_agent(agent_id)
            if agent:
                agent.update_context(context)
                
    async def _handle_agent_status(self, message: AgentMessage) -> None:
        """Handle agent status message."""
        # Log agent status updates
        logger.info(f"Agent status update: {message.content}")
        
    async def _handle_error_message(self, message: AgentMessage) -> None:
        """Handle error message."""
        logger.error(f"Agent error from {message.sender_id}: {message.content}")
        
    def _update_coordination_metrics(
        self, 
        result: Optional[CoordinationResult], 
        success: bool
    ) -> None:
        """Update coordination performance metrics."""
        self.metrics['total_coordinations'] += 1
        
        if success:
            self.metrics['successful_coordinations'] += 1
            
            if result:
                # Update average coordination time
                total = self.metrics['total_coordinations']
                current_avg = self.metrics['average_coordination_time']
                new_avg = ((current_avg * (total - 1)) + result.coordination_time) / total
                self.metrics['average_coordination_time'] = new_avg
                
                # Update conflict resolution rate
                if result.conflicts:
                    conflicts_resolved = len([c for c in result.conflicts if 'resolved' in c])
                    resolution_rate = conflicts_resolved / len(result.conflicts)
                    current_rate = self.metrics['conflict_resolution_rate']
                    new_rate = ((current_rate * (total - 1)) + resolution_rate) / total
                    self.metrics['conflict_resolution_rate'] = new_rate
                    
    def get_metrics(self) -> Dict[str, Any]:
        """Get orchestrator performance metrics."""
        return self.metrics.copy()
        
    def get_coordination_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent coordination history."""
        recent = self.coordination_history[-limit:] if limit > 0 else self.coordination_history
        
        return [
            {
                'primary_agent': result.primary_response.agent_id,
                'supporting_agents': [r.agent_id for r in result.supporting_responses],
                'consensus_score': result.consensus_score,
                'conflicts_count': len(result.conflicts),
                'coordination_time': result.coordination_time,
                'timestamp': result.primary_response.timestamp.isoformat()
            }
            for result in recent
        ]