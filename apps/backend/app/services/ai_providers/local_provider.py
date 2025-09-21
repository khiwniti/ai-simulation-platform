"""
Local AI Provider for code suggestions using local models or fallback implementations.
"""

import time
import random
import asyncio
from typing import Dict, List, Any, Optional, AsyncGenerator
from .base_provider import (
    BaseAIProvider,
    AIProviderConfig,
    CodeSuggestionRequest,
    CodeSuggestion,
    AIProviderResponse,
)


class LocalAIProvider(BaseAIProvider):
    """
    Local AI provider that provides basic code suggestions without external APIs.

    This provider serves as:
    1. A fallback when external providers are unavailable
    2. A testing/development provider
    3. A template for implementing custom local models

    Features:
    - Basic code completion using pattern matching
    - Simple syntax error detection
    - Common physics and visualization snippets
    - Fast response times
    """

    def __init__(self, config: AIProviderConfig):
        super().__init__(config)

        # Physics-related completions
        self.physics_completions = {
            "import": [
                "import numpy as np",
                "import physx_ai as px",
                "from physx_ai import scene, rigidbody",
                "import scipy.spatial",
                "import matplotlib.pyplot as plt",
            ],
            "scene": [
                "scene = px.create_scene(gravity=(0, -9.81, 0))",
                "scene.set_timestep(1.0/60.0)",
                "scene.add_actor(actor)",
                "scene.simulate(timestep)",
            ],
            "rigidbody": [
                "body = px.create_rigidbody(geometry, material)",
                "body.set_position((x, y, z))",
                "body.set_velocity((vx, vy, vz))",
                "body.add_force((fx, fy, fz))",
            ],
            "geometry": [
                "box_geometry = px.BoxGeometry(width, height, depth)",
                "sphere_geometry = px.SphereGeometry(radius)",
                "plane_geometry = px.PlaneGeometry()",
                "mesh_geometry = px.MeshGeometry(vertices, indices)",
            ],
        }

        # Visualization completions
        self.viz_completions = {
            "three": [
                "scene = new THREE.Scene()",
                "camera = new THREE.PerspectiveCamera(75, width/height, 0.1, 1000)",
                "renderer = new THREE.WebGLRenderer()",
                "mesh = new THREE.Mesh(geometry, material)",
            ],
            "matplotlib": [
                "fig, ax = plt.subplots()",
                "plt.plot(x, y)",
                "plt.scatter(x, y, z)",
                "plt.show()",
            ],
        }

        # Common patterns and fixes
        self.common_fixes = {
            "IndentationError": "Check your indentation - Python requires consistent spacing",
            "SyntaxError": "Check for missing parentheses, brackets, or quotes",
            "NameError": "Variable not defined - check spelling and scope",
            "TypeError": "Check data types and function arguments",
            "ImportError": "Module not found - check installation and import path",
        }

    async def _initialize_provider(self) -> None:
        """Initialize local provider."""
        # No external dependencies to initialize
        pass

    async def _get_suggestions_impl(
        self, request: CodeSuggestionRequest
    ) -> AIProviderResponse:
        """Get suggestions using local patterns and rules."""
        start_time = time.time()

        try:
            suggestions = []

            if request.suggestion_type == "completion":
                suggestions = self._get_completion_suggestions(request)
            elif request.suggestion_type == "explanation":
                suggestions = self._get_explanation_suggestions(request)
            elif request.suggestion_type == "fix":
                suggestions = self._get_fix_suggestions(request)
            elif request.suggestion_type == "optimization":
                suggestions = self._get_optimization_suggestions(request)

            return AIProviderResponse(
                suggestions=suggestions,
                processing_time=time.time() - start_time,
                tokens_used=len(request.code_context.split()),  # Approximate
                model_used="local-patterns",
                provider_name="local",
            )

        except Exception as e:
            return AIProviderResponse(
                suggestions=[],
                processing_time=time.time() - start_time,
                tokens_used=0,
                model_used="local-patterns",
                provider_name="local",
                error=str(e),
            )

    def _get_completion_suggestions(
        self, request: CodeSuggestionRequest
    ) -> List[CodeSuggestion]:
        """Get code completion suggestions based on patterns."""
        suggestions = []
        context = request.code_context.lower()

        # Get current line and word
        lines = request.code_context.split("\n")
        current_pos = 0
        current_line = ""

        for line in lines:
            if current_pos + len(line) + 1 > request.cursor_position:
                current_line = line
                break
            current_pos += len(line) + 1

        current_word = self._get_current_word(
            current_line, request.cursor_position - current_pos
        )

        # Physics completions
        if any(term in context for term in ["physics", "physx", "simulation"]):
            suggestions.extend(
                self._get_physics_completions(current_word, current_line)
            )

        # Visualization completions
        if any(term in context for term in ["three", "plot", "matplotlib", "viz"]):
            suggestions.extend(self._get_viz_completions(current_word, current_line))

        # Common Python completions
        suggestions.extend(self._get_python_completions(current_word, current_line))

        return suggestions

    def _get_explanation_suggestions(
        self, request: CodeSuggestionRequest
    ) -> List[CodeSuggestion]:
        """Get code explanation suggestions."""
        context = request.code_context.lower()

        explanations = []

        # Physics explanations
        if "physx" in context or "physics" in context:
            explanations.append(
                CodeSuggestion(
                    id=f"local_explain_{int(time.time() * 1000)}",
                    text="Physics Simulation Code",
                    explanation="This code appears to be setting up a physics simulation using PhysX AI. "
                    "It likely involves creating rigid bodies, defining materials, and running "
                    "time-stepped simulations to model physical interactions.",
                    confidence_score=0.7,
                    suggestion_type="explanation",
                    provider_name="local",
                    model_used="local-patterns",
                )
            )

        # Visualization explanations
        if any(term in context for term in ["three", "scene", "camera", "renderer"]):
            explanations.append(
                CodeSuggestion(
                    id=f"local_explain_{int(time.time() * 1000)}_1",
                    text="3D Visualization Code",
                    explanation="This appears to be 3D graphics code, likely using Three.js. "
                    "It involves creating scenes, cameras, renderers, and 3D objects "
                    "for interactive visualization in a web browser.",
                    confidence_score=0.7,
                    suggestion_type="explanation",
                    provider_name="local",
                    model_used="local-patterns",
                )
            )

        # Fallback explanation
        if not explanations:
            explanations.append(
                CodeSuggestion(
                    id=f"local_explain_{int(time.time() * 1000)}_fallback",
                    text="Code Analysis",
                    explanation="This code appears to be a Python script. For more detailed analysis, "
                    "consider using an AI-powered code assistant or adding comments to "
                    "describe the code's purpose.",
                    confidence_score=0.5,
                    suggestion_type="explanation",
                    provider_name="local",
                    model_used="local-patterns",
                )
            )

        return explanations

    def _get_fix_suggestions(
        self, request: CodeSuggestionRequest
    ) -> List[CodeSuggestion]:
        """Get code fix suggestions based on common patterns."""
        fixes = []
        code = request.code_context

        # Check for common syntax issues
        if code.count("(") != code.count(")"):
            fixes.append(
                CodeSuggestion(
                    id=f"local_fix_{int(time.time() * 1000)}",
                    text="Mismatched Parentheses",
                    explanation="There's a mismatch in parentheses. Check that every opening '(' has a corresponding closing ')'.",
                    confidence_score=0.8,
                    suggestion_type="fix",
                    provider_name="local",
                    model_used="local-patterns",
                )
            )

        if code.count("[") != code.count("]"):
            fixes.append(
                CodeSuggestion(
                    id=f"local_fix_{int(time.time() * 1000)}_1",
                    text="Mismatched Brackets",
                    explanation="There's a mismatch in square brackets. Check that every opening '[' has a corresponding closing ']'.",
                    confidence_score=0.8,
                    suggestion_type="fix",
                    provider_name="local",
                    model_used="local-patterns",
                )
            )

        # Check for indentation issues
        lines = code.split("\n")
        for i, line in enumerate(lines):
            if line.strip() and not line[0].isspace() and line.strip().endswith(":"):
                if (
                    i + 1 < len(lines)
                    and lines[i + 1].strip()
                    and not lines[i + 1].startswith("    ")
                ):
                    fixes.append(
                        CodeSuggestion(
                            id=f"local_fix_{int(time.time() * 1000)}_{i}",
                            text="Indentation Error",
                            explanation=f"Line {i + 2} may need proper indentation after the colon on line {i + 1}.",
                            confidence_score=0.7,
                            suggestion_type="fix",
                            provider_name="local",
                            model_used="local-patterns",
                        )
                    )

        return fixes

    def _get_optimization_suggestions(
        self, request: CodeSuggestionRequest
    ) -> List[CodeSuggestion]:
        """Get code optimization suggestions."""
        optimizations = []
        context = request.code_context.lower()

        # List comprehension suggestion
        if "for" in context and "append" in context:
            optimizations.append(
                CodeSuggestion(
                    id=f"local_opt_{int(time.time() * 1000)}",
                    text="Consider List Comprehension",
                    explanation="If you're using a loop to append items to a list, "
                    "consider using list comprehension for better performance: "
                    "[item for item in iterable if condition]",
                    confidence_score=0.6,
                    suggestion_type="optimization",
                    provider_name="local",
                    model_used="local-patterns",
                )
            )

        # NumPy optimization
        if "for" in context and any(
            term in context for term in ["array", "math", "numpy"]
        ):
            optimizations.append(
                CodeSuggestion(
                    id=f"local_opt_{int(time.time() * 1000)}_1",
                    text="Vectorize with NumPy",
                    explanation="Consider using NumPy vectorized operations instead of loops "
                    "for better performance with numerical computations.",
                    confidence_score=0.7,
                    suggestion_type="optimization",
                    provider_name="local",
                    model_used="local-patterns",
                )
            )

        return optimizations

    def _get_physics_completions(
        self, current_word: str, current_line: str
    ) -> List[CodeSuggestion]:
        """Get physics-specific completions."""
        completions = []

        for category, items in self.physics_completions.items():
            if (
                category.startswith(current_word.lower())
                or current_word.lower() in category
            ):
                for i, item in enumerate(items[:3]):  # Limit to 3 per category
                    completions.append(
                        CodeSuggestion(
                            id=f"local_physics_{category}_{i}",
                            text=f"Physics: {item}",
                            insert_text=item,
                            confidence_score=0.7,
                            suggestion_type="completion",
                            provider_name="local",
                            model_used="local-patterns",
                        )
                    )

        return completions

    def _get_viz_completions(
        self, current_word: str, current_line: str
    ) -> List[CodeSuggestion]:
        """Get visualization-specific completions."""
        completions = []

        for category, items in self.viz_completions.items():
            if (
                category.startswith(current_word.lower())
                or current_word.lower() in category
            ):
                for i, item in enumerate(items[:3]):
                    completions.append(
                        CodeSuggestion(
                            id=f"local_viz_{category}_{i}",
                            text=f"Visualization: {item}",
                            insert_text=item,
                            confidence_score=0.7,
                            suggestion_type="completion",
                            provider_name="local",
                            model_used="local-patterns",
                        )
                    )

        return completions

    def _get_python_completions(
        self, current_word: str, current_line: str
    ) -> List[CodeSuggestion]:
        """Get common Python completions."""
        completions = []

        common_patterns = {
            "if": "if condition:",
            "for": "for item in iterable:",
            "def": "def function_name():",
            "class": "class ClassName:",
            "try": "try:\n    # code\nexcept Exception as e:\n    # handle error",
            "with": "with open('file.txt', 'r') as f:",
            "import": "import module_name",
            "from": "from module import function",
        }

        for keyword, pattern in common_patterns.items():
            if keyword.startswith(current_word.lower()) and len(current_word) > 0:
                completions.append(
                    CodeSuggestion(
                        id=f"local_python_{keyword}",
                        text=f"Python: {keyword} statement",
                        insert_text=pattern,
                        confidence_score=0.6,
                        suggestion_type="completion",
                        provider_name="local",
                        model_used="local-patterns",
                    )
                )

        return completions

    def _get_current_word(self, line: str, column: int) -> str:
        """Extract the current word at cursor position."""
        if column >= len(line):
            return ""

        start = column
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1

        end = column
        while end < len(line) and (line[end].isalnum() or line[end] == "_"):
            end += 1

        return line[start:end]

    async def _get_streaming_suggestions_impl(
        self, request: CodeSuggestionRequest
    ) -> AsyncGenerator[CodeSuggestion, None]:
        """Get streaming suggestions (simulated for local provider)."""
        # Get all suggestions first
        response = await self._get_suggestions_impl(request)

        # Simulate streaming by yielding with small delays
        for suggestion in response.suggestions:
            yield suggestion
            # Small delay to simulate streaming
            await asyncio.sleep(0.1)
