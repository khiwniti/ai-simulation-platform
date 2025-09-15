print("Starting test...")

try:
    import uuid
    print("✓ uuid imported")
    
    from sqlalchemy import Column, String
    print("✓ SQLAlchemy imported")
    
    from pydantic import BaseModel
    print("✓ Pydantic imported")
    
    print("All basic imports successful!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()