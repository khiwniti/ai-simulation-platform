#!/usr/bin/env python3
"""
Simple validation script for specialized AI agents.
"""

import asyncio
import sys
import os
from uuid import uuid4

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.agents.base import AgentContext
from services.agents.physics_agent import PhysicsAgent
from services.agents.visualization_agent import VisualizationAgent
from services.agents.optimization_agent import OptimizationAgent
from services.agents.debug_agent import DebugAgent


async def test_physics_agent():
    """Test Physics Agent functionality."""
    print("Testing Physics Agent...")
    
    agent = PhysicsAgent()
    context = AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        cell_id=uuid4(),
        current_code="import physx as px\nscene = px.create_scene()",
        physics_parameters={'gravity': -9.81}
    )
    
    # Test physics-related queries
    queries = [
        "How do I set up a PhysX rigid body simulation?",
        "My physics simulation is unstable, what should I check?",
        "How do I optimize physics parameters for better performance?",
        "What are the best practices for collision detection in PhysX?"
    ]
    
    for query in queries:
        confidence = agent.can_handle_query(query, context)
        print(f"  Query: '{query[:50]}...'")
        print(f"  Confidence: {confidence:.2f}")
        
        if confidence > 0.5:
            response = await agent.process_query(query, context)
            print(f"  Response length: {len(response.response)} chars")
            print(f"  Suggestions: {len(response.suggestions)}")
            print(f"  Code snippets: {len(response.code_snippets)}")
        print()
    
    print("Physics Agent test completed.\n")


async def test_visualization_agent():
    """Test Visualization Agent functionality."""
    print("Testing Visualization Agent...")
    
    agent = VisualizationAgent()
    context = AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        cell_id=uuid4(),
        current_code="import * as THREE from 'three';\nconst scene = new THREE.Scene();",
        physics_parameters={}
    )
    
    # Test visualization-related queries
    queries = [
        "How do I create a 3D scene with Three.js?",
        "How can I visualize physics simulation data in real-time?",
        "What's the best way to optimize 3D rendering performance?",
        "How do I add interactive controls to my 3D visualization?"
    ]
    
    for query in queries:
        confidence = agent.can_handle_query(query, context)
        print(f"  Query: '{query[:50]}...'")
        print(f"  Confidence: {confidence:.2f}")
        
        if confidence > 0.5:
            response = await agent.process_query(query, context)
            print(f"  Response length: {len(response.response)} chars")
            print(f"  Suggestions: {len(response.suggestions)}")
            print(f"  Code snippets: {len(response.code_snippets)}")
        print()
    
    print("Visualization Agent test completed.\n")


async def test_optimization_agent():
    """Test Optimization Agent functionality."""
    print("Testing Optimization Agent...")
    
    agent = OptimizationAgent()
    context = AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        cell_id=uuid4(),
        current_code="# Performance bottleneck in physics simulation",
        physics_parameters={'solver_iterations': 8}
    )
    
    # Test optimization-related queries
    queries = [
        "How can I optimize GPU performance for physics simulation?",
        "My simulation is running slowly, what can I optimize?",
        "How do I improve memory usage in large-scale simulations?",
        "What are the best practices for parallel physics processing?"
    ]
    
    for query in queries:
        confidence = agent.can_handle_query(query, context)
        print(f"  Query: '{query[:50]}...'")
        print(f"  Confidence: {confidence:.2f}")
        
        if confidence > 0.5:
            response = await agent.process_query(query, context)
            print(f"  Response length: {len(response.response)} chars")
            print(f"  Suggestions: {len(response.suggestions)}")
            print(f"  Code snippets: {len(response.code_snippets)}")
        print()
    
    print("Optimization Agent test completed.\n")


async def test_debug_agent():
    """Test Debug Agent functionality."""
    print("Testing Debug Agent...")
    
    agent = DebugAgent()
    context = AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        cell_id=uuid4(),
        current_code="# Error: objects falling through ground",
        physics_parameters={'gravity': -9.81}
    )
    
    # Test debug-related queries
    queries = [
        "My physics objects are falling through the ground, how do I fix this?",
        "The simulation crashes with a segmentation fault, what should I check?",
        "Objects in my simulation are behaving unrealistically, help me debug",
        "How do I troubleshoot physics simulation instability?"
    ]
    
    for query in queries:
        confidence = agent.can_handle_query(query, context)
        print(f"  Query: '{query[:50]}...'")
        print(f"  Confidence: {confidence:.2f}")
        
        if confidence > 0.5:
            response = await agent.process_query(query, context)
            print(f"  Response length: {len(response.response)} chars")
            print(f"  Suggestions: {len(response.suggestions)}")
            print(f"  Code snippets: {len(response.code_snippets)}")
        print()
    
    print("Debug Agent test completed.\n")


async def test_agent_specialization():
    """Test that agents properly specialize in their domains."""
    print("Testing Agent Specialization...")
    
    agents = {
        'Physics': PhysicsAgent(),
        'Visualization': VisualizationAgent(),
        'Optimization': OptimizationAgent(),
        'Debug': DebugAgent()
    }
    
    context = AgentContext(
        session_id=uuid4(),
        notebook_id=uuid4(),
        cell_id=uuid4(),
        current_code="test code",
        physics_parameters={}
    )
    
    # Test queries that should be handled by specific agents
    test_cases = [
        ("How do I set up PhysX rigid bodies?", "Physics"),
        ("How do I create a Three.js scene?", "Visualization"),
        ("How can I optimize GPU performance?", "Optimization"),
        ("My simulation is crashing, help debug", "Debug")
    ]
    
    for query, expected_specialist in test_cases:
        print(f"  Query: '{query}'")
        print(f"  Expected specialist: {expected_specialist}")
        
        confidences = {}
        for name, agent in agents.items():
            confidence = agent.can_handle_query(query, context)
            confidences[name] = confidence
            print(f"    {name}: {confidence:.2f}")
        
        # Check if the expected specialist has highest confidence
        best_agent = max(confidences, key=confidences.get)
        if best_agent == expected_specialist:
            print(f"    ✓ Correct specialization")
        else:
            print(f"    ✗ Expected {expected_specialist}, got {best_agent}")
        print()
    
    print("Agent Specialization test completed.\n")


async def main():
    """Run all agent validation tests."""
    print("=== AI Agent Validation Tests ===\n")
    
    try:
        await test_physics_agent()
        await test_visualization_agent()
        await test_optimization_agent()
        await test_debug_agent()
        await test_agent_specialization()
        
        print("=== All Tests Completed Successfully ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)