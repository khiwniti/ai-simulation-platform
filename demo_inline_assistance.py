#!/usr/bin/env python3
"""
Demonstration of the inline AI assistance system.
"""

import asyncio
import sys
import os

# Add the backend app directory to Python path
sys.path.insert(0, os.path.join('apps', 'backend', 'app'))

async def demo_inline_assistance():
    """Demonstrate the inline assistance system."""
    print("🚀 Inline AI Assistance System Demo\n")
    
    try:
        from services.inline_assistance_service import InlineAssistanceService
        from uuid import uuid4
        
        service = InlineAssistanceService()
        
        print("1. 🧠 Context Analysis Demo")
        print("=" * 40)
        
        # Demo code samples
        physics_code = """import physx_ai
import numpy as np

def create_physics_simulation():
    # Create physics scene
    scene = physx_ai.create_scene()
    
    # Add rigid body
    geometry = physx_ai.BoxGeometry(1, 1, 1)
    material = physx_ai.Material(0.5, 0.5, 0.1)
    body = scene.add_rigid_body(geometry, material)
    
    return scene
"""
        
        # Analyze physics code
        result = await service.analyze_code_context(
            code_content=physics_code,
            cursor_position=150,  # Inside the function
            line_number=8,
            column_number=20
        )
        
        context = result['context']
        print(f"✓ Code Type Detected: {context['code_type']}")
        print(f"✓ Function Context: {context['function_context']}")
        print(f"✓ Import Statements: {len(context['import_statements'])}")
        print(f"✓ Variables in Scope: {len(context['variables_in_scope'])}")
        print(f"✓ Processing Time: {result['processing_time']:.3f}s")
        
        print("\n2. 🤖 Agent Selection Demo")
        print("=" * 40)
        
        # Test agent selection for different contexts
        agents_physics = service._select_agents_for_context(context, 'completion')
        print(f"✓ Physics Code Agents: {agents_physics}")
        
        viz_context = {'code_type': 'visualization', 'syntax_errors': []}
        agents_viz = service._select_agents_for_context(viz_context, 'completion')
        print(f"✓ Visualization Code Agents: {agents_viz}")
        
        error_context = {'code_type': 'general', 'syntax_errors': ['Syntax error']}
        agents_debug = service._select_agents_for_context(error_context, 'manual')
        print(f"✓ Error Code Agents: {agents_debug}")
        
        print("\n3. 🔍 Code Analysis Features")
        print("=" * 40)
        
        # Test different code types
        test_codes = [
            ("Physics", "import physx_ai\nscene = physx_ai.create_scene()"),
            ("Visualization", "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()"),
            ("Math", "import numpy as np\narray = np.array([1,2,3])"),
            ("General", "def hello():\n    print('Hello world')")
        ]
        
        for name, code in test_codes:
            code_type = service._determine_code_type(code)
            print(f"✓ {name} Code → {code_type}")
        
        print("\n4. 🎯 Word Extraction Demo")
        print("=" * 40)
        
        test_line = "scene = physx_ai.create_scene()"
        positions = [0, 8, 15, 25]
        
        for pos in positions:
            word = service._get_word_at_position(test_line, pos)
            char = test_line[pos] if pos < len(test_line) else 'EOF'
            print(f"✓ Position {pos} ('{char}') → Word: '{word}'")
        
        print("\n5. 🔧 Service Status")
        print("=" * 40)
        
        print(f"✓ Service Active: {service.is_active()}")
        print(f"✓ Cache Size: {len(service.suggestion_cache)}")
        print(f"✓ Applied Suggestions: {len(service.applied_suggestions)}")
        print(f"✓ Rejected Suggestions: {len(service.rejected_suggestions)}")
        
        print("\n🎉 Demo Complete!")
        print("=" * 50)
        print("The inline AI assistance system is fully operational!")
        print("\nKey Features Demonstrated:")
        print("• Context-aware code analysis")
        print("• Intelligent agent selection")
        print("• Multi-language code type detection")
        print("• Precise word extraction")
        print("• Real-time performance")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(demo_inline_assistance())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")
    sys.exit(0 if success else 1)