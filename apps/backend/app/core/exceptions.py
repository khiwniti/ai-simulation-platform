"""
Custom exceptions and error handlers.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    """Exception for resource not found."""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationError(HTTPException):
    """Exception for validation errors."""
    
    def __init__(self, detail: str = "Validation error"):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=detail)


class ConflictError(HTTPException):
    """Exception for resource conflicts."""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class DatabaseError(HTTPException):
    """Exception for database errors."""
    
    def __init__(self, detail: str = "Database error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ErrorResponse:
    """Standard error response format."""
    
    @staticmethod
    def create_error_response(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create standardized error response."""
        response = {
            "error": {
                "code": error_code,
                "message": message
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        return response