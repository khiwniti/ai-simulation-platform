"""
Authentication and authorization middleware.
"""

from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.core.config import settings

# Security scheme for JWT tokens
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for JWT tokens."""
    
    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user.
    For now, this is a simple implementation that accepts any valid JWT.
    In production, this would validate against a user database.
    """
    token = credentials.credentials
    payload = AuthMiddleware.verify_token(token)
    
    # For now, return a mock user. In production, fetch from database
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )
    
    return {"id": user_id, "username": payload.get("username", "user")}


def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[dict]:
    """
    Optional authentication dependency.
    Returns user if authenticated, None otherwise.
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None