"""
Anthropic Claude Provider for code suggestions.
"""

import os
import json
import time
from typing import Dict, List, Any, Optional, AsyncGenerator
from .base_provider import (
    BaseAIProvider, 
    AIProviderConfig, 
    CodeSuggestionRequest, 
    CodeSuggestion, 
    AIProviderResponse
)

try:
    import anthropic
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    AsyncAnthropic = None


class AnthropicProvider(BaseAIProvider):
    """
    Anthropic Claude provider for code suggestions.
    
    Supports:
    - Claude 3 (Haiku, Sonnet, Opus) for code completion and analysis
    - Streaming responses for real-time suggestions
    - Long context understanding (up to 200k tokens)
    - Advanced reasoning for complex code analysis
    """
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.client: Optional[AsyncAnthropic] = None
        
        # Model configurations
        self.model_configs = {
            "claude-3-haiku-20240307": {
                "max_tokens": 4096,
                "context_length": 200000,
                "cost_per_1k_tokens": 0.00025
            },
            "claude-3-sonnet-20240229": {
                "max_tokens": 4096,
                "context_length": 200000,
                "cost_per_1k_tokens": 0.003
            },
            "claude-3-opus-20240229": {
                "max_tokens": 4096,
                "context_length": 200000,
                "cost_per_1k_tokens": 0.015
            }
        }
    
    async def _initialize_provider(self) -> None:
        """Initialize Anthropic client."""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("Anthropic library not available. Install with: pip install anthropic")
        
        api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("Anthropic API key not provided")
        
        self.client = AsyncAnthropic(
            api_key=api_key,
            base_url=self.config.base_url
        )
    
    async def _get_suggestions_impl(
        self, 
        request: CodeSuggestionRequest
    ) -> AIProviderResponse:
        """Get code suggestions from Anthropic Claude."""
        start_time = time.time()
        
        try:
            # Build the prompt
            system_prompt = self._get_system_prompt(request.suggestion_type, request.language)
            user_prompt = self._get_user_prompt(request)
            
            # Make API call
            response = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=min(self.config.max_tokens, self._get_max_tokens_for_model()),
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            # Parse suggestions
            suggestions = self._parse_response(response, request)
            
            # Get token usage
            tokens_used = 0
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.input_tokens + response.usage.output_tokens
            
            return AIProviderResponse(
                suggestions=suggestions,
                processing_time=time.time() - start_time,
                tokens_used=tokens_used,
                model_used=self.config.model_name,
                provider_name="anthropic"
            )
            
        except Exception as e:
            return AIProviderResponse(
                suggestions=[],
                processing_time=time.time() - start_time,
                tokens_used=0,
                model_used=self.config.model_name,
                provider_name="anthropic",
                error=str(e)
            )
    
    async def _get_streaming_suggestions_impl(
        self, 
        request: CodeSuggestionRequest
    ) -> AsyncGenerator[CodeSuggestion, None]:
        """Get streaming suggestions from Anthropic Claude."""
        try:
            system_prompt = self._get_system_prompt(request.suggestion_type, request.language)
            user_prompt = self._get_user_prompt(request)
            
            stream = await self.client.messages.create(
                model=self.config.model_name,
                max_tokens=min(self.config.max_tokens, self._get_max_tokens_for_model()),
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                stream=True
            )
            
            current_suggestion = ""
            suggestion_id = f"anthropic_{int(time.time() * 1000)}"
            
            async for chunk in stream:
                if chunk.type == "content_block_delta" and hasattr(chunk, 'delta'):
                    if hasattr(chunk.delta, 'text'):
                        current_suggestion += chunk.delta.text
                        
                        # Yield incremental suggestion
                        yield CodeSuggestion(
                            id=suggestion_id,
                            text=current_suggestion,
                            insert_text=current_suggestion,
                            confidence_score=0.85,
                            suggestion_type=request.suggestion_type,
                            provider_name="anthropic",
                            model_used=self.config.model_name,
                            processing_time=time.time()
                        )
            
        except Exception as e:
            # Fallback to non-streaming
            response = await self._get_suggestions_impl(request)
            for suggestion in response.suggestions:
                yield suggestion
    
    def _get_system_prompt(self, suggestion_type: str, language: str) -> str:
        """Get system prompt for Claude."""
        base_prompt = f"""You are Claude, an AI assistant specialized in {language} programming with expertise in:

- Physics simulation and NVIDIA PhysX AI
- 3D visualization with Three.js and WebGL
- Scientific computing with NumPy, SciPy, and related libraries
- Machine learning and AI frameworks
- Performance optimization and code quality
- Debugging and error resolution

You provide accurate, efficient, and well-documented code suggestions with clear explanations."""

        if suggestion_type == "completion":
            return base_prompt + """

For code completion tasks:
1. Analyze the code context thoroughly
2. Provide multiple relevant completion options
3. Consider variable scope, imports, and function signatures
4. Follow Python best practices and PEP 8 style
5. Include brief descriptions for each suggestion

Format your response as JSON:
{
  "completions": [
    {
      "code": "suggested completion",
      "description": "what this does",
      "confidence": 0.9
    }
  ]
}"""

        elif suggestion_type == "explanation":
            return base_prompt + """

For code explanation tasks:
1. Provide clear, comprehensive explanations
2. Break down complex concepts into understandable parts
3. Explain the purpose and functionality
4. Identify key libraries, frameworks, and patterns used
5. Mention potential improvements or considerations

Provide detailed explanations in natural language."""

        elif suggestion_type == "fix":
            return base_prompt + """

For code fixing tasks:
1. Identify all syntax errors, bugs, and logical issues
2. Provide corrected code with clear explanations
3. Explain why each fix is necessary
4. Suggest preventive measures for similar issues
5. Consider edge cases and error handling

Format your response as JSON:
{
  "fixes": [
    {
      "issue": "description of the problem",
      "solution": "corrected code",
      "explanation": "detailed explanation of the fix",
      "severity": "high|medium|low"
    }
  ]
}"""

        elif suggestion_type == "optimization":
            return base_prompt + """

For code optimization tasks:
1. Analyze performance bottlenecks and inefficiencies
2. Suggest algorithmic improvements and better data structures
3. Recommend Python-specific optimizations
4. Consider memory usage, time complexity, and readability
5. Provide performance estimates when possible

Format your response as JSON:
{
  "optimizations": [
    {
      "current": "current implementation",
      "improved": "optimized version",
      "benefit": "description of improvement",
      "impact": "high|medium|low",
      "reasoning": "detailed explanation"
    }
  ]
}"""

        return base_prompt
    
    def _get_user_prompt(self, request: CodeSuggestionRequest) -> str:
        """Build user prompt with context for Claude."""
        context = request.code_context
        cursor_pos = request.cursor_position
        
        # Extract context around cursor position
        lines = context.split('\n')
        
        # Find current line
        current_pos = 0
        current_line_idx = 0
        for i, line in enumerate(lines):
            if current_pos + len(line) + 1 > cursor_pos:
                current_line_idx = i
                break
            current_pos += len(line) + 1
        
        # Get broader context for Claude (it can handle more)
        start_line = max(0, current_line_idx - 10)
        end_line = min(len(lines), current_line_idx + 11)
        context_lines = lines[start_line:end_line]
        
        # Mark cursor position
        if current_line_idx - start_line < len(context_lines):
            cursor_line = context_lines[current_line_idx - start_line]
            col_pos = cursor_pos - current_pos
            if 0 <= col_pos <= len(cursor_line):
                cursor_line = cursor_line[:col_pos] + "│" + cursor_line[col_pos:]
                context_lines[current_line_idx - start_line] = cursor_line
        
        formatted_context = '\n'.join(context_lines)
        
        # Add additional context if available
        additional_info = ""
        if request.additional_context:
            imports = request.additional_context.get('imports', [])
            variables = request.additional_context.get('variables', [])
            function_context = request.additional_context.get('function_context')
            
            if imports:
                additional_info += f"\nImports in scope: {', '.join(imports)}"
            if variables:
                additional_info += f"\nVariables in scope: {', '.join(variables)}"
            if function_context:
                additional_info += f"\nCurrent function: {function_context}"
        
        if request.suggestion_type == "completion":
            return f"""I need code completion suggestions for the cursor position (marked with │):

```python
{formatted_context}
```

Context details:
- Cursor position: {cursor_pos} (line {current_line_idx + 1})
- Language: {request.language}
- Max suggestions: {request.max_suggestions}{additional_info}

Please provide {request.max_suggestions} relevant code completion suggestions considering the context, variable scope, and coding patterns. Focus on practical, useful completions that would help the developer continue writing code efficiently."""

        elif request.suggestion_type == "explanation":
            return f"""Please explain the following code, focusing on the area around the cursor (marked with │):

```python
{formatted_context}
```

Provide a comprehensive explanation covering:
- What this code does and its purpose
- Key concepts and patterns used
- Any libraries or frameworks involved
- Potential improvements or considerations{additional_info}"""

        elif request.suggestion_type == "fix":
            return f"""Please analyze this code for errors and provide fixes. The cursor position is marked with │:

```python
{formatted_context}
```

Look for:
- Syntax errors
- Logical bugs
- Runtime issues
- Type errors
- Best practice violations{additional_info}

Provide specific fixes with explanations."""

        elif suggestion_type == "optimization":
            return f"""Please analyze this code for optimization opportunities. Focus on the area around the cursor (marked with │):

```python
{formatted_context}
```

Consider:
- Performance bottlenecks
- Algorithmic improvements
- Memory optimization
- Python-specific optimizations
- Code readability{additional_info}

Suggest concrete improvements with reasoning."""

        return f"""Please analyze this code context:

```python
{formatted_context}
```

The cursor is at the position marked with │. Provide helpful insights and suggestions based on the code.{additional_info}"""
    
    def _parse_response(
        self, 
        response: Any, 
        request: CodeSuggestionRequest
    ) -> List[CodeSuggestion]:
        """Parse Anthropic response into code suggestions."""
        suggestions = []
        
        try:
            content = response.content[0].text if response.content else ""
            
            # Try to parse as JSON first
            try:
                parsed = json.loads(content)
                suggestions.extend(self._parse_json_response(parsed, request))
            except json.JSONDecodeError:
                # Treat as plain text suggestion
                suggestions.append(CodeSuggestion(
                    id=f"anthropic_{int(time.time() * 1000)}",
                    text=content,
                    insert_text=content if request.suggestion_type == "completion" else None,
                    confidence_score=0.85,
                    explanation=content if request.suggestion_type != "completion" else None,
                    suggestion_type=request.suggestion_type,
                    provider_name="anthropic",
                    model_used=self.config.model_name
                ))
        
        except Exception as e:
            print(f"Error parsing Anthropic response: {e}")
        
        return suggestions
    
    def _parse_json_response(
        self, 
        parsed: Dict[str, Any], 
        request: CodeSuggestionRequest
    ) -> List[CodeSuggestion]:
        """Parse JSON response from Claude."""
        suggestions = []
        
        # Handle different response formats
        if "completions" in parsed:
            for i, item in enumerate(parsed["completions"]):
                suggestions.append(CodeSuggestion(
                    id=f"anthropic_{int(time.time() * 1000)}_{i}",
                    text=item.get("description", item.get("code", "")),
                    insert_text=item.get("code"),
                    confidence_score=item.get("confidence", 0.85),
                    suggestion_type=request.suggestion_type,
                    provider_name="anthropic",
                    model_used=self.config.model_name
                ))
        
        elif "fixes" in parsed:
            for i, item in enumerate(parsed["fixes"]):
                confidence = 0.9 if item.get("severity") == "high" else 0.8
                suggestions.append(CodeSuggestion(
                    id=f"anthropic_{int(time.time() * 1000)}_{i}",
                    text=item.get("issue", "Code fix"),
                    insert_text=item.get("solution"),
                    confidence_score=confidence,
                    explanation=item.get("explanation"),
                    suggestion_type="fix",
                    provider_name="anthropic",
                    model_used=self.config.model_name
                ))
        
        elif "optimizations" in parsed:
            for i, item in enumerate(parsed["optimizations"]):
                confidence = 0.9 if item.get("impact") == "high" else 0.7
                suggestions.append(CodeSuggestion(
                    id=f"anthropic_{int(time.time() * 1000)}_{i}",
                    text=item.get("benefit", "Code optimization"),
                    insert_text=item.get("improved"),
                    confidence_score=confidence,
                    explanation=item.get("reasoning"),
                    suggestion_type="optimization",
                    provider_name="anthropic",
                    model_used=self.config.model_name
                ))
        
        return suggestions
    
    def _get_max_tokens_for_model(self) -> int:
        """Get maximum tokens for the current model."""
        model_config = self.model_configs.get(self.config.model_name)
        if model_config:
            return model_config["max_tokens"]
        return 4096  # Default for Claude
