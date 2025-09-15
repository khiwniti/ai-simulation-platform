"""
API dependencies.
"""

from typing import Generator, Dict, Any
from sqlalchemy.orm import Session
from app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user() -> Dict[str, Any]:
    """
    Dependency to get current user.
    For now, returns a mock user since authentication is not implemented.
    """
    return {
        "id": "mock-user-id",
        "username": "mock-user",
        "email": "mock@example.com"
    }