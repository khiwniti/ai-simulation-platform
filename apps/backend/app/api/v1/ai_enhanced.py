"""
Enhanced AI API endpoints for code suggestions and smart features.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.notebook import Notebook
from app.services.ai_enhanced import (
    ai_suggestion_engine,
    code_analyzer,
    context_manager,
    template_engine,
)

router = APIRouter()
logger = logging.getLogger(__name__)


class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    notebook_id: Optional[str] = None
    cell_id: Optional[str] = None


class CodeSuggestionRequest(BaseModel):
    code: str
    language: str = "python"
    notebook_id: Optional[str] = None
    cell_id: Optional[str] = None
    suggestion_type: str = "all"  # all, completion, optimization, error_fix


class TemplateRequest(BaseModel):
    topic: Optional[str] = None
    language: str = "python"
    requirements: Optional[str] = None
    notebook_id: Optional[str] = None


class ContextRequest(BaseModel):
    notebook_id: Optional[str] = None
    cell_id: Optional[str] = None


@router.post("/analyze-code")
async def analyze_code(
    request: CodeAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Analyze code and provide insights."""
    try:
        # Get notebook and cell if provided
        notebook = None
        cell = None

        if request.notebook_id:
            notebook = (
                db.query(Notebook)
                .filter(
                    Notebook.id == request.notebook_id,
                    Notebook.user_id == current_user.id,
                )
                .first()
            )

            if not notebook:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found"
                )

        if request.cell_id and notebook:
            cell = next(
                (c for c in notebook.cells if str(c.id) == request.cell_id), None
            )

        # Analyze code
        analysis = code_analyzer.analyze_code(request.code, request.language)

        # Build context
        context = context_manager.build_context(current_user, notebook, cell)

        return {
            "analysis": analysis,
            "context": context,
            "timestamp": context["session"]["timestamp"],
        }

    except Exception as e:
        logger.error(f"Code analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Code analysis failed",
        )


@router.post("/code-suggestions")
async def get_code_suggestions(
    request: CodeSuggestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get AI-powered code suggestions."""
    try:
        # Get notebook and cell if provided
        notebook = None
        cell = None

        if request.notebook_id:
            notebook = (
                db.query(Notebook)
                .filter(
                    Notebook.id == request.notebook_id,
                    Notebook.user_id == current_user.id,
                )
                .first()
            )

        if request.cell_id and notebook:
            cell = next(
                (c for c in notebook.cells if str(c.id) == request.cell_id), None
            )

        # Get suggestions
        suggestions = ai_suggestion_engine.get_code_suggestions(
            current_user, request.code, request.language, notebook, cell
        )

        # Filter by suggestion type if specified
        if request.suggestion_type != "all":
            filtered_suggestions = {}
            if request.suggestion_type == "completion":
                filtered_suggestions["completion_suggestions"] = suggestions.get(
                    "completion_suggestions", []
                )
            elif request.suggestion_type == "optimization":
                filtered_suggestions["optimization_tips"] = suggestions.get(
                    "optimization_tips", []
                )
            elif request.suggestion_type == "error_fix":
                filtered_suggestions["error_fixes"] = suggestions.get("error_fixes", [])
            else:
                filtered_suggestions = suggestions

            suggestions = filtered_suggestions

        return {
            "suggestions": suggestions,
            "request_type": request.suggestion_type,
            "language": request.language,
        }

    except Exception as e:
        logger.error(f"Code suggestions failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate code suggestions",
        )


@router.post("/smart-templates")
async def get_smart_templates(
    request: TemplateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get smart code templates based on context."""
    try:
        # Get notebook if provided
        notebook = None
        if request.notebook_id:
            notebook = (
                db.query(Notebook)
                .filter(
                    Notebook.id == request.notebook_id,
                    Notebook.user_id == current_user.id,
                )
                .first()
            )

        # Build context
        context = context_manager.build_context(current_user, notebook)

        # Get relevant templates
        if request.requirements:
            # Generate custom template
            custom_template = template_engine.generate_custom_template(
                context, request.requirements
            )
            templates = [custom_template]
        else:
            # Get relevant templates
            templates = template_engine.get_relevant_templates(context)

        return {
            "templates": templates,
            "context_topics": context.get("notebook_context", {}).get("topics", []),
            "language": request.language,
        }

    except Exception as e:
        logger.error(f"Smart templates failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate smart templates",
        )


@router.post("/context")
async def get_context(
    request: ContextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get context information for AI assistance."""
    try:
        # Get notebook and cell if provided
        notebook = None
        cell = None

        if request.notebook_id:
            notebook = (
                db.query(Notebook)
                .filter(
                    Notebook.id == request.notebook_id,
                    Notebook.user_id == current_user.id,
                )
                .first()
            )

            if not notebook:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Notebook not found"
                )

        if request.cell_id and notebook:
            cell = next(
                (c for c in notebook.cells if str(c.id) == request.cell_id), None
            )

        # Build context
        context = context_manager.build_context(current_user, notebook, cell)

        return context

    except Exception as e:
        logger.error(f"Context retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve context",
        )


@router.get("/code-patterns")
async def get_code_patterns(
    language: str = "python", current_user: User = Depends(get_current_user)
):
    """Get common code patterns and best practices."""
    try:
        patterns = {
            "python": {
                "data_structures": [
                    {
                        "name": "List Comprehension",
                        "pattern": "[expression for item in iterable if condition]",
                        "example": "squares = [x**2 for x in range(10) if x % 2 == 0]",
                        "description": "Efficient way to create lists",
                    },
                    {
                        "name": "Dictionary Comprehension",
                        "pattern": "{key: value for item in iterable}",
                        "example": "word_lengths = {word: len(word) for word in words}",
                        "description": "Create dictionaries efficiently",
                    },
                ],
                "error_handling": [
                    {
                        "name": "Try-Except Block",
                        "pattern": ("try:\n    # code\nexcept SpecificError as e:"
                                   "\n    # handle error"),
                        "example": ("try:\n    result = 10 / x\nexcept "
                                   "ZeroDivisionError:\n    result = 0"),
                        "description": "Handle specific exceptions",
                    }
                ],
                "best_practices": [
                    {
                        "name": "Function Documentation",
                        "pattern": 'def function(param):\n    """Description."""\n    return result',
                        "example": 'def calculate_area(radius):\n    """Calculate circle area."""\n    return 3.14159 * radius ** 2',
                        "description": "Always document your functions",
                    }
                ],
            },
            "javascript": {
                "modern_syntax": [
                    {
                        "name": "Arrow Functions",
                        "pattern": "(param) => expression",
                        "example": "const square = x => x * x",
                        "description": "Concise function syntax",
                    },
                    {
                        "name": "Destructuring",
                        "pattern": "const {prop1, prop2} = object",
                        "example": "const {name, age} = person",
                        "description": "Extract properties from objects",
                    },
                ]
            },
        }

        return {
            "language": language,
            "patterns": patterns.get(language, {}),
            "available_languages": list(patterns.keys()),
        }

    except Exception as e:
        logger.error(f"Code patterns retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve code patterns",
        )


@router.post("/explain-code")
async def explain_code(
    request: CodeAnalysisRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Explain what a piece of code does."""
    try:
        # Analyze the code
        analysis = code_analyzer.analyze_code(request.code, request.language)

        # Generate explanation based on analysis
        explanation = {
            "summary": f"This {request.language} code contains {analysis.get('line_count', 0)} lines",
            "components": [],
            "complexity": analysis.get("complexity_score", 0),
            "suggestions": analysis.get("suggestions", []),
        }

        # Add component explanations
        if analysis.get("imports"):
            explanation["components"].append(
                {
                    "type": "imports",
                    "description": f"Imports {len(analysis['imports'])} modules/libraries",
                    "items": analysis["imports"],
                }
            )

        if analysis.get("functions"):
            explanation["components"].append(
                {
                    "type": "functions",
                    "description": f"Defines {len(analysis['functions'])} functions",
                    "items": analysis["functions"],
                }
            )

        if analysis.get("classes"):
            explanation["components"].append(
                {
                    "type": "classes",
                    "description": f"Defines {len(analysis['classes'])} classes",
                    "items": analysis["classes"],
                }
            )

        if analysis.get("variables"):
            explanation["components"].append(
                {
                    "type": "variables",
                    "description": f"Creates {len(analysis['variables'])} variables",
                    "items": analysis["variables"][:10],  # Limit to first 10
                }
            )

        return explanation

    except Exception as e:
        logger.error(f"Code explanation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to explain code",
        )
