"""
Validate the FastAPI backend structure by checking file existence and basic syntax.
"""

import os
import ast

def check_file_exists(filepath):
    """Check if file exists and return status."""
    if os.path.exists(filepath):
        print(f"✓ {filepath}")
        return True
    else:
        print(f"✗ {filepath} - NOT FOUND")
        return False

def check_python_syntax(filepath):
    """Check if Python file has valid syntax."""
    if not os.path.exists(filepath):
        return False
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        ast.parse(content)
        return True
    except SyntaxError as e:
        print(f"✗ {filepath} - SYNTAX ERROR: {e}")
        return False
    except Exception as e:
        print(f"✗ {filepath} - ERROR: {e}")
        return False

def validate_backend_structure():
    """Validate the complete backend structure."""
    print("Validating FastAPI Backend Structure")
    print("=" * 50)
    
    # Core files
    core_files = [
        "main.py",
        "app/__init__.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/exceptions.py",
        "app/core/error_handlers.py",
        "app/middleware/__init__.py",
        "app/middleware/auth.py",
        "app/api/__init__.py",
        "app/api/deps.py",
        "app/api/v1/__init__.py",
        "app/api/v1/api.py",
        "app/api/v1/workbooks.py",
        "app/api/v1/notebooks.py",
        "app/crud/__init__.py",
        "app/crud/base.py",
        "app/crud/workbook.py",
        "app/crud/notebook.py",
    ]
    
    # Test files
    test_files = [
        "tests/conftest.py",
        "tests/test_api_workbooks.py",
        "tests/test_api_notebooks.py",
        "tests/test_auth_middleware.py",
        "tests/test_error_handling.py",
    ]
    
    # Configuration files
    config_files = [
        "requirements.txt",
        "pyproject.toml",
        "pytest.ini",
    ]
    
    all_files = core_files + test_files + config_files
    
    print("\n1. Checking file existence:")
    print("-" * 30)
    existence_results = [check_file_exists(f) for f in all_files]
    
    print("\n2. Checking Python syntax:")
    print("-" * 30)
    python_files = [f for f in all_files if f.endswith('.py')]
    syntax_results = []
    
    for filepath in python_files:
        if os.path.exists(filepath):
            if check_python_syntax(filepath):
                print(f"✓ {filepath} - Valid syntax")
                syntax_results.append(True)
            else:
                syntax_results.append(False)
        else:
            syntax_results.append(False)
    
    print("\n3. Summary:")
    print("-" * 30)
    files_exist = sum(existence_results)
    total_files = len(all_files)
    syntax_valid = sum(syntax_results)
    total_python = len(python_files)
    
    print(f"Files exist: {files_exist}/{total_files}")
    print(f"Valid syntax: {syntax_valid}/{total_python}")
    
    if files_exist == total_files and syntax_valid == total_python:
        print("\n🎉 Backend structure validation PASSED!")
        return True
    else:
        print("\n❌ Backend structure validation FAILED!")
        return False

if __name__ == "__main__":
    validate_backend_structure()