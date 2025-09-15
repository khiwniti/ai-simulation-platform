"""
Database configuration and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Database URL from environment variable or default for development
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:password@localhost:5432/ai_jupyter_notebook"
)

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
    echo=os.getenv("SQL_DEBUG", "false").lower() == "true"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()