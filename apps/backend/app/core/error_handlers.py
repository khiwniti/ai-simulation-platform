"""
Global error handlers for FastAPI.
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.core.exceptions import ErrorResponse
import logging

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.create_error_response(
            error_code=f"HTTP_{exc.status_code}",
            message=exc.detail
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(x) for x in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content=ErrorResponse.create_error_response(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"errors": errors}
        )
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database errors."""
    logger.error(f"Database error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create_error_response(
            error_code="DATABASE_ERROR",
            message="A database error occurred"
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle general exceptions."""
    logger.error(f"Unexpected error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse.create_error_response(
            error_code="INTERNAL_ERROR",
            message="An internal server error occurred"
        )
    )