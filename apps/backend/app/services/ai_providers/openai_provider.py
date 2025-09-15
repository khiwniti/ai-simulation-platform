"""
OpenAI Provider for code suggestions using GPT models.
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
    import openai
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    AsyncOpenAI = None

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


class OpenAIProvider(BaseAIProvider):
    """
    OpenAI provider for code suggestions using GPT models.
    
    Supports:
    - GPT-4 and GPT-3.5-turbo for code completion and analysis
    - Streaming responses for real-time suggestions
    - Token counting and cost estimation
    - Context-aware code understanding
    """
    
    def __init__(self, config: AIProviderConfig):
        super().__init__(config)
        self.client: Optional[AsyncOpenAI] = None
        self.tokenizer = None
        
        # Model configurations
        self.model_configs = {
            "gpt-4": {
                "max_tokens": 8192,
                "context_length": 8192,
                "cost_per_1k_tokens": 0.03
            },
            "gpt-4-turbo-preview": {
                "max_tokens": 4096,
                "context_length": 128000,
                "cost_per_1k_tokens": 0.01
            },
            "gpt-3.5-turbo": {
                "max_tokens": 4096,
                "context_length": 16385,
                "cost_per_1k_tokens": 0.002
            },
            "gpt-3.5-turbo-16k": {
                "max_tokens": 4096,
                "context_length": 16385,
                "cost_per_1k_tokens": 0.004
            }
        }
    
    async def _initialize_provider(self) -> None:
        """Initialize OpenAI client and tokenizer."""
        if not OPENAI_AVAILABLE:
            raise ImportError("OpenAI library not available. Install with: pip install openai")
        
        api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OpenAI API key not provided")
        
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=self.config.base_url
        )
        
        # Initialize tokenizer for token counting
        if TIKTOKEN_AVAILABLE:
            try:
                model_name = self.config.model_name
                if "gpt-4" in model_name:
                    encoding_name = "cl100k_base"
                else:
                    encoding_name = "cl100k_base"
                self.tokenizer = tiktoken.get_encoding(encoding_name)
            except Exception as e:
                print(f"Warning: Could not initialize tokenizer: {e}")
    
    async def _get_suggestions_impl(
        self, 
        request: CodeSuggestionRequest
    ) -> AIProviderResponse:
        """Get code suggestions from OpenAI."""
        start_time = time.time()
        
        try:
            # Build messages for the chat completion
            messages = self._build_messages(request)
            
            # Count tokens
            tokens_used = self._count_tokens(messages) if self.tokenizer else 0
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=min(self.config.max_tokens, self._get_max_tokens_for_model()),
                temperature=self.config.temperature,
                n=min(request.max_suggestions, 3),  # Limit to 3 for cost control
                stream=False
            )
            
            # Parse suggestions
            suggestions = self._parse_response(response, request)
            
            # Update token usage
            if hasattr(response, 'usage') and response.usage:
                tokens_used = response.usage.total_tokens
            
            return AIProviderResponse(
                suggestions=suggestions,
                processing_time=time.time() - start_time,
                tokens_used=tokens_used,
                model_used=self.config.model_name,
                provider_name="openai"
            )
            
        except Exception as e:
            return AIProviderResponse(
                suggestions=[],
                processing_time=time.time() - start_time,
                tokens_used=0,
                model_used=self.config.model_name,
                provider_name="openai",
                error=str(e)
            )
    
    async def _get_streaming_suggestions_impl(
        self, 
        request: CodeSuggestionRequest
    ) -> AsyncGenerator[CodeSuggestion, None]:
        """Get streaming suggestions from OpenAI."""
        try:
            messages = self._build_messages(request)
            
            stream = await self.client.chat.completions.create(
                model=self.config.model_name,
                messages=messages,
                max_tokens=min(self.config.max_tokens, self._get_max_tokens_for_model()),
                temperature=self.config.temperature,
                stream=True
            )
            
            current_suggestion = ""
            suggestion_id = f"openai_{int(time.time() * 1000)}"
            
            async for chunk in stream:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        current_suggestion += delta.content
                        
                        # Yield incremental suggestion
                        yield CodeSuggestion(
                            id=suggestion_id,
                            text=current_suggestion,
                            insert_text=current_suggestion,
                            confidence_score=0.8,
                            suggestion_type=request.suggestion_type,
                            provider_name="openai",
                            model_used=self.config.model_name,
                            processing_time=time.time()
                        )
            
        except Exception as e:
            # Fallback to non-streaming
            response = await self._get_suggestions_impl(request)
            for suggestion in response.suggestions:
                yield suggestion
    
    def _build_messages(self, request: CodeSuggestionRequest) -> List[Dict[str, str]]:
        """Build messages for OpenAI chat completion."""
        system_prompt = self._get_system_prompt(request.suggestion_type, request.language)
        user_prompt = self._get_user_prompt(request)
        
        return [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    
    def _get_system_prompt(self, suggestion_type: str, language: str) -> str:
        """Get system prompt based on suggestion type."""
        base_prompt = f"""You are an expert {language} programmer with deep knowledge of:
- Physics simulation and NVIDIA PhysX AI
- 3D visualization with Three.js and WebGL
- Scientific computing with NumPy, SciPy
- Machine learning and AI frameworks
- Performance optimization and debugging

You provide accurate, efficient, and well-documented code suggestions."""

        if suggestion_type == "completion":
            return base_prompt + """

For code completion:
1. Analyze the context and provide relevant completions
2. Consider variable names, function calls, and imports in scope
3. Suggest multiple alternatives when appropriate
4. Include brief explanations for complex suggestions
5. Follow Python PEP 8 style guidelines

Respond with JSON format:
{
  "suggestions": [
    {
      "code": "completion code here",
      "description": "brief description",
      "explanation": "detailed explanation if needed"
    }
  ]
}"""

        elif suggestion_type == "explanation":
            return base_prompt + """

For code explanation:
1. Analyze the code and provide clear explanations
2. Explain purpose, functionality, and key concepts
3. Identify potential issues or improvements
4. Provide context about libraries and frameworks used
5. Include relevant documentation links when helpful

Respond with clear, educational explanations."""

        elif suggestion_type == "fix":
            return base_prompt + """

For code fixes:
1. Identify syntax errors, logical issues, and potential bugs
2. Provide corrected code with explanations
3. Suggest best practices and improvements
4. Consider performance and security implications
5. Explain why the fix is necessary

Respond with JSON format:
{
  "fixes": [
    {
      "issue": "description of issue",
      "fix": "corrected code",
      "explanation": "why this fix is needed"
    }
  ]
}"""

        elif suggestion_type == "optimization":
            return base_prompt + """

For code optimization:
1. Analyze performance bottlenecks and inefficiencies
2. Suggest more efficient algorithms or data structures
3. Recommend Python-specific optimizations
4. Consider memory usage and computational complexity
5. Provide benchmarking suggestions when relevant

Respond with JSON format:
{
  "optimizations": [
    {
      "original": "current code",
      "optimized": "improved code",
      "improvement": "description of improvement",
      "reasoning": "why this is better"
    }
  ]
}"""

        else:
            return base_prompt
    
    def _get_user_prompt(self, request: CodeSuggestionRequest) -> str:
        """Build user prompt with context."""
        context = request.code_context
        cursor_pos = request.cursor_position
        
        # Extract relevant context around cursor
        lines = context.split('\n')
        
        # Find current line
        current_pos = 0
        current_line_idx = 0
        for i, line in enumerate(lines):
            if current_pos + len(line) + 1 > cursor_pos:
                current_line_idx = i
                break
            current_pos += len(line) + 1
        
        # Get context window
        start_line = max(0, current_line_idx - 5)
        end_line = min(len(lines), current_line_idx + 6)
        context_lines = lines[start_line:end_line]
        
        # Mark current position
        if current_line_idx - start_line < len(context_lines):
            cursor_line = context_lines[current_line_idx - start_line]
            col_pos = cursor_pos - current_pos
            if 0 <= col_pos <= len(cursor_line):
                cursor_line = cursor_line[:col_pos] + "█" + cursor_line[col_pos:]
                context_lines[current_line_idx - start_line] = cursor_line
        
        formatted_context = '\n'.join(context_lines)
        
        if request.suggestion_type == "completion":
            return f"""Please provide code completion suggestions for the cursor position (marked with █):

```python
{formatted_context}
```

Context:
- Cursor is at position {cursor_pos}
- Current line: {current_line_idx + 1}
- Language: {request.language}

Please suggest appropriate completions considering the context, variable scope, and imports."""

        elif request.suggestion_type == "explanation":
            return f"""Please explain the following code context:

```python
{formatted_context}
```

Focus on the area around the cursor (marked with █). Explain what this code does, key concepts involved, and any relevant details."""

        elif request.suggestion_type == "fix":
            return f"""Please analyze this code for errors and provide fixes:

```python
{formatted_context}
```

The cursor is at the position marked with █. Look for syntax errors, logical issues, and potential bugs. Provide corrected code with explanations."""

        elif request.suggestion_type == "optimization":
            return f"""Please analyze this code for optimization opportunities:

```python
{formatted_context}
```

Focus on the area around the cursor (marked with █). Suggest performance improvements, better algorithms, or more efficient approaches."""

        else:
            return f"""Please analyze this code:

```python
{formatted_context}
```

Cursor position is marked with █. Provide helpful insights and suggestions."""
    
    def _parse_response(
        self, 
        response: Any, 
        request: CodeSuggestionRequest
    ) -> List[CodeSuggestion]:
        """Parse OpenAI response into code suggestions."""
        suggestions = []
        
        try:
            for i, choice in enumerate(response.choices):
                content = choice.message.content
                
                # Try to parse as JSON first
                try:
                    parsed = json.loads(content)
                    suggestions.extend(self._parse_json_response(parsed, request, i))
                except json.JSONDecodeError:
                    # Treat as plain text suggestion
                    suggestions.append(CodeSuggestion(
                        id=f"openai_{int(time.time() * 1000)}_{i}",
                        text=content,
                        insert_text=content if request.suggestion_type == "completion" else None,
                        confidence_score=0.8,
                        explanation=content if request.suggestion_type == "explanation" else None,
                        suggestion_type=request.suggestion_type,
                        provider_name="openai",
                        model_used=self.config.model_name
                    ))
        
        except Exception as e:
            print(f"Error parsing OpenAI response: {e}")
        
        return suggestions
    
    def _parse_json_response(
        self, 
        parsed: Dict[str, Any], 
        request: CodeSuggestionRequest, 
        choice_idx: int
    ) -> List[CodeSuggestion]:
        """Parse JSON response from OpenAI."""
        suggestions = []
        
        # Handle different response formats
        if "suggestions" in parsed:
            for i, item in enumerate(parsed["suggestions"]):
                suggestions.append(CodeSuggestion(
                    id=f"openai_{int(time.time() * 1000)}_{choice_idx}_{i}",
                    text=item.get("description", item.get("code", "")),
                    insert_text=item.get("code"),
                    confidence_score=0.8,
                    explanation=item.get("explanation"),
                    suggestion_type=request.suggestion_type,
                    provider_name="openai",
                    model_used=self.config.model_name
                ))
        
        elif "fixes" in parsed:
            for i, item in enumerate(parsed["fixes"]):
                suggestions.append(CodeSuggestion(
                    id=f"openai_{int(time.time() * 1000)}_{choice_idx}_{i}",
                    text=item.get("issue", "Fix suggestion"),
                    insert_text=item.get("fix"),
                    confidence_score=0.9,
                    explanation=item.get("explanation"),
                    suggestion_type="fix",
                    provider_name="openai",
                    model_used=self.config.model_name
                ))
        
        elif "optimizations" in parsed:
            for i, item in enumerate(parsed["optimizations"]):
                suggestions.append(CodeSuggestion(
                    id=f"openai_{int(time.time() * 1000)}_{choice_idx}_{i}",
                    text=item.get("improvement", "Optimization suggestion"),
                    insert_text=item.get("optimized"),
                    confidence_score=0.8,
                    explanation=item.get("reasoning"),
                    suggestion_type="optimization",
                    provider_name="openai",
                    model_used=self.config.model_name
                ))
        
        return suggestions
    
    def _count_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in messages."""
        if not self.tokenizer:
            return 0
        
        try:
            total = 0
            for message in messages:
                # Approximate token count for chat format
                content = message.get("content", "")
                tokens = len(self.tokenizer.encode(content))
                total += tokens + 4  # 4 tokens per message for chat format
            return total + 3  # 3 tokens for reply priming
        except Exception:
            return 0
    
    def _get_max_tokens_for_model(self) -> int:
        """Get maximum tokens for the current model."""
        model_config = self.model_configs.get(self.config.model_name)
        if model_config:
            return model_config["max_tokens"]
        return 2048  # Default fallback
