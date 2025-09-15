#!/usr/bin/env python3
"""
Simple integration test for inline assistance system.
"""

import asyncio
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from services.inline_assistance_service import InlineAssistanceService
from uuid import uuid4


async def test_inline_assistance():
    """Test the inline assistance service."""
    print("Testing Inline Assistance Service...")
    
    service = InlineAssistanceService()
    
    # Test 1: Code context analysis
    print("\n1. Testing code context analysis...")
    sample_code = """import physx_ai
import numpy as np

def create_simulation():
    scene = physx_ai.create_scene()
    # Add rigid body
    body = scene.add_rigid_body()
    return scene
"""
    
    try:
        result = await service.analyze_code_context(
            code_content=sample_code,
            cursor_position=80,  # Position in function
            line_number=5,
            column_number=10
        )
        
        print(f"✓ Context analysis completed in {result['processing_time']:.3f}s")
        print(f"  - Code type: {result['context']['code_type']}")
        print(f"  - Function context: {result['context']['function_context']}")
        print(f"  - Import statements: {len(result['context']['import_statements'])}")
        
    except Exception as e:
        print(f"✗ Context analysis failed: {e}")
        return False
    
    # Test 2: Agent selection
    print("\n2. Testing agent selection...")
    try:
        agents = service._select_agents_for_context(result['context'], 'completion')
        print(f"✓ Selected agents: {agents}")
        
    except Exception as e:
        print(f"✗ Agent selection failed: {e}")
        return False
    
    # Test 3: Service status
    print("\n3. Testing service status...")
    try:
        is_active = service.is_active()
        print(f"✓ Service is {'active' if is_active else 'inactive'}")
        
    except Exception as e:
        print(f"✗ Service status check failed: {e}")
        return False
    
    # Test 4: Word extraction
    print("\n4. Testing word extraction...")
    try:
        word = service._get_word_at_position("scene = physx_ai.create_scene()", 15)
        print(f"✓ Extracted word: '{word}'")
        
    except Exception as e:
        print(f"✗ Word extraction failed: {e}")
        return False
    
    # Test 5: Code type detection
    print("\n5. Testing code type detection...")
    try:
        physics_type = service._determine_code_type("import physx_ai\nscene = physx_ai.create_scene()")
        viz_type = service._determine_code_type("import matplotlib.pyplot as plt\nfig, ax = plt.subplots()")
        general_type = service._determine_code_type("def hello():\n    print('Hello')")
        
        print(f"✓ Physics code type: {physics_type}")
        print(f"✓ Visualization code type: {viz_type}")
        print(f"✓ General code type: {general_type}")
        
    except Exception as e:
        print(f"✗ Code type detection failed: {e}")
        return False
    
    print("\n✅ All inline assistance tests passed!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_inline_assistance())
    sys.exit(0 if success else 1)