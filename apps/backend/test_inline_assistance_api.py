#!/usr/bin/env python3
"""
Test the inline assistance API endpoints.
"""

import asyncio
import sys
import os
import json
from uuid import uuid4

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_inline_assistance_api():
    """Test the inline assistance API endpoints."""
    print("Testing Inline Assistance API...")
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = client.get("/api/v1/inline-assistance/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Health check passed: {data['status']}")
            print(f"  - Service active: {data['service_active']}")
            print(f"  - Supported triggers: {data['supported_triggers']}")
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False
    
    # Test 2: Context analysis
    print("\n2. Testing context analysis...")
    try:
        params = {
            "code_content": "import physx_ai\nscene = physx_ai.create_scene()",
            "cursor_position": "30",
            "line_number": "2",
            "column_number": "10"
        }
        response = client.get("/api/v1/inline-assistance/context-analysis", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Context analysis completed")
            print(f"  - Processing time: {data.get('processing_time', 0):.3f}s")
            if 'context' in data:
                print(f"  - Code type: {data['context'].get('code_type', 'unknown')}")
        else:
            print(f"✗ Context analysis failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Context analysis error: {e}")
        return False
    
    # Test 3: Get suggestions
    print("\n3. Testing get suggestions...")
    try:
        request_data = {
            "session_id": str(uuid4()),
            "notebook_id": str(uuid4()),
            "cell_id": str(uuid4()),
            "code_content": "import physx_ai\nscene = physx_ai.",
            "cursor_position": 30,
            "line_number": 2,
            "column_number": 20,
            "trigger_type": "completion",
            "context": {}
        }
        response = client.post("/api/v1/inline-assistance/suggestions", json=request_data)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ Suggestions retrieved")
            print(f"  - Number of suggestions: {len(data.get('suggestions', []))}")
            print(f"  - Processing time: {data.get('processing_time', 0):.3f}s")
            print(f"  - Agents used: {data.get('agents_used', [])}")
            
            # Store suggestion ID for later tests
            suggestions = data.get('suggestions', [])
            if suggestions:
                global test_suggestion_id
                test_suggestion_id = suggestions[0]['id']
                print(f"  - First suggestion: {suggestions[0].get('text', 'N/A')}")
        else:
            print(f"✗ Get suggestions failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Get suggestions error: {e}")
        return False
    
    print("\n✅ All API tests passed!")
    return True


if __name__ == "__main__":
    success = test_inline_assistance_api()
    sys.exit(0 if success else 1)