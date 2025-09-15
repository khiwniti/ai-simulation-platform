"""
Comprehensive tests for specialized AI agents.
"""

import pytest
import asyncio
from uuid import uuid4
from datetime import datetime

from app.services.agents.base import AgentContext, AgentCapability
from app.services.agents.physics_agent import PhysicsAgent
from app.services.agents.visualization_agent import VisualizationAgent
from app.services.agents.optimization_agent import OptimizationAgent
from app.services.agents.debug_agent import DebugAgent


@pytest.fixture
def base_context():
    """Create a base agent context for testing."""
    return AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        cell_id=uuid4(),
        current_code="# Test code",
        physics_parameters={'gravity': -9.81},
        gpu_resources={'available': True}
    )


class TestPhysicsAgent:
    """Test Physics Agent functionality."""
    
    def test_physics_agent_initialization(self):
        """Test physics agent initialization."""
        agent = PhysicsAgent()
        
        assert agent.name == "Physics Simulation Expert"
        assert AgentCapability.PHYSICS_SIMULATION in agent.capabilities
        assert AgentCapability.PHYSICS_DEBUGGING in agent.capabilities
        assert AgentCapability.PARAMETER_TUNING in agent.capabilities
        assert AgentCapability.EQUATION_ASSISTANCE in agent.capabilities
        
    def test_physics_query_confidence_scoring(self, base_context):
        """Test physics query confidence scoring."""
        agent = PhysicsAgent()
        
        # High confidence queries
        high_conf_queries = [
            "How do I set up a PhysX rigid body simulation?",
            "My physics simulation is unstable",
            "How to configure PhysX materials?",
            "PxRigidDynamic creation help"
        ]
        
        for query in high_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence >= 0.6, f"Low confidence for physics query: {query}"
            
        # Low confidence queries
        low_conf_queries = [
            "How do I style CSS elements?",
            "Database query optimization",
            "React component lifecycle"
        ]
        
        for query in low_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence <= 0.3, f"High confidence for non-physics query: {query}"
            
    @pytest.mark.asyncio
    async def test_physics_query_processing(self, base_context):
        """Test physics query processing."""
        agent = PhysicsAgent()
        
        query = "How do I set up a basic PhysX scene with rigid bodies?"
        response = await agent.process_query(query, base_context)
        
        assert response.agent_id == agent.agent_id
        assert response.confidence_score > 0.5
        assert len(response.response) > 100
        assert len(response.suggestions) > 0
        assert len(response.code_snippets) > 0
        assert response.response_time > 0
        
        # Check that response contains physics-related content
        response_lower = response.response.lower()
        assert any(term in response_lower for term in ['physx', 'physics', 'rigid', 'scene'])
        
    @pytest.mark.asyncio
    async def test_physics_query_types(self, base_context):
        """Test different types of physics queries."""
        agent = PhysicsAgent()
        
        query_types = {
            'setup': "How do I initialize a PhysX physics scene?",
            'debug': "My physics objects are not colliding properly",
            'optimization': "How can I optimize PhysX performance?",
            'parameter_tuning': "What material properties should I use?",
            'equation': "What is the formula for kinetic energy?",
            'collision': "How do I handle collision detection?",
            'dynamics': "How do I apply forces to rigid bodies?"
        }
        
        for query_type, query in query_types.items():
            response = await agent.process_query(query, base_context)
            assert response.confidence_score > 0.5
            assert len(response.suggestions) > 0
            assert query_type in response.context['query_type']


class TestVisualizationAgent:
    """Test Visualization Agent functionality."""
    
    def test_visualization_agent_initialization(self):
        """Test visualization agent initialization."""
        agent = VisualizationAgent()
        
        assert agent.name == "3D Visualization Expert"
        assert AgentCapability.VISUALIZATION_3D in agent.capabilities
        assert AgentCapability.VISUALIZATION_PLOTS in agent.capabilities
        assert AgentCapability.PERFORMANCE_OPTIMIZATION in agent.capabilities
        
    def test_visualization_query_confidence_scoring(self, base_context):
        """Test visualization query confidence scoring."""
        agent = VisualizationAgent()
        
        # High confidence queries
        high_conf_queries = [
            "How do I create a Three.js scene?",
            "3D visualization with WebGL",
            "How to render physics simulation data?",
            "THREE.Scene setup help"
        ]
        
        for query in high_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence >= 0.6, f"Low confidence for visualization query: {query}"
            
        # Low confidence queries
        low_conf_queries = [
            "How do I configure database connections?",
            "Physics simulation setup",
            "Backend API development"
        ]
        
        for query in low_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence <= 0.3, f"High confidence for non-visualization query: {query}"
            
    @pytest.mark.asyncio
    async def test_visualization_query_processing(self, base_context):
        """Test visualization query processing."""
        agent = VisualizationAgent()
        
        query = "How do I create an interactive 3D scene with Three.js?"
        response = await agent.process_query(query, base_context)
        
        assert response.confidence_score > 0.5
        assert len(response.response) > 100
        assert len(response.suggestions) > 0
        assert len(response.code_snippets) > 0
        
        # Check that response contains visualization-related content
        response_lower = response.response.lower()
        assert any(term in response_lower for term in ['three', '3d', 'scene', 'render', 'visualization'])
        
    @pytest.mark.asyncio
    async def test_visualization_query_types(self, base_context):
        """Test different types of visualization queries."""
        agent = VisualizationAgent()
        
        query_types = {
            'setup': "How do I set up a basic Three.js scene?",
            '3d_graphics': "How do I create 3D meshes and geometries?",
            'animation': "How do I animate 3D objects?",
            'interaction': "How do I add mouse controls to 3D scene?",
            'performance': "How do I optimize 3D rendering performance?"
        }
        
        for query_type, query in query_types.items():
            response = await agent.process_query(query, base_context)
            assert response.confidence_score > 0.5
            assert len(response.suggestions) > 0


class TestOptimizationAgent:
    """Test Optimization Agent functionality."""
    
    def test_optimization_agent_initialization(self):
        """Test optimization agent initialization."""
        agent = OptimizationAgent()
        
        assert agent.name == "Performance Optimization Expert"
        assert AgentCapability.PERFORMANCE_OPTIMIZATION in agent.capabilities
        assert AgentCapability.GPU_OPTIMIZATION in agent.capabilities
        
    def test_optimization_query_confidence_scoring(self, base_context):
        """Test optimization query confidence scoring."""
        agent = OptimizationAgent()
        
        # High confidence queries
        high_conf_queries = [
            "How can I optimize GPU performance?",
            "My simulation is running slowly",
            "Memory optimization strategies",
            "CUDA performance tuning"
        ]
        
        for query in high_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence >= 0.6, f"Low confidence for optimization query: {query}"
            
        # Low confidence queries
        low_conf_queries = [
            "How do I create React components?",
            "Database schema design",
            "CSS styling techniques"
        ]
        
        for query in low_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence <= 0.3, f"High confidence for non-optimization query: {query}"
            
    @pytest.mark.asyncio
    async def test_optimization_query_processing(self, base_context):
        """Test optimization query processing."""
        agent = OptimizationAgent()
        
        query = "How can I optimize GPU performance for physics simulations?"
        response = await agent.process_query(query, base_context)
        
        assert response.confidence_score > 0.5
        assert len(response.response) > 100
        assert len(response.suggestions) > 0
        assert len(response.code_snippets) > 0
        
        # Check that response contains optimization-related content
        response_lower = response.response.lower()
        assert any(term in response_lower for term in ['gpu', 'performance', 'optimization', 'memory'])
        
    @pytest.mark.asyncio
    async def test_optimization_query_types(self, base_context):
        """Test different types of optimization queries."""
        agent = OptimizationAgent()
        
        query_types = {
            'gpu_optimization': "How do I optimize CUDA kernels?",
            'memory_optimization': "How can I reduce memory usage?",
            'physics_optimization': "How do I optimize PhysX performance?",
            'profiling': "How do I profile application performance?"
        }
        
        for query_type, query in query_types.items():
            response = await agent.process_query(query, base_context)
            assert response.confidence_score > 0.5
            assert len(response.suggestions) > 0


class TestDebugAgent:
    """Test Debug Agent functionality."""
    
    def test_debug_agent_initialization(self):
        """Test debug agent initialization."""
        agent = DebugAgent()
        
        assert agent.name == "Debug & Error Analysis Expert"
        assert AgentCapability.CODE_DEBUGGING in agent.capabilities
        assert AgentCapability.ERROR_ANALYSIS in agent.capabilities
        assert AgentCapability.PHYSICS_DEBUGGING in agent.capabilities
        
    def test_debug_query_confidence_scoring(self, base_context):
        """Test debug query confidence scoring."""
        agent = DebugAgent()
        
        # High confidence queries
        high_conf_queries = [
            "My simulation is crashing with segfault",
            "Objects are falling through the ground",
            "Debug physics simulation instability",
            "Error: null pointer exception"
        ]
        
        for query in high_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence >= 0.6, f"Low confidence for debug query: {query}"
            
        # Low confidence queries
        low_conf_queries = [
            "How do I create beautiful UI designs?",
            "Best practices for API design",
            "Database normalization techniques"
        ]
        
        for query in low_conf_queries:
            confidence = agent.can_handle_query(query, base_context)
            assert confidence <= 0.3, f"High confidence for non-debug query: {query}"
            
    @pytest.mark.asyncio
    async def test_debug_query_processing(self, base_context):
        """Test debug query processing."""
        agent = DebugAgent()
        
        query = "My physics objects are falling through the ground, how do I fix this?"
        response = await agent.process_query(query, base_context)
        
        assert response.confidence_score > 0.5
        assert len(response.response) > 100
        assert len(response.suggestions) > 0
        assert len(response.code_snippets) > 0
        
        # Check that response contains debug-related content
        response_lower = response.response.lower()
        assert any(term in response_lower for term in ['debug', 'fix', 'collision', 'ground'])
        
    @pytest.mark.asyncio
    async def test_debug_query_types(self, base_context):
        """Test different types of debug queries."""
        agent = DebugAgent()
        
        query_types = {
            'physics_debug': "My physics simulation is unstable",
            'crash_debug': "Application crashes with segmentation fault",
            'performance_debug': "Simulation is running very slowly",
            'memory_debug': "Memory leak in physics objects"
        }
        
        for query_type, query in query_types.items():
            response = await agent.process_query(query, base_context)
            assert response.confidence_score > 0.5
            assert len(response.suggestions) > 0


class TestAgentSpecialization:
    """Test agent specialization and domain expertise."""
    
    def test_agent_domain_specialization(self, base_context):
        """Test that agents specialize in their respective domains."""
        agents = {
            'Physics': PhysicsAgent(),
            'Visualization': VisualizationAgent(),
            'Optimization': OptimizationAgent(),
            'Debug': DebugAgent()
        }
        
        # Test queries that should be handled by specific agents
        specialization_tests = [
            ("How do I set up PhysX rigid bodies?", "Physics"),
            ("How do I create a Three.js scene?", "Visualization"),
            ("How can I optimize GPU performance?", "Optimization"),
            ("My simulation is crashing, help debug", "Debug"),
            ("PxRigidDynamic creation and setup", "Physics"),
            ("WebGL rendering optimization", "Visualization"),
            ("CUDA memory management", "Optimization"),
            ("Segmentation fault troubleshooting", "Debug")
        ]
        
        for query, expected_specialist in specialization_tests:
            confidences = {}
            for name, agent in agents.items():
                confidence = agent.can_handle_query(query, base_context)
                confidences[name] = confidence
            
            # The expected specialist should have the highest confidence
            best_agent = max(confidences, key=confidences.get)
            assert best_agent == expected_specialist, (
                f"Query: '{query}' - Expected {expected_specialist}, got {best_agent}. "
                f"Confidences: {confidences}"
            )
            
    @pytest.mark.asyncio
    async def test_agent_response_quality(self, base_context):
        """Test the quality of agent responses."""
        agents = [
            (PhysicsAgent(), "How do I set up a PhysX physics scene?"),
            (VisualizationAgent(), "How do I create a 3D visualization?"),
            (OptimizationAgent(), "How can I optimize performance?"),
            (DebugAgent(), "My code is crashing, help me debug it")
        ]
        
        for agent, query in agents:
            response = await agent.process_query(query, base_context)
            
            # Check response quality metrics
            assert response.confidence_score > 0.5
            assert len(response.response) >= 100  # Substantial response
            assert len(response.suggestions) >= 3  # Multiple suggestions
            assert response.response_time > 0  # Measured response time
            
            # Check that capabilities are properly reported
            assert len(response.capabilities_used) > 0
            assert all(cap in agent.capabilities for cap in response.capabilities_used)
            
    def test_agent_performance_metrics(self, base_context):
        """Test agent performance metrics tracking."""
        agent = PhysicsAgent()
        
        # Initial metrics
        initial_queries = agent.performance_metrics['total_queries']
        
        # Simulate query processing
        from app.services.agents.base import AgentResponse
        response = AgentResponse(
            agent_id=agent.agent_id,
            agent_type=agent.agent_type,
            response="Test response",
            confidence_score=0.85,
            response_time=0.5
        )
        
        agent.update_performance_metrics(response)
        
        # Check metrics update
        assert agent.performance_metrics['total_queries'] == initial_queries + 1
        assert agent.performance_metrics['average_confidence'] > 0
        assert agent.performance_metrics['average_response_time'] > 0
        
    @pytest.mark.asyncio
    async def test_error_handling_in_agents(self, base_context):
        """Test error handling in agent query processing."""
        
        class FailingAgent(PhysicsAgent):
            async def _generate_physics_response(self, query, query_type, context):
                raise Exception("Simulated error")
        
        agent = FailingAgent()
        response = await agent.process_query("test query", base_context)
        
        # Should return error response instead of raising exception
        assert response.confidence_score == 0.1
        assert "error" in response.response.lower()
        assert response.response_time > 0


class TestAgentContextHandling:
    """Test agent context handling and adaptation."""
    
    @pytest.mark.asyncio
    async def test_context_aware_responses(self):
        """Test that agents adapt responses based on context."""
        agent = PhysicsAgent()
        
        # Context with physics code
        physics_context = AgentContext(
            session_id=uuid4(),
            notebook_id=uuid4(),
            cell_id=uuid4(),
            current_code="import physx as px\nscene = px.create_scene()",
            physics_parameters={'gravity': -9.81}
        )
        
        # Context without physics code
        generic_context = AgentContext(
            session_id=uuid4(),
            notebook_id=uuid4(),
            cell_id=uuid4(),
            current_code="print('hello world')",
            physics_parameters={}
        )
        
        query = "How do I improve simulation performance?"
        
        physics_confidence = agent.can_handle_query(query, physics_context)
        generic_confidence = agent.can_handle_query(query, generic_context)
        
        # Should have higher confidence with physics context
        assert physics_confidence >= generic_confidence
        
    def test_gpu_resource_awareness(self, base_context):
        """Test agent awareness of GPU resources."""
        agent = OptimizationAgent()
        
        # Context with GPU available
        gpu_context = base_context
        gpu_context.gpu_resources = {'available': True, 'memory': '8GB'}
        
        # Context without GPU
        no_gpu_context = AgentContext(
            session_id=uuid4(),
            notebook_id=uuid4(),
            cell_id=uuid4(),
            current_code="test code",
            gpu_resources={'available': False}
        )
        
        gpu_query = "How can I optimize GPU performance?"
        
        gpu_confidence = agent.can_handle_query(gpu_query, gpu_context)
        no_gpu_confidence = agent.can_handle_query(gpu_query, no_gpu_context)
        
        # Both should handle GPU queries, but context might influence confidence
        assert gpu_confidence > 0.5
        assert no_gpu_confidence > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])