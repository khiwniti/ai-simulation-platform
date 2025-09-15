"""
Simple test to validate API structure without running the server.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

def test_imports():
    """Test that all modules can be imported successfully."""
    try:
        # Test core imports
        from app.core.config import settings
        from app.core.exceptions import NotFoundError, ValidationError
        from app.core.error_handlers import http_exception_handler
        
        # Test middleware imports
        from app.middleware.auth import AuthMiddleware
        
        # Test CRUD imports
        from app.crud.workbook import workbook
        from app.crud.notebook import notebook
        
        # Test API imports
        from app.api.v1.workbooks import router as workbook_router
        from app.api.v1.notebooks import router as notebook_router
        from app.api.v1.api import api_router
        
        # Test main app import
        from app.main import app
        
        print("✓ All imports successful")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_api_structure():
    """Test API structure and configuration."""
    try:
        from app.main import app
        from app.core.config import settings
        
        # Check app configuration
        assert app.title == settings.PROJECT_NAME
        assert app.version == settings.VERSION
        
        # Check routes are registered
        routes = [route.path for route in app.routes]
        
        # Should have basic routes
        assert "/" in routes
        assert "/health" in routes
        
        print("✓ API structure validation successful")
        return True
        
    except Exception as e:
        print(f"✗ API structure error: {e}")
        return False

def test_schema_validation():
    """Test schema definitions."""
    try:
        from app.schemas.workbook import WorkbookCreate, WorkbookResponse
        from app.schemas.notebook import NotebookCreate, NotebookResponse
        
        # Test workbook schema
        workbook_data = {
            "title": "Test Workbook",
            "description": "Test description"
        }
        workbook_create = WorkbookCreate(**workbook_data)
        assert workbook_create.title == "Test Workbook"
        
        # Test notebook schema
        from uuid import uuid4
        notebook_data = {
            "title": "Test Notebook",
            "workbook_id": uuid4()
        }
        notebook_create = NotebookCreate(**notebook_data)
        assert notebook_create.title == "Test Notebook"
        
        print("✓ Schema validation successful")
        return True
        
    except Exception as e:
        print(f"✗ Schema validation error: {e}")
        return False

def test_crud_operations():
    """Test CRUD class definitions."""
    try:
        from app.crud.workbook import CRUDWorkbook
        from app.crud.notebook import CRUDNotebook
        from app.models.workbook import Workbook
        from app.models.notebook import Notebook
        
        # Test CRUD class instantiation
        workbook_crud = CRUDWorkbook(Workbook)
        notebook_crud = CRUDNotebook(Notebook)
        
        # Check methods exist
        assert hasattr(workbook_crud, 'get')
        assert hasattr(workbook_crud, 'create')
        assert hasattr(workbook_crud, 'update')
        assert hasattr(workbook_crud, 'remove')
        
        print("✓ CRUD operations validation successful")
        return True
        
    except Exception as e:
        print(f"✗ CRUD operations error: {e}")
        return False

if __name__ == "__main__":
    print("Testing FastAPI backend structure...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_api_structure,
        test_schema_validation,
        test_crud_operations
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 All tests passed! FastAPI backend structure is valid.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)