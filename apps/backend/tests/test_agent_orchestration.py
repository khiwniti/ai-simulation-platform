"""
Tests for AI agent orchestration system.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch

from app.services.agents.base import (
    BaseAgent, AgentContext, AgentResponse, AgentCapability, 
    agent_registry, AgentRegistry
)
from app.services.agents.orchestrator import (
    AgentOrchestrator, CoordinationRequest, MessageType, 
    MessagePriority, AgentMessage
)
from app.services.agents.physics_agent import PhysicsAgent
from app.services.agents.visualization_agent import VisualizationAgent
from app.services.agents.optimization_agent import OptimizationAgent
from app.services.agents.debug_agent import DebugAgent


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, agent_id=None, capabilities=None, confidence=0.8):
        super().__init__(agent_id)
        self.capabilities = capabilities or {AgentCapability.PHYSICS_SIMULATION}
        self._confidence = confidence
        self._response_text = "Mock response"
        
    @property
    def name(self):
        return "Mock Agent"
        
    @property
    def description(self):
        return "Mock agent for testing"
        
    def can_handle_query(self, query, context):
        return self._confidence
        
    async def process_query(self, query, context):
        return AgentResponse(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            response=self._response_text,
            confidence_score=self._confidence,
            capabilities_used=list(self.capabilities),
            response_time=0.1
        )


@pytest.fixture
def agent_context():
    """Create a test agent context."""
    return AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        cell_id=uuid4(),
        current_code="test_code = 'hello world'",
        physics_parameters={'gravity': -9.81},
        gpu_resources={'available': True}
    )


@pytest.fixture
def orchestrator():
    """Create a test orchestrator."""
    return AgentOrchestrator()


@pytest.fixture
async def running_orchestrator():
    """Create and start a test orchestrator."""
    orch = AgentOrchestrator()
    await orch.start()
    yield orch
    await orch.stop()


class TestAgentRegistry:
    """Test agent registry functionality."""
    
    def test_register_agent_type(self):
        """Test registering agent types."""
        registry = AgentRegistry()
        registry.register_agent_type("test", MockAgent)
        
        assert "test" in registry.get_agent_types()
        
    def test_create_agent(self):
        """Test creating agent instances."""
        registry = AgentRegistry()
        registry.register_agent_type("test", MockAgent)
        
        agent = registry.create_agent("test")
        assert isinstance(agent, MockAgent)
        assert agent.agent_id in [a.agent_id for a in registry.get_all_agents()]
        
    def test_create_unknown_agent_type(self):
        """Test creating agent with unknown type."""
        registry = AgentRegistry()
        
        with pytest.raises(ValueError, match="Unknown agent type"):
            registry.create_agent("unknown")
            
    def test_get_agents_by_capability(self):
        """Test getting agents by capability."""
        registry = AgentRegistry()
        registry.register_agent_type("physics", MockAgent)
        
        agent = registry.create_agent("physics")
        agents = registry.get_agents_by_capability(AgentCapability.PHYSICS_SIMULATION)
        
        assert agent in agents
        
    def test_remove_agent(self):
        """Test removing agents."""
        registry = AgentRegistry()
        registry.register_agent_type("test", MockAgent)
        
        agent = registry.create_agent("test")
        agent_id = agent.agent_id
        
        success = registry.remove_agent(agent_id)
        assert success
        assert registry.get_agent(agent_id) is None


class TestBaseAgent:
    """Test base agent functionality."""
    
    @pytest.mark.asyncio
    async def test_agent_initialization(self, agent_context):
        """Test agent initialization."""
        agent = MockAgent()
        
        assert not agent.is_active
        assert agent.context is None
        
        await agent.initialize(agent_context)
        
        assert agent.is_active
        assert agent.context == agent_context
        
    @pytest.mark.asyncio
    async def test_agent_shutdown(self, agent_context):
        """Test agent shutdown."""
        agent = MockAgent()
        await agent.initialize(agent_context)
        
        assert agent.is_active
        
        await agent.shutdown()
        
        assert not agent.is_active
        assert agent.context is None
        
    def test_agent_capabilities(self):
        """Test agent capability management."""
        capabilities = {AgentCapability.PHYSICS_SIMULATION, AgentCapability.GPU_OPTIMIZATION}
        agent = MockAgent(capabilities=capabilities)
        
        assert agent.get_capabilities() == capabilities
        assert agent.has_capability(AgentCapability.PHYSICS_SIMULATION)
        assert not agent.has_capability(AgentCapability.VISUALIZATION_3D)
        
    def test_performance_metrics_update(self):
        """Test performance metrics updates."""
        agent = MockAgent()
        
        response = AgentResponse(
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
            response="test",
            confidence_score=0.9,
            response_time=0.5
        )
        
        initial_queries = agent.performance_metrics['total_queries']
        agent.update_performance_metrics(response)
        
        assert agent.performance_metrics['total_queries'] == initial_queries + 1
        assert agent.performance_metrics['average_confidence'] > 0
        assert agent.performance_metrics['average_response_time'] > 0


class TestSpecializedAgents:
    """Test specialized agent implementations."""
    
    @pytest.mark.asyncio
    async def test_physics_agent_query_handling(self, agent_context):
        """Test physics agent query handling."""
        agent = PhysicsAgent()
        
        # Test physics-related query
        physics_query = "How do I set up a PhysX rigid body simulation?"
        confidence = agent.can_handle_query(physics_query, agent_context)
        assert confidence > 0.5
        
        response = await agent.process_query(physics_query, agent_context)
        assert response.confidence_score > 0.5
        assert "physx" in response.response.lower() or "physics" in response.response.lower()
        assert len(response.suggestions) > 0
        
    @pytest.mark.asyncio
    async def test_visualization_agent_query_handling(self, agent_context):
        """Test visualization agent query handling."""
        agent = VisualizationAgent()
        
        # Test visualization-related query
        viz_query = "How do I create a 3D scene with Three.js?"
        confidence = agent.can_handle_query(viz_query, agent_context)
        assert confidence > 0.5
        
        response = await agent.process_query(viz_query, agent_context)
        assert response.confidence_score > 0.5
        assert "three" in response.response.lower() or "3d" in response.response.lower()
        assert len(response.code_snippets) > 0
        
    @pytest.mark.asyncio
    async def test_optimization_agent_query_handling(self, agent_context):
        """Test optimization agent query handling."""
        agent = OptimizationAgent()
        
        # Test optimization-related query
        opt_query = "How can I optimize GPU performance for physics simulation?"
        confidence = agent.can_handle_query(opt_query, agent_context)
        assert confidence > 0.5
        
        response = await agent.process_query(opt_query, agent_context)
        assert response.confidence_score > 0.5
        assert "gpu" in response.response.lower() or "performance" in response.response.lower()
        
    @pytest.mark.asyncio
    async def test_debug_agent_query_handling(self, agent_context):
        """Test debug agent query handling."""
        agent = DebugAgent()
        
        # Test debug-related query
        debug_query = "My physics simulation is unstable and objects are exploding"
        confidence = agent.can_handle_query(debug_query, agent_context)
        assert confidence > 0.5
        
        response = await agent.process_query(debug_query, agent_context)
        assert response.confidence_score > 0.5
        assert "unstable" in response.response.lower() or "debug" in response.response.lower()


class TestAgentOrchestrator:
    """Test agent orchestrator functionality."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_startup_shutdown(self, orchestrator):
        """Test orchestrator startup and shutdown."""
        assert not orchestrator.is_running
        
        await orchestrator.start()
        assert orchestrator.is_running
        
        await orchestrator.stop()
        assert not orchestrator.is_running
        
    @pytest.mark.asyncio
    async def test_session_management(self, running_orchestrator):
        """Test session creation and management."""
        session_id = uuid4()
        
        # Create session
        context = await running_orchestrator.create_session(
            session_id=session_id,
            notebook_id=uuid4()
        )
        
        assert session_id in running_orchestrator.active_sessions
        assert context.session_id == session_id
        
        # End session
        await running_orchestrator.end_session(session_id)
        assert session_id not in running_orchestrator.active_sessions
        
    @pytest.mark.asyncio
    async def test_context_update_broadcast(self, running_orchestrator, agent_context):
        """Test context update broadcasting."""
        session_id = agent_context.session_id
        
        # Create session
        await running_orchestrator.create_session(session_id=session_id)
        
        # Update context
        context_update = {'new_parameter': 'test_value'}
        await running_orchestrator.broadcast_context_update(session_id, context_update)
        
        # Verify update
        session_context = running_orchestrator.active_sessions[session_id]
        assert session_context.shared_variables['new_parameter'] == 'test_value'
        
    @pytest.mark.asyncio
    async def test_agent_coordination(self, running_orchestrator):
        """Test multi-agent coordination."""
        # Register mock agents
        agent_registry.register_agent_type("mock1", MockAgent)
        agent_registry.register_agent_type("mock2", MockAgent)
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        # Create coordination request
        request = CoordinationRequest(
            query="Test coordination query",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=2
        )
        
        # Coordinate agents
        result = await running_orchestrator.coordinate_agents(request)
        
        assert result.primary_response is not None
        assert result.primary_response.response == "Mock response"
        assert result.coordination_time > 0
        
    @pytest.mark.asyncio
    async def test_message_processing(self, running_orchestrator):
        """Test message queue processing."""
        message = AgentMessage(
            type=MessageType.CONTEXT_UPDATE,
            sender_id="test_sender",
            content={"test": "data"},
            session_id=uuid4()
        )
        
        await running_orchestrator.send_message(message)
        
        # Give time for message processing
        await asyncio.sleep(0.1)
        
        # Message should be processed (no exception raised)
        assert True
        
    def test_metrics_collection(self, orchestrator):
        """Test metrics collection."""
        metrics = orchestrator.get_metrics()
        
        assert 'total_coordinations' in metrics
        assert 'successful_coordinations' in metrics
        assert 'average_coordination_time' in metrics
        assert 'conflict_resolution_rate' in metrics
        
    def test_coordination_history(self, orchestrator):
        """Test coordination history tracking."""
        history = orchestrator.get_coordination_history(limit=5)
        
        assert isinstance(history, list)
        assert len(history) <= 5


class TestAgentSelection:
    """Test agent selection algorithms."""
    
    @pytest.mark.asyncio
    async def test_agent_selection_by_capability(self, running_orchestrator):
        """Test agent selection based on capabilities."""
        # Register agents with different capabilities
        agent_registry.register_agent_type("physics", lambda: MockAgent(
            capabilities={AgentCapability.PHYSICS_SIMULATION}
        ))
        agent_registry.register_agent_type("viz", lambda: MockAgent(
            capabilities={AgentCapability.VISUALIZATION_3D}
        ))
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Physics simulation question",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=1
        )
        
        # This should select the physics agent
        result = await running_orchestrator.coordinate_agents(request)
        
        assert result.primary_response is not None
        
    @pytest.mark.asyncio
    async def test_agent_confidence_scoring(self, running_orchestrator):
        """Test agent selection based on confidence scores."""
        # Register agents with different confidence levels
        agent_registry.register_agent_type("high_conf", lambda: MockAgent(confidence=0.9))
        agent_registry.register_agent_type("low_conf", lambda: MockAgent(confidence=0.3))
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Test query",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=2
        )
        
        result = await running_orchestrator.coordinate_agents(request)
        
        # Higher confidence agent should be primary
        assert result.primary_response.confidence_score >= 0.3


class TestErrorHandling:
    """Test error handling in agent system."""
    
    @pytest.mark.asyncio
    async def test_agent_query_error_handling(self, agent_context):
        """Test error handling in agent queries."""
        
        class FailingAgent(MockAgent):
            async def process_query(self, query, context):
                raise Exception("Test error")
        
        agent = FailingAgent()
        response = await agent.process_query("test", agent_context)
        
        # Should return error response instead of raising
        assert response.confidence_score == 0.1
        assert "error" in response.response.lower()
        
    @pytest.mark.asyncio
    async def test_coordination_timeout_handling(self, running_orchestrator):
        """Test coordination timeout handling."""
        
        class SlowAgent(MockAgent):
            async def process_query(self, query, context):
                await asyncio.sleep(2)  # Longer than timeout
                return await super().process_query(query, context)
        
        agent_registry.register_agent_type("slow", SlowAgent)
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Test query",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=1,
            timeout_seconds=1  # Short timeout
        )
        
        # Should handle timeout gracefully
        with pytest.raises(ValueError, match="No suitable agents"):
            await running_orchestrator.coordinate_agents(request)
            
    @pytest.mark.asyncio
    async def test_no_suitable_agents_error(self, running_orchestrator):
        """Test error when no suitable agents are found."""
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Test query",
            context=context,
            required_capabilities={AgentCapability.VISUALIZATION_3D},  # No agents with this capability
            max_agents=1
        )
        
        with pytest.raises(ValueError, match="No suitable agents"):
            await running_orchestrator.coordinate_agents(request)


class TestConflictResolution:
    """Test conflict resolution between agents."""
    
    @pytest.mark.asyncio
    async def test_conflicting_suggestions_detection(self, running_orchestrator):
        """Test detection of conflicting agent suggestions."""
        
        class Agent1(MockAgent):
            async def process_query(self, query, context):
                response = await super().process_query(query, context)
                response.suggestions = ["Use approach A", "Set parameter X to 1"]
                return response
        
        class Agent2(MockAgent):
            async def process_query(self, query, context):
                response = await super().process_query(query, context)
                response.suggestions = ["Use approach B", "Set parameter X to 2"]
                return response
        
        agent_registry.register_agent_type("agent1", Agent1)
        agent_registry.register_agent_type("agent2", Agent2)
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Test query",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=2
        )
        
        result = await running_orchestrator.coordinate_agents(request)
        
        # Should detect conflicts in suggestions
        assert len(result.conflicts) > 0
        
    def test_consensus_calculation(self, orchestrator):
        """Test consensus score calculation."""
        responses = [
            AgentResponse("agent1", "type1", "response", 0.9, response_time=0.1),
            AgentResponse("agent2", "type2", "response", 0.8, response_time=0.1),
            AgentResponse("agent3", "type3", "response", 0.85, response_time=0.1)
        ]
        
        consensus = orchestrator._calculate_consensus(responses)
        
        assert 0.0 <= consensus <= 1.0
        assert consensus > 0.5  # Should be high for similar confidence scores


class TestAdvancedCoordination:
    """Test advanced coordination features."""
    
    @pytest.mark.asyncio
    async def test_intelligent_team_assembly(self, running_orchestrator):
        """Test intelligent team assembly for complex queries."""
        # Register agents with different capabilities
        agent_registry.register_agent_type("physics", lambda: MockAgent(
            capabilities={AgentCapability.PHYSICS_SIMULATION, AgentCapability.PARAMETER_TUNING}
        ))
        agent_registry.register_agent_type("viz", lambda: MockAgent(
            capabilities={AgentCapability.VISUALIZATION_3D}
        ))
        agent_registry.register_agent_type("opt", lambda: MockAgent(
            capabilities={AgentCapability.PERFORMANCE_OPTIMIZATION, AgentCapability.GPU_OPTIMIZATION}
        ))
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        # Test complex query requiring multiple agents
        request = CoordinationRequest(
            query="Create an advanced physics simulation with optimized 3D visualization",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=3
        )
        
        result = await running_orchestrator.coordinate_agents(request)
        
        assert result.primary_response is not None
        assert len(result.supporting_responses) >= 1
        assert result.consensus_score > 0.0
        
    @pytest.mark.asyncio
    async def test_conflict_resolution_hybrid_approach(self, running_orchestrator):
        """Test hybrid approach conflict resolution."""
        
        class ConflictingAgent1(MockAgent):
            async def process_query(self, query, context):
                response = await super().process_query(query, context)
                response.suggestions = ["Use approach A", "Set parameter X to high"]
                response.confidence_score = 0.8
                return response
        
        class ConflictingAgent2(MockAgent):
            async def process_query(self, query, context):
                response = await super().process_query(query, context)
                response.suggestions = ["Use approach B", "Set parameter X to low"]
                response.confidence_score = 0.82
                return response
        
        agent_registry.register_agent_type("conf1", ConflictingAgent1)
        agent_registry.register_agent_type("conf2", ConflictingAgent2)
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Test conflict resolution",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=2
        )
        
        result = await running_orchestrator.coordinate_agents(request)
        
        # Should detect and resolve conflicts
        assert len(result.conflicts) > 0
        resolved_conflicts = [c for c in result.conflicts if c.get('resolved', False)]
        assert len(resolved_conflicts) > 0
        
    @pytest.mark.asyncio
    async def test_fallback_mechanisms(self, running_orchestrator):
        """Test fallback mechanisms for agent failures."""
        
        class FailingAgent(MockAgent):
            async def process_query(self, query, context):
                raise Exception("Simulated agent failure")
        
        class TimeoutAgent(MockAgent):
            async def process_query(self, query, context):
                await asyncio.sleep(35)  # Timeout after 30s
                return await super().process_query(query, context)
        
        agent_registry.register_agent_type("failing", FailingAgent)
        agent_registry.register_agent_type("timeout", TimeoutAgent)
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Test fallback mechanisms",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=2
        )
        
        result = await running_orchestrator.coordinate_agents(request)
        
        # Should get fallback response
        assert result.primary_response is not None
        assert result.primary_response.agent_id.startswith('fallback_') or result.primary_response.agent_id == 'emergency_fallback'
        
    @pytest.mark.asyncio
    async def test_agent_health_monitoring(self, running_orchestrator):
        """Test agent health monitoring."""
        agent = MockAgent()
        
        # Test healthy agent
        agent.is_active = True
        agent.context = AgentContext(session_id=uuid4())
        agent.performance_metrics['total_queries'] = 10
        agent.performance_metrics['success_rate'] = 0.8
        
        is_healthy = await running_orchestrator._check_agent_health(agent)
        assert is_healthy is True
        
        # Test unhealthy agent (low success rate)
        agent.performance_metrics['success_rate'] = 0.2
        is_healthy = await running_orchestrator._check_agent_health(agent)
        assert is_healthy is False
        
    def test_response_quality_validation(self, orchestrator):
        """Test response quality validation."""
        # Good response
        good_response = AgentResponse(
            agent_id="test",
            agent_type="test",
            response="This is a comprehensive response with detailed explanation",
            confidence_score=0.8
        )
        
        assert orchestrator._validate_response_quality(good_response) is True
        
        # Poor response (too short)
        poor_response = AgentResponse(
            agent_id="test",
            agent_type="test",
            response="Bad",
            confidence_score=0.8
        )
        
        assert orchestrator._validate_response_quality(poor_response) is False
        
        # Poor response (low confidence)
        low_conf_response = AgentResponse(
            agent_id="test",
            agent_type="test",
            response="This is a longer response but with low confidence",
            confidence_score=0.05
        )
        
        assert orchestrator._validate_response_quality(low_conf_response) is False
        
    @pytest.mark.asyncio
    async def test_team_synergy_calculation(self, orchestrator):
        """Test team synergy calculation."""
        physics_agent = MockAgent(agent_id="physics1")
        physics_agent.agent_type = "physics"
        
        viz_agent = MockAgent(agent_id="viz1")
        viz_agent.agent_type = "visualization"
        
        opt_agent = MockAgent(agent_id="opt1")
        opt_agent.agent_type = "optimization"
        
        # Test synergy with empty team
        synergy = orchestrator._calculate_team_synergy(physics_agent, [])
        assert synergy == 0.5
        
        # Test positive synergy
        current_team = [(physics_agent, 0.8)]
        synergy = orchestrator._calculate_team_synergy(viz_agent, current_team)
        assert synergy > 0.5  # Should have positive synergy
        
        # Test negative synergy (duplicate type)
        duplicate_physics = MockAgent(agent_id="physics2")
        duplicate_physics.agent_type = "physics"
        synergy = orchestrator._calculate_team_synergy(duplicate_physics, current_team)
        assert synergy < 0.5  # Should have penalty for duplicate
        
    @pytest.mark.asyncio
    async def test_complex_query_analysis(self, orchestrator):
        """Test complex query analysis for team composition."""
        # Simple query
        simple_request = CoordinationRequest(
            query="How do I create a basic box?",
            context=AgentContext(session_id=uuid4()),
            required_capabilities=set(),
            max_agents=3
        )
        
        composition = await orchestrator._analyze_optimal_team_composition(simple_request)
        assert composition['complexity_level'] == 'low'
        assert composition['max_agents'] <= 2
        
        # Complex query
        complex_request = CoordinationRequest(
            query="Create an advanced multi-threaded physics simulation with real-time optimization and sophisticated 3D visualization",
            context=AgentContext(session_id=uuid4()),
            required_capabilities=set(),
            max_agents=4
        )
        
        composition = await orchestrator._analyze_optimal_team_composition(complex_request)
        assert composition['complexity_level'] == 'high'
        assert composition['max_agents'] >= 3
        assert len(composition['recommended_types']) >= 2
        
    @pytest.mark.asyncio
    async def test_performance_based_selection(self, orchestrator):
        """Test agent selection based on performance metrics."""
        # High performance agent
        high_perf_agent = MockAgent()
        high_perf_agent.performance_metrics.update({
            'total_queries': 100,
            'average_confidence': 0.9,
            'average_response_time': 1.0,
            'success_rate': 0.95
        })
        
        # Low performance agent
        low_perf_agent = MockAgent()
        low_perf_agent.performance_metrics.update({
            'total_queries': 50,
            'average_confidence': 0.6,
            'average_response_time': 5.0,
            'success_rate': 0.7
        })
        
        high_score = orchestrator._calculate_performance_score(high_perf_agent)
        low_score = orchestrator._calculate_performance_score(low_perf_agent)
        
        assert high_score > low_score
        assert high_score > 0.8
        assert low_score < 0.7
        
    @pytest.mark.asyncio
    async def test_emergency_fallback_handling(self, running_orchestrator):
        """Test emergency fallback when all agents fail."""
        
        class CompletelyFailingAgent(MockAgent):
            async def process_query(self, query, context):
                raise Exception("Complete failure")
        
        agent_registry.register_agent_type("complete_fail", CompletelyFailingAgent)
        
        session_id = uuid4()
        context = await running_orchestrator.create_session(session_id=session_id)
        
        request = CoordinationRequest(
            query="Test complete failure",
            context=context,
            required_capabilities={AgentCapability.PHYSICS_SIMULATION},
            max_agents=1
        )
        
        result = await running_orchestrator.coordinate_agents(request)
        
        # Should get emergency fallback
        assert result.primary_response.agent_id == "emergency_fallback"
        assert result.consensus_score == 0.0
        assert len(result.conflicts) > 0
        assert result.conflicts[0]['type'] == 'coordination_complete_failure'


if __name__ == "__main__":
    pytest.main([__file__])