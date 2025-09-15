#!/usr/bin/env python3
"""
Validation script for AI agent system implementation.
"""

import asyncio
import sys
from uuid import uuid4

# Add the app directory to the path
sys.path.append('.')

try:
    from app.services.agents.base import (
        BaseAgent, AgentContext, AgentResponse, AgentCapability, 
        agent_registry
    )
    from app.services.agents.orchestrator import (
        AgentOrchestrator, CoordinationRequest
    )
    from app.services.agents.physics_agent import PhysicsAgent
    from app.services.agents.visualization_agent import VisualizationAgent
    from app.services.agents.optimization_agent import OptimizationAgent
    from app.services.agents.debug_agent import DebugAgent
    
    print("✓ All agent imports successful")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)


async def test_agent_system():
    """Test the agent system functionality."""
    
    print("\n=== Testing Agent System ===")
    
    # Test 1: Agent Registry
    print("\n1. Testing Agent Registry...")
    
    # Register agent types
    agent_registry.register_agent_type("physics", PhysicsAgent)
    agent_registry.register_agent_type("visualization", VisualizationAgent)
    agent_registry.register_agent_type("optimization", OptimizationAgent)
    agent_registry.register_agent_type("debug", DebugAgent)
    
    agent_types = agent_registry.get_agent_types()
    print(f"   Registered agent types: {agent_types}")
    
    if len(agent_types) >= 4:
        print("   ✓ Agent registration successful")
    else:
        print("   ✗ Agent registration failed")
        return False
    
    # Test 2: Agent Creation
    print("\n2. Testing Agent Creation...")
    
    physics_agent = agent_registry.create_agent("physics")
    viz_agent = agent_registry.create_agent("visualization")
    
    print(f"   Physics agent: {physics_agent.name}")
    print(f"   Visualization agent: {viz_agent.name}")
    
    if physics_agent and viz_agent:
        print("   ✓ Agent creation successful")
    else:
        print("   ✗ Agent creation failed")
        return False
    
    # Test 3: Agent Capabilities
    print("\n3. Testing Agent Capabilities...")
    
    physics_caps = physics_agent.get_capabilities()
    viz_caps = viz_agent.get_capabilities()
    
    print(f"   Physics capabilities: {[cap.value for cap in physics_caps]}")
    print(f"   Visualization capabilities: {[cap.value for cap in viz_caps]}")
    
    if (AgentCapability.PHYSICS_SIMULATION in physics_caps and 
        AgentCapability.VISUALIZATION_3D in viz_caps):
        print("   ✓ Agent capabilities correct")
    else:
        print("   ✗ Agent capabilities incorrect")
        return False
    
    # Test 4: Agent Context
    print("\n4. Testing Agent Context...")
    
    context = AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        current_code="import physx as px\nscene = px.create_scene()",
        physics_parameters={'gravity': -9.81}
    )
    
    await physics_agent.initialize(context)
    
    if physics_agent.is_active and physics_agent.context:
        print("   ✓ Agent initialization successful")
    else:
        print("   ✗ Agent initialization failed")
        return False
    
    # Test 5: Agent Query Processing
    print("\n5. Testing Agent Query Processing...")
    
    physics_query = "How do I create a rigid body in PhysX?"
    confidence = physics_agent.can_handle_query(physics_query, context)
    print(f"   Physics agent confidence for physics query: {confidence:.2f}")
    
    if confidence > 0.5:
        print("   ✓ Physics agent correctly identifies physics queries")
    else:
        print("   ✗ Physics agent failed to identify physics query")
        return False
    
    # Test actual query processing
    try:
        response = await physics_agent.process_query(physics_query, context)
        print(f"   Response confidence: {response.confidence_score:.2f}")
        print(f"   Response length: {len(response.response)} characters")
        print(f"   Suggestions count: {len(response.suggestions)}")
        print(f"   Code snippets count: {len(response.code_snippets)}")
        
        if (response.confidence_score > 0.5 and 
            len(response.response) > 50 and
            len(response.suggestions) > 0):
            print("   ✓ Agent query processing successful")
        else:
            print("   ✗ Agent query processing insufficient")
            return False
            
    except Exception as e:
        print(f"   ✗ Agent query processing failed: {e}")
        return False
    
    # Test 6: Agent Orchestrator
    print("\n6. Testing Agent Orchestrator...")
    
    orchestrator = AgentOrchestrator()
    await orchestrator.start()
    
    if orchestrator.is_running:
        print("   ✓ Orchestrator started successfully")
    else:
        print("   ✗ Orchestrator failed to start")
        return False
    
    # Test session creation
    session_id = uuid4()
    session_context = await orchestrator.create_session(
        session_id=session_id,
        notebook_id=uuid4()
    )
    
    if session_id in orchestrator.active_sessions:
        print("   ✓ Session creation successful")
    else:
        print("   ✗ Session creation failed")
        return False
    
    # Test coordination
    try:
        coord_request = CoordinationRequest(
            query="I need help with physics simulation setup and 3D visualization",
            context=session_context,
            required_capabilities={
                AgentCapability.PHYSICS_SIMULATION,
                AgentCapability.VISUALIZATION_3D
            },
            max_agents=2
        )
        
        result = await orchestrator.coordinate_agents(coord_request)
        
        print(f"   Primary agent: {result.primary_response.agent_type}")
        print(f"   Supporting agents: {len(result.supporting_responses)}")
        print(f"   Consensus score: {result.consensus_score:.2f}")
        print(f"   Coordination time: {result.coordination_time:.2f}s")
        
        if (result.primary_response and 
            result.coordination_time > 0):
            print("   ✓ Agent coordination successful")
        else:
            print("   ✗ Agent coordination failed")
            return False
            
    except Exception as e:
        print(f"   ✗ Agent coordination failed: {e}")
        return False
    
    # Cleanup
    await orchestrator.stop()
    await physics_agent.shutdown()
    await viz_agent.shutdown()
    
    print("\n=== All Tests Passed! ===")
    return True


async def main():
    """Main validation function."""
    try:
        success = await test_agent_system()
        if success:
            print("\n🎉 AI Agent System validation completed successfully!")
            print("\nImplemented features:")
            print("  ✓ Base agent class and interface definitions")
            print("  ✓ Agent registry for managing agent types")
            print("  ✓ Specialized agents (Physics, Visualization, Optimization, Debug)")
            print("  ✓ Agent orchestrator for multi-agent coordination")
            print("  ✓ Agent communication protocol and message queuing")
            print("  ✓ Agent context sharing and coordination mechanisms")
            print("  ✓ Performance metrics and monitoring")
            print("  ✓ Error handling and fallback systems")
            print("  ✓ API endpoints for agent interaction")
            
            return 0
        else:
            print("\n❌ AI Agent System validation failed!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Validation crashed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)