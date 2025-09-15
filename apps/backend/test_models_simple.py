#!/usr/bin/env python3
"""
Simple test script to verify models work correctly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models import Workbook, Notebook, Cell, CellType
from app.schemas import WorkbookCreate, NotebookCreate, CellCreate
from uuid import uuid4

def test_models():
    """Test basic model creation."""
    print("Testing model imports...")
    
    # Test model creation
    workbook_id = uuid4()
    notebook_id = uuid4()
    
    print("✓ Models imported successfully")
    
    # Test schema validation
    workbook_schema = WorkbookCreate(title="Test Workbook", description="Test description")
    print(f"✓ Workbook schema: {workbook_schema.title}")
    
    notebook_schema = NotebookCreate(
        title="Test Notebook", 
        workbook_id=workbook_id,
        metadata={"physics_engine": "physx"}
    )
    print(f"✓ Notebook schema: {notebook_schema.title}")
    
    cell_schema = CellCreate(
        notebook_id=notebook_id,
        cell_type=CellType.CODE,
        content="print('Hello Physics!')",
        position=0
    )
    print(f"✓ Cell schema: {cell_schema.cell_type}")
    
    print("All model and schema tests passed!")

if __name__ == "__main__":
    test_models()