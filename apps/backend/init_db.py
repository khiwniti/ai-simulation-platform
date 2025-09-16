#!/usr/bin/env python3
"""
Database initialization script for AI Jupyter Notebook platform.
"""

import os
import sys
from sqlalchemy import create_engine
from app.database import Base
from app.models import *

def init_database():
    """Initialize the database with all tables."""
    
    # Get database URL
    database_url = os.getenv(
        "DATABASE_URL", 
        "sqlite:///./ai_jupyter_notebook.db"
    )
    
    print(f"Initializing database: {database_url}")
    
    # Create engine
    engine = create_engine(database_url)
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully!")
        
        # Print created tables
        print("\nCreated tables:")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")
            
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_database()